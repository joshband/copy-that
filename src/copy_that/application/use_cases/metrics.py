from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any

from copy_that.application.ports.metrics import MetricsService


async def stream_metrics(
    service: MetricsService, *, project_id: int
) -> AsyncIterator[dict[str, Any]]:
    async for event in service.stream(project_id=project_id):
        yield event


async def get_metrics(service: MetricsService, *, project_id: int) -> dict[str, dict[str, Any]]:
    return await service.compute_all(project_id=project_id)
