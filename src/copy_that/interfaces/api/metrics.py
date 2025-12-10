"""Metrics API - Progressive streaming of design system metrics.

Provides Server-Sent Events (SSE) streaming of metrics computed by multiple providers:
- TIER 1 (Quantitative): Fast, deterministic analysis (~50ms)
- TIER 2 (Accessibility): WCAG compliance checks (~100ms)
- TIER 3 (Qualitative): AI-powered insights (5-15s or null)
"""

import json
import logging

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from copy_that.domain.models import Project
from copy_that.infrastructure.database import get_db
from copy_that.services.metrics.accessibility import AccessibilityMetricsProvider
from copy_that.services.metrics.orchestrator import MetricsOrchestrator
from copy_that.services.metrics.qualitative import QualitativeMetricsProvider
from copy_that.services.metrics.quantitative import QuantitativeMetricsProvider
from copy_that.services.metrics.registry import MetricProviderRegistry

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/metrics", tags=["metrics"])


@router.get("/projects/{project_id}/stream")
async def stream_metrics(
    project_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Stream design system metrics progressively using Server-Sent Events.

    Metrics are computed in priority order and streamed as they become available:
    1. TIER 1 (Quantitative) - Returns first (~50ms)
    2. TIER 2 (Accessibility) - Returns second (~100ms)
    3. TIER 3 (Qualitative) - Returns last (5-15s or null if API unavailable)

    Each event contains:
    - tier: "tier_1", "tier_2", or "tier_3"
    - provider: Provider name (e.g., "quantitative")
    - timestamp: ISO 8601 timestamp
    - data: Computed metrics (or null if error/unavailable)
    - error: Error message if computation failed
    - duration_ms: How long the computation took

    Args:
        project_id: Project to compute metrics for
        db: Database session

    Returns:
        Server-Sent Events stream with progressive metrics

    Raises:
        HTTPException: 404 if project not found

    Example:
        # JavaScript frontend
        const eventSource = new EventSource(`/api/metrics/projects/${projectId}/stream`);

        eventSource.onmessage = (event) => {
          const result = JSON.parse(event.data);

          if (result.tier === "tier_1") {
            // Show quantitative metrics immediately
            updateUI({ quantitative: result.data });
          } else if (result.tier === "tier_2") {
            // Add accessibility analysis
            updateUI({ accessibility: result.data });
          } else if (result.tier === "tier_3") {
            // Stream AI insights (or show "unavailable" if null)
            updateUI({ qualitative: result.data });
          }
        };
    """
    # Verify project exists
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(status_code=404, detail=f"Project {project_id} not found")

    # Create registry and register all providers
    registry = MetricProviderRegistry()

    # Register providers (order doesn't matter - orchestrator sorts by tier/priority)
    registry.register(QuantitativeMetricsProvider(db))
    registry.register(AccessibilityMetricsProvider(db))
    registry.register(QualitativeMetricsProvider(db))

    # Create orchestrator
    orchestrator = MetricsOrchestrator(registry)

    logger.info(f"Starting metrics stream for project {project_id}")

    # Stream generator
    async def generate_events():
        """Generate Server-Sent Events for metrics."""
        try:
            async for event in orchestrator.stream_metrics(project_id):
                # Format as SSE
                yield f"data: {json.dumps(event)}\n\n"

            # Send completion event
            yield f"data: {json.dumps({'event': 'complete'})}\n\n"

        except Exception as e:
            logger.error(f"Error streaming metrics for project {project_id}: {e}", exc_info=True)
            # Send error event
            error_event = {
                "event": "error",
                "error": str(e),
            }
            yield f"data: {json.dumps(error_event)}\n\n"

    return StreamingResponse(
        generate_events(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        },
    )


@router.get("/projects/{project_id}")
async def get_metrics(
    project_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get all metrics for a project (non-streaming).

    Computes all metrics and returns them in a single response.
    Useful for testing or when streaming is not needed.

    Note: This endpoint waits for ALL metrics (including TIER 3) before returning,
    so it may take 5-15 seconds. Use the streaming endpoint for better UX.

    Args:
        project_id: Project to compute metrics for
        db: Database session

    Returns:
        JSON with all computed metrics

    Raises:
        HTTPException: 404 if project not found
    """
    # Verify project exists
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(status_code=404, detail=f"Project {project_id} not found")

    # Create registry and register all providers
    registry = MetricProviderRegistry()
    registry.register(QuantitativeMetricsProvider(db))
    registry.register(AccessibilityMetricsProvider(db))
    registry.register(QualitativeMetricsProvider(db))

    # Create orchestrator
    orchestrator = MetricsOrchestrator(registry)

    logger.info(f"Computing metrics for project {project_id}")

    # Compute all metrics
    results = await orchestrator.compute_all(project_id)

    # Format response
    response = {}
    for provider_name, result in results.items():
        response[provider_name] = {
            "tier": result.tier.value,
            "data": result.data,
            "error": result.error,
            "duration_ms": result.duration_ms,
        }

    return response


@router.get("/providers")
async def list_providers():
    """List all registered metric providers.

    Returns information about available providers including:
    - name: Provider identifier
    - tier: Which tier it belongs to (tier_1, tier_2, tier_3)
    - priority: Execution order (lower = earlier)

    Returns:
        JSON with provider information
    """
    # Create registry and register all providers
    registry = MetricProviderRegistry()
    registry.register(QuantitativeMetricsProvider(db=None))  # type: ignore
    registry.register(AccessibilityMetricsProvider(db=None))  # type: ignore
    registry.register(QualitativeMetricsProvider(db=None))  # type: ignore

    # Create orchestrator
    orchestrator = MetricsOrchestrator(registry)

    return {
        "providers": orchestrator.get_provider_info(),
        "count": len(registry),
    }
