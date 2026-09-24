"""
Mood Board API - AI-curated aesthetic boards based on extracted color tokens

Text: Anthropic Claude (default) or OpenAI-compatible (LM Studio) via MOOD_BOARD_TEXT_*.
Images: policy router over flux_fast / local_mflux / DALL·E / token_collage.
"""

import logging
import os
from typing import Any, Literal

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from copy_that.application.ports.jobs import JobExecutor, JobRepository
from copy_that.application.use_cases import jobs as job_use_cases
from copy_that.domain.jobs import JobStatus
from copy_that.infrastructure.celery.app import app as celery_app
from copy_that.interfaces.api import dependencies as deps
from copy_that.services.mood_board_images.registry import health_snapshot

logger = logging.getLogger(__name__)


def _payload_with_measured_shares(payload: dict[str, Any]) -> dict[str, Any]:
    """Stamp palette area and keep a resized JPEG for the design brief."""
    image_b64 = payload.pop("source_image_base64", None)
    if not image_b64:
        return payload
    try:
        from copy_that.services.mood_board_generator import (
            measure_palette_shares,
            resize_reference_jpeg,
        )

        resized = resize_reference_jpeg(image_b64)
        payload["colors"] = measure_palette_shares(list(payload.get("colors") or []), resized)
        payload["source_image_base64"] = resized
    except Exception:
        logger.warning("Could not prepare the source reference image", exc_info=True)
    return payload

router = APIRouter(
    prefix="/api/v1/mood-board",
    tags=["mood-board"],
    responses={404: {"description": "Not found"}},
)


class ColorInput(BaseModel):
    """Simplified color token for mood board generation"""

    hex: str
    name: str | None = None
    temperature: Literal["warm", "cool", "neutral"] | None = None
    saturation_level: Literal["vibrant", "muted", "desaturated", "grayscale"] | None = None
    lightness_level: str | None = None
    hue_family: str | None = None
    design_intent: str | None = None
    usage: list[str] | None = None
    background_role: str | None = None
    is_accent: bool | None = None
    prominence_percentage: float | None = Field(default=None, ge=0, le=100)


class VisualElement(BaseModel):
    """Visual element description"""

    type: Literal["texture", "shape", "pattern", "object", "composition"]
    description: str
    prominence: Literal["primary", "secondary", "accent"]


class AestheticReference(BaseModel):
    """Cultural/artistic reference"""

    movement: str
    artist: str | None = None
    period: str | None = None
    characteristics: list[str] = Field(default_factory=list)


class GeneratedImage(BaseModel):
    """AI-generated image data"""

    url: str
    prompt: str
    revised_prompt: str | None = None
    provider: str | None = None
    selection: dict[str, Any] | None = None
    focus_type: Literal["material", "ui", "typography"] | None = None
    role: Literal["material", "ui", "typography"] | None = None


class ImageSlot(BaseModel):
    """Per-image focus for the materials, UI, and typography studies."""

    focus_type: Literal["material", "ui", "typography"] = "material"


class MoodBoardTheme(BaseModel):
    """Complete mood board theme"""

    name: str
    description: str
    tags: list[str] = Field(default_factory=list)
    visual_elements: list[VisualElement] = Field(default_factory=list)
    color_palette: list[str] = Field(default_factory=list)
    references: list[AestheticReference] = Field(default_factory=list)
    generated_images: list[GeneratedImage] = Field(default_factory=list)


class MoodBoardVariant(BaseModel):
    """Complete mood board variant"""

    id: str
    title: str
    subtitle: str
    theme: MoodBoardTheme
    dominant_colors: list[str] = Field(default_factory=list)
    vibe: str


class MoodBoardRequest(BaseModel):
    """Request to generate mood board"""

    colors: list[ColorInput] = Field(..., min_length=1, max_length=20)
    num_variants: int = Field(default=2, ge=1, le=3)
    include_images: bool = Field(default=True)
    num_images_per_variant: int = Field(default=4, ge=1, le=6)
    focus_type: Literal["material", "typography", "mixed"] = Field(default="material")
    image_slots: list[ImageSlot] | None = Field(
        default=None,
        description=(
            "Optional per-image focus plan. Default composition when omitted and "
            "imagery is on: material, material, typography (FE sends this explicitly)."
        ),
        max_length=6,
    )
    policy: Literal["balanced", "fast", "cheap", "private", "quality"] = Field(
        default="balanced"
    )
    allow_cloud: bool = Field(default=True)
    max_latency_ms: float | None = Field(default=None, ge=1_000, le=3_600_000)
    source_image_base64: str | None = Field(
        default=None,
        max_length=8_000_000,
        description=(
            "Session source image. Resized to a JPEG and kept on the job so palette "
            "area can be measured, a design brief can be read, and Fal can use it as a "
            "style reference. It is not an image-to-image init. The original upload is not stored."
        ),
    )


