"""
Typography Extraction Router
"""

import json
import logging
import os
from typing import Any

import anthropic
import requests
from fastapi import APIRouter, Depends, HTTPException, Query, status
from jsonschema import ValidationError  # type: ignore[import-untyped]
from pydantic import BaseModel, Field

from copy_that.application.ports.color_token_records import ColorTokenRepository
from copy_that.application.ports.projects import ProjectRepository
from copy_that.application.ports.typography_tokens import TypographyTokenRepository
from copy_that.application.typography_extractor import (
    AITypographyExtractor,
    TypographyExtractionResult,
)
from copy_that.core_tokens.adapters.w3c import tokens_to_w3c_flat
from copy_that.design_tokens.validation import validate_w3c_export
from copy_that.domain.typography import TypographyTokenCreate
from copy_that.extractors.typography.cv_extractor import CVTypographyExtractor
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
from copy_that.services import typography_extraction_service as typography_extraction
from copy_that.services.typography_recommendation import (
    infer_style_from_colors,
    recommend_typography_tokens,
)
from copy_that.services.typography_service import (
    build_typography_repo_from_db,
)

logger = logging.getLogger(__name__)


def _use_multi_extractor(request: ExtractTypographyRequest) -> bool:
    env_on = os.getenv("COPY_THAT_MULTI_EXTRACTOR", "0") == "1"
    return env_on or bool(getattr(request, "use_multi_extractor", False))


class TypographyBatchRequest(BaseModel):
    image_urls: list[str] = Field(..., min_length=1, description="Image URLs to process")
    project_id: int | None = Field(None, description="Optional project to persist tokens")
    max_tokens: int = Field(15, ge=1, le=50, description="Max typography tokens per image")


router = APIRouter(prefix="/api/v1", tags=["typography"])


def _clamp_unit_interval(value: float | None) -> float | None:
    """Clamp optional scores that must live in [0, 1] for response models."""
    if value is None:
        return None
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return None
    return max(0.0, min(1.0, numeric))


def _typography_token_responses(tokens: list[Any]) -> list[TypographyTokenResponse]:
    """Convert extracted typography tokens to response models."""
    responses: list[TypographyTokenResponse] = []
    for token in tokens:
        payload = token.model_dump(exclude_none=True)
        if "prominence" in payload:
            payload["prominence"] = _clamp_unit_interval(payload.get("prominence"))
        if "readability_score" in payload:
            payload["readability_score"] = _clamp_unit_interval(payload.get("readability_score"))
        if "confidence" in payload:
            payload["confidence"] = _clamp_unit_interval(payload.get("confidence")) or 0.0
        responses.append(TypographyTokenResponse(**payload))
    return responses


def _result_to_response(
    result: TypographyExtractionResult,
    namespace: str = "token/typography/api",
    failed_extractors: list[dict[str, str]] | None = None,
) -> TypographyExtractionResponse:
    """Build API response from extraction result."""
    return TypographyExtractionResponse(
        typography_tokens=_typography_token_responses(result.tokens),
        typography_palette=result.typography_palette,
        extraction_confidence=result.extraction_confidence,
        extractor_used=result.extractor_used,
        color_associations=result.color_associations,
        failed_extractors=failed_extractors,
    )


def _extraction_input(
    request: ExtractTypographyRequest,
) -> typography_extraction.TypographyExtractionInput:
    return typography_extraction.TypographyExtractionInput(
        project_id=request.project_id,
        image_url=request.image_url,
        image_base64=request.image_base64,
        image_media_type=request.image_media_type,
        max_tokens=request.max_tokens,
        extractor=request.extractor,
    )


def _outcome_to_response(
    outcome: typography_extraction.TypographyExtractionOutcome,
) -> TypographyExtractionResponse:
    return _result_to_response(
        outcome.result, namespace=outcome.namespace, failed_extractors=outcome.failed_extractors
    )


@router.post("/typography/extract/multi", response_model=TypographyExtractionResponse)
async def extract_typography_multi(
    request: ExtractTypographyRequest,
    project_repo: ProjectRepository = Depends(deps.get_project_repo),
    typography_repo: TypographyTokenRepository = Depends(deps.get_typography_repo),
    _rate_limit: None = Depends(rate_limit(requests=10, seconds=60)),
):
    """Extract typography via CV+AI multi-extractor orchestration."""
    project = await project_repo.get(project_id=request.project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Project {request.project_id} not found"
        )
    if not request.image_url and not request.image_base64:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either image_url or image_base64 must be provided",
        )

    try:
        outcome = await typography_extraction.extract_typography_multi(
            _extraction_input(request), typography_repo, http_get=requests.get
        )
        return _outcome_to_response(outcome)
    except HTTPException:
        raise
    except Exception:
        logger.exception("Typography multi-extractor extraction failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Typography multi-extractor extraction failed",
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
    2. Uses Claude to analyze and extract typography
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
    if _use_multi_extractor(request):
        return await extract_typography_multi(
            request=request,
            project_repo=project_repo,
            typography_repo=typography_repo,
            _rate_limit=_rate_limit,
        )

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
        outcome = await typography_extraction.extract_typography(
            _extraction_input(request),
            typography_repo,
            color_repo,
            ai_factory=AITypographyExtractor,
            cv_factory=CVTypographyExtractor,
            http_get=requests.get,
            infer_style=infer_style_from_colors,
            recommend_tokens=recommend_typography_tokens,
        )
        return _outcome_to_response(outcome)
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
    return await typography_extraction.extract_typography_batch(
        request.image_urls,
        request.project_id,
        request.max_tokens,
        typography_repo,
        ai_factory=AITypographyExtractor,
        response_factory=_outcome_to_response,
    )


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
