"""Typography extraction orchestration, fallback and persistence independent of HTTP."""

from __future__ import annotations

import base64
import json
import logging
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

import requests

from copy_that.application.ports.color_token_records import ColorTokenRepository
from copy_that.application.ports.typography_tokens import TypographyTokenRepository
from copy_that.application.typography_extractor import (
    AITypographyExtractor,
    ExtractedTypographyToken,
    TypographyExtractionResult,
)
from copy_that.domain.typography import TypographyTokenCreate
from copy_that.extractors.typography.cv_extractor import CVTypographyExtractor
from copy_that.extractors.typography.recommender import StyleAttributes
from copy_that.services.typography_recommendation import (
    infer_style_from_colors,
    recommend_typography_tokens,
)
from copy_that.services.typography_service import merge_typography

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class TypographyExtractionInput:
    project_id: int
    image_url: str | None = None
    image_base64: str | None = None
    image_media_type: str | None = None
    max_tokens: int = 15
    extractor: str | None = None


@dataclass(frozen=True)
class TypographyExtractionOutcome:
    result: TypographyExtractionResult
    namespace: str
    failed_extractors: list[dict[str, str]] | None = None


def detect_image_format(base64_data: str) -> str | None:
    """Detect image format from base64 data by reading magic bytes.

    Args:
        base64_data: Base64-encoded image data

    Returns:
        MIME type string (e.g., 'image/jpeg') or None if detection fails
    """
    try:
        # Decode first few bytes to read magic bytes
        image_bytes = base64.b64decode(base64_data[:100])

        # Check magic bytes for common formats
        if image_bytes.startswith(b"\xff\xd8\xff"):
            return "image/jpeg"
        elif image_bytes.startswith(b"\x89PNG"):
            return "image/png"
        elif image_bytes.startswith(b"GIF87a") or image_bytes.startswith(b"GIF89a"):
            return "image/gif"
        elif image_bytes.startswith(b"RIFF") and b"WEBP" in image_bytes[:20]:
            return "image/webp"
    except Exception as e:
        logger.debug("Failed to detect image format: %s", e)

    return None


def only_fallback_tokens(tokens: list[Any]) -> bool:
    if not tokens:
        return True
    for token in tokens:
        meta = getattr(token, "extraction_metadata", None) or {}
        source = meta.get("extraction_source") or meta.get("source")
        if source != "fallback":
            return False
    return True


async def _persist(
    project_id: int,
    source_url: str,
    extraction_result: TypographyExtractionResult,
    typography_repo: TypographyTokenRepository,
    result_data: dict[str, Any],
) -> int:
    return await typography_repo.record_extraction(
        project_id=project_id,
        source_url=source_url,
        tokens=[
            TypographyTokenCreate(
                project_id=project_id,
                extraction_job_id=None,
                font_family=token.font_family,
                font_weight=token.font_weight,
                font_style=token.font_style,
                font_size=token.font_size,
                line_height=token.line_height,
                letter_spacing=token.letter_spacing,
                text_transform=token.text_transform,
                text_align=token.text_align,
                name=token.name,
                semantic_role=token.semantic_role,
                category=token.category,
                confidence=token.confidence,
                prominence=token.prominence,
                is_readable=token.is_readable,
                readability_score=token.readability_score,
                extraction_metadata=json.dumps(token.extraction_metadata)
                if token.extraction_metadata
                else None,
            )
            for token in extraction_result.tokens
        ],
        result_data=result_data,
    )


