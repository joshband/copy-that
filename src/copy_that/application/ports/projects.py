from __future__ import annotations

from typing import Protocol

from copy_that.domain.projects import Project


class ProjectRepository(Protocol):
    async def create(self, *, name: str, description: str | None) -> Project: ...

    async def get(self, *, project_id: int) -> Project | None: ...

    async def list(self, *, limit: int, offset: int) -> list[Project]: ...

    async def count(self) -> int: ...

    async def update(
        self, *, project_id: int, name: str | None, description: str | None
    ) -> Project | None: ...

    async def delete(self, *, project_id: int) -> bool: ...
