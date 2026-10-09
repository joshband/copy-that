"""
Color Extraction Router
"""

import base64
import json
import logging
from typing import Any

import anthropic
import requests
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from jsonschema import ValidationError  # type: ignore[import-untyped]
from pydantic import BaseModel, Field

from copy_that.application.cost_tracker import cost_tracker
from copy_that.application.ports.color_token_records import ColorTokenRepository
from copy_that.application.ports.projects import ProjectRepository
from copy_that.core_tokens.adapters.w3c import tokens_to_w3c_flat
from copy_that.design_tokens.validation import validate_w3c_export
from copy_that.domain.color_tokens import ColorTokenCreate
from copy_that.extractors.color.adapters import (
    CVColorExtractorAdapter,
    KMeansColorExtractorAdapter,
)
from copy_that.extractors.color.cv_extractor import CVColorExtractor
from copy_that.extractors.color.extractor import (
    ColorExtractionResult,
)
from copy_that.extractors.color.orchestrator import MultiExtractorOrchestrator
from copy_that.infrastructure.cache.extraction_cache import (
    get_extraction_cache,
)
from copy_that.infrastructure.security.rate_limiter import rate_limit
from copy_that.interfaces.api import dependencies as deps
from copy_that.interfaces.api.schemas import (
    ArtifactBundle,
    ColorExtractionResponse,
    ColorTokenCreateRequest,
    ColorTokenDetailResponse,
    ExtractColorRequest,
)
from copy_that.interfaces.api.utils import sanitize_json_value
from copy_that.interfaces.api.validators import validate_base64_image, validate_max_colors
from copy_that.services.color_pipeline import (
    ColorPipelineDependencies,
    _add_color_ramps,
    _json_or_none,
    batch_color_payloads,
    color_result_payload,
    extract_color_payload,
    multi_color_payload,
    stream_color_events,
)
from copy_that.services.color_pipeline import (
    _add_colors_to_repo as _add_colors_to_repo,
)
from copy_that.services.colors_service import (
    db_colors_to_repo,
    get_extractor,
    serialize_color_token,
)
from copy_that.tokens.color.aggregator import ColorAggregator

logger = logging.getLogger(__name__)


class ColorBatchRequest(BaseModel):
    image_urls: list[str] = Field(..., min_length=1, description="Image URLs to process")
    project_id: int | None = Field(None, description="Optional project to persist tokens")
    max_colors: int = Field(10, ge=1, le=50, description="Max colors per image")
    include_science_artifacts: bool = Field(
        False,
        description="Include palette-level color science artifacts (non-debug)",
    )


router = APIRouter(prefix="/api/v1", tags=["colors"])


def _result_to_response(
    result: ColorExtractionResult,
    namespace: str = "token/color/api",
    *,
    science_artifacts: ArtifactBundle | None = None,
) -> ColorExtractionResponse:
    return ColorExtractionResponse.model_validate(
        color_result_payload(result, namespace, science_artifacts=science_artifacts)
    )


def _pipeline_dependencies() -> ColorPipelineDependencies:
    return ColorPipelineDependencies(
        get_extractor=get_extractor,
        cv_extractor=CVColorExtractor,
        get_cache=get_extraction_cache,
        cost_tracker=cost_tracker,
        kmeans_adapter=KMeansColorExtractorAdapter,
        cv_adapter=CVColorExtractorAdapter,
        aggregator=ColorAggregator,
        orchestrator=MultiExtractorOrchestrator,
    )


