from __future__ import annotations

from typing import Any, Protocol

from copy_that.domain.jobs import Job, JobStatus


class JobRepository(Protocol):
    async def create(
        self, *, job_type: str, payload: dict[str, Any] | None, queue: str | None
    ) -> Job: ...

    async def get(self, *, job_id: int) -> Job | None: ...

    async def mark_queued(self, *, job_id: int, message: str | None = None) -> Job | None: ...

    async def mark_started(self, *, job_id: int, message: str | None = None) -> Job | None: ...

    async def mark_progress(
        self, *, job_id: int, progress: float, message: str | None = None
    ) -> Job | None: ...

    async def mark_completed(
        self, *, job_id: int, result: dict[str, Any] | None = None, message: str | None = None
    ) -> Job | None: ...

    async def mark_failed(
        self, *, job_id: int, error: str, message: str | None = None
    ) -> Job | None: ...

    async def update_status(
        self,
        *,
        job_id: int,
        status: JobStatus,
        progress: float | None = None,
        error: str | None = None,
        result: dict[str, Any] | None = None,
        message: str | None = None,
    ) -> Job | None: ...


class JobExecutor(Protocol):
    async def enqueue(self, job: Job, payload: dict[str, Any]) -> None: ...
