from __future__ import annotations

import base64
import logging
import math
import os
import tempfile
from pathlib import Path
from typing import Any, cast

import numpy as np
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, HttpUrl

from copy_that.application.ai_shadow_extractor import AIShadowExtractor
from copy_that.application.cv_shadow_extractor import CVShadowExtractor
from copy_that.application.execution.async_executor import AsyncExecutor
from copy_that.application.ports.projects import ProjectRepository
from copy_that.application.ports.shadow_tokens import ShadowTokenRepository
from copy_that.domain.shadows import ShadowTokenCreate
from copy_that.infrastructure.security.rate_limiter import rate_limit
from copy_that.interfaces.api import dependencies as deps
from copy_that.interfaces.api.utils import enforce_payload_size
from copy_that.shadowlab.orchestrator import ShadowPipelineOrchestrator


def _shadowlab_enabled() -> bool:
    env = os.getenv("ENABLE_SHADOWLAB", "true").lower()
    return env not in {"0", "false", "no", "off"}


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


class ShadowExtractionResponse(BaseModel):
    """Response model for shadow extraction result."""

    tokens: list[ShadowTokenResponse] = Field(..., description="Extracted shadow tokens")
    extraction_confidence: float = Field(
        ..., ge=0, le=1, description="Overall extraction confidence"
    )
    extraction_metadata: dict[str, Any] | None = Field(
        None, description="Extraction metadata and diagnostics"
    )
    warnings: list[str] | None = Field(None, description="Any warnings during extraction")


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
        # Use CV-based shadow extraction (designed for UI mockups)
        cv_extractor = CVShadowExtractor()
        cv_result = await async_executor.run(
            lambda: cv_extractor.extract_shadows(
                base64_image=cv_b64 or "",
                media_type=media_type,
            )
        )

        logger.info(f"CV extraction found {cv_result.shadow_count} shadows")

        # Try AI enhancement if available (but don't fail if API key missing)
        ai_result = None
        extractor_source = "cv_edge_detection"
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
                logger.info(f"AI extraction enhanced with {ai_result.shadow_count} shadows")
                # Use AI results if available, otherwise fall back to CV
                result = ai_result
                extractor_source = "claude_sonnet_4.5_with_cv_fallback"
            else:
                # AI didn't find anything, use CV results
                logger.info("AI found no shadows, using CV results")
                result = cv_result
        except Exception as e:
            # AI API unavailable/failed - use CV results gracefully
            logger.warning(f"AI extraction unavailable ({type(e).__name__}), using CV results: {e}")
            result = cv_result
            extractor_source = "cv_edge_detection_fallback"

        shadowlab_meta: dict[str, Any] | None = None
        if _shadowlab_enabled() and cv_b64:
            try:
                shadowlab_meta = await async_executor.run(
                    lambda: _run_shadowlab_pipeline(cv_b64 or "", media_type)
                )
            except Exception as e:  # pragma: no cover - best-effort path
                logger.warning("Shadowlab pipeline failed: %s", e)
                shadowlab_meta = {"error": str(e)}

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

        return ShadowExtractionResponse(
            tokens=token_responses,
            extraction_confidence=overall_confidence,
            extraction_metadata={
                "extraction_source": extractor_source,
                "model": "claude-sonnet-4-5-20250929"
                if "claude" in extractor_source
                else "cv_edge_detection",
                "token_count": len(token_responses),
                "fallback_used": extractor_source != "claude_sonnet_4.5_with_cv_fallback",
                **({"shadowlab": shadowlab_meta} if shadowlab_meta else {}),
            },
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
        extractor_source = "cv_edge_detection"
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

            try:
                ai_extractor = AIShadowExtractor()
                ai_result = await async_executor.run(
                    lambda ai_extractor=ai_extractor,
                    cv_b64=cv_b64,
                    media_type=media_type: ai_extractor.extract_shadows(
                        base64_image=cv_b64,
                        media_type=media_type,
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
                extractor_source = "cv_edge_detection_fallback"

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
