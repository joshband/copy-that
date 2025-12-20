from __future__ import annotations

import asyncio
import logging
import os

from celery import Celery

from copy_that.application.ports.jobs import JobExecutor
from copy_that.domain.jobs import Job

logger = logging.getLogger(__name__)

DEFAULT_MOOD_BOARD_QUEUE = os.getenv("CELERY_MOOD_BOARD_QUEUE", "mood-board")
DEFAULT_BATCH_QUEUE = os.getenv("CELERY_BATCH_QUEUE", "batch-extract")


class CeleryJobExecutor(JobExecutor):
    """Celery-backed executor for long-running jobs."""

    def __init__(self, celery_app: Celery, queue: str | None = None) -> None:
        self._app = celery_app
        self._queue = queue or DEFAULT_MOOD_BOARD_QUEUE

    async def enqueue(self, job: Job, payload: dict[str, object]) -> None:
        try:
            task_name = self._task_for_job(job.job_type)
            queue = job.queue or self._queue
            await asyncio.to_thread(
                self._app.send_task, task_name, args=[job.id, payload], queue=queue
            )
        except Exception:
            logger.exception("Failed to enqueue Celery job %s", job.id)
            raise

    def _task_for_job(self, job_type: str) -> str:
        if job_type == "mood_board":
            return "copy_that.mood_board.generate_job"
        if job_type == "batch_extract":
            return "copy_that.batch.process_extract_job"
        logger.warning("Unknown job_type %s; defaulting to mood_board task", job_type)
        return "copy_that.mood_board.generate_job"
