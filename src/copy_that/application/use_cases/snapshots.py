from __future__ import annotations

from copy_that.application.ports.snapshots import SnapshotRepository
from copy_that.domain.snapshots import ProjectSnapshot


async def list_project_snapshots(
    repo: SnapshotRepository, *, project_id: int
) -> list[ProjectSnapshot]:
    return await repo.list_for_project(project_id=project_id)


async def get_project_snapshot(
    repo: SnapshotRepository, *, project_id: int, snapshot_id: int
) -> ProjectSnapshot | None:
    return await repo.get_for_project(project_id=project_id, snapshot_id=snapshot_id)
