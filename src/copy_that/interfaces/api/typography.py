"""
Typography Extraction Router
"""

import json
import logging
from typing import Any

import anthropic
import requests
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from copy_that.application.ai_typography_extractor import (
    AITypographyExtractor,
    TypographyExtractionResult,
)
from copy_that.application.cv.typography_cv_extractor import CVTypographyExtractor
from copy_that.domain.models import ExtractionJob, Project, TypographyToken
from copy_that.infrastructure.database import get_db
from copy_that.infrastructure.security.rate_limiter import rate_limit
from copy_that.interfaces.api.schemas import (
    ExtractTypographyRequest,
    TypographyExtractionResponse,
    TypographyTokenCreateRequest,
    TypographyTokenDetailResponse,
    TypographyTokenResponse,
)
from copy_that.interfaces.api.utils import sanitize_json_value
from copy_that.services.typography_service import (
    build_typography_repo_from_db,
    merge_typography,
)
from core.tokens.adapters.w3c import tokens_to_w3c

logger = logging.getLogger(__name__)


def _detect_image_format(base64_data: str) -> str | None:
    """Detect image format from base64 data by reading magic bytes.

    Args:
        base64_data: Base64-encoded image data

    Returns:
        MIME type string (e.g., 'image/jpeg') or None if detection fails
    """
    import base64

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


class TypographyBatchRequest(BaseModel):
    image_urls: list[str] = Field(..., min_length=1, description="Image URLs to process")
    project_id: int | None = Field(None, description="Optional project to persist tokens")
    max_tokens: int = Field(15, ge=1, le=50, description="Max typography tokens per image")


router = APIRouter(prefix="/api/v1", tags=["typography"])


def _typography_token_responses(tokens: list[Any]) -> list[TypographyTokenResponse]:
    """Convert extracted typography tokens to response models."""
    return [TypographyTokenResponse(**token.model_dump(exclude_none=True)) for token in tokens]


def _result_to_response(
    result: TypographyExtractionResult, namespace: str = "token/typography/api"
) -> TypographyExtractionResponse:
    """Build API response from extraction result."""
    return TypographyExtractionResponse(
        typography_tokens=_typography_token_responses(result.tokens),
        typography_palette=result.typography_palette,
        extraction_confidence=result.extraction_confidence,
        extractor_used=result.extractor_used,
        color_associations=result.color_associations,
    )


