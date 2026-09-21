from __future__ import annotations

from typing import Any

from copy_that.application.ports.jobs import JobRepository
from copy_that.domain.jobs import Job, JobStatus


async def create_job(
    repo: JobRepository, *, job_type: str, payload: dict[str, Any] | None, queue: str | None
) -> Job:
    return await repo.create(job_type=job_type, payload=payload, queue=queue)


async def get_job(repo: JobRepository, *, job_id: int) -> Job | None:
    return await repo.get(job_id=job_id)


async def mark_queued(
    repo: JobRepository, *, job_id: int, message: str | None = None
) -> Job | None:
    return await repo.update_status(
        job_id=job_id, status=JobStatus.QUEUED, progress=0.0, message=message
    )


async def mark_started(
    repo: JobRepository, *, job_id: int, message: str | None = None
) -> Job | None:
    return await repo.update_status(
        job_id=job_id, status=JobStatus.RUNNING, progress=0.05, message=message
    )


async def mark_progress(
    repo: JobRepository, *, job_id: int, progress: float, message: str | None = None
) -> Job | None:
    return await repo.mark_progress(job_id=job_id, progress=progress, message=message)


async def mark_completed(
    repo: JobRepository,
    *,
    job_id: int,
    result: dict[str, Any] | None = None,
    message: str | None = None,
) -> Job | None:
    return await repo.mark_completed(job_id=job_id, result=result, message=message)


async def mark_failed(
    repo: JobRepository, *, job_id: int, error: str, message: str | None = None
) -> Job | None:
    return await repo.mark_failed(job_id=job_id, error=error, message=message)
