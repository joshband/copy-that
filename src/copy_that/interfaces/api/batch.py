from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from copy_that.application.use_cases import jobs as job_use_cases
from copy_that.infrastructure.celery.app import robust_redis_connection
from copy_that.interfaces.api import dependencies as deps
from copy_that.interfaces.api.multi_extract import MultiExtractRequest

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/batch", tags=["batch"])


class BatchEnqueueResponse(BaseModel):
    job_id: int
    queue: str
    status: str


class BatchMetricsResponse(BaseModel):
    queue: str
    depth: int
    note: str | None = None


@router.post("/enqueue", response_model=BatchEnqueueResponse)
async def enqueue_batch_extract(
    request: MultiExtractRequest,
    job_repo=Depends(deps.get_job_repo),
    job_executor=Depends(deps.get_job_executor),
) -> BatchEnqueueResponse:
    """
    Enqueue a batch extraction job for throughput-optimized processing.
    """
    try:
        job = await job_use_cases.create_job(
            job_repo,
            job_type="batch_extract",
            payload=request.model_dump(),
            queue="batch-extract",
        )
        await job_use_cases.mark_queued(
            job_repo, job_id=job.id, message="queued_for_batch_processing"
        )
        await job_executor.enqueue(job, payload=request.model_dump())
        return BatchEnqueueResponse(
            job_id=job.id, queue=job.queue or "batch-extract", status="queued"
        )
    except Exception as e:
        logger.exception("Failed to enqueue batch extract job: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to enqueue batch job",
        )


@router.get("/metrics", response_model=BatchMetricsResponse)
async def batch_queue_metrics() -> BatchMetricsResponse:
    """
    Return basic queue depth metrics for the batch queue.
    """
    conn = robust_redis_connection()
    if not conn:
        return BatchMetricsResponse(queue="batch-extract", depth=0, note="Redis unavailable")
    try:
        depth = int(conn.llen("celery"))  # default Celery queue key
        return BatchMetricsResponse(queue="batch-extract", depth=depth)
    except Exception as e:  # pragma: no cover - defensive
        logger.warning("Failed to read queue depth: %s", e)
        return BatchMetricsResponse(queue="batch-extract", depth=0, note="Failed to read depth")
