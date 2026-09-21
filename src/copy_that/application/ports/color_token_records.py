from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol

from copy_that.domain.color_tokens import ColorToken, ColorTokenCreate


class ColorTokenRepository(Protocol):
    async def record_extraction(
        self,
        *,
        project_id: int,
        source_url: str,
        tokens: Sequence[ColorTokenCreate],
        result_data: dict[str, object],
    ) -> int: ...

    async def list_by_project(self, *, project_id: int) -> list[ColorToken]: ...

    async def list_all(self, *, project_id: int | None) -> list[ColorToken]: ...

    async def list_by_job(self, *, extraction_job_id: int) -> list[ColorToken]: ...

    async def get(self, *, color_id: int) -> ColorToken | None: ...

    async def create(
        self, *, project_id: int, extraction_job_id: int | None, token: ColorTokenCreate
    ) -> ColorToken: ...

    async def update(
        self,
        *,
        color_id: int,
        semantic_names: str | None,
        design_intent: str | None,
    ) -> ColorToken | None: ...
