from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Protocol

from copy_that.domain.color_tokens import ColorToken


class ColorTokenLibraryRepository(Protocol):
    async def list_by_library_id(self, *, library_id: int) -> list[ColorToken]: ...

    async def assign_roles(
        self,
        *,
        library_id: int,
        role_by_token_id: Mapping[int, str],
    ) -> int: ...

    async def list_by_ids_for_library(
        self,
        *,
        library_id: int,
        token_ids: Sequence[int],
    ) -> list[ColorToken]: ...
