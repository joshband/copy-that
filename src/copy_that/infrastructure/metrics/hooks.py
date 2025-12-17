"""Lightweight metrics hooks for orchestrators."""

from __future__ import annotations

import logging
from collections.abc import Callable, Coroutine
from typing import Any

MetricsHook = Callable[[str, dict[str, Any]], Coroutine[None, None, None] | None]


def logging_metrics_hook(logger: logging.Logger | None = None) -> MetricsHook:
    """Return a metrics hook that logs orchestrator payloads."""

    log = logger or logging.getLogger("metrics.orchestrator")

    async def _hook(orchestrator_name: str, payload: dict[str, Any]) -> None:
        log.info("orchestrator_metrics", extra={"orchestrator": orchestrator_name, **payload})

    return _hook