async def extract_typography(
    request: TypographyExtractionInput,
    typography_repo: TypographyTokenRepository,
    color_repo: ColorTokenRepository,
    *,
    ai_factory: Callable[[], AITypographyExtractor] = AITypographyExtractor,
    cv_factory: Callable[[], CVTypographyExtractor] = CVTypographyExtractor,
    http_get: Callable[..., requests.Response] = requests.get,
    infer_style: Callable[..., StyleAttributes] = infer_style_from_colors,
    recommend_tokens: Callable[
        [StyleAttributes], tuple[list[ExtractedTypographyToken], float]
    ] = recommend_typography_tokens,
) -> TypographyExtractionOutcome:
    extractor_choice = (request.extractor or "auto").lower()
    if extractor_choice not in {"auto", "ai", "cv", "recommendation"}:
        raise ValueError("extractor must be one of: auto, ai, cv, recommendation")

    ai_result = None
    cv_result = None
    merged_tokens: list[Any] = []

    if extractor_choice not in {"recommendation", "cv"}:
        try:
            ai_extractor = ai_factory()
            if request.image_base64:
                media_type = (
                    request.image_media_type
                    or detect_image_format(request.image_base64)
                    or "image/jpeg"
                )
                ai_result = ai_extractor.extract_typography_from_base64(
                    request.image_base64, media_type=media_type, max_tokens=request.max_tokens
                )
            else:
                ai_result = ai_extractor.extract_typography_from_image_url(
                    request.image_url, max_tokens=request.max_tokens
                )
        except Exception as e:
            # Missing API key / client init failures should not 500 in auto mode —
            # fall through to CV then color-based recommendation.
            if extractor_choice == "ai":
                raise
            logger.warning("AI typography unavailable, continuing with CV/recommendation: %s", e)
            ai_result = None

    if (
        extractor_choice == "cv"
        or (
            extractor_choice == "auto"
            and (ai_result is None or (ai_result and ai_result.extraction_confidence < 0.6))
        )
        or (ai_result and ai_result.extraction_confidence < 0.6 and extractor_choice != "ai")
    ):
        cv_extractor = cv_factory()
        try:
            if request.image_base64:
                payload = request.image_base64.split(",", 1)[-1]
                cv_bytes = base64.b64decode(payload)
            else:
                resp = http_get(request.image_url, timeout=10)
                resp.raise_for_status()
                cv_bytes = resp.content
            cv_tokens = await cv_extractor.extract(cv_bytes)
            if cv_tokens:
                cv_confidence = sum(t.confidence for t in cv_tokens) / len(cv_tokens)
                cv_result = TypographyExtractionResult(
                    tokens=cv_tokens,
                    typography_palette="OCR typography extraction",
                    extraction_confidence=cv_confidence,
                    extractor_used="cv_ocr_extractor",
                    color_associations=None,
                )
        except Exception as e:
            logger.debug("CV fallback skipped: %s", e)
            cv_result = None

    if cv_result and ai_result:
        merged_tokens = merge_typography(cv_result, ai_result).tokens
    elif ai_result:
        merged_tokens = ai_result.tokens
    elif cv_result:
        merged_tokens = cv_result.tokens

    use_recommendation = extractor_choice == "recommendation"
    if extractor_choice == "auto" and (only_fallback_tokens(merged_tokens) or not merged_tokens):
        use_recommendation = True

    if use_recommendation:
        colors = await color_repo.list_by_project(project_id=request.project_id)
        style_attributes = infer_style(colors)
        recommended_tokens, recommendation_confidence = recommend_tokens(style_attributes)
        extraction_result = TypographyExtractionResult(
            tokens=recommended_tokens,
            typography_palette="Recommended typography system based on project colors",
            extraction_confidence=recommendation_confidence,
            extractor_used="typography_recommender",
            color_associations={"style_attributes": style_attributes},
        )
    else:
        extraction_result = TypographyExtractionResult(
            tokens=merged_tokens,
            typography_palette=(
                ai_result.typography_palette
                if ai_result
                else cv_result.typography_palette
                if cv_result
                else None
            ),
            extraction_confidence=(
                ai_result.extraction_confidence
                if ai_result
                else cv_result.extraction_confidence
                if cv_result
                else 0.0
            ),
            extractor_used=(
                ai_result.extractor_used
                if ai_result
                else cv_result.extractor_used
                if cv_result
                else "unknown"
            ),
            color_associations=(
                ai_result.color_associations
                if ai_result
                else cv_result.color_associations
                if cv_result
                else None
            ),
        )

    source_identifier = request.image_url or "base64_upload"
    result_payload: dict[str, Any] = {
        "typography_count": len(extraction_result.tokens),
        "palette": extraction_result.typography_palette,
        "source": extraction_result.extractor_used,
    }
    if use_recommendation:
        associations = extraction_result.color_associations or {}
        result_payload["style_attributes"] = associations.get("style_attributes", associations)

    job_id = await _persist(
        request.project_id, source_identifier, extraction_result, typography_repo, result_payload
    )
    logger.info(
        "Extracted %d typography tokens for project %d",
        len(extraction_result.tokens),
        request.project_id,
    )

    return TypographyExtractionOutcome(
        extraction_result, f"token/typography/project/{request.project_id}/job/{job_id}"
    )


