from __future__ import annotations

import asyncio
import logging
from typing import Any

from copy_that.application.use_cases import jobs as job_use_cases
from copy_that.infrastructure.celery.app import app
from copy_that.infrastructure.database import AsyncSessionLocal
from copy_that.infrastructure.persistence.repositories.jobs import SQLAlchemyJobRepository
from copy_that.services.mood_board_generator import MoodBoardGenerator

logger = logging.getLogger(__name__)


@app.task(  # type: ignore[misc]
    name="copy_that.mood_board.generate_job",
    bind=True,
    max_retries=3,
    soft_time_limit=900,
    time_limit=960,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_jitter=True,
)
def generate_mood_board_job(self, job_id: int, payload: dict[str, Any]) -> None:
    """Celery entrypoint for generating mood board jobs."""

    asyncio.run(_run_mood_board_job(job_id, payload))


async def _run_mood_board_job(job_id: int, payload: dict[str, Any]) -> None:
    async with AsyncSessionLocal() as session:
        repo = SQLAlchemyJobRepository(session)
        generator = MoodBoardGenerator()

        await job_use_cases.mark_started(repo, job_id=job_id, message="worker_started")
        await job_use_cases.mark_progress(
            repo, job_id=job_id, progress=0.2, message="generating_themes"
        )

        try:
            themes_result = await generator.generate(
                colors=list(payload.get("colors", [])),
                num_variants=int(payload.get("num_variants", 2)),
                include_images=bool(payload.get("include_images", True)),
                num_images_per_variant=int(payload.get("num_images_per_variant", 4)),
                focus_type=str(payload.get("focus_type", "material")),
            )
            await job_use_cases.mark_progress(
                repo, job_id=job_id, progress=0.7, message="rendering_images"
            )
            await job_use_cases.mark_completed(
                repo, job_id=job_id, result=themes_result, message="completed"
            )
        except Exception as exc:  # pragma: no cover - defensive logging for worker failures
            logger.exception("Mood board job %s failed", job_id)
            await job_use_cases.mark_failed(repo, job_id=job_id, error=str(exc), message="failed")
            raise
