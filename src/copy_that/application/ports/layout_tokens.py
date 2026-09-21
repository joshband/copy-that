from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol

from copy_that.domain.layout_tokens import LayoutToken, LayoutTokenCreate


class LayoutTokenRepository(Protocol):
    async def record_extraction(
        self,
        *,
        project_id: int,
        extraction_job_id: int | None,
        tokens: Sequence[LayoutTokenCreate],
    ) -> int: ...

    async def list_by_project(self, *, project_id: int) -> list[LayoutToken]: ...

    async def list_all(self, *, project_id: int | None) -> list[LayoutToken]: ...