@router.post("/colors/extract", response_model=ColorExtractionResponse)
async def extract_colors_from_image(
    request: ExtractColorRequest,
    project_repo: ProjectRepository = Depends(deps.get_project_repo),
    color_repo: ColorTokenRepository = Depends(deps.get_color_token_repo),
    session=Depends(deps.get_db_session),
    _rate_limit: None = Depends(rate_limit(requests=10, seconds=60)),
):
    """Extract colors from an image URL or base64 data using AI

    This endpoint:
    1. Accepts either an image URL or base64 encoded image data
    2. Uses Claude to analyze and extract colors
    3. Stores extracted colors in the database
    4. Returns the extracted color palette

    Args:
        request: ExtractColorRequest with image_url or image_base64 and project_id
        db: Database session

    Returns:
        ColorExtractionResponse with extracted colors

    Raises:
        HTTPException: If project not found or extraction fails
    """
    # Verify project exists
    project = await project_repo.get(project_id=request.project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Project {request.project_id} not found"
        )

    # Verify at least one image source is provided
    if not request.image_url and not request.image_base64:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either image_url or image_base64 must be provided",
        )

    # Validate input parameters
    try:
        validate_max_colors(request.max_colors)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    # Validate base64 image if provided
    if request.image_base64:
        try:
            validate_base64_image(request.image_base64)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid image: {str(e)}",
            )

    try:
        return ColorExtractionResponse.model_validate(
            await extract_color_payload(request, color_repo, _pipeline_dependencies())
        )

    except ValueError as e:
        logger.error("Invalid input for color extraction: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid input: {str(e)}",
        )
    except requests.RequestException as e:
        logger.error("Failed to fetch image: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Failed to fetch image from URL: {str(e)}",
        )
    except anthropic.APIError as e:
        logger.error("Claude API error: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"AI service error: {str(e)}",
        )
    except Exception:
        logger.exception("Unexpected error during color extraction")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Color extraction failed due to an unexpected error",
        )


@router.post("/colors/extract-streaming")
async def extract_colors_streaming(
    request: ExtractColorRequest,
    project_repo: ProjectRepository = Depends(deps.get_project_repo),
    color_repo: ColorTokenRepository = Depends(deps.get_color_token_repo),
    session=Depends(deps.get_db_session),
    _rate_limit: None = Depends(rate_limit(requests=10, seconds=60)),
):
    """Stream color extraction results as they become available

    Returns Server-Sent Events (SSE) stream with:
    1. Phase 1 (instant): Basic color extraction from image
    2. Phase 2 (async): Claude AI enhancements (semantic names, harmonies)

    This allows progressive/streaming results instead of waiting for Claude.

    Args:
        request: ExtractColorRequest with image data

    Returns:
        StreamingResponse with newline-delimited JSON events
    """

    cost_headers: dict[str, str] = {"Cache-Control": "no-cache"}

    async def color_extraction_stream():
        empty_artifacts: dict[str, Any] = ArtifactBundle().model_dump(by_alias=True)
        try:
            # Verify project exists
            project = await project_repo.get(project_id=request.project_id)
            if not project:
                error_payload: dict[str, Any] = {
                    "error": f"Project {request.project_id} not found",
                    "artifacts": empty_artifacts,
                }
                yield f"data: {json.dumps(error_payload)}\n\n"
                return

            # Validate input parameters
            try:
                validate_max_colors(request.max_colors)
                if request.image_base64:
                    validate_base64_image(request.image_base64)
            except ValueError as e:
                error_payload = {
                    "error": f"Invalid input: {str(e)}",
                    "phase": -1,
                    "status": "validation_failed",
                    "artifacts": empty_artifacts,
                }
                yield f"data: {json.dumps(error_payload)}\n\n"
                return

            async for payload in stream_color_events(
                request, color_repo, session, cost_headers, _pipeline_dependencies()
            ):
                yield f"data: {json.dumps(payload, default=str)}\n\n"

        except Exception as e:
            logger.exception("Color extraction streaming failed")
            error_payload = {
                "error": f"Color extraction failed: {str(e)}",
                "artifacts": empty_artifacts,
            }
            yield f"data: {json.dumps(error_payload)}\n\n"

    return StreamingResponse(
        color_extraction_stream(),
        media_type="text/event-stream",
        headers=cost_headers,
    )


