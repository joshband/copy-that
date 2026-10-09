"""Shadow extraction orchestration, persistence, and diagnostic artifacts."""

from __future__ import annotations

import base64
import json
import logging
import math
import mimetypes
import os
import tempfile
from collections.abc import Callable
from pathlib import Path
from typing import Any, cast

import numpy as np

from copy_that.application.ai_shadow_extractor import AIShadowExtractor
from copy_that.application.ai_shadow_extractor import ShadowExtractionResult as AIShadowResult
from copy_that.application.execution.async_executor import AsyncExecutor
from copy_that.application.ports.projects import ProjectRepository
from copy_that.application.ports.shadow_tokens import ShadowTokenRepository
from copy_that.domain.shadows import ShadowTokenCreate
from copy_that.extractors.shadow.cv_extractor import (
    NO_ELEVATION_DETECTED_MESSAGE,
    CVShadowExtractor,
)
from copy_that.extractors.shadow.cv_extractor import (
    ShadowExtractionResult as CVShadowResult,
)
from copy_that.extractors.shadow.upload_pipeline import ClassicalUploadPipeline
from copy_that.infrastructure.ai_models import claude_shadow_model
from copy_that.services.artifact_models import ArtifactBundle, ArtifactImage, ArtifactJson
from copy_that.services.shadow_extraction_models import (
    ShadowBatchItemResponse,
    ShadowBatchRequest,
    ShadowBatchResponse,
    ShadowExtractionRequest,
    ShadowExtractionResponse,
    ShadowTokenResponse,
)

logger = logging.getLogger(__name__)


class ShadowServiceError(Exception):
    """An extraction request failure mapped to HTTP by the router."""

    def __init__(self, *, status_code: int, detail: str) -> None:
        super().__init__(detail)
        self.status_code = status_code
        self.detail = detail


def _shadowlab_enabled() -> bool:
    env = os.getenv("ENABLE_SHADOWLAB", "true").lower()
    return env not in {"0", "false", "no", "off"}


_SHADOWLAB_ARTIFACT_LABELS: dict[str, str] = {
    "shadow_overlay": "Shadow overlay",
    "final_shadow_mask": "Final shadow mask",
    "ml_shadow_mask": "ML shadow mask",
    "candidate_mask": "Candidate mask",
    "illumination_map": "Illumination map",
    "reflectance_map": "Reflectance map",
    "shading_map": "Shading map",
    "depth_map": "Depth map",
    "normal_map_rgb": "Normal map",
}

_SHADOWLAB_JSON_LABELS: dict[str, str] = {
    "pipeline_results": "Pipeline results",
    "shadow_tokens": "Shadow tokens",
}


def _read_artifact_image(path: str) -> tuple[str, str] | None:
    if not path:
        return None
    file_path = Path(path)
    if not file_path.is_file():
        return None
    try:
        with open(file_path, "rb") as handle:
            encoded = base64.b64encode(handle.read()).decode("ascii")
    except Exception:
        return None
    mime_type, _ = mimetypes.guess_type(file_path.name)
    return encoded, (mime_type or "image/png")


def _read_artifact_json(path: str) -> dict[str, Any] | None:
    if not path:
        return None
    file_path = Path(path)
    if not file_path.is_file():
        return None
    try:
        with open(file_path, encoding="utf-8") as handle:
            payload = json.load(handle)
    except Exception:
        return None
    return payload if isinstance(payload, dict) else {"value": payload}


def _shadowlab_artifacts_bundle(shadowlab_meta: dict[str, Any] | None) -> ArtifactBundle | None:
    if not shadowlab_meta or not isinstance(shadowlab_meta, dict):
        return None
    artifacts = shadowlab_meta.get("artifacts")
    if not isinstance(artifacts, dict):
        return None
    images: list[ArtifactImage] = []
    json_items: list[ArtifactJson] = []
    for name, path in artifacts.items():
        if name not in _SHADOWLAB_ARTIFACT_LABELS:
            continue
        encoded = _read_artifact_image(str(path))
        if not encoded:
            continue
        payload, mime = encoded
        images.append(
            ArtifactImage(
                type=name,
                mime=mime,
                base64=payload,
                stage="shadowlab",
                description=_SHADOWLAB_ARTIFACT_LABELS.get(name),
            )
        )
    for name, path in artifacts.items():
        if name not in _SHADOWLAB_JSON_LABELS:
            continue
        json_payload = _read_artifact_json(str(path))
        if json_payload is None:
            continue
        json_items.append(
            ArtifactJson(
                type=name,
                payload=json_payload,
                stage="shadowlab",
            )
        )
    if not images and not json_items:
        return None
    return ArtifactBundle(images=images, json_=json_items)


