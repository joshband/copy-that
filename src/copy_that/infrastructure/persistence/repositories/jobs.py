from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from copy_that.domain.jobs import Job, JobStatus
from copy_that.domain.time import utc_now
from copy_that.infrastructure.persistence.models import Job as JobModel


def _to_entity(model: JobModel) -> Job:
    return Job(
        id=model.id,
        job_type=model.job_type,
        status=JobStatus(model.status),
        progress=float(model.progress or 0.0),
        queue=model.queue,
        payload=model.payload,
        result=model.result_data,
        error=model.error_message,
        message=model.status_message,
        created_at=model.created_at,
        updated_at=model.updated_at,
        started_at=model.started_at,
        completed_at=model.completed_at,
    )


class SQLAlchemyJobRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(
        self, *, job_type: str, payload: dict[str, Any] | None, queue: str | None
    ) -> Job:
        job = JobModel(
            job_type=job_type,
            payload=payload,
            queue=queue,
            status=JobStatus.PENDING.value,
            progress=0.0,
            status_message="pending",
        )
        self._session.add(job)
        await self._session.commit()
        await self._session.refresh(job)
        return _to_entity(job)

    async def get(self, *, job_id: int) -> Job | None:
        result = await self._session.execute(select(JobModel).where(JobModel.id == job_id))
        job = result.scalar_one_or_none()
        return _to_entity(job) if job else None

    async def mark_queued(self, *, job_id: int, message: str | None = None) -> Job | None:
        return await self.update_status(
            job_id=job_id, status=JobStatus.QUEUED, progress=0.0, message=message
        )

    async def mark_started(self, *, job_id: int, message: str | None = None) -> Job | None:
        return await self.update_status(
            job_id=job_id, status=JobStatus.RUNNING, progress=0.05, message=message
        )

    async def mark_progress(
        self, *, job_id: int, progress: float, message: str | None = None
    ) -> Job | None:
        return await self.update_status(
            job_id=job_id, status=JobStatus.RUNNING, progress=progress, message=message
        )

    async def mark_completed(
        self, *, job_id: int, result: dict[str, Any] | None = None, message: str | None = None
    ) -> Job | None:
        return await self.update_status(
            job_id=job_id,
            status=JobStatus.COMPLETED,
            progress=1.0,
            result=result,
            message=message or "completed",
        )

    async def mark_failed(
        self, *, job_id: int, error: str, message: str | None = None
    ) -> Job | None:
        return await self.update_status(
            job_id=job_id,
            status=JobStatus.FAILED,
            progress=1.0,
            error=error,
            message=message or "failed",
        )

    async def update_status(
        self,
        *,
        job_id: int,
        status: JobStatus,
        progress: float | None = None,
        error: str | None = None,
        result: dict[str, Any] | None = None,
        message: str | None = None,
    ) -> Job | None:
        result_set = await self._session.execute(select(JobModel).where(JobModel.id == job_id))
        job = result_set.scalar_one_or_none()
        if not job:
            return None

        job.status = status.value
        job.updated_at = utc_now()
        if progress is not None:
            job.progress = max(0.0, min(progress, 1.0))
        if message is not None:
            job.status_message = message
        if error is not None:
            job.error_message = error
        if result is not None:
            job.result_data = result
        if status == JobStatus.RUNNING and job.started_at is None:
            job.started_at = utc_now()
        if status in (JobStatus.COMPLETED, JobStatus.FAILED):
            job.completed_at = utc_now()

        self._session.add(job)
        await self._session.commit()
        await self._session.refresh(job)
        return _to_entity(job)