@router.get("/projects/{project_id}/colors", response_model=list[ColorTokenDetailResponse])
async def get_project_colors(
    project_id: int,
    project_repo: ProjectRepository = Depends(deps.get_project_repo),
    color_repo: ColorTokenRepository = Depends(deps.get_color_token_repo),
):
    """Get all color tokens for a project

    Args:
        project_id: Project ID
        db: Database session

    Returns:
        List of color tokens for the project

    Raises:
        HTTPException: If project not found
    """
    # Verify project exists
    project = await project_repo.get(project_id=project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Project {project_id} not found"
        )

    colors = await color_repo.list_by_project(project_id=project_id)

    return [
        ColorTokenDetailResponse(
            id=color.id,
            project_id=color.project_id,
            extraction_job_id=color.extraction_job_id,
            hex=color.hex,
            rgb=color.rgb,
            name=color.name,
            design_intent=color.design_intent,
            semantic_names=json.loads(color.semantic_names) if color.semantic_names else None,
            extraction_metadata=json.loads(color.extraction_metadata)
            if color.extraction_metadata
            else None,
            confidence=color.confidence,
            harmony=color.harmony,
            usage=json.loads(color.usage) if color.usage else None,
            created_at=color.created_at.isoformat(),
        )
        for color in colors
    ]


@router.get("/colors/export/w3c")
async def export_colors_w3c(
    project_id: int | None = None,
    validate: bool = Query(default=False, description="Validate output against W3C schemas"),
    color_repo: ColorTokenRepository = Depends(deps.get_color_token_repo),
):
    """Export color tokens (optionally by project) as W3C Design Tokens JSON."""
    colors = await color_repo.list_all(project_id=project_id)
    namespace = (
        f"token/color/export/project/{project_id}"
        if project_id is not None
        else "token/color/export/all"
    )
    repo = db_colors_to_repo(colors, namespace=namespace)
    _add_color_ramps(repo, colors, namespace)
    payload = sanitize_json_value(tokens_to_w3c_flat(repo))
    if validate:
        try:
            validate_w3c_export(payload, validate_color=True)
        except ValidationError as exc:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"W3C export failed validation: {exc.message}",
            ) from exc
    return payload


@router.post("/colors/batch", response_model=list[ColorExtractionResponse])
async def batch_extract_colors(
    request: ColorBatchRequest,
    color_repo: ColorTokenRepository = Depends(deps.get_color_token_repo),
    _rate_limit: None = Depends(rate_limit(requests=5, seconds=60)),
) -> list[ColorExtractionResponse]:
    """Batch extract colors from multiple image URLs."""
    payloads = await batch_color_payloads(request, color_repo, _pipeline_dependencies())
    return [ColorExtractionResponse.model_validate(payload) for payload in payloads]


@router.post("/colors", response_model=ColorTokenDetailResponse, status_code=201)
async def create_color_token(
    request: ColorTokenCreateRequest,
    project_repo: ProjectRepository = Depends(deps.get_project_repo),
    color_repo: ColorTokenRepository = Depends(deps.get_color_token_repo),
):
    """Create a new color token

    Args:
        request: ColorTokenCreateRequest with color details
        db: Database session

    Returns:
        Created color token

    Raises:
        HTTPException: If project not found
    """
    # Verify project exists
    project = await project_repo.get(project_id=request.project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Project {request.project_id} not found"
        )

    # Create color token
    token = ColorTokenCreate(
        hex=request.hex,
        rgb=request.rgb,
        hsl=request.hsl,
        hsv=request.hsv,
        name=request.name,
        design_intent=request.design_intent,
        semantic_names=_json_or_none(request.semantic_names),
        extraction_metadata=_json_or_none(request.extraction_metadata),
        category=None,
        confidence=request.confidence,
        harmony=request.harmony,
        temperature=request.temperature,
        saturation_level=request.saturation_level,
        lightness_level=request.lightness_level,
        usage=request.usage,
        count=1,
        prominence_percentage=None,
        wcag_contrast_on_white=request.wcag_contrast_on_white,
        wcag_contrast_on_black=request.wcag_contrast_on_black,
        wcag_aa_compliant_text=request.wcag_aa_compliant_text,
        wcag_aaa_compliant_text=request.wcag_aaa_compliant_text,
        wcag_aa_compliant_normal=request.wcag_aa_compliant_normal,
        wcag_aaa_compliant_normal=request.wcag_aaa_compliant_normal,
        colorblind_safe=request.colorblind_safe,
        tint_color=request.tint_color,
        shade_color=request.shade_color,
        tone_color=request.tone_color,
        closest_web_safe=request.closest_web_safe,
        closest_css_named=request.closest_css_named,
        delta_e_to_dominant=request.delta_e_to_dominant,
        is_neutral=request.is_neutral,
        background_role=None,
        foreground_role=None,
        contrast_category=None,
        provenance=_json_or_none(request.provenance),
    )
    color_token = await color_repo.create(
        project_id=request.project_id, extraction_job_id=request.extraction_job_id, token=token
    )

    return ColorTokenDetailResponse(
        **serialize_color_token(color_token),
        project_id=color_token.project_id,
        extraction_job_id=color_token.extraction_job_id,
        created_at=color_token.created_at.isoformat(),
    )