def _failed_extractors_payload(
    failed: list[tuple[str, str]],
) -> list[dict[str, str]] | None:
    if not failed:
        return None
    return [{"name": name, "error": error} for name, error in failed]


async def extract_shadows_multi(
    request: ShadowExtractionRequest,
    project_repo: ProjectRepository,
    shadow_repo: ShadowTokenRepository,
    *,
    payload_guard: Callable[[str | None], None],
) -> ShadowExtractionResponse:
    """Extract shadows via CV+AI multi-extractor orchestration (not shadowlab)."""
    from copy_that.extractors.shadow.adapters import (
        AIShadowExtractorAdapter,
        CVShadowExtractorAdapter,
    )
    from copy_that.extractors.shadow.orchestrator import (
        ShadowAggregator,
        ShadowExtractionOrchestrator,
    )
    from copy_that.extractors.shadow.token_bridge import shadow_style_to_api_dict

    if request.project_id:
        project = await project_repo.get(project_id=request.project_id)
        if not project:
            raise ShadowServiceError(
                status_code=404,
                detail=f"Project {request.project_id} not found",
            )

    if not request.image_url and not request.image_base64:
        raise ShadowServiceError(
            status_code=400,
            detail="Either image_url or image_base64 must be provided",
        )

    try:
        payload_guard(request.image_base64)
        if request.image_base64:
            payload = request.image_base64
            if "," in payload:
                payload = payload.split(",", 1)[1]
            image_bytes = base64.b64decode(payload)
        else:
            import requests

            resp = requests.get(str(request.image_url), timeout=15)
            resp.raise_for_status()
            image_bytes = resp.content

        extractors = [
            CVShadowExtractorAdapter(),
            AIShadowExtractorAdapter(),
        ]
        orchestrator = ShadowExtractionOrchestrator(
            extractors=extractors,
            aggregator=ShadowAggregator(distance_threshold=5.0),
        )
        import uuid

        image_id = f"shadow_multi_{uuid.uuid4().hex[:8]}"
        result = await orchestrator.extract_all_safe(image_bytes, image_id)

        limited = result.aggregated_tokens[: request.max_tokens]
        token_responses = [
            ShadowTokenResponse(**shadow_style_to_api_dict(style, idx))
            for idx, style in enumerate(limited)
        ]

        if request.project_id and token_responses:
            await shadow_repo.record_extraction(
                project_id=request.project_id,
                source_url=str(request.image_url) if request.image_url else "base64_upload",
                shadows=[
                    ShadowTokenCreate(
                        x_offset=t.x_offset,
                        y_offset=t.y_offset,
                        blur_radius=t.blur_radius,
                        spread_radius=t.spread_radius,
                        color_hex=t.color_hex,
                        opacity=t.opacity,
                        name=t.name,
                        shadow_type=t.shadow_type,
                        semantic_role=t.semantic_role,
                        confidence=t.confidence,
                    )
                    for t in token_responses
                ],
            )

        return ShadowExtractionResponse(
            tokens=token_responses,
            extraction_confidence=float(result.overall_confidence or 0.0),
            extraction_metadata={
                "failed_extractors": result.failed_extractors,
                "total_time_ms": result.total_time_ms,
            },
            artifacts=None,
            warnings=None,
            extractor_used="multi-extractor-orchestrator",
            failed_extractors=_failed_extractors_payload(result.failed_extractors),
        )
    except ShadowServiceError:
        raise
    except Exception as e:
        logger.exception("Shadow multi-extractor extraction failed")
        raise ShadowServiceError(
            status_code=500,
            detail=f"Shadow multi-extractor extraction failed: {e}",
        ) from e


