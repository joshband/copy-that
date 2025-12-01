"""
Color Extraction Router
"""

import json
import logging
from collections.abc import Sequence
from typing import Any

import anthropic
import requests
from coloraide import Color
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from copy_that.application.color_extractor import (
    ColorExtractionResult,
    ExtractedColorToken,
)
from copy_that.application.cv.color_cv_extractor import CVColorExtractor
from copy_that.domain.models import ColorToken, ExtractionJob, Project
from copy_that.infrastructure.database import get_db
from copy_that.infrastructure.security.rate_limiter import rate_limit
from copy_that.interfaces.api.schemas import (
    ColorExtractionResponse,
    ColorTokenCreateRequest,
    ColorTokenDetailResponse,
    ColorTokenResponse,
    ExtractColorRequest,
)
from copy_that.interfaces.api.utils import sanitize_json_value
from copy_that.interfaces.api.validators import validate_base64_image, validate_max_colors
from copy_that.services.colors_service import (
    add_role_tokens,
    db_colors_to_repo,
    default_shadow_tokens,
    find_accent_hex,
    get_extractor,
    parse_metadata,
    post_process_colors,
    serialize_color_token,
)
from core.tokens.adapters.w3c import tokens_to_w3c
from core.tokens.color import make_color_ramp, make_color_token, ramp_to_dict
from core.tokens.model import Token
from core.tokens.repository import InMemoryTokenRepository, TokenRepository

logger = logging.getLogger(__name__)


class ColorBatchRequest(BaseModel):
    image_urls: list[str] = Field(..., min_length=1, description="Image URLs to process")
    project_id: int | None = Field(None, description="Optional project to persist tokens")
    max_colors: int = Field(10, ge=1, le=50, description="Max colors per image")


router = APIRouter(prefix="/api/v1", tags=["colors"])


def _color_token_responses(colors: Sequence[ExtractedColorToken]) -> list[ColorTokenResponse]:
    """Convert extracted color tokens to response models."""
    return [ColorTokenResponse(**color.model_dump()) for color in colors]


def _add_colors_to_repo(
    repo: TokenRepository, colors: Sequence[ExtractedColorToken], namespace: str
) -> None:
    """Add colors to repo (wrapper for service function)."""
    for index, color in enumerate(colors, start=1):
        attributes = color.model_dump(exclude_none=True)
        repo.upsert_token(
            make_color_token(f"{namespace}/{index:02d}", Color(color.hex), attributes)
        )


def _add_color_ramps(
    repo: TokenRepository, colors: Sequence[Any], namespace: str
) -> dict[str, Token]:
    """Add accent ramps to the repo; return the created tokens."""
    accent_hex = find_accent_hex(colors)
    if not accent_hex:
        return {}
    ramp_tokens = make_color_ramp(accent_hex, prefix=f"{namespace}/accent")
    for tok in ramp_tokens.values():
        repo.upsert_token(tok)
    return ramp_tokens


def _result_to_response(
    result: ColorExtractionResult, namespace: str = "token/color/api"
) -> ColorExtractionResponse:
    """Build API response from extraction result."""
    repo = InMemoryTokenRepository()
    _add_colors_to_repo(repo, result.colors, namespace)
    add_role_tokens(repo, namespace, result.background_colors)
    _add_color_ramps(repo, result.colors, namespace)
    return ColorExtractionResponse(
        colors=_color_token_responses(result.colors),
        dominant_colors=result.dominant_colors,
        color_palette=result.color_palette,
        extraction_confidence=result.extraction_confidence,
        extractor_used=result.extractor_used,
        design_tokens=tokens_to_w3c(repo),
    )


