from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol

from copy_that.domain.typography import TypographyToken, TypographyTokenCreate


class TypographyTokenRepository(Protocol):
    async def record_extraction(
        self,
        *,
        project_id: int,
        source_url: str,
        tokens: Sequence[TypographyTokenCreate],
        result_data: dict[str, object],
    ) -> int: ...

    async def list_by_project(self, *, project_id: int) -> list[TypographyToken]: ...

    async def list_all(self, *, project_id: int | None) -> list[TypographyToken]: ...

    async def create(self, *, token: TypographyTokenCreate) -> TypographyToken: ...

    async def get(self, *, token_id: int) -> TypographyToken | None: ...

    async def update(
        self,
        *,
        token_id: int,
        token: TypographyTokenCreate,
    ) -> TypographyToken | None: ...

    async def delete(self, *, token_id: int) -> bool: ...
