from __future__ import annotations

from typing import Protocol

from copy_that.domain.snapshots import ProjectSnapshot


class SnapshotRepository(Protocol):
    async def list_for_project(self, *, project_id: int) -> list[ProjectSnapshot]: ...

    async def get_for_project(
        self, *, project_id: int, snapshot_id: int
    ) -> ProjectSnapshot | None: ...

    async def create(self, *, project_id: int, version: int, data: str) -> ProjectSnapshot: ...