@router.post("/colors/extract", response_model=ColorExtractionResponse)
async def extract_colors_from_image(
    request: ExtractColorRequest,
    db: AsyncSession = Depends(get_db),
    _rate_limit: None = Depends(rate_limit(requests=10, seconds=60)),
):
    """Extract colors from an image URL or base64 data using AI

    This endpoint:
    1. Accepts either an image URL or base64 encoded image data
    2. Uses Claude Sonnet 4.5 to analyze and extract colors
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
    result = await db.execute(select(Project).where(Project.id == request.project_id))
    project = result.scalar_one_or_none()
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
        # CV-first fast pass
        cv_result = None
        if request.image_base64:
            cv_result = CVColorExtractor(max_colors=request.max_colors).extract_from_base64(
                request.image_base64
            )
        elif request.image_url:
            try:
                # Download and convert to base64 for CV extractor
                resp = requests.get(request.image_url, timeout=10)
                resp.raise_for_status()
                import base64

                cv_b64 = base64.b64encode(resp.content).decode("utf-8")
                cv_result = CVColorExtractor(max_colors=request.max_colors).extract_from_base64(
                    cv_b64
                )
            except requests.RequestException as e:
                logger.debug("CV pre-pass skipped - failed to fetch image: %s", e)
                cv_result = None

        # AI refinement
        extractor, extractor_name = get_extractor(request.extractor or "auto")
        if request.image_base64:
            ai_result = extractor.extract_colors_from_base64(
                request.image_base64, media_type="image/png", max_colors=request.max_colors
            )
        else:
            ai_result = extractor.extract_colors_from_image_url(
                request.image_url, max_colors=request.max_colors
            )

        # Merge CV + AI
        merged_colors = []
        ai_by_hex = {c.hex.lower(): c for c in ai_result.colors}
        cv_by_hex = {c.hex.lower(): c for c in cv_result.colors} if cv_result else {}
        seen = set()
        for hx, tok in ai_by_hex.items():
            merged_colors.append(tok)
            seen.add(hx)
        for hx, tok in cv_by_hex.items():
            if hx in seen:
                continue
            merged_colors.append(tok)

        processed_colors, backgrounds = post_process_colors(
            merged_colors, ai_result.dominant_colors if ai_result else None
        )

        # Normalize possibly mocked fields into concrete types
        palette_source = ai_result if ai_result else cv_result
        color_palette = _safe_str(getattr(palette_source, "color_palette", ""))
        extractor_used = _safe_str(
            extractor_name or getattr(palette_source, "extractor_used", extractor_name)
        )
        dominant_colors = list(
            getattr(palette_source, "dominant_colors", [])
            or (cv_result.dominant_colors if cv_result else [])
        )
        try:
            extraction_confidence = float(
                getattr(palette_source, "extraction_confidence", 0.0) or 0.0
            )
        except (ValueError, TypeError):
            extraction_confidence = 0.0

        extraction_result = ColorExtractionResult(
            colors=processed_colors,
            dominant_colors=dominant_colors,
            color_palette=color_palette,
            extraction_confidence=extraction_confidence,
            extractor_used=extractor_used,
            background_colors=backgrounds,
        )

        # Create extraction job record
        source_identifier = request.image_url or "base64_upload"
        extraction_job = ExtractionJob(
            project_id=request.project_id,
            source_url=source_identifier,
            extraction_type="color",
            status="completed",
            result_data=json.dumps(
                {
                    "color_count": len(extraction_result.colors),
                    "palette": extraction_result.color_palette,
                },
                default=str,
            ),
        )
        db.add(extraction_job)
        await db.flush()
        response = _result_to_response(
            extraction_result,
            namespace=f"token/color/project/{request.project_id}/job/{extraction_job.id}",
        )

        # Store color tokens in database
        for color in extraction_result.colors:
            color_token = ColorToken(
                project_id=request.project_id,
                extraction_job_id=extraction_job.id,
                hex=color.hex,
                rgb=color.rgb,
                name=color.name,
                design_intent=color.design_intent,
                semantic_names=json.dumps(color.semantic_names) if color.semantic_names else None,
                extraction_metadata=json.dumps(color.extraction_metadata)
                if color.extraction_metadata
                else None,
                confidence=color.confidence,
                harmony=color.harmony,
                usage=json.dumps(color.usage) if color.usage else None,
            )
            db.add(color_token)

        await db.commit()
        logger.info(
            "Extracted %d colors for project %d", len(extraction_result.colors), request.project_id
        )

        return response

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
    db: AsyncSession = Depends(get_db),
    _rate_limit: None = Depends(rate_limit(requests=10, seconds=60)),
):
    """Stream color extraction results as they become available

    Returns Server-Sent Events (SSE) stream with:
    1. Phase 1 (instant): Basic color extraction from image
    2. Phase 2 (async): Claude AI enhancements (semantic names, harmonies)

    This allows progressive/streaming results instead of waiting for Claude.

    Args:
        request: ExtractColorRequest with image data
        db: Database session

    Returns:
        StreamingResponse with newline-delimited JSON events
    """

    async def color_extraction_stream():
        try:
            # Verify project exists
            result = await db.execute(select(Project).where(Project.id == request.project_id))
            project = result.scalar_one_or_none()
            if not project:
                yield f"data: {json.dumps({'error': f'Project {request.project_id} not found'})}\n\n"
                return

            # Validate input parameters
            try:
                validate_max_colors(request.max_colors)
                if request.image_base64:
                    validate_base64_image(request.image_base64)
            except ValueError as e:
                yield f"data: {json.dumps({'error': f'Invalid input: {str(e)}', 'phase': -1, 'status': 'validation_failed'})}\n\n"
                return

            # Phase 1: Fast local color extraction (instant)
            logger.info(
                "[Phase 1] Starting fast color extraction for project %d", request.project_id
            )
            extractor, extractor_name = get_extractor(request.extractor or "auto")

            if request.image_base64:
                raw_result = extractor.extract_colors_from_base64(
                    request.image_base64, media_type="image/png", max_colors=request.max_colors
                )
            else:
                raw_result = extractor.extract_colors_from_image_url(
                    request.image_url, max_colors=request.max_colors
                )

            processed_colors, backgrounds = post_process_colors(
                raw_result.colors, getattr(raw_result, "dominant_colors", None)
            )
            color_palette = _safe_str(getattr(raw_result, "color_palette", ""))
            dominant_colors = list(getattr(raw_result, "dominant_colors", []) or [])
            try:
                extraction_confidence = float(
                    getattr(raw_result, "extraction_confidence", 0.0) or 0.0
                )
            except (ValueError, TypeError):
                extraction_confidence = 0.0
            # Send Phase 1 results immediately
            phase1_data = json.dumps(
                {
                    "phase": 1,
                    "status": "colors_extracted",
                    "color_count": len(processed_colors),
                    "message": f"Extracted {len(processed_colors)} colors using fast algorithms",
                }
            )
            yield f"data: {phase1_data}\n\n"

            # Create extraction job record
            source_identifier = request.image_url or "base64_upload"
            extraction_job = ExtractionJob(
                project_id=request.project_id,
                source_url=source_identifier,
                extraction_type="color",
                status="completed",
                result_data=json.dumps(
                    {
                        "color_count": len(processed_colors),
                        "palette": color_palette,
                    },
                    default=str,
                ),
            )
            db.add(extraction_job)
            await db.flush()

            # Store color tokens - keep track for later use
            stored_colors: list[ColorToken] = []
            for i, color in enumerate(processed_colors):
                color_token = ColorToken(
                    project_id=request.project_id,
                    extraction_job_id=extraction_job.id,
                    hex=color.hex,
                    rgb=color.rgb,
                    hsl=color.hsl,
                    hsv=color.hsv,
                    name=color.name,
                    design_intent=color.design_intent,
                    semantic_names=json.dumps(color.semantic_names)
                    if color.semantic_names
                    else None,
                    harmony=color.harmony,
                    temperature=color.temperature,
                    saturation_level=color.saturation_level,
                    lightness_level=color.lightness_level,
                    confidence=color.confidence,
                    usage=json.dumps(color.usage) if color.usage else None,
                    count=color.count,
                    wcag_contrast_on_white=color.wcag_contrast_on_white,
                    wcag_contrast_on_black=color.wcag_contrast_on_black,
                    wcag_aa_compliant_text=color.wcag_aa_compliant_text,
                    wcag_aaa_compliant_text=color.wcag_aaa_compliant_text,
                    wcag_aa_compliant_normal=color.wcag_aa_compliant_normal,
                    wcag_aaa_compliant_normal=color.wcag_aaa_compliant_normal,
                    colorblind_safe=color.colorblind_safe,
                    tint_color=color.tint_color,
                    shade_color=color.shade_color,
                    tone_color=color.tone_color,
                    closest_web_safe=color.closest_web_safe,
                    closest_css_named=color.closest_css_named,
                    delta_e_to_dominant=color.delta_e_to_dominant,
                    is_neutral=color.is_neutral,
                    extraction_metadata=json.dumps(color.extraction_metadata)
                    if color.extraction_metadata
                    else None,
                )
                db.add(color_token)
                stored_colors.append(color_token)

                # Stream each color as it's processed
                if (i + 1) % 5 == 0 or i == len(processed_colors) - 1:
                    streaming_data = json.dumps(
                        {
                            "phase": 1,
                            "status": "colors_streaming",
                            "progress": (i + 1) / len(processed_colors),
                            "message": f"Processed {i + 1}/{len(processed_colors)} colors",
                        }
                    )
                    yield f"data: {streaming_data}\n\n"

            await db.commit()
            # After commit, stored_colors objects have their IDs populated

            # Phase 2: Return complete extraction with all color data from database
            shadow_tokens = default_shadow_tokens(stored_colors)
            ramp_repo = InMemoryTokenRepository()
            ramp_tokens = _add_color_ramps(ramp_repo, processed_colors, "token/color/stream")
            accent_tokens = []
            text_roles = []
            for stored_color in stored_colors:
                meta = parse_metadata(getattr(stored_color, "extraction_metadata", None))
                if meta.get("accent") or meta.get("state_role"):
                    accent_tokens.append(
                        {
                            "hex": stored_color.hex,
                            "role": meta.get("state_role")
                            or ("accent" if meta.get("accent") else None),
                        }
                    )
                if meta.get("text_role"):
                    text_roles.append(
                        {
                            "hex": stored_color.hex,
                            "role": meta.get("text_role"),
                            "contrast": meta.get("contrast_to_background"),
                        }
                    )
            color_payloads: list[dict[str, Any]] = []
            for idx, color_model in enumerate(processed_colors):
                payload = color_model.model_dump(exclude_none=True)
                stored_color_model: ColorToken | None = (
                    stored_colors[idx] if idx < len(stored_colors) else None
                )
                if stored_color_model is not None:
                    payload["id"] = stored_color_model.id
                    payload["project_id"] = stored_color_model.project_id
                    payload["extraction_job_id"] = stored_color_model.extraction_job_id
                color_payloads.append(sanitize_json_value(payload))

            debug_value = getattr(raw_result, "debug", None)
            if debug_value is not None and not isinstance(debug_value, (dict, list, str)):
                debug_value = None

            complete_payload = sanitize_json_value(
                {
                    "phase": 2,
                    "status": "extraction_complete",
                    "summary": color_palette,
                    "dominant_colors": dominant_colors,
                    "extraction_confidence": extraction_confidence,
                    "extractor_used": extractor_name,
                    "colors": color_payloads,
                    "shadows": shadow_tokens,
                    "background_colors": backgrounds,
                    "text_roles": text_roles,
                    "accent_tokens": accent_tokens,
                    "ramps": ramp_to_dict(ramp_tokens) if ramp_tokens else {},
                    "debug": debug_value,
                }
            )
            yield f"data: {json.dumps(complete_payload, default=str)}\n\n"

            logger.info(
                "Extracted %d colors for project %d", len(processed_colors), request.project_id
            )

        except Exception as e:
            logger.exception("Color extraction streaming failed")
            yield f"data: {json.dumps({'error': f'Color extraction failed: {str(e)}'})}\n\n"
        finally:
            # Ensure database session is properly cleaned up
            # This handles cases where client disconnects mid-stream
            if db.is_active:
                await db.close()

    return StreamingResponse(
        color_extraction_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache"},
    )


@router.get("/projects/{project_id}/colors", response_model=list[ColorTokenDetailResponse])
async def get_project_colors(project_id: int, db: AsyncSession = Depends(get_db)):
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
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Project {project_id} not found"
        )

    # Get all colors for the project
    result = await db.execute(
        select(ColorToken)
        .where(ColorToken.project_id == project_id)
        .order_by(ColorToken.created_at.desc())
    )
    colors = result.scalars().all()

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
async def export_colors_w3c(project_id: int | None = None, db: AsyncSession = Depends(get_db)):
    """Export color tokens (optionally by project) as W3C Design Tokens JSON."""
    query = select(ColorToken)
    if project_id:
        query = query.where(ColorToken.project_id == project_id)
    result = await db.execute(query)
    colors = result.scalars().all()
    namespace = (
        f"token/color/export/project/{project_id}"
        if project_id is not None
        else "token/color/export/all"
    )
    repo = db_colors_to_repo(colors, namespace=namespace)
    _add_color_ramps(repo, colors, namespace)
    return sanitize_json_value(tokens_to_w3c(repo))


@router.post("/colors/batch", response_model=list[ColorExtractionResponse])
async def batch_extract_colors(
    request: ColorBatchRequest,
    db: AsyncSession = Depends(get_db),
    _rate_limit: None = Depends(rate_limit(requests=5, seconds=60)),
) -> list[ColorExtractionResponse]:
    """Batch extract colors from multiple image URLs."""
    extractor, extractor_name = get_extractor("auto")
    responses: list[ColorExtractionResponse] = []
    for url in request.image_urls:
        try:
            extraction_result = extractor.extract_colors_from_image_url(url, request.max_colors)
            extraction_result.extractor_used = extractor_name
            job_id: int | None = None
            # Optional persistence
            if request.project_id:
                job = ExtractionJob(
                    project_id=request.project_id,
                    source_url=url,
                    extraction_type="color",
                    status="completed",
                    result_data=json.dumps({"color_count": len(extraction_result.colors)}),
                )
                db.add(job)
                await db.flush()
                for color in extraction_result.colors:
                    db.add(
                        ColorToken(
                            project_id=request.project_id,
                            extraction_job_id=job.id,
                            hex=color.hex,
                            rgb=color.rgb,
                            name=color.name,
                            design_intent=color.design_intent,
                            semantic_names=json.dumps(color.semantic_names)
                            if color.semantic_names
                            else None,
                            extraction_metadata=json.dumps(color.extraction_metadata)
                            if color.extraction_metadata
                            else None,
                            confidence=color.confidence,
                            harmony=color.harmony,
                            usage=json.dumps(color.usage) if color.usage else None,
                        )
                    )
                await db.commit()
                job_id = job.id
            namespace = (
                f"token/color/project/{request.project_id}/job/{job_id}"
                if job_id is not None and request.project_id
                else f"token/color/batch/{len(responses) + 1:02d}"
            )
            responses.append(_result_to_response(extraction_result, namespace=namespace))
        except Exception as e:
            logger.error("Batch color extraction failed for %s: %s", url, str(e))
            continue
    return responses


@router.post("/colors", response_model=ColorTokenDetailResponse, status_code=201)
async def create_color_token(request: ColorTokenCreateRequest, db: AsyncSession = Depends(get_db)):
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
    result = await db.execute(select(Project).where(Project.id == request.project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Project {request.project_id} not found"
        )

    # Create color token
    color_token = ColorToken(
        project_id=request.project_id,
        extraction_job_id=request.extraction_job_id,
        hex=request.hex,
        rgb=request.rgb,
        hsl=request.hsl,
        hsv=request.hsv,
        name=request.name,
        design_intent=request.design_intent,
        semantic_names=json.dumps(request.semantic_names) if request.semantic_names else None,
        extraction_metadata=json.dumps(request.extraction_metadata)
        if request.extraction_metadata
        else None,
        confidence=request.confidence,
        harmony=request.harmony,
        temperature=request.temperature,
        saturation_level=request.saturation_level,
        lightness_level=request.lightness_level,
        usage=request.usage,
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
        provenance=json.dumps(request.provenance) if request.provenance else None,
    )
    db.add(color_token)
    await db.commit()
    await db.refresh(color_token)

    return ColorTokenDetailResponse(
        **serialize_color_token(color_token),
        project_id=color_token.project_id,
        extraction_job_id=color_token.extraction_job_id,
        created_at=color_token.created_at.isoformat(),
    )


@router.get("/colors/{color_id}", response_model=ColorTokenDetailResponse)
async def get_color_token(color_id: int, db: AsyncSession = Depends(get_db)):
    """Get a specific color token

    Args:
        color_id: Color token ID
        db: Database session

    Returns:
        Color token details

    Raises:
        HTTPException: If color not found
    """
    result = await db.execute(select(ColorToken).where(ColorToken.id == color_id))
    color = result.scalar_one_or_none()
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


def _safe_str(value: Any) -> str:
    """Coerce arbitrary objects (including MagicMock) to string safely."""
    try:
        return "" if value is None else str(value)
    except Exception:
        return ""
