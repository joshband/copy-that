from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol

from copy_that.domain.gradient_tokens import GradientToken, GradientTokenCreate


class GradientTokenRepository(Protocol):
    async def record_extraction(
        self,
        *,
        project_id: int,
        source_url: str,
        gradients: Sequence[GradientTokenCreate],
    ) -> int: ...

    async def list_by_project(self, *, project_id: int) -> list[GradientToken]: ...

    async def list_all(self, *, project_id: int | None) -> list[GradientToken]: ...
