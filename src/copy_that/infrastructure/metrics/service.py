from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from copy_that.application.errors import ApplicationError
from copy_that.application.ports.metrics import MetricsService
from copy_that.infrastructure.metrics.accessibility import AccessibilityMetricsProvider
from copy_that.infrastructure.metrics.orchestrator import MetricsOrchestrator
from copy_that.infrastructure.metrics.qualitative import QualitativeMetricsProvider
from copy_that.infrastructure.metrics.quantitative import QuantitativeMetricsProvider
from copy_that.infrastructure.metrics.registry import MetricProviderRegistry
from copy_that.infrastructure.persistence.models import Project


class ProjectNotFoundError(ApplicationError):
    pass


class SQLAlchemyMetricsService(MetricsService):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def _ensure_project_exists(self, project_id: int) -> None:
        result = await self._session.execute(select(Project).where(Project.id == project_id))
        if result.scalar_one_or_none() is None:
            raise ProjectNotFoundError(f"Project {project_id} not found")

    async def ensure_project(self, *, project_id: int) -> None:
        await self._ensure_project_exists(project_id)

    def stream(self, *, project_id: int) -> AsyncIterator[dict[str, Any]]:
        async def gen() -> AsyncIterator[dict[str, Any]]:
            await self._ensure_project_exists(project_id)

            registry = MetricProviderRegistry()
            registry.register(QuantitativeMetricsProvider(self._session))
            registry.register(AccessibilityMetricsProvider(self._session))
            registry.register(QualitativeMetricsProvider(self._session))

            orchestrator = MetricsOrchestrator(registry)
            async for event in orchestrator.stream_metrics(project_id):
                yield event

        return gen()

    async def compute_all(self, *, project_id: int) -> dict[str, dict[str, Any]]:
        await self._ensure_project_exists(project_id)

        registry = MetricProviderRegistry()
        registry.register(QuantitativeMetricsProvider(self._session))
        registry.register(AccessibilityMetricsProvider(self._session))
        registry.register(QualitativeMetricsProvider(self._session))

        orchestrator = MetricsOrchestrator(registry)
        results = await orchestrator.compute_all(project_id)

        response: dict[str, dict[str, Any]] = {}
        for provider_name, result in results.items():
            response[provider_name] = {
                "tier": result.tier.value,
                "data": result.data,
                "error": result.error,
                "duration_ms": result.duration_ms,
            }
        return response

    def provider_info(self) -> list[dict[str, Any]]:
        registry = MetricProviderRegistry()
        registry.register(QuantitativeMetricsProvider(self._session))
        registry.register(AccessibilityMetricsProvider(self._session))
        registry.register(QualitativeMetricsProvider(self._session))
        orchestrator = MetricsOrchestrator(registry)
        return orchestrator.get_provider_info()