@router.post("/typography/extract", response_model=TypographyExtractionResponse)
async def extract_typography_from_image(
    request: ExtractTypographyRequest,
    db: AsyncSession = Depends(get_db),
    _rate_limit: None = Depends(rate_limit(requests=10, seconds=60)),
):
    """Extract typography from an image URL or base64 data using AI

    This endpoint:
    1. Accepts either an image URL or base64 encoded image data
    2. Uses Claude Sonnet 4.5 to analyze and extract typography
    3. Stores extracted typography in the database
    4. Returns the extracted typography palette

    Args:
        request: ExtractTypographyRequest with image_url or image_base64 and project_id
        db: Database session

    Returns:
        TypographyExtractionResponse with extracted typography tokens

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

    try:
        # AI extraction
        ai_extractor = AITypographyExtractor()
        if request.image_base64:
            # Use provided media type or detect from magic bytes
            media_type = (
                request.image_media_type
                or _detect_image_format(request.image_base64)
                or "image/jpeg"
            )
            ai_result = ai_extractor.extract_typography_from_base64(
                request.image_base64, media_type=media_type, max_tokens=request.max_tokens
            )
        else:
            ai_result = ai_extractor.extract_typography_from_image_url(
                request.image_url, max_tokens=request.max_tokens
            )

        # CV fallback if AI result has low confidence
        cv_result = None
        if ai_result and ai_result.extraction_confidence < 0.6:
            cv_extractor = CVTypographyExtractor()
            try:
                if request.image_base64:
                    cv_result = cv_extractor.extract_from_base64(request.image_base64)
                else:
                    resp = requests.get(request.image_url, timeout=10)
                    resp.raise_for_status()
                    import base64

                    cv_b64 = base64.b64encode(resp.content).decode("utf-8")
                    cv_result = cv_extractor.extract_from_base64(cv_b64)
            except Exception as e:
                logger.debug("CV fallback skipped: %s", e)
                cv_result = None

        # Merge results
        if cv_result and ai_result:
            merged_tokens = merge_typography(cv_result.tokens, ai_result.tokens)
        else:
            merged_tokens = ai_result.tokens if ai_result else []

        extraction_result = TypographyExtractionResult(
            tokens=merged_tokens,
            typography_palette=ai_result.typography_palette if ai_result else None,
            extraction_confidence=ai_result.extraction_confidence if ai_result else 0.0,
            extractor_used=ai_result.extractor_used if ai_result else "unknown",
            color_associations=ai_result.color_associations if ai_result else None,
        )

        # Create extraction job record
        source_identifier = request.image_url or "base64_upload"
        extraction_job = ExtractionJob(
            project_id=request.project_id,
            source_url=source_identifier,
            extraction_type="typography",
            status="completed",
            result_data=json.dumps(
                {
                    "typography_count": len(extraction_result.tokens),
                    "palette": extraction_result.typography_palette,
                },
                default=str,
            ),
        )
        db.add(extraction_job)
        await db.flush()

        # Store typography tokens in database
        for token in extraction_result.tokens:
            typography_token = TypographyToken(
                project_id=request.project_id,
                extraction_job_id=extraction_job.id,
                font_family=token.font_family,
                font_weight=token.font_weight,
                font_size=token.font_size,
                line_height=token.line_height,
                letter_spacing=token.letter_spacing,
                text_transform=token.text_transform,
                semantic_role=token.semantic_role,
                category=token.category,
                name=token.name,
                confidence=token.confidence,
                prominence=token.prominence,
                is_readable=token.is_readable,
                readability_score=token.readability_score,
                extraction_metadata=json.dumps(token.extraction_metadata)
                if token.extraction_metadata
                else None,
            )
            db.add(typography_token)

        await db.commit()
        logger.info(
            "Extracted %d typography tokens for project %d",
            len(extraction_result.tokens),
            request.project_id,
        )

        return _result_to_response(
            extraction_result,
            namespace=f"token/typography/project/{request.project_id}/job/{extraction_job.id}",
        )

    except ValueError as e:
        logger.error("Invalid input for typography extraction: %s", str(e))
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
        logger.exception("Unexpected error during typography extraction")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Typography extraction failed due to an unexpected error",
        )


@router.get("/projects/{project_id}/typography", response_model=list[TypographyTokenDetailResponse])
async def get_project_typography(project_id: int, db: AsyncSession = Depends(get_db)):
    """Get all typography tokens for a project

    Args:
        project_id: Project ID
        db: Database session

    Returns:
        List of typography tokens for the project

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

    # Get all typography tokens for the project
    result = await db.execute(
        select(TypographyToken)
        .where(TypographyToken.project_id == project_id)
        .order_by(TypographyToken.created_at.desc())
    )
    tokens = result.scalars().all()

    return [
        TypographyTokenDetailResponse(
            id=token.id,
            project_id=token.project_id,
            extraction_job_id=token.extraction_job_id,
            font_family=token.font_family,
            font_weight=token.font_weight,
            font_size=token.font_size,
            line_height=token.line_height,
            letter_spacing=token.letter_spacing,
            text_transform=token.text_transform,
            semantic_role=token.semantic_role,
            category=token.category,
            name=token.name,
            confidence=token.confidence,
            prominence=token.prominence,
            is_readable=token.is_readable,
            readability_score=token.readability_score,
            extraction_metadata=json.loads(token.extraction_metadata)
            if token.extraction_metadata
            else None,
            created_at=token.created_at.isoformat(),
        )
        for token in tokens
    ]


@router.get("/typography/export/w3c")
async def export_typography_w3c(project_id: int | None = None, db: AsyncSession = Depends(get_db)):
    """Export typography tokens (optionally by project) as W3C Design Tokens JSON."""
    query = select(TypographyToken)
    if project_id:
        query = query.where(TypographyToken.project_id == project_id)
    result = await db.execute(query)
    tokens = result.scalars().all()
    namespace = (
        f"token/typography/export/project/{project_id}"
        if project_id is not None
        else "token/typography/export/all"
    )
    repo = build_typography_repo_from_db(tokens, namespace=namespace)
    return sanitize_json_value(tokens_to_w3c(repo))


