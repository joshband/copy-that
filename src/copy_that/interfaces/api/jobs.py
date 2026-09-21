"""Job status and progress streaming endpoints."""

from __future__ import annotations

import asyncio
import json

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from copy_that.application.ports.jobs import JobRepository
from copy_that.domain.jobs import JobStatus
from copy_that.interfaces.api import dependencies as deps

router = APIRouter(prefix="/api/v1/jobs", tags=["jobs"])


class JobStatusResponse(BaseModel):
    job_id: int
    status: str
    progress: float
    queue: str | None = None
    message: str | None = None
    error: str | None = None
    result: dict[str, object] | None = None


@router.get("/{job_id}", response_model=JobStatusResponse)
async def get_job(job_id: int, job_repo: JobRepository = Depends(deps.get_job_repo)):
    job = await job_repo.get(job_id=job_id)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Job {job_id} not found")
    return JobStatusResponse(
        job_id=job.id,
        status=job.status.value,
        progress=job.progress,
        queue=job.queue,
        message=job.message,
        error=job.error,
        result=job.result,
    )


@router.get("/{job_id}/stream")
async def stream_job(
    job_id: int,
    job_repo: JobRepository = Depends(deps.get_job_repo),
):
    async def event_stream():
        last_status: JobStatus | None = None
        last_progress: float | None = None

        while True:
            job = await job_repo.get(job_id=job_id)
            if not job:
                yield f"event: error\ndata: {json.dumps({'error': f'Job {job_id} not found'})}\n\n"
                return

            if last_status != job.status or last_progress != job.progress:
                payload = {
                    "job_id": job.id,
                    "status": job.status.value,
                    "progress": job.progress,
                    "queue": job.queue,
                    "message": job.message,
                    "error": job.error,
                    "result": job.result if job.status == JobStatus.COMPLETED else None,
                }
                yield f"data: {json.dumps(payload, default=str)}\n\n"
                last_status = job.status
                last_progress = job.progress

            if job.status in (JobStatus.COMPLETED, JobStatus.FAILED):
                return

            await asyncio.sleep(0.75)

    return StreamingResponse(event_stream(), media_type="text/event-stream")
