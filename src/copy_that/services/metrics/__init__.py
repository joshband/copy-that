"""Metrics service with pluggable provider architecture.

This module implements a composable metrics pipeline where each provider
independently computes metrics and streams results as they become available.

Architecture:
- MetricProvider: Abstract base for metric computation
- MetricsOrchestrator: Coordinates providers and streams results
- Registry: Auto-discovers and loads metric providers

Non-blocking design:
- TIER 1 (Quantitative): Returns immediately (~50ms)
- TIER 2 (Accessibility): Returns quickly (~100ms)
- TIER 3 (Qualitative): Streams when available or returns null
"""

from .base import MetricProvider, MetricResult, MetricTier
from .orchestrator import MetricsOrchestrator
from .registry import MetricProviderRegistry

__all__ = [
    "MetricProvider",
    "MetricResult",
    "MetricTier",
    "MetricProviderRegistry",
    "MetricsOrchestrator",
]