async def extract_typography_multi(
    request: TypographyExtractionInput,
    typography_repo: TypographyTokenRepository,
    *,
    http_get: Callable[..., requests.Response] = requests.get,
) -> TypographyExtractionOutcome:
    from copy_that.extractors.typography.adapters import (
        AITypographyExtractorAdapter,
        CVTypographyExtractorAdapter,
    )
    from copy_that.extractors.typography.orchestrator import (
        TypographyAggregator,
        TypographyExtractionOrchestrator,
    )

    if request.image_base64:
        payload = request.image_base64
        if "," in payload:
            payload = payload.split(",", 1)[1]
        image_bytes = base64.b64decode(payload)
    else:
        resp = http_get(str(request.image_url), timeout=15)
        resp.raise_for_status()
        image_bytes = resp.content

    extractors = [
        CVTypographyExtractorAdapter(),
        AITypographyExtractorAdapter(),
    ]
    orchestrator = TypographyExtractionOrchestrator(
        extractors=extractors,
        aggregator=TypographyAggregator(font_size_threshold=3),
    )
    import uuid

    image_id = f"typography_multi_{uuid.uuid4().hex[:8]}"
    result = await orchestrator.extract_all_safe(image_bytes, image_id)

    extraction_result = TypographyExtractionResult(
        tokens=list(result.aggregated_tokens),
        typography_palette="Multi-extractor orchestrated typography",
        extraction_confidence=float(result.overall_confidence or 0.0),
        extractor_used="multi-extractor-orchestrator",
        color_associations=None,
    )

    job_id = await _persist(
        request.project_id,
        str(request.image_url) if request.image_url else "base64_upload",
        extraction_result,
        typography_repo,
        {
            "token_count": len(extraction_result.tokens),
            "extractor_used": "multi-extractor-orchestrator",
            "failed_extractors": result.failed_extractors,
        },
    )
    return TypographyExtractionOutcome(
        extraction_result,
        f"token/typography/project/{request.project_id}/job/{job_id}",
        [{"name": name, "error": error} for name, error in result.failed_extractors] or None,
    )


async def extract_typography_batch[ResponseT](
    image_urls: list[str],
    project_id: int | None,
    max_tokens: int,
    typography_repo: TypographyTokenRepository,
    *,
    ai_factory: Callable[[], AITypographyExtractor] = AITypographyExtractor,
    response_factory: Callable[[TypographyExtractionOutcome], ResponseT],
) -> list[ResponseT]:
    """Skip failed items, including persistence or response validation failures."""
    ai_extractor = ai_factory()
    responses: list[ResponseT] = []
    for url in image_urls:
        try:
            extraction_result = ai_extractor.extract_typography_from_image_url(
                url, max_tokens=max_tokens
            )
            job_id = None
            if project_id:
                job_id = await _persist(
                    project_id,
                    url,
                    extraction_result,
                    typography_repo,
                    {"typography_count": len(extraction_result.tokens)},
                )
            namespace = (
                f"token/typography/project/{project_id}/job/{job_id}"
                if job_id is not None and project_id
                else f"token/typography/batch/{len(responses) + 1:02d}"
            )
            responses.append(
                response_factory(TypographyExtractionOutcome(extraction_result, namespace))
            )
        except Exception as e:
            logger.error("Batch typography extraction failed for %s: %s", url, str(e))
    return responses
