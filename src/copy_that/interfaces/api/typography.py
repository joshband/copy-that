"""
Typography Extraction Router
"""

import base64
import json
import logging
from typing import Any

import anthropic
import requests
from fastapi import APIRouter, Depends, HTTPException, Query, status
from jsonschema import ValidationError  # type: ignore[import-untyped]
from pydantic import BaseModel, Field

from copy_that.application.cv.typography_cv_extractor import CVTypographyExtractor
from copy_that.application.ports.color_token_records import ColorTokenRepository
from copy_that.application.ports.projects import ProjectRepository
from copy_that.application.ports.typography_tokens import TypographyTokenRepository
from copy_that.application.typography_extractor import (
    AITypographyExtractor,
    TypographyExtractionResult,
)
from copy_that.design_tokens.validation import validate_w3c_export
from copy_that.domain.typography import TypographyTokenCreate
from copy_that.infrastructure.security.rate_limiter import rate_limit
from copy_that.interfaces.api import dependencies as deps
from copy_that.interfaces.api.schemas import (
    ExtractTypographyRequest,
    TypographyExtractionResponse,
    TypographyTokenCreateRequest,
    TypographyTokenDetailResponse,
    TypographyTokenResponse,
)
from copy_that.interfaces.api.utils import sanitize_json_value
from copy_that.services.typography_recommendation import (
    infer_style_from_colors,
    recommend_typography_tokens,
)
from copy_that.services.typography_service import (
    build_typography_repo_from_db,
    merge_typography,
)
from core.tokens.adapters.w3c import tokens_to_w3c_flat

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


