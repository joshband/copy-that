from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol

from copy_that.domain.spacing_tokens import SpacingToken, SpacingTokenCreate


class SpacingTokenRepository(Protocol):
    async def record_extraction(
        self,
        *,
        project_id: int,
        source_url: str,
        tokens: Sequence[SpacingTokenCreate],
        result_data: dict[str, object],
    ) -> int: ...

    async def list_by_project(self, *, project_id: int) -> list[SpacingToken]: ...

    async def list_all(self, *, project_id: int | None) -> list[SpacingToken]: ...
