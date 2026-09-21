"""Lightweight performance budget tracking for extractors."""

from __future__ import annotations

import logging
import os
import resource
import time
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

logger = logging.getLogger(__name__)

# Budgets in milliseconds; tune as real data arrives.
BUDGETS_MS: dict[str, int] = {
    # Image upload to first token should stay under 2s on average
    "upload.first_token": 2_000,
    # Extraction per token type
    "extract.color.ai": 10_000,
    "extract.spacing.ai": 10_000,
    "extract.shadow.ai": 10_000,
    "extract.typography.ai": 10_000,
}

# Memory budgets in MB
MEMORY_BUDGETS_MB: dict[str, int] = {
    "upload.first_token": 512,
    "extract.color.ai": 512,
    "extract.spacing.ai": 512,
    "extract.shadow.ai": 512,
    "extract.typography.ai": 512,
}


def _budget(operation: str) -> int | None:
    return BUDGETS_MS.get(operation)


def _enforce() -> bool:
    return os.getenv("PERF_BUDGET_ENFORCE", "").lower() in {"1", "true", "yes"}


@contextmanager
def track_perf(
    operation: str, attrs: dict[str, Any] | None = None, measure_memory: bool = False
) -> Iterator[None]:
    """Context manager to log duration and optionally enforce budgets.

    Logs a structured payload under the `perf` key to keep parsers simple.
    When PERF_BUDGET_ENFORCE is truthy, exceeding the budget raises RuntimeError
    (intended for CI checks).
    """
    start = time.perf_counter()
    start_rss_mb: float | None = _current_rss_mb() if measure_memory else None
    try:
        yield
    finally:
        elapsed_ms = (time.perf_counter() - start) * 1000
        budget_ms = _budget(operation)
        rss_mb = _current_rss_mb() if measure_memory else None
        mem_budget_mb = MEMORY_BUDGETS_MB.get(operation) if measure_memory else None
        payload: dict[str, Any] = {
            "metric": "perf_ms",
            "operation": operation,
            "duration_ms": round(elapsed_ms, 2),
        }
        if budget_ms is not None:
            payload["budget_ms"] = budget_ms
            payload["over_budget"] = elapsed_ms > budget_ms
        if rss_mb is not None:
            payload["rss_mb"] = round(rss_mb, 2)
            payload["start_rss_mb"] = round(start_rss_mb or rss_mb, 2)
            if mem_budget_mb is not None:
                payload["memory_budget_mb"] = mem_budget_mb
                payload["over_memory_budget"] = rss_mb > mem_budget_mb
        if attrs:
            payload.update(attrs)

        logger.info("perf_timing", extra={"perf": payload})

        exceeded = False
        if budget_ms is not None and elapsed_ms > budget_ms:
            exceeded = True
        if mem_budget_mb is not None and rss_mb is not None and rss_mb > mem_budget_mb:
            exceeded = True
        if exceeded:
            logger.warning("perf budget exceeded", extra={"perf": payload})
            if _enforce():
                raise RuntimeError(
                    f"Performance budget exceeded for {operation}: {elapsed_ms:.2f}ms (budget {budget_ms}ms), rss {rss_mb}MB (budget {mem_budget_mb}MB)"
                )


def _current_rss_mb() -> float:
    """Return current RSS in MB using resource; handle platform differences."""
    usage = resource.getrusage(resource.RUSAGE_SELF)
    rss_kb = usage.ru_maxrss
    # macOS reports bytes; Linux reports kilobytes
    if rss_kb > 10_000_000:
        return rss_kb / (1024 * 1024)
    return rss_kb / 1024