def _only_fallback_tokens(tokens: list[Any]) -> bool:
    if not tokens:
        return True
    for token in tokens:
        meta = getattr(token, "extraction_metadata", None) or {}
        source = meta.get("extraction_source") or meta.get("source")
        if source != "fallback":
            return False
    return True


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
    project_repo: ProjectRepository = Depends(deps.get_project_repo),
    typography_repo: TypographyTokenRepository = Depends(deps.get_typography_repo),
    color_repo: ColorTokenRepository = Depends(deps.get_color_token_repo),
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
        extractor_choice = (request.extractor or "auto").lower()
        if extractor_choice not in {"auto", "ai", "cv", "recommendation"}:
            raise ValueError("extractor must be one of: auto, ai, cv, recommendation")

        ai_result = None
        cv_result = None
        merged_tokens: list[Any] = []

        if extractor_choice not in {"recommendation", "cv"}:
            ai_extractor = AITypographyExtractor()
            if request.image_base64:
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

        if extractor_choice == "cv" or (
            ai_result and ai_result.extraction_confidence < 0.6 and extractor_choice != "ai"
        ):
            cv_extractor = CVTypographyExtractor()
            try:
                if request.image_base64:
                    payload = request.image_base64.split(",", 1)[-1]
                    cv_bytes = base64.b64decode(payload)
                else:
                    resp = requests.get(request.image_url, timeout=10)
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
        if extractor_choice == "auto" and _only_fallback_tokens(merged_tokens):
            use_recommendation = True

        if use_recommendation:
            colors = await color_repo.list_by_project(project_id=request.project_id)
            style_attributes = infer_style_from_colors(colors)
            recommended_tokens, recommendation_confidence = recommend_typography_tokens(
                style_attributes
            )
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

        job_id = await typography_repo.record_extraction(
            project_id=request.project_id,
            source_url=source_identifier,
            tokens=[
                TypographyTokenCreate(
                    project_id=request.project_id,
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
            result_data=result_payload,
        )
        logger.info(
            "Extracted %d typography tokens for project %d",
            len(extraction_result.tokens),
            request.project_id,
        )

        return _result_to_response(
            extraction_result,
            namespace=f"token/typography/project/{request.project_id}/job/{job_id}",
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
async def get_project_typography(
    project_id: int,
    project_repo: ProjectRepository = Depends(deps.get_project_repo),
    typography_repo: TypographyTokenRepository = Depends(deps.get_typography_repo),
):
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
    project = await project_repo.get(project_id=project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Project {project_id} not found"
        )

    # Get all typography tokens for the project
    tokens = await typography_repo.list_by_project(project_id=project_id)

    return [
        TypographyTokenDetailResponse(
            id=token.id,
            project_id=token.project_id,
            extraction_job_id=token.extraction_job_id,
            font_family=token.font_family,
            font_weight=token.font_weight,
            font_style=token.font_style,
            font_size=token.font_size,
            line_height=token.line_height,
            letter_spacing=token.letter_spacing,
            text_transform=token.text_transform,
            text_align=token.text_align,
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
async def export_typography_w3c(
    project_id: int | None = None,
    validate: bool = Query(default=False, description="Validate output against W3C schemas"),
    typography_repo: TypographyTokenRepository = Depends(deps.get_typography_repo),
):
    """Export typography tokens (optionally by project) as W3C Design Tokens JSON."""
    tokens = await typography_repo.list_all(project_id=project_id)
    namespace = (
        f"token/typography/export/project/{project_id}"
        if project_id is not None
        else "token/typography/export/all"
    )
    repo = build_typography_repo_from_db(tokens, namespace=namespace)
    payload = sanitize_json_value(tokens_to_w3c_flat(repo))
    if validate:
        try:
            validate_w3c_export(payload)
        except ValidationError as exc:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"W3C export failed validation: {exc.message}",
            ) from exc
    return payload


@router.post("/typography/batch", response_model=list[TypographyExtractionResponse])
async def batch_extract_typography(
    request: TypographyBatchRequest,
    typography_repo: TypographyTokenRepository = Depends(deps.get_typography_repo),
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
                job_id = await typography_repo.record_extraction(
                    project_id=request.project_id,
                    source_url=url,
                    tokens=[
                        TypographyTokenCreate(
                            project_id=request.project_id,
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
                    result_data={"typography_count": len(extraction_result.tokens)},
                )
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
    request: TypographyTokenCreateRequest,
    project_repo: ProjectRepository = Depends(deps.get_project_repo),
    typography_repo: TypographyTokenRepository = Depends(deps.get_typography_repo),
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
    project = await project_repo.get(project_id=request.project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Project {request.project_id} not found"
        )

    typography_token = await typography_repo.create(
        token=TypographyTokenCreate(
            project_id=request.project_id,
            extraction_job_id=request.extraction_job_id,
            font_family=request.font_family,
            font_weight=request.font_weight,
            font_style=request.font_style,
            font_size=request.font_size,
            line_height=request.line_height,
            letter_spacing=request.letter_spacing,
            text_transform=request.text_transform,
            text_align=request.text_align,
            name=request.name,
            semantic_role=request.semantic_role,
            category=request.category,
            confidence=request.confidence,
            prominence=request.prominence,
            is_readable=request.is_readable,
            readability_score=request.readability_score,
            extraction_metadata=json.dumps(request.extraction_metadata)
            if request.extraction_metadata
            else None,
        )
    )

    return TypographyTokenDetailResponse(
        id=typography_token.id,
        project_id=typography_token.project_id,
        extraction_job_id=typography_token.extraction_job_id,
        font_family=typography_token.font_family,
        font_weight=typography_token.font_weight,
        font_style=typography_token.font_style,
        font_size=typography_token.font_size,
        line_height=typography_token.line_height,
        letter_spacing=typography_token.letter_spacing,
        text_transform=typography_token.text_transform,
        text_align=typography_token.text_align,
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
async def get_typography_token(
    token_id: int,
    typography_repo: TypographyTokenRepository = Depends(deps.get_typography_repo),
):
    """Get a specific typography token

    Args:
        token_id: Typography token ID
        db: Database session

    Returns:
        Typography token details

    Raises:
        HTTPException: If token not found
    """
    token = await typography_repo.get(token_id=token_id)
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
        font_style=token.font_style,
        font_size=token.font_size,
        line_height=token.line_height,
        letter_spacing=token.letter_spacing,
        text_transform=token.text_transform,
        text_align=token.text_align,
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
    typography_repo: TypographyTokenRepository = Depends(deps.get_typography_repo),
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
    token = await typography_repo.update(
        token_id=token_id,
        token=TypographyTokenCreate(
            project_id=request.project_id,
            extraction_job_id=request.extraction_job_id,
            font_family=request.font_family,
            font_weight=request.font_weight,
            font_style=request.font_style,
            font_size=request.font_size,
            line_height=request.line_height,
            letter_spacing=request.letter_spacing,
            text_transform=request.text_transform,
            text_align=request.text_align,
            name=request.name,
            semantic_role=request.semantic_role,
            category=request.category,
            confidence=request.confidence,
            prominence=request.prominence,
            is_readable=request.is_readable,
            readability_score=request.readability_score,
            extraction_metadata=json.dumps(request.extraction_metadata)
            if request.extraction_metadata
            else None,
        ),
    )
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
        font_style=token.font_style,
        font_size=token.font_size,
        line_height=token.line_height,
        letter_spacing=token.letter_spacing,
        text_transform=token.text_transform,
        text_align=token.text_align,
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
async def delete_typography_token(
    token_id: int,
    typography_repo: TypographyTokenRepository = Depends(deps.get_typography_repo),
):
    """Delete a typography token

    Args:
        token_id: Typography token ID
        db: Database session

    Raises:
        HTTPException: If token not found
    """
    deleted = await typography_repo.delete(token_id=token_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Typography token {token_id} not found",
        )
    return None
