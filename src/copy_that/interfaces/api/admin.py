"""Admin endpoints for cost visibility."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from copy_that.infrastructure.persistence import models
from copy_that.interfaces.api import dependencies as deps
from copy_that.interfaces.api.auth import get_current_user

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/costs/projects")
async def list_project_costs(
    limit: int = 100,
    session: AsyncSession = Depends(deps.get_db_session),
    current_user=Depends(get_current_user),
):
    if not getattr(current_user, "is_superuser", False):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin only")
    result = await session.execute(
        select(models.ProjectCost)
        .order_by(models.ProjectCost.window.desc(), models.ProjectCost.project_id)
        .limit(limit)
    )
    rows = result.scalars().all()
    return [
        {
            "project_id": row.project_id,
            "window": row.window,
            "total_usd": row.total_usd,
            "soft_limit_usd": row.soft_limit_usd,
            "hard_limit_usd": row.hard_limit_usd,
            "updated_at": row.updated_at,
        }
        for row in rows
    ]


@router.get("/costs/projects/{project_id}")
async def get_project_cost(
    project_id: int,
    session: AsyncSession = Depends(deps.get_db_session),
    current_user=Depends(get_current_user),
):
    if not getattr(current_user, "is_superuser", False):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin only")
    result = await session.execute(
        select(models.ProjectCost)
        .where(models.ProjectCost.project_id == project_id)
        .order_by(models.ProjectCost.window.desc())
    )
    rows = result.scalars().all()
    if not rows:
        raise HTTPException(status_code=404, detail="Project cost not found")
    return [
        {
            "project_id": row.project_id,
            "window": row.window,
            "total_usd": row.total_usd,
            "soft_limit_usd": row.soft_limit_usd,
            "hard_limit_usd": row.hard_limit_usd,
            "updated_at": row.updated_at,
        }
        for row in rows
    ]
