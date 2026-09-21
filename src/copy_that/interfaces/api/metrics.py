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

from copy_that.application.errors import ApplicationError
from copy_that.application.ports.metrics import MetricsService
from copy_that.application.use_cases import metrics as metrics_use_cases
from copy_that.interfaces.api import dependencies as deps

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/metrics", tags=["metrics"])


@router.get("/projects/{project_id}/stream")
async def stream_metrics(
    project_id: int,
    metrics_service: MetricsService = Depends(deps.get_metrics_service),
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
    try:
        await metrics_service.ensure_project(project_id=project_id)
    except ApplicationError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    logger.info(f"Starting metrics stream for project {project_id}")

    # Stream generator
    async def generate_events():
        """Generate Server-Sent Events for metrics."""
        try:
            async for event in metrics_use_cases.stream_metrics(
                metrics_service, project_id=project_id
            ):
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
    metrics_service: MetricsService = Depends(deps.get_metrics_service),
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
    try:
        await metrics_service.ensure_project(project_id=project_id)
    except ApplicationError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    logger.info(f"Computing metrics for project {project_id}")
    return await metrics_use_cases.get_metrics(metrics_service, project_id=project_id)


@router.get("/providers")
async def list_providers(metrics_service: MetricsService = Depends(deps.get_metrics_service)):
    """List all registered metric providers.

    Returns information about available providers including:
    - name: Provider identifier
    - tier: Which tier it belongs to (tier_1, tier_2, tier_3)
    - priority: Execution order (lower = earlier)

    Returns:
        JSON with provider information
    """
    providers = metrics_service.provider_info()
    return {
        "providers": providers,
        "count": len(providers),
    }
