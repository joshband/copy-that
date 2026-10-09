from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from copy_that.application.ai_shadow_extractor import AIShadowExtractor
from copy_that.application.execution.async_executor import AsyncExecutor
from copy_that.application.ports.projects import ProjectRepository
from copy_that.application.ports.shadow_tokens import ShadowTokenRepository
from copy_that.extractors.shadow.cv_extractor import CVShadowExtractor
from copy_that.infrastructure.security.rate_limiter import rate_limit
from copy_that.interfaces.api import dependencies as deps
from copy_that.interfaces.api.utils import enforce_payload_size
from copy_that.services import shadow_extraction_service as service
from copy_that.services.shadow_extraction_models import (
    ShadowBatchItemResponse as ShadowBatchItemResponse,
)
from copy_that.services.shadow_extraction_models import ShadowBatchRequest as ShadowBatchRequest
from copy_that.services.shadow_extraction_models import ShadowBatchResponse as ShadowBatchResponse
from copy_that.services.shadow_extraction_models import (
    ShadowExtractionRequest as ShadowExtractionRequest,
)
from copy_that.services.shadow_extraction_models import (
    ShadowExtractionResponse as ShadowExtractionResponse,
)
from copy_that.services.shadow_extraction_models import ShadowTokenResponse as ShadowTokenResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/shadows", tags=["shadows"])

# Explicit injection hooks retained for route callers and tests.
_shadowlab_enabled = service._shadowlab_enabled
_run_shadowlab_pipeline = service._run_shadowlab_pipeline
_shadowlab_artifacts_bundle = service._shadowlab_artifacts_bundle


def _payload_guard(image_base64: str | None) -> None:
    try:
        enforce_payload_size(image_base64)
    except HTTPException as exc:
        raise service.ShadowServiceError(
            status_code=exc.status_code, detail=str(exc.detail)
        ) from exc


def _use_multi_extractor(request: ShadowExtractionRequest) -> bool:
    env_on = service.multi_extractor_enabled()
    return env_on or bool(getattr(request, "use_multi_extractor", False))


@router.post("/extract/multi", response_model=ShadowExtractionResponse)
async def extract_shadows_multi(
    request: ShadowExtractionRequest,
    project_repo: ProjectRepository = Depends(deps.get_project_repo),
    shadow_repo: ShadowTokenRepository = Depends(deps.get_shadow_repo),
    _rate_limit: None = Depends(rate_limit(requests=10, seconds=60)),
) -> ShadowExtractionResponse:
    """Extract shadows via CV+AI multi-extractor orchestration."""
    try:
        return await service.extract_shadows_multi(
            request,
            project_repo,
            shadow_repo,
            payload_guard=_payload_guard,
        )
    except service.ShadowServiceError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc


@router.post("/extract", response_model=ShadowExtractionResponse)
async def extract_shadows(
    request: ShadowExtractionRequest,
    project_repo: ProjectRepository = Depends(deps.get_project_repo),
    shadow_repo: ShadowTokenRepository = Depends(deps.get_shadow_repo),
    async_executor: AsyncExecutor = Depends(deps.get_async_executor),
    _rate_limit: None = Depends(rate_limit(requests=10, seconds=60)),
) -> ShadowExtractionResponse:
    """Extract shadow tokens and optionally persist them to a project."""
    if _use_multi_extractor(request):
        return await extract_shadows_multi(request, project_repo, shadow_repo, _rate_limit)
    try:
        return await service.extract_shadows(
            request,
            project_repo,
            shadow_repo,
            async_executor,
            cv_factory=CVShadowExtractor,
            ai_factory=AIShadowExtractor,
            shadowlab_enabled=_shadowlab_enabled,
            pipeline_runner=_run_shadowlab_pipeline,
            payload_guard=_payload_guard,
            artifact_builder=_shadowlab_artifacts_bundle,
        )
    except service.ShadowServiceError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc


@router.post("/batch-extract", response_model=ShadowBatchResponse)
async def extract_shadows_batch(
    request: ShadowBatchRequest,
    async_executor: AsyncExecutor = Depends(deps.get_async_executor),
) -> ShadowBatchResponse:
    """Extract shadows from multiple images without persistence."""
    return await service.extract_shadows_batch(
        request,
        async_executor,
        cv_factory=CVShadowExtractor,
        ai_factory=AIShadowExtractor,
        shadowlab_enabled=_shadowlab_enabled,
        pipeline_runner=_run_shadowlab_pipeline,
    )


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
