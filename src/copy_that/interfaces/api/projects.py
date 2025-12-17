"""
Project Management Router
"""

import json
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status

from copy_that.application.ports.projects import ProjectRepository
from copy_that.application.use_cases import projects as projects_use_cases
from copy_that.interfaces.api import dependencies as deps
from copy_that.interfaces.api.schemas import (
    ProjectCreateRequest,
    ProjectResponse,
    ProjectUpdateRequest,
)

router = APIRouter(prefix="/api/v1/projects", tags=["projects"])


def _encode_description(
    text: str | None,
    image_base64: str | None,
    image_media_type: str | None,
    spacing_tokens: list[dict[str, Any]] | None = None,
) -> str | None:
    """Store text + image metadata as JSON in the description column."""
    if not any([text, image_base64, image_media_type, spacing_tokens]):
        return text
    payload: dict[str, Any] = {}
    if text:
        payload["text"] = text
    if image_base64:
        payload["image_base64"] = image_base64
    if image_media_type:
        payload["image_media_type"] = image_media_type
    if spacing_tokens:
        payload["spacing_tokens"] = spacing_tokens
    return json.dumps(payload)


def _decode_description(
    raw: str | None,
) -> tuple[str | None, str | None, str | None, list[dict[str, Any]] | None]:
    """Decode description JSON if present."""
    if raw is None:
        return None, None, None, None
    if raw == "":
        return "", None, None, None
    try:
        data: dict[str, Any] | str = json.loads(raw)
        if isinstance(data, dict):
            return (
                data.get("text"),
                data.get("image_base64"),
                data.get("image_media_type"),
                data.get("spacing_tokens"),
            )
    except json.JSONDecodeError:
        return raw, None, None, None
    return raw, None, None, None


@router.post("", response_model=ProjectResponse, status_code=201)
async def create_project(
    request: ProjectCreateRequest,
    project_repo: ProjectRepository = Depends(deps.get_project_repo),
):
    """Create a new project

    Args:
        request: ProjectCreateRequest with name and optional description
        db: Database session

    Returns:
        Created project with ID
    """
    description = _encode_description(
        request.description, request.image_base64, request.image_media_type, request.spacing_tokens
    )
    project = await projects_use_cases.create_project(
        project_repo, name=request.name, description=description
    )

    text, img_b64, img_type, spacing_tokens = _decode_description(project.description)
    return ProjectResponse(
        id=project.id,
        name=project.name,
        description=text,
        image_base64=img_b64,
        image_media_type=img_type,
        spacing_tokens=spacing_tokens,
        created_at=project.created_at.isoformat(),
        updated_at=project.updated_at.isoformat(),
    )


@router.get("", response_model=list[ProjectResponse])
async def list_projects(
    project_repo: ProjectRepository = Depends(deps.get_project_repo),
    limit: int = Query(
        default=100, ge=1, le=1000, description="Maximum number of projects to return"
    ),
    offset: int = Query(default=0, ge=0, description="Number of projects to skip"),
):
    """List all projects

    Args:
        db: Database session
        limit: Maximum number of projects to return
        offset: Number of projects to skip

    Returns:
        List of projects
    """
    projects = await projects_use_cases.list_projects(project_repo, limit=limit, offset=offset)

    responses: list[ProjectResponse] = []
    for p in projects:
        text, img_b64, img_type, spacing_tokens = _decode_description(p.description)
        responses.append(
            ProjectResponse(
                id=p.id,
                name=p.name,
                description=text,
                image_base64=img_b64,
                image_media_type=img_type,
                spacing_tokens=spacing_tokens,
                created_at=p.created_at.isoformat(),
                updated_at=p.updated_at.isoformat(),
            )
        )
    return responses


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: int, project_repo: ProjectRepository = Depends(deps.get_project_repo)
):
    """Get a specific project

    Args:
        project_id: Project ID
        db: Database session

    Returns:
        Project details

    Raises:
        HTTPException: If project not found
    """
    project = await projects_use_cases.get_project(project_repo, project_id=project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Project {project_id} not found"
        )

    text, img_b64, img_type, spacing_tokens = _decode_description(project.description)
    return ProjectResponse(
        id=project.id,
        name=project.name,
        description=text,
        image_base64=img_b64,
        image_media_type=img_type,
        spacing_tokens=spacing_tokens,
        created_at=project.created_at.isoformat(),
        updated_at=project.updated_at.isoformat(),
    )


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: int,
    request: ProjectUpdateRequest,
    project_repo: ProjectRepository = Depends(deps.get_project_repo),
):
    """Update a project

    Args:
        project_id: Project ID
        request: ProjectUpdateRequest with fields to update
        db: Database session

    Returns:
        Updated project

    Raises:
        HTTPException: If project not found
    """
    project = await projects_use_cases.get_project(project_repo, project_id=project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Project {project_id} not found"
        )

    # Update fields if provided
    # Merge description/image fields
    current_text, current_img_b64, current_img_type, current_spacing = _decode_description(
        project.description
    )
    new_text = request.description if request.description is not None else current_text
    new_img_b64 = request.image_base64 if request.image_base64 is not None else current_img_b64
    new_img_type = (
        request.image_media_type if request.image_media_type is not None else current_img_type
    )
    new_spacing = request.spacing_tokens if request.spacing_tokens is not None else current_spacing
    merged_description = _encode_description(new_text, new_img_b64, new_img_type, new_spacing)
    project = await projects_use_cases.update_project(
        project_repo,
        project_id=project_id,
        name=request.name,
        description=merged_description,
    )
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Project {project_id} not found"
        )

    text, img_b64, img_type, spacing_tokens = _decode_description(project.description)
    return ProjectResponse(
        id=project.id,
        name=project.name,
        description=text,
        image_base64=img_b64,
        image_media_type=img_type,
        spacing_tokens=spacing_tokens,
        created_at=project.created_at.isoformat(),
        updated_at=project.updated_at.isoformat(),
    )


@router.delete("/{project_id}", status_code=204)
async def delete_project(
    project_id: int,
    project_repo: ProjectRepository = Depends(deps.get_project_repo),
):
    """Delete a project

    Args:
        project_id: Project ID
        db: Database session

    Raises:
        HTTPException: If project not found
    """
    deleted = await projects_use_cases.delete_project(project_repo, project_id=project_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Project {project_id} not found"
        )
