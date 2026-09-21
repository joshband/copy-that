"""
Project snapshots: list and fetch stored token snapshots.
"""

import json
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status

from copy_that.application.ports.projects import ProjectRepository
from copy_that.application.ports.snapshots import SnapshotRepository
from copy_that.application.use_cases import snapshots as snapshots_use_cases
from copy_that.interfaces.api import dependencies as deps

router = APIRouter(prefix="/api/v1/projects", tags=["snapshots"])


@router.get("/{project_id}/snapshots")
async def list_snapshots(
    project_id: int,
    project_repo: ProjectRepository = Depends(deps.get_project_repo),
    snapshot_repo: SnapshotRepository = Depends(deps.get_snapshot_repo),
) -> list[dict[str, Any]]:
    """List snapshots for a project."""
    project = await project_repo.get(project_id=project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Project {project_id} not found"
        )
    snaps = await snapshots_use_cases.list_project_snapshots(snapshot_repo, project_id=project_id)
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
async def get_snapshot(
    project_id: int,
    snapshot_id: int,
    snapshot_repo: SnapshotRepository = Depends(deps.get_snapshot_repo),
) -> dict[str, Any]:
    """Fetch a snapshot payload."""
    snap = await snapshots_use_cases.get_project_snapshot(
        snapshot_repo, project_id=project_id, snapshot_id=snapshot_id
    )
    if not snap:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Snapshot {snapshot_id} not found for project {project_id}",
        )
    try:
        data = json.loads(snap.data)
    except json.JSONDecodeError:
        data = snap.data
    return {
        "id": snap.id,
        "project_id": snap.project_id,
        "version": snap.version,
        "created_at": snap.created_at.isoformat(),
        "data": data,
    }