@router.post("/typography/batch", response_model=list[TypographyExtractionResponse])
async def batch_extract_typography(
    request: TypographyBatchRequest,
    db: AsyncSession = Depends(get_db),
    _rate_limit: None = Depends(rate_limit(requests=5, seconds=60)),
) -> list[TypographyExtractionResponse]:
    """Batch extract typography from multiple image URLs."""
    ai_extractor = AITypographyExtractor()
    responses: list[TypographyExtractionResponse] = []
    for url in request.image_urls:
        try:
            extraction_result = ai_extractor.extract_typography_from_image_url(
                url, max_tokens=request.max_tokens
            )
            job_id: int | None = None
            # Optional persistence
            if request.project_id:
                job = ExtractionJob(
                    project_id=request.project_id,
                    source_url=url,
                    extraction_type="typography",
                    status="completed",
                    result_data=json.dumps({"typography_count": len(extraction_result.tokens)}),
                )
                db.add(job)
                await db.flush()
                for token in extraction_result.tokens:
                    db.add(
                        TypographyToken(
                            project_id=request.project_id,
                            extraction_job_id=job.id,
                            font_family=token.font_family,
                            font_weight=token.font_weight,
                            font_size=token.font_size,
                            line_height=token.line_height,
                            letter_spacing=token.letter_spacing,
                            text_transform=token.text_transform,
                            semantic_role=token.semantic_role,
                            category=token.category,
                            name=token.name,
                            confidence=token.confidence,
                            prominence=token.prominence,
                            is_readable=token.is_readable,
                            readability_score=token.readability_score,
                            extraction_metadata=json.dumps(token.extraction_metadata)
                            if token.extraction_metadata
                            else None,
                        )
                    )
                await db.commit()
                job_id = job.id
            namespace = (
                f"token/typography/project/{request.project_id}/job/{job_id}"
                if job_id is not None and request.project_id
                else f"token/typography/batch/{len(responses) + 1:02d}"
            )
            responses.append(_result_to_response(extraction_result, namespace=namespace))
        except Exception as e:
            logger.error("Batch typography extraction failed for %s: %s", url, str(e))
            continue
    return responses