async def extract_shadows(
    request: ShadowExtractionRequest,
    project_repo: ProjectRepository,
    shadow_repo: ShadowTokenRepository,
    async_executor: AsyncExecutor,
    *,
    cv_factory: Callable[[], CVShadowExtractor],
    ai_factory: Callable[[], AIShadowExtractor],
    shadowlab_enabled: Callable[[], bool],
    pipeline_runner: Callable[[str, str], dict[str, Any]],
    payload_guard: Callable[[str | None], None],
    artifact_builder: Callable[
        [dict[str, Any] | None], ArtifactBundle | None
    ] = _shadowlab_artifacts_bundle,
) -> ShadowExtractionResponse:
    """Extract, combine diagnostics, and persist optional shadow tokens."""
    # Validate project exists if provided
    if request.project_id:
        project = await project_repo.get(project_id=request.project_id)
        if not project:
            raise ShadowServiceError(
                status_code=404,
                detail=f"Project {request.project_id} not found",
            )

    # Validate at least one image source
    if not request.image_url and not request.image_base64:
        raise ShadowServiceError(
            status_code=400,
            detail="Either image_url or image_base64 must be provided",
        )

    try:
        # Download image if URL provided
        cv_b64 = request.image_base64
        media_type = request.image_media_type or "image/png"

        if request.image_url and not request.image_base64:
            try:
                import base64

                import requests

                resp = requests.get(str(request.image_url), timeout=10)
                resp.raise_for_status()
                cv_b64 = base64.b64encode(resp.content).decode("utf-8")
            except Exception as e:
                logger.error("Failed to download image from URL: %s", e)
                raise ShadowServiceError(
                    status_code=400,
                    detail=f"Failed to fetch image: {str(e)}",
                )

        payload_guard(request.image_base64)
        # Default CV path: classical shadowlab → CSS tokens (dark-blob opt-in only)
        cv_extractor = cv_factory()
        cv_result = await async_executor.run(
            lambda: cv_extractor.extract_shadows(
                base64_image=cv_b64 or "",
                media_type=media_type,
            )
        )

        logger.info(
            "CV extraction found %s shadows via %s",
            cv_result.shadow_count,
            cv_result.extractor_used,
        )

        # Try AI enhancement if available (but don't fail if API key missing)
        ai_result = None
        extractor_source = cv_result.extractor_used or "cv_classical_css"
        result: CVShadowResult | AIShadowResult = cv_result
        try:
            ai_extractor = ai_factory()
            ai_result = await async_executor.run(
                lambda: ai_extractor.extract_shadows(
                    base64_image=cv_b64 or "",
                    media_type=media_type,
                    quality=request.quality,
                )
            )
            if ai_result.shadow_count > 0:
                logger.info("AI extraction enhanced with %s shadows", ai_result.shadow_count)
                result = ai_result
                extractor_source = "claude_sonnet_4.5_with_cv_fallback"
            else:
                logger.info("AI found no shadows, using CV results (%s)", cv_result.extractor_used)
                result = cv_result
        except Exception as e:
            # AI API unavailable/failed - use classical / CV results gracefully
            logger.warning(
                "AI extraction unavailable (%s), using CV results: %s",
                type(e).__name__,
                e,
            )
            result = cv_result
            extractor_source = f"{cv_result.extractor_used}_fallback"

        shadowlab_meta: dict[str, Any] | None = None
        if shadowlab_enabled() and cv_b64:
            try:
                shadowlab_meta = await async_executor.run(
                    lambda: pipeline_runner(cv_b64 or "", media_type)
                )
            except Exception as e:  # pragma: no cover - best-effort path
                logger.warning("Shadowlab pipeline failed: %s", e)
                shadowlab_meta = {"error": str(e)}

        shadowlab_artifacts = (
            artifact_builder(shadowlab_meta) if request.include_artifacts else None
        )

        # Convert to response format
        token_responses = [
            ShadowTokenResponse(
                x_offset=shadow.x_offset,
                y_offset=shadow.y_offset,
                blur_radius=shadow.blur_radius,
                spread_radius=shadow.spread_radius,
                color_hex=shadow.color_hex,
                opacity=shadow.opacity,
                name=shadow.semantic_name,
                shadow_type=shadow.shadow_type,
                semantic_role="inset" if shadow.is_inset else "drop",
                confidence=shadow.confidence,
            )
            for shadow in result.shadows
        ]

        # Calculate overall confidence
        overall_confidence = (
            sum(t.confidence for t in token_responses) / len(token_responses)
            if token_responses
            else 0.0
        )

        # Ensure it's a float for the response
        overall_confidence = float(overall_confidence)

        # Persist to database if project_id provided
        if request.project_id:
            await shadow_repo.record_extraction(
                source_url=str(request.image_url) if request.image_url else "base64_upload",
                project_id=request.project_id,
                shadows=[
                    ShadowTokenCreate(
                        x_offset=shadow.x_offset,
                        y_offset=shadow.y_offset,
                        blur_radius=shadow.blur_radius,
                        spread_radius=shadow.spread_radius,
                        color_hex=shadow.color_hex,
                        opacity=shadow.opacity,
                        name=shadow.semantic_name,
                        shadow_type=shadow.shadow_type,
                        semantic_role="inset" if shadow.is_inset else "drop",
                        confidence=shadow.confidence,
                    )
                    for shadow in result.shadows
                ],
            )
            logger.info(
                "Persisted %d shadow tokens for project %d",
                len(token_responses),
                request.project_id,
            )

        opacity_tokens = list(getattr(cv_result, "opacity_tokens", None) or [])
        if not opacity_tokens and token_responses:
            seen_ops: set[float] = set()
            for tok in token_responses:
                op = round(float(tok.opacity), 3)
                if op in seen_ops:
                    continue
                seen_ops.add(op)
                opacity_tokens.append(
                    {
                        "id": f"opacity.shadow-{tok.name}",
                        "value": op,
                        "source": "shadow",
                        "shadow_name": tok.name,
                    }
                )

        warnings_out: list[str] = []
        product_message: str | None = getattr(cv_result, "product_message", None)
        if not token_responses and (
            cv_result.extractor_used == "cv_classical_empty" or product_message
        ):
            msg = product_message or NO_ELEVATION_DETECTED_MESSAGE
            product_message = msg
            warnings_out.append(msg)
        for w in getattr(cv_result, "warnings", None) or []:
            if isinstance(w, str) and w and w not in warnings_out:
                warnings_out.append(w)

        return ShadowExtractionResponse(
            tokens=token_responses,
            extraction_confidence=overall_confidence,
            extraction_metadata={
                "extraction_source": extractor_source,
                "model": claude_shadow_model()
                if "claude" in extractor_source
                else cv_result.extractor_used,
                "token_count": len(token_responses),
                "fallback_used": extractor_source != "claude_sonnet_4.5_with_cv_fallback",
                "cv_extractor_used": cv_result.extractor_used,
                "opacity_from_shadows": opacity_tokens,
                **(
                    {
                        "product_message": product_message,
                        "empty_reason": "no_elevation",
                    }
                    if product_message and not token_responses
                    else {}
                ),
                **({"shadowlab": shadowlab_meta} if shadowlab_meta else {}),
            },
            warnings=warnings_out or None,
            artifacts=shadowlab_artifacts,
        )

    except ShadowServiceError:
        raise
    except Exception as e:
        logger.exception("Shadow extraction completely failed (CV and AI): %s", e)
        # Return graceful empty result instead of 500 error
        return ShadowExtractionResponse(
            tokens=[],
            extraction_confidence=0.0,
            extraction_metadata={
                "extraction_source": "failed_cv_and_ai",
                "error": str(e),
                "token_count": 0,
            },
            artifacts=None,
        )


