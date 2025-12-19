"""Lightweight performance budget tracking for extractors."""

from __future__ import annotations

import logging
import os
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
}


def _budget(operation: str) -> int | None:
    return BUDGETS_MS.get(operation)


def _enforce() -> bool:
    return os.getenv("PERF_BUDGET_ENFORCE", "").lower() in {"1", "true", "yes"}


@contextmanager
def track_perf(operation: str, attrs: dict[str, Any] | None = None) -> Iterator[None]:
    """Context manager to log duration and optionally enforce budgets.

    Logs a structured payload under the `perf` key to keep parsers simple.
    When PERF_BUDGET_ENFORCE is truthy, exceeding the budget raises RuntimeError
    (intended for CI checks).
    """
    start = time.perf_counter()
    try:
        yield
    finally:
        elapsed_ms = (time.perf_counter() - start) * 1000
        budget_ms = _budget(operation)
        payload: dict[str, Any] = {
            "metric": "perf_ms",
            "operation": operation,
            "duration_ms": round(elapsed_ms, 2),
        }
        if budget_ms is not None:
            payload["budget_ms"] = budget_ms
            payload["over_budget"] = elapsed_ms > budget_ms
        if attrs:
            payload.update(attrs)

        logger.info("perf_timing", extra={"perf": payload})

        if budget_ms is not None and elapsed_ms > budget_ms:
            logger.warning("perf budget exceeded", extra={"perf": payload})
            if _enforce():
                raise RuntimeError(
                    f"Performance budget exceeded for {operation}: {elapsed_ms:.2f}ms > {budget_ms}ms"
                )
