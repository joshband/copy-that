"""Metrics orchestrator for coordinating providers and streaming results.

The orchestrator:
- Manages metric provider lifecycle
- Streams results as they become available (non-blocking)
- Handles errors gracefully (one provider failing doesn't block others)
- Sorts providers by priority (TIER 1 first, TIER 3 last)
"""

import logging
from datetime import datetime
from time import time

from .base import MetricResult, MetricTier
from .registry import MetricProviderRegistry

logger = logging.getLogger(__name__)


class MetricsOrchestrator:
    """Coordinates metric providers and streams results progressively.

    Usage:
        registry = MetricProviderRegistry()
        # ... register providers ...

        orchestrator = MetricsOrchestrator(registry)

        # Stream metrics as SSE
        async for result in orchestrator.stream_metrics(project_id):
            yield f"data: {json.dumps(result)}\n\n"
    """

    def __init__(self, registry: MetricProviderRegistry):
        """Initialize orchestrator with a provider registry.

        Args:
            registry: MetricProviderRegistry with registered providers
        """
        self.registry = registry
        self.logger = logger

    async def stream_metrics(self, project_id: int, filter_tiers: list[MetricTier] | None = None):
        """Stream metrics progressively, emitting results as they become available.

        Providers are executed in priority order (TIER 1, then TIER 2, then TIER 3).
        If a provider fails, the error is emitted but other providers continue.

        Args:
            project_id: Project to compute metrics for
            filter_tiers: Optional list of tiers to compute. If None, all tiers.

        Yields:
            dict with provider result (data or error)
        """
        providers = self.registry.get_all_providers()

        if filter_tiers:
            providers = [p for p in providers if p.tier in filter_tiers]

        self.logger.info(
            f"Starting metrics computation for project {project_id} with {len(providers)} providers"
        )

        for provider in providers:
            try:
                start_time = time()
                result = await provider.compute(project_id)
                duration_ms = (time() - start_time) * 1000

                result.duration_ms = duration_ms

                self.logger.info(f"Provider '{provider.name}' completed in {duration_ms:.1f}ms")

                yield {
                    "tier": result.tier.value,
                    "provider": provider.name,
                    "timestamp": datetime.utcnow().isoformat(),
                    "data": result.data,
                    "error": result.error,
                    "duration_ms": result.duration_ms,
                }

            except Exception as e:
                self.logger.error(
                    f"Provider '{provider.name}' failed with exception: {e}",
                    exc_info=True,
                )

                yield {
                    "tier": provider.tier.value,
                    "provider": provider.name,
                    "timestamp": datetime.utcnow().isoformat(),
                    "data": None,
                    "error": f"Provider failed: {str(e)}",
                    "duration_ms": None,
                }

    async def compute_all(
        self, project_id: int, filter_tiers: list[MetricTier] | None = None
    ) -> dict[str, MetricResult]:
        """Compute all metrics and return as a dict.

        Useful for non-streaming endpoints or batched processing.

        Args:
            project_id: Project to compute metrics for
            filter_tiers: Optional list of tiers to compute. If None, all tiers.

        Returns:
            Dict mapping provider name to MetricResult
        """
        results = {}

        async for event in self.stream_metrics(project_id, filter_tiers):
            provider_name = event["provider"]
            result = MetricResult(
                tier=MetricTier(event["tier"]),
                provider_name=provider_name,
                data=event["data"],
                error=event["error"],
                duration_ms=event["duration_ms"],
            )
            results[provider_name] = result

        return results

    async def compute_tier(self, project_id: int, tier: MetricTier) -> dict[str, MetricResult]:
        """Compute metrics for a specific tier only.

        Args:
            project_id: Project to compute metrics for
            tier: The tier to compute

        Returns:
            Dict mapping provider name to MetricResult
        """
        return await self.compute_all(project_id, filter_tiers=[tier])

    def get_provider_info(self) -> list[dict]:
        """Get information about all registered providers.

        Returns:
            List of dicts with provider metadata
        """
        providers = self.registry.get_all_providers()
        return [
            {
                "name": p.name,
                "tier": p.tier.value,
                "priority": p.priority,
            }
            for p in providers
        ]