async def extract_shadows_batch(
    request: ShadowBatchRequest,
    async_executor: AsyncExecutor,
    *,
    cv_factory: Callable[[], CVShadowExtractor],
    ai_factory: Callable[[], AIShadowExtractor],
    shadowlab_enabled: Callable[[], bool],
    pipeline_runner: Callable[[str, str], dict[str, Any]],
) -> ShadowBatchResponse:
    """
    Batch shadow extraction for multiple image URLs (no persistence).
    """
    results: list[ShadowBatchItemResponse] = []
    cv_extractor = cv_factory()

    for url in request.image_urls:
        warnings: list[str] = []
        extractor_source = "cv_classical_css"
        try:
            import requests

            resp = requests.get(str(url), timeout=10)
            resp.raise_for_status()
            media_type = resp.headers.get("Content-Type", "image/png")
            cv_b64 = base64.b64encode(resp.content).decode("utf-8")

            cv_result = await async_executor.run(
                lambda cv_b64=cv_b64, media_type=media_type: cv_extractor.extract_shadows(
                    base64_image=cv_b64, media_type=media_type
                )
            )
            extractor_source = cv_result.extractor_used or "cv_classical_css"

            try:
                ai_extractor = ai_factory()
                ai_result = await async_executor.run(
                    lambda ai_extractor=ai_extractor, cv_b64=cv_b64, media_type=media_type: (
                        ai_extractor.extract_shadows(
                            base64_image=cv_b64,
                            media_type=media_type,
                        )
                    )
                )
                if ai_result.shadow_count > 0:
                    result = ai_result
                    extractor_source = "claude_sonnet_4.5_with_cv_fallback"
                else:
                    result = cv_result
            except Exception as e:  # pragma: no cover - best-effort
                warnings.append(f"AI extraction unavailable: {e}")
                result = cv_result
                extractor_source = f"{cv_result.extractor_used}_fallback"

            shadowlab_meta: dict[str, Any] | None = None
            if shadowlab_enabled():
                try:
                    shadowlab_meta = await async_executor.run(
                        lambda cv_b64=cv_b64, media_type=media_type: pipeline_runner(
                            cv_b64, media_type
                        )
                    )
                except Exception as e:  # pragma: no cover
                    warnings.append(f"Shadowlab failed: {e}")

            tokens = [
                ShadowTokenResponse(
                    x_offset=shadow.x_offset,
                    y_offset=shadow.y_offset,
                    blur_radius=shadow.blur_radius,
                    spread_radius=shadow.spread_radius,
                    color_hex=shadow.color_hex,
                    opacity=shadow.opacity,
                    name=shadow.semantic_name,
                    shadow_type=shadow.shadow_type,
                    semantic_role="inset" if shadow.is_inset else "drop",
                    confidence=shadow.confidence,
                )
                for shadow in result.shadows
            ]

            overall_confidence = sum(t.confidence for t in tokens) / len(tokens) if tokens else 0.0

            warnings_out = warnings if warnings else None
            if shadowlab_meta:
                warnings_out = (warnings_out or []) + ["Shadowlab metrics available"]
            if not tokens and getattr(cv_result, "extractor_used", None) == "cv_classical_empty":
                msg = getattr(cv_result, "product_message", None) or NO_ELEVATION_DETECTED_MESSAGE
                warnings_out = (warnings_out or []) + [msg]

            results.append(
                ShadowBatchItemResponse(
                    image_url=url,
                    tokens=tokens,
                    extractor_used=extractor_source,
                    extraction_confidence=float(overall_confidence),
                    warnings=warnings_out,
                )
            )
        except Exception as e:
            results.append(
                ShadowBatchItemResponse(
                    image_url=url,
                    tokens=[],
                    extractor_used="error",
                    extraction_confidence=0.0,
                    warnings=[f"Failed to process: {e}"],
                )
            )

    return ShadowBatchResponse(results=results)