class MoodBoardResponse(BaseModel):
    """Response with generated mood boards"""

    variants: list[MoodBoardVariant]
    generation_time_ms: float
    models_used: dict[str, str]
    focus_type: str


class MoodBoardJobResponse(BaseModel):
    job_id: int
    status: str
    queue: str | None = None
    stream_url: str


@router.post("/generate", response_model=MoodBoardJobResponse, status_code=status.HTTP_202_ACCEPTED)
async def generate_mood_board(
    request: MoodBoardRequest,
    job_repo: JobRepository = Depends(deps.get_job_repo),
    job_executor: JobExecutor = Depends(deps.get_job_executor),
):
    """
    Enqueue AI-curated mood board generation as a durable background job.

    Returns a job handle for SSE progress tracking; results are available via
    `/api/v1/jobs/{job_id}` when complete.
    """
    queue = os.getenv("CELERY_MOOD_BOARD_QUEUE", "mood-board")

    # Fast fail locally when Celery/broker is not configured to avoid 500s/CORS noise
    broker_url = (os.getenv("CELERY_BROKER_URL") or "").strip()
    if not broker_url:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Mood board generation requires Celery (CELERY_BROKER_URL not configured).",
        )

    # Prefer inspect.ping, but solo-pool workers cannot answer while busy — fall back
    # to a broker ping so enqueue still works when a worker is mid-task.
    worker_reachable = False
    try:
        insp = celery_app.control.inspect(timeout=2.0)
        stats = insp.ping() if insp else None
        worker_reachable = bool(stats)
    except Exception as exc:  # noqa: BLE001
        logger.warning("Celery inspect failed: %s", exc)

    if not worker_reachable:
        try:
            import redis

            client = redis.from_url(
                broker_url, socket_connect_timeout=1.0, socket_timeout=1.0
            )
            if not client.ping():
                raise RuntimeError("broker ping returned false")
            logger.warning(
                "Celery inspect empty/failed; broker reachable — enqueueing "
                "(solo pool may be busy)"
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning("Celery broker/worker unavailable: %s", exc)
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Mood board generation temporarily unavailable (Celery broker/worker not reachable).",
            ) from exc

    payload = _payload_with_measured_shares(request.model_dump())
    job = await job_use_cases.create_job(
        job_repo, job_type="mood_board", payload=payload, queue=queue
    )
    await job_use_cases.mark_queued(job_repo, job_id=job.id, message="enqueued")

    try:
        await job_executor.enqueue(job, payload)
    except Exception as exc:
        await job_use_cases.mark_failed(
            job_repo, job_id=job.id, error=str(exc), message="enqueue_failed"
        )
        logger.exception("Failed to enqueue mood board job %s", job.id)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Failed to enqueue mood board job",
        ) from exc

    return MoodBoardJobResponse(
        job_id=job.id,
        status=JobStatus.QUEUED.value,
        queue=job.queue or queue,
        stream_url=f"/api/v1/jobs/{job.id}/stream",
    )


@router.get("/health")
async def health_check():
    """Health check for mood board service (reports configured providers + router)."""
    text_base = (os.getenv("MOOD_BOARD_TEXT_BASE_URL") or "").strip()
    image_base = (os.getenv("MOOD_BOARD_IMAGE_BASE_URL") or "").strip()
    flux_base = (os.getenv("MOOD_BOARD_FLUX_BASE_URL") or "").strip()
    openai_key = bool(os.getenv("OPENAI_API_KEY"))
    anthropic_key = bool(os.getenv("ANTHROPIC_API_KEY"))

    if text_base:
        text_provider = "openai_compatible"
        text_configured = True
    else:
        text_provider = "anthropic"
        text_configured = anthropic_key

    snap = health_snapshot()
    backends = snap.get("backends") or []
    non_collage = [b for b in backends if b.get("id") != "token_collage"]
    primary = non_collage[0] if non_collage else (backends[0] if backends else None)
    image_provider = primary["id"] if primary else "none"
    image_configured = bool(backends)

    return {
        "status": "healthy",
        "anthropic_configured": anthropic_key,
        "openai_configured": openai_key,
        "text_provider": text_provider,
        "text_configured": text_configured,
        "text_base_url": text_base or None,
        "text_model": os.getenv("MOOD_BOARD_TEXT_MODEL")
        if text_base
        else "claude-sonnet-4-5-20250929",
        "image_provider": image_provider,
        "image_configured": image_configured,
        "image_base_url": image_base or flux_base or None,
        "image_model": (
            os.getenv("MOOD_BOARD_FLUX_MODEL")
            or os.getenv("MOOD_BOARD_IMAGE_MODEL")
            or ("dall-e-3" if openai_key else "token_collage")
        ),
        "backends": backends,
        "recommended_policy": snap.get("recommended_policy"),
        "default_policy": snap.get("default_policy"),
    }
