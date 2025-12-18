from __future__ import annotations

import asyncio
import logging
import os

from celery import Celery

from copy_that.application.ports.jobs import JobExecutor
from copy_that.domain.jobs import Job

logger = logging.getLogger(__name__)

DEFAULT_MOOD_BOARD_QUEUE = os.getenv("CELERY_MOOD_BOARD_QUEUE", "mood-board")


class CeleryJobExecutor(JobExecutor):
    """Celery-backed executor for long-running jobs."""

    def __init__(self, celery_app: Celery, queue: str | None = None) -> None:
        self._app = celery_app
        self._queue = queue or DEFAULT_MOOD_BOARD_QUEUE

    async def enqueue(self, job: Job, payload: dict[str, object]) -> None:
        try:
            await asyncio.to_thread(
                self._app.send_task,
                "copy_that.mood_board.generate_job",
                args=[job.id, payload],
                queue=job.queue or self._queue,
            )
        except Exception:
            logger.exception("Failed to enqueue Celery job %s", job.id)
            raise
