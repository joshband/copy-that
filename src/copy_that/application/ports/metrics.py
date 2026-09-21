from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any, Protocol


class MetricsService(Protocol):
    async def ensure_project(self, *, project_id: int) -> None: ...

    def stream(self, *, project_id: int) -> AsyncIterator[dict[str, Any]]: ...

    async def compute_all(self, *, project_id: int) -> dict[str, dict[str, Any]]: ...

    def provider_info(self) -> list[dict[str, Any]]: ...
