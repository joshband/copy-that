from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol

from copy_that.domain.shadows import ShadowToken, ShadowTokenCreate


class ShadowTokenRepository(Protocol):
    async def record_extraction(
        self,
        *,
        project_id: int,
        source_url: str,
        shadows: Sequence[ShadowTokenCreate],
    ) -> int: ...

    async def list_by_project(self, *, project_id: int) -> list[ShadowToken]: ...

    async def list_all(self, *, project_id: int | None) -> list[ShadowToken]: ...

    async def get(self, *, shadow_id: int) -> ShadowToken | None: ...

    async def update(
        self,
        *,
        shadow_id: int,
        name: str | None,
        semantic_role: str | None,
        shadow_type: str | None,
        confidence: float | None,
    ) -> ShadowToken | None: ...

    async def delete(self, *, shadow_id: int) -> bool: ...