def _run_shadowlab_pipeline(image_b64: str, media_type: str) -> dict[str, Any]:
    """Run the shadowlab orchestrator on a base64 image and return metrics."""
    image_bytes = base64.b64decode(image_b64)
    suffix = ".jpg" if "jpeg" in media_type else ".png"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(image_bytes)
        tmp_path = tmp.name

    output_dir = Path(tempfile.mkdtemp(prefix="shadowlab_"))

    def _json_safe(value: Any) -> Any:
        if isinstance(value, dict):
            return {k: _json_safe(v) for k, v in value.items()}
        if isinstance(value, list):
            return [_json_safe(v) for v in value]
        if isinstance(value, tuple):
            return [_json_safe(v) for v in value]
        if isinstance(value, Path):
            return str(value)
        if isinstance(value, float):
            return value if math.isfinite(value) else None
        if isinstance(value, np.generic):
            return _json_safe(value.item())
        if isinstance(value, np.ndarray):
            return _json_safe(value.tolist())
        return value

    try:
        orchestrator = ClassicalUploadPipeline(
            image_path=tmp_path,
            output_dir=output_dir,
            verbose=False,
        )
        result = orchestrator.run()
        pipeline_results = result.get("pipeline_results") or {}
        stages = pipeline_results.get("stages") or []

        def _stage(stage_id: str) -> dict[str, Any] | None:
            for stage in stages:
                if isinstance(stage, dict) and stage.get("id") == stage_id:
                    return stage
            return None

        ml_stage = _stage("shadow_stage_04_ml_mask")
        geom_stage = _stage("shadow_stage_06_geometry")
        pipeline_summary = {
            "mode": result.get("pipeline_mode"),
            "ml_backend": (ml_stage or {}).get("artifacts", {}).get("ml_backend"),
            "geometry_backends": (geom_stage or {}).get("artifacts", {}).get("geometry_backends"),
        }
        payload = {
            "token_set": result.get("shadow_token_set"),
            "duration_ms": result.get("total_duration_ms"),
            "artifacts": result.get("artifacts_paths"),
            "pipeline": pipeline_summary,
        }
        safe_payload = _json_safe(payload)
        return cast(dict[str, Any], safe_payload)
    finally:
        try:
            os.remove(tmp_path)
        except Exception:
            pass


def multi_extractor_enabled() -> bool:
    """Read the opt-in multi-extractor override."""
    return os.getenv("COPY_THAT_MULTI_EXTRACTOR", "0") == "1"
