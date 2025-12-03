from __future__ import annotations

import asyncio
import json
import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, HttpUrl
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from copy_that.application.ai_shadow_extractor import AIShadowExtractor
from copy_that.domain.models import ExtractionJob, Project, ShadowToken
from copy_that.infrastructure.database import get_db
from copy_that.infrastructure.security.rate_limiter import rate_limit

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


@router.post("/extract", response_model=ShadowExtractionResponse)
async def extract_shadows(
    request: ShadowExtractionRequest,
    db: AsyncSession = Depends(get_db),
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
        result = await db.execute(select(Project).where(Project.id == request.project_id))
        project = result.scalar_one_or_none()
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
        loop = asyncio.get_event_loop()
        extractor = AIShadowExtractor()

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

        # Extract shadows using AI
        result = await loop.run_in_executor(
            None,
            lambda: extractor.extract_shadows(
                base64_image=cv_b64 or "",
                media_type=media_type,
            ),
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

        # Persist to database if project_id provided
        if request.project_id:
            job = ExtractionJob(
                project_id=request.project_id,
                source_url=str(request.image_url) if request.image_url else "base64_upload",
                extraction_type="shadow",
                status="completed",
                result_data=json.dumps({"token_count": len(token_responses)}),
            )
            db.add(job)
            await db.flush()

            for shadow in result.shadows:
                db.add(
                    ShadowToken(
                        project_id=request.project_id,
                        extraction_job_id=job.id,
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
                )

            await db.commit()
            logger.info(
                "Persisted %d shadow tokens for project %d (job %d)",
                len(token_responses),
                request.project_id,
                job.id,
            )

        return ShadowExtractionResponse(
            tokens=token_responses,
            extraction_confidence=overall_confidence,
            extraction_metadata={
                "extraction_source": "claude_sonnet_4.5",
                "model": "claude-sonnet-4-5-20250929",
                "token_count": len(token_responses),
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Shadow extraction failed: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Shadow extraction failed: {str(e)}",
        )


@router.get("/projects/{project_id}", response_model=list[ShadowTokenResponse])
async def list_project_shadows(
    project_id: int,
    db: AsyncSession = Depends(get_db),
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
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project {project_id} not found",
        )

    # Query shadow tokens
    result = await db.execute(select(ShadowToken).where(ShadowToken.project_id == project_id))
    shadows = result.scalars().all()

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
    db: AsyncSession = Depends(get_db),
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
    result = await db.execute(select(ShadowToken).where(ShadowToken.id == shadow_id))
    shadow = result.scalar_one_or_none()

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
    db: AsyncSession = Depends(get_db),
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
    result = await db.execute(select(ShadowToken).where(ShadowToken.id == shadow_id))
    shadow = result.scalar_one_or_none()

    if not shadow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Shadow {shadow_id} not found",
        )

    # Update fields if provided
    if request.name is not None:
        shadow.name = request.name
    if request.semantic_role is not None:
        shadow.semantic_role = request.semantic_role
    if request.shadow_type is not None:
        shadow.shadow_type = request.shadow_type
    if request.confidence is not None:
        shadow.confidence = request.confidence

    db.add(shadow)
    await db.commit()
    await db.refresh(shadow)

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
    db: AsyncSession = Depends(get_db),
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
    result = await db.execute(select(ShadowToken).where(ShadowToken.id == shadow_id))
    shadow = result.scalar_one_or_none()

    if not shadow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Shadow {shadow_id} not found",
        )

    await db.delete(shadow)
    await db.commit()

    logger.info(f"Deleted shadow token {shadow_id}")
