"""Base classes for metric providers.

Each provider computes metrics independently and streams results
as they become available, enabling non-blocking progressive loading.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any


class MetricTier(str, Enum):
    """Metric computation tiers for progressive loading."""

    TIER_1 = "tier_1"  # Quantitative - immediate, ~0-50ms
    TIER_2 = "tier_2"  # Accessibility - fast, ~50-100ms
    TIER_3 = "tier_3"  # Qualitative/AI - slow, 5-15s or null


@dataclass
class MetricResult:
    """Result from a metric provider computation.

    Attributes:
        tier: Which tier this metric belongs to
        provider_name: Name of the provider that computed this
        data: The actual metric data (varies by provider)
        error: If computation failed, the error message
        duration_ms: How long computation took
    """

    tier: MetricTier
    provider_name: str
    data: dict[str, Any] | None = None
    error: str | None = None
    duration_ms: float | None = None


class MetricProvider(ABC):
    """Abstract base for metric providers.

    Each provider:
    - Computes one category of metrics independently
    - Returns results quickly (non-blocking)
    - Can fail gracefully without blocking other providers

    Example:
        class CustomMetricsProvider(MetricProvider):
            name = "custom"
            tier = MetricTier.TIER_2

            async def compute(self, project_id: int) -> MetricResult:
                try:
                    data = await self._analyze(project_id)
                    return MetricResult(
                        tier=self.tier,
                        provider_name=self.name,
                        data=data
                    )
                except Exception as e:
                    return MetricResult(
                        tier=self.tier,
                        provider_name=self.name,
                        error=str(e)
                    )
    """

    # Override in subclasses
    name: str = "unknown"
    tier: MetricTier = MetricTier.TIER_1

    @abstractmethod
    async def compute(self, project_id: int) -> MetricResult:
        """Compute metrics for a project.

        Args:
            project_id: The project to compute metrics for

        Returns:
            MetricResult with computed data or error
        """
        pass

    @property
    def priority(self) -> int:
        """Providers are computed in priority order.

        Lower tier number = higher priority (computed first)
        """
        tier_priority = {
            MetricTier.TIER_1: 1,
            MetricTier.TIER_2: 2,
            MetricTier.TIER_3: 3,
        }
        return tier_priority.get(self.tier, 999)
