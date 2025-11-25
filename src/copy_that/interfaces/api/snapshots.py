"""
Project snapshots: list and fetch stored token snapshots.
"""

import json

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from copy_that.domain.models import Project, ProjectSnapshot
from copy_that.infrastructure.database import get_db

router = APIRouter(prefix="/api/v1/projects", tags=["snapshots"])


@router.get("/{project_id}/snapshots")
async def list_snapshots(project_id: int, db: AsyncSession = Depends(get_db)):
    """List snapshots for a project."""
    project = await db.scalar(select(Project).where(Project.id == project_id))
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Project {project_id} not found"
        )
    result = await db.execute(
        select(ProjectSnapshot)
        .where(ProjectSnapshot.project_id == project_id)
        .order_by(ProjectSnapshot.created_at.desc())
    )
    snaps = result.scalars().all()
    return [
        {
            "id": s.id,
            "project_id": s.project_id,
            "version": s.version,
            "created_at": s.created_at.isoformat(),
        }
        for s in snaps
    ]


@router.get("/{project_id}/snapshots/{snapshot_id}")
async def get_snapshot(project_id: int, snapshot_id: int, db: AsyncSession = Depends(get_db)):
    """Fetch a snapshot payload."""
    snap = await db.scalar(
        select(ProjectSnapshot).where(
            ProjectSnapshot.id == snapshot_id, ProjectSnapshot.project_id == project_id
        )
    )
    if not snap:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Snapshot {snapshot_id} not found for project {project_id}",
        )
    try:
        data = json.loads(snap.data)
    except Exception:
        data = snap.data
    return {
        "id": snap.id,
        "project_id": snap.project_id,
        "version": snap.version,
        "created_at": snap.created_at.isoformat(),
        "data": data,
    }
