from __future__ import annotations

from typing import Protocol

from copy_that.domain.sessions import ExtractionSession


class SessionRepository(Protocol):
    async def get(self, *, session_id: int) -> ExtractionSession | None: ...

    async def create(
        self, *, project_id: int, name: str, description: str | None
    ) -> ExtractionSession: ...

    async def set_image_count(
        self, *, session_id: int, image_count: int
    ) -> ExtractionSession | None: ...
