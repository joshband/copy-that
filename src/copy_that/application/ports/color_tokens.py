from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol

from core.tokens.model import Token


class ColorTokenWriter(Protocol):
    async def persist_aggregated_library(
        self,
        *,
        library_id: int,
        project_id: int,
        aggregated_tokens: Sequence[Token],
        statistics: dict,
    ) -> int: ...