@router.post("/typography", response_model=TypographyTokenDetailResponse, status_code=201)
async def create_typography_token(
    request: TypographyTokenCreateRequest, db: AsyncSession = Depends(get_db)
):
    """Create a new typography token

    Args:
        request: TypographyTokenCreateRequest with typography details
        db: Database session

    Returns:
        Created typography token

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

    # Create typography token
    typography_token = TypographyToken(
        project_id=request.project_id,
        extraction_job_id=request.extraction_job_id,
        font_family=request.font_family,
        font_weight=request.font_weight,
        font_size=request.font_size,
        line_height=request.line_height,
        letter_spacing=request.letter_spacing,
        text_transform=request.text_transform,
        semantic_role=request.semantic_role,
        category=request.category,
        name=request.name,
        confidence=request.confidence,
        prominence=request.prominence,
        is_readable=request.is_readable,
        readability_score=request.readability_score,
        extraction_metadata=json.dumps(request.extraction_metadata)
        if request.extraction_metadata
        else None,
    )
    db.add(typography_token)
    await db.commit()
    await db.refresh(typography_token)

    return TypographyTokenDetailResponse(
        id=typography_token.id,
        project_id=typography_token.project_id,
        extraction_job_id=typography_token.extraction_job_id,
        font_family=typography_token.font_family,
        font_weight=typography_token.font_weight,
        font_size=typography_token.font_size,
        line_height=typography_token.line_height,
        letter_spacing=typography_token.letter_spacing,
        text_transform=typography_token.text_transform,
        semantic_role=typography_token.semantic_role,
        category=typography_token.category,
        name=typography_token.name,
        confidence=typography_token.confidence,
        prominence=typography_token.prominence,
        is_readable=typography_token.is_readable,
        readability_score=typography_token.readability_score,
        extraction_metadata=json.loads(typography_token.extraction_metadata)
        if typography_token.extraction_metadata
        else None,
        usage=request.usage,
        created_at=typography_token.created_at.isoformat(),
    )


@router.get("/typography/{token_id}", response_model=TypographyTokenDetailResponse)
async def get_typography_token(token_id: int, db: AsyncSession = Depends(get_db)):
    """Get a specific typography token

    Args:
        token_id: Typography token ID
        db: Database session

    Returns:
        Typography token details

    Raises:
        HTTPException: If token not found
    """
    result = await db.execute(select(TypographyToken).where(TypographyToken.id == token_id))
    token = result.scalar_one_or_none()
    if not token:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Typography token {token_id} not found",
        )

    return TypographyTokenDetailResponse(
        id=token.id,
        project_id=token.project_id,
        extraction_job_id=token.extraction_job_id,
        font_family=token.font_family,
        font_weight=token.font_weight,
        font_size=token.font_size,
        line_height=token.line_height,
        letter_spacing=token.letter_spacing,
        text_transform=token.text_transform,
        semantic_role=token.semantic_role,
        category=token.category,
        name=token.name,
        confidence=token.confidence,
        prominence=token.prominence,
        is_readable=token.is_readable,
        readability_score=token.readability_score,
        extraction_metadata=json.loads(token.extraction_metadata)
        if token.extraction_metadata
        else None,
        created_at=token.created_at.isoformat(),
    )


@router.put("/typography/{token_id}", response_model=TypographyTokenDetailResponse)
async def update_typography_token(
    token_id: int,
    request: TypographyTokenCreateRequest,
    db: AsyncSession = Depends(get_db),
):
    """Update an existing typography token

    Args:
        token_id: Typography token ID
        request: Updated typography token data
        db: Database session

    Returns:
        Updated typography token

    Raises:
        HTTPException: If token not found
    """
    result = await db.execute(select(TypographyToken).where(TypographyToken.id == token_id))
    token = result.scalar_one_or_none()
    if not token:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Typography token {token_id} not found",
        )

    # Update fields
    token.font_family = request.font_family
    token.font_weight = request.font_weight
    token.font_size = request.font_size
    token.line_height = request.line_height
    token.letter_spacing = request.letter_spacing
    token.text_transform = request.text_transform
    token.semantic_role = request.semantic_role
    token.category = request.category
    token.name = request.name
    token.confidence = request.confidence
    token.prominence = request.prominence
    token.is_readable = request.is_readable
    token.readability_score = request.readability_score
    token.extraction_metadata = (
        json.dumps(request.extraction_metadata) if request.extraction_metadata else None
    )

    db.add(token)
    await db.commit()
    await db.refresh(token)

    return TypographyTokenDetailResponse(
        id=token.id,
        project_id=token.project_id,
        extraction_job_id=token.extraction_job_id,
        font_family=token.font_family,
        font_weight=token.font_weight,
        font_size=token.font_size,
        line_height=token.line_height,
        letter_spacing=token.letter_spacing,
        text_transform=token.text_transform,
        semantic_role=token.semantic_role,
        category=token.category,
        name=token.name,
        confidence=token.confidence,
        prominence=token.prominence,
        is_readable=token.is_readable,
        readability_score=token.readability_score,
        extraction_metadata=json.loads(token.extraction_metadata)
        if token.extraction_metadata
        else None,
        usage=request.usage,
        created_at=token.created_at.isoformat(),
    )


@router.delete("/typography/{token_id}", status_code=204)
async def delete_typography_token(token_id: int, db: AsyncSession = Depends(get_db)):
    """Delete a typography token

    Args:
        token_id: Typography token ID
        db: Database session

    Raises:
        HTTPException: If token not found
    """
    result = await db.execute(select(TypographyToken).where(TypographyToken.id == token_id))
    token = result.scalar_one_or_none()
    if not token:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Typography token {token_id} not found",
        )

    await db.delete(token)
    await db.commit()
    return None
