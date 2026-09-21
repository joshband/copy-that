from __future__ import annotations

import base64
import json
import logging
import math
import mimetypes
import os
import tempfile
from pathlib import Path
from typing import Any, cast

import numpy as np
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, HttpUrl

from copy_that.application.ai_shadow_extractor import AIShadowExtractor
from copy_that.application.execution.async_executor import AsyncExecutor
from copy_that.application.ports.projects import ProjectRepository
from copy_that.application.ports.shadow_tokens import ShadowTokenRepository
from copy_that.domain.shadows import ShadowTokenCreate
from copy_that.extractors.shadow.cv_extractor import (
    NO_ELEVATION_DETECTED_MESSAGE,
    CVShadowExtractor,
)
from copy_that.infrastructure.security.rate_limiter import rate_limit
from copy_that.interfaces.api import dependencies as deps
from copy_that.interfaces.api.schemas import ArtifactBundle, ArtifactImage, ArtifactJson
from copy_that.interfaces.api.utils import enforce_payload_size
from copy_that.shadowlab.orchestrator import ShadowPipelineOrchestrator


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
        payload = _read_artifact_json(str(path))
        if payload is None:
            continue
        json_items.append(
            ArtifactJson(
                type=name,
                payload=payload,
                stage="shadowlab",
            )
        )
    if not images and not json_items:
        return None
    return ArtifactBundle(images=images, json_=json_items)


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/shadows", tags=["shadows"])


# Request/Response Schemas
class ShadowTokenResponse(BaseModel):
    """Response model for a single shadow token."""

    x_offset: float = Field(..., description="X offset in pixels")
    y_offset: float = Field(..., description="Y offset in pixels")
    blur_radius: float = Field(..., description="Blur radius in pixels")
    spread_radius: float = Field(default=0.0, description="Spread radius in pixels")
    color_hex: str = Field(..., description="Shadow color in hex format")
    opacity: float = Field(..., ge=0, le=1, description="Opacity (0-1)")
    name: str = Field(..., description="Shadow token name")
    shadow_type: str | None = Field(None, description="Shadow type (drop, inner, text)")
    semantic_role: str | None = Field(None, description="Semantic role (subtle, medium, strong)")
    confidence: float = Field(..., ge=0, le=1, description="Extraction confidence")


class ShadowExtractionRequest(BaseModel):
    """Request model for shadow extraction."""

    image_url: HttpUrl | None = Field(None, description="URL of the image to analyze")
    image_base64: str | None = Field(
        None, description="Base64 image payload (data URL payload without the prefix)"
    )
    image_media_type: str | None = Field(
        "image/png", description="Media type for base64 image (e.g., image/png)"
    )
    project_id: int | None = Field(None, description="Optional project to persist tokens")
    max_tokens: int = Field(default=10, ge=1, le=50, description="Maximum shadow tokens to extract")
    quality: str = Field("standard", description="Extraction quality: fast|standard|premium")
    include_artifacts: bool = Field(
        default=False, description="Include shadowlab artifact previews"
    )
    use_multi_extractor: bool = Field(
        default=False,
        description="When true, use ShadowExtractionOrchestrator (CV+AI parallel)",
    )


class ShadowExtractionResponse(BaseModel):
    """Response model for shadow extraction result."""

    tokens: list[ShadowTokenResponse] = Field(..., description="Extracted shadow tokens")
    extraction_confidence: float = Field(
        ..., ge=0, le=1, description="Overall extraction confidence"
    )
    extraction_metadata: dict[str, Any] | None = Field(
        None, description="Extraction metadata and diagnostics"
    )
    artifacts: ArtifactBundle | None = Field(None, description="Shadow extraction artifacts")
    warnings: list[str] | None = Field(None, description="Any warnings during extraction")
    extractor_used: str | None = Field(
        default=None, description="Extractor path used (e.g. multi-extractor-orchestrator)"
    )
    failed_extractors: list[dict[str, str]] | None = Field(
        default=None, description="Extractors that failed during multi-extractor runs"
    )


class ShadowBatchRequest(BaseModel):
    """Batch shadow extraction request."""

    image_urls: list[HttpUrl] = Field(..., min_length=1, description="Image URLs to analyze")
    project_id: int | None = Field(None, description="Optional project for persistence")
    max_tokens: int = Field(default=10, ge=1, le=50, description="Maximum shadow tokens per image")


class ShadowBatchItemResponse(BaseModel):
    """Per-image batch extraction result."""

    image_url: HttpUrl
    tokens: list[ShadowTokenResponse]
    extractor_used: str
    extraction_confidence: float
    warnings: list[str] | None = None


