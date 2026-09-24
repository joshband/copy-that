from __future__ import annotations

import asyncio
import logging
from typing import Any

from copy_that.application.ai_shadow_extractor import AIShadowExtractor
from copy_that.application.openai_color_extractor import OpenAIColorExtractor
from copy_that.application.spacing_extractor import AISpacingExtractor
from copy_that.application.use_cases import jobs as job_use_cases
from copy_that.extractors.color.cv_extractor import CVColorExtractor
from copy_that.extractors.spacing.cv_extractor import CVSpacingExtractor
from copy_that.infrastructure.celery.app import app
from copy_that.infrastructure.database import AsyncSessionLocal
from copy_that.infrastructure.persistence.repositories.jobs import SQLAlchemyJobRepository
from copy_that.interfaces.api.multi_extract import MultiExtractRequest
from copy_that.services.mood_board_generator import MoodBoardGenerator

logger = logging.getLogger(__name__)


@app.task(  # type: ignore[untyped-decorator]
    name="copy_that.mood_board.generate_job",
    bind=True,
    max_retries=3,
    # Local mflux: ~5+ min/image; Midjourney-pair smoke ~18 min for 4 images.
    soft_time_limit=2700,
    time_limit=3000,
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

        async def on_progress(progress: float, message: str) -> None:
            await job_use_cases.mark_progress(
                repo, job_id=job_id, progress=progress, message=message
            )

        try:
            themes_result = await generator.generate(
                colors=list(payload.get("colors", [])),
                num_variants=int(payload.get("num_variants", 2)),
                include_images=bool(payload.get("include_images", True)),
                num_images_per_variant=int(payload.get("num_images_per_variant", 4)),
                focus_type=str(payload.get("focus_type", "material")),
                image_slots=payload.get("image_slots"),
                on_progress=on_progress,
                policy=payload.get("policy") or None,
                allow_cloud=bool(payload.get("allow_cloud", True)),
                max_latency_ms=(
                    float(payload["max_latency_ms"])
                    if payload.get("max_latency_ms") is not None
                    else None
                ),
            )
            await job_use_cases.mark_completed(
                repo, job_id=job_id, result=themes_result, message="completed"
            )
        except Exception as exc:  # pragma: no cover - defensive logging for worker failures
            logger.exception("Mood board job %s failed", job_id)
            await job_use_cases.mark_failed(repo, job_id=job_id, error=str(exc), message="failed")
            raise


@app.task(  # type: ignore[untyped-decorator]
    name="copy_that.batch.process_extract_job",
    bind=True,
    max_retries=3,
    soft_time_limit=1200,
    time_limit=1500,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_jitter=True,
)
def process_extract_job(self, job_id: int, payload: dict[str, Any]) -> None:
    """Celery entrypoint for batch extraction (throughput-optimized)."""

    asyncio.run(_run_batch_extract_job(job_id, payload))


async def _run_batch_extract_job(job_id: int, payload: dict[str, Any]) -> None:
    async with AsyncSessionLocal() as session:
        repo = SQLAlchemyJobRepository(session)
        await job_use_cases.mark_started(repo, job_id=job_id, message="worker_started")

        try:
            request = MultiExtractRequest.model_validate(payload)
            b64 = (
                request.image_base64.split(",")[1]
                if "," in request.image_base64
                else request.image_base64
            )
            media_type = request.image_media_type or "image/png"

            # CV (fast) path
            cv_colors = CVColorExtractor(max_colors=request.max_colors).extract_from_base64(
                request.image_base64
            )
            cv_spacing = CVSpacingExtractor(
                max_tokens=request.max_spacing_tokens
            ).extract_from_base64(request.image_base64)

            # AI refinement (respect quality tier)
            from copy_that.application.quality import (
                QualityTier,
                color_model_for_quality,
                spacing_model_for_quality,
            )

            tier = QualityTier.from_str(getattr(request, "quality", "standard"))
            color_task = asyncio.to_thread(
                OpenAIColorExtractor(
                    model=color_model_for_quality(tier)
                ).extract_colors_from_base64,
                request.image_base64,
                media_type,
                request.max_colors,
            )
            spacing_task = asyncio.to_thread(
                AISpacingExtractor(
                    model=spacing_model_for_quality(tier)
                ).extract_spacing_from_base64,
                b64,
                media_type,
                request.max_spacing_tokens,
            )
            shadow_task = asyncio.to_thread(
                AIShadowExtractor().extract_shadows,
                b64,
                media_type,
            )

            ai_color_result, ai_spacing_result, ai_shadow_result = await asyncio.gather(
                color_task, spacing_task, shadow_task
            )

            result: dict[str, Any] = {
                "cv": {
                    "colors": [c.model_dump() for c in cv_colors.colors],
                    "spacing": [s.model_dump() for s in cv_spacing.tokens],
                },
                "ai": {
                    "colors": [c.model_dump() for c in ai_color_result.colors],
                    "spacing": [t.model_dump() for t in ai_spacing_result.tokens],
                    "shadows": [s.model_dump() for s in ai_shadow_result.shadows],
                },
                "metadata": {
                    "base_unit": getattr(ai_spacing_result, "base_unit", None),
                    "base_unit_confidence": getattr(
                        ai_spacing_result, "base_unit_confidence", None
                    ),
                },
            }

            await job_use_cases.mark_completed(
                repo, job_id=job_id, result=result, message="completed"
            )
        except Exception as exc:  # pragma: no cover
            logger.exception("Batch extract job %s failed", job_id)
            await job_use_cases.mark_failed(repo, job_id=job_id, error=str(exc), message="failed")
            raise