@router.get("/colors/{color_id}", response_model=ColorTokenDetailResponse)
async def get_color_token(
    color_id: int,
    color_repo: ColorTokenRepository = Depends(deps.get_color_token_repo),
):
    """Get a specific color token

    Args:
        color_id: Color token ID
        db: Database session

    Returns:
        Color token details

    Raises:
        HTTPException: If color not found
    """
    color = await color_repo.get(color_id=color_id)
    if not color:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Color token {color_id} not found"
        )

    return ColorTokenDetailResponse(
        id=color.id,
        project_id=color.project_id,
        extraction_job_id=color.extraction_job_id,
        hex=color.hex,
        rgb=color.rgb,
        name=color.name,
        design_intent=color.design_intent,
        semantic_names=json.loads(color.semantic_names) if color.semantic_names else None,
        extraction_metadata=json.loads(color.extraction_metadata)
        if color.extraction_metadata
        else None,
        confidence=color.confidence,
        harmony=color.harmony,
        usage=json.loads(color.usage) if color.usage else None,
        created_at=color.created_at.isoformat(),
    )


@router.post("/colors/extract/multi")
async def extract_colors_multi(
    request: ExtractColorRequest,
    project_repo: ProjectRepository = Depends(deps.get_project_repo),
    _rate_limit: None = Depends(rate_limit(requests=10, seconds=60)),
):
    """Extract colors from an image using multiple extractors in parallel

    This endpoint:
    1. Runs multiple color extractors in parallel (Claude, K-means, CV)
    2. Deduplicates colors using Delta-E (threshold: 2.3)
    3. Tracks provenance (which extractors found each color)
    4. Returns aggregated, high-confidence color palette

    Args:
        request: ExtractColorRequest with image_url or image_base64 and project_id

    Returns:
        ColorExtractionResponse with deduplicated colors from all extractors

    Raises:
        HTTPException: If project not found or extraction fails
    """

    # Verify project exists
    project = await project_repo.get(project_id=request.project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Project {request.project_id} not found"
        )

    # Verify at least one image source is provided
    if not request.image_url and not request.image_base64:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either image_url or image_base64 must be provided",
        )

    try:
        # Convert image to base64 if URL is provided
        if request.image_url:
            try:
                resp = requests.get(request.image_url, timeout=10)
                resp.raise_for_status()
                image_base64 = base64.b64encode(resp.content).decode("utf-8")
            except requests.RequestException as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Failed to fetch image from URL: {str(e)}",
                )
        else:
            image_base64 = request.image_base64

        # Validate base64 image
        try:
            validate_base64_image(image_base64)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid image: {str(e)}",
            )

        return ColorExtractionResponse.model_validate(
            await multi_color_payload(request, image_base64, _pipeline_dependencies())
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Multi-extractor extraction failed: {e}", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Color extraction failed: {str(e)}",
        )