class ShadowBatchResponse(BaseModel):
    """Batch response."""

    results: list[ShadowBatchItemResponse]


def _use_multi_extractor(request: ShadowExtractionRequest) -> bool:
    env_on = os.getenv("COPY_THAT_MULTI_EXTRACTOR", "0") == "1"
    return env_on or bool(getattr(request, "use_multi_extractor", False))


def _failed_extractors_payload(
    failed: list[tuple[str, str]],
) -> list[dict[str, str]] | None:
    if not failed:
        return None
    return [{"name": name, "error": error} for name, error in failed]


@router.post("/extract/multi", response_model=ShadowExtractionResponse)
async def extract_shadows_multi(
    request: ShadowExtractionRequest,
    project_repo: ProjectRepository = Depends(deps.get_project_repo),
    shadow_repo: ShadowTokenRepository = Depends(deps.get_shadow_repo),
    _rate_limit: None = Depends(rate_limit(requests=10, seconds=60)),
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
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project {request.project_id} not found",
            )

    if not request.image_url and not request.image_base64:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either image_url or image_base64 must be provided",
        )

    try:
        enforce_payload_size(request.image_base64)
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
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Shadow multi-extractor extraction failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Shadow multi-extractor extraction failed: {e}",
        ) from e


@router.post("/extract", response_model=ShadowExtractionResponse)
async def extract_shadows(
    request: ShadowExtractionRequest,
    project_repo: ProjectRepository = Depends(deps.get_project_repo),
    shadow_repo: ShadowTokenRepository = Depends(deps.get_shadow_repo),
    async_executor: AsyncExecutor = Depends(deps.get_async_executor),
    _rate_limit: None = Depends(rate_limit(requests=10, seconds=60)),
) -> ShadowExtractionResponse:
    """
    Extract shadow tokens from an image using AI analysis.

    This endpoint:
    1. Accepts either an image URL or base64 encoded image data
    2. Uses Claude Sonnet 4.5 to analyze and extract shadow patterns
    3. Stores extracted shadows in the database (if project_id provided)
    4. Returns the extracted shadow palette

    Args:
        request: ShadowExtractionRequest with image_url or image_base64 and optional project_id
        db: Database session

    Returns:
        ShadowExtractionResponse with extracted shadows

    Raises:
        HTTPException: If project not found or extraction fails
    """
    if _use_multi_extractor(request):
        return await extract_shadows_multi(
            request=request,
            project_repo=project_repo,
            shadow_repo=shadow_repo,
            _rate_limit=_rate_limit,
        )

    # Validate project exists if provided
    if request.project_id:
        project = await project_repo.get(project_id=request.project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project {request.project_id} not found",
            )

    # Validate at least one image source
    if not request.image_url and not request.image_base64:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
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
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Failed to fetch image: {str(e)}",
                )

        enforce_payload_size(request.image_base64)
        # Default CV path: classical shadowlab → CSS tokens (dark-blob opt-in only)
        cv_extractor = CVShadowExtractor()
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
        result = cv_result
        try:
            ai_extractor = AIShadowExtractor()
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
        if _shadowlab_enabled() and cv_b64:
            try:
                shadowlab_meta = await async_executor.run(
                    lambda: _run_shadowlab_pipeline(cv_b64 or "", media_type)
                )
            except Exception as e:  # pragma: no cover - best-effort path
                logger.warning("Shadowlab pipeline failed: %s", e)
                shadowlab_meta = {"error": str(e)}

        shadowlab_artifacts = (
            _shadowlab_artifacts_bundle(shadowlab_meta) if request.include_artifacts else None
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
                "model": "claude-sonnet-4-5-20250929"
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

    except HTTPException:
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


@router.post("/batch-extract", response_model=ShadowBatchResponse)
async def extract_shadows_batch(
    request: ShadowBatchRequest,
    async_executor: AsyncExecutor = Depends(deps.get_async_executor),
) -> ShadowBatchResponse:
    """
    Batch shadow extraction for multiple image URLs (no persistence).
    """
    results: list[ShadowBatchItemResponse] = []
    cv_extractor = CVShadowExtractor()

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
                ai_extractor = AIShadowExtractor()
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
            if _shadowlab_enabled():
                try:
                    shadowlab_meta = await async_executor.run(
                        lambda cv_b64=cv_b64, media_type=media_type: _run_shadowlab_pipeline(
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
        orchestrator = ShadowPipelineOrchestrator(
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


@router.get("/projects/{project_id}", response_model=list[ShadowTokenResponse])
async def list_project_shadows(
    project_id: int,
    project_repo: ProjectRepository = Depends(deps.get_project_repo),
    shadow_repo: ShadowTokenRepository = Depends(deps.get_shadow_repo),
    _rate_limit: None = Depends(rate_limit(requests=30, seconds=60)),
) -> list[ShadowTokenResponse]:
    """
    List all shadow tokens for a project.

    Args:
        project_id: ID of the project
        db: Database session

    Returns:
        List of shadow tokens for the project

    Raises:
        HTTPException: If project not found
    """
    # Verify project exists
    project = await project_repo.get(project_id=project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project {project_id} not found",
        )

    shadows = await shadow_repo.list_by_project(project_id=project_id)

    return [
        ShadowTokenResponse(
            x_offset=shadow.x_offset,
            y_offset=shadow.y_offset,
            blur_radius=shadow.blur_radius,
            spread_radius=shadow.spread_radius,
            color_hex=shadow.color_hex,
            opacity=shadow.opacity,
            name=shadow.name,
            shadow_type=shadow.shadow_type,
            semantic_role=shadow.semantic_role,
            confidence=shadow.confidence,
        )
        for shadow in shadows
    ]


@router.get("/{shadow_id}", response_model=ShadowTokenResponse)
async def get_shadow(
    shadow_id: int,
    shadow_repo: ShadowTokenRepository = Depends(deps.get_shadow_repo),
    _rate_limit: None = Depends(rate_limit(requests=30, seconds=60)),
) -> ShadowTokenResponse:
    """
    Get a specific shadow token by ID.

    Args:
        shadow_id: ID of the shadow token
        db: Database session

    Returns:
        Shadow token details

    Raises:
        HTTPException: If shadow not found
    """
    shadow = await shadow_repo.get(shadow_id=shadow_id)

    if not shadow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Shadow {shadow_id} not found",
        )

    return ShadowTokenResponse(
        x_offset=shadow.x_offset,
        y_offset=shadow.y_offset,
        blur_radius=shadow.blur_radius,
        spread_radius=shadow.spread_radius,
        color_hex=shadow.color_hex,
        opacity=shadow.opacity,
        name=shadow.name,
        shadow_type=shadow.shadow_type,
        semantic_role=shadow.semantic_role,
        confidence=shadow.confidence,
    )


class ShadowUpdateRequest(BaseModel):
    """Request model for updating a shadow token."""

    name: str | None = Field(None, description="Shadow token name")
    semantic_role: str | None = Field(None, description="Semantic role (subtle, medium, strong)")
    shadow_type: str | None = Field(None, description="Shadow type (drop, inner, text)")
    confidence: float | None = Field(None, ge=0, le=1, description="Confidence score")


@router.put("/{shadow_id}", response_model=ShadowTokenResponse)
async def update_shadow(
    shadow_id: int,
    request: ShadowUpdateRequest,
    shadow_repo: ShadowTokenRepository = Depends(deps.get_shadow_repo),
    _rate_limit: None = Depends(rate_limit(requests=10, seconds=60)),
) -> ShadowTokenResponse:
    """
    Update a shadow token.

    Args:
        shadow_id: ID of the shadow token
        request: Update request with new values
        db: Database session

    Returns:
        Updated shadow token

    Raises:
        HTTPException: If shadow not found
    """
    shadow = await shadow_repo.update(
        shadow_id=shadow_id,
        name=request.name,
        semantic_role=request.semantic_role,
        shadow_type=request.shadow_type,
        confidence=request.confidence,
    )
    if not shadow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Shadow {shadow_id} not found"
        )

    logger.info(f"Updated shadow token {shadow_id}")

    return ShadowTokenResponse(
        x_offset=shadow.x_offset,
        y_offset=shadow.y_offset,
        blur_radius=shadow.blur_radius,
        spread_radius=shadow.spread_radius,
        color_hex=shadow.color_hex,
        opacity=shadow.opacity,
        name=shadow.name,
        shadow_type=shadow.shadow_type,
        semantic_role=shadow.semantic_role,
        confidence=shadow.confidence,
    )


@router.delete("/{shadow_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_shadow(
    shadow_id: int,
    shadow_repo: ShadowTokenRepository = Depends(deps.get_shadow_repo),
    _rate_limit: None = Depends(rate_limit(requests=10, seconds=60)),
) -> None:
    """
    Delete a shadow token.

    Args:
        shadow_id: ID of the shadow token
        db: Database session

    Raises:
        HTTPException: If shadow not found
    """
    deleted = await shadow_repo.delete(shadow_id=shadow_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Shadow {shadow_id} not found"
        )

    logger.info(f"Deleted shadow token {shadow_id}")
