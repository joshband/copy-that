"""
Mood Board API - AI-curated aesthetic boards based on extracted color tokens

Text: Anthropic Claude (default) or OpenAI-compatible (LM Studio) via MOOD_BOARD_TEXT_*.
Images: DALL·E 3 or OpenAI-compatible local via MOOD_BOARD_IMAGE_*.
"""

import logging
import os
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from copy_that.application.ports.jobs import JobExecutor, JobRepository
from copy_that.application.use_cases import jobs as job_use_cases
from copy_that.domain.jobs import JobStatus
from copy_that.infrastructure.celery.app import app as celery_app
from copy_that.interfaces.api import dependencies as deps

logger = logging.getLogger(__name__)

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
    hue_family: str | None = None


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
    focus_type: Literal["material", "typography"] = Field(default="material")


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
    if not os.getenv("CELERY_BROKER_URL"):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Mood board generation requires Celery (CELERY_BROKER_URL not configured).",
        )

    # Check broker/worker availability
    try:
        insp = celery_app.control.inspect(timeout=1.0)
        stats = insp.ping() if insp else None
        if not stats:
            raise RuntimeError("No Celery workers responded")
    except Exception as exc:  # noqa: BLE001
        logger.warning("Celery broker/worker unavailable: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Mood board generation temporarily unavailable (Celery broker/worker not reachable).",
        ) from exc

    job = await job_use_cases.create_job(
        job_repo, job_type="mood_board", payload=request.model_dump(), queue=queue
    )
    await job_use_cases.mark_queued(job_repo, job_id=job.id, message="enqueued")

    try:
        await job_executor.enqueue(job, request.model_dump())
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
    """Health check for mood board service (reports configured providers)."""
    text_base = (os.getenv("MOOD_BOARD_TEXT_BASE_URL") or "").strip()
    image_base = (os.getenv("MOOD_BOARD_IMAGE_BASE_URL") or "").strip()
    openai_key = bool(os.getenv("OPENAI_API_KEY"))
    anthropic_key = bool(os.getenv("ANTHROPIC_API_KEY"))

    if text_base:
        text_provider = "openai_compatible"
        text_configured = True
    else:
        text_provider = "anthropic"
        text_configured = anthropic_key

    if image_base:
        image_provider = "openai_compatible"
        image_configured = True
    elif openai_key:
        image_provider = "openai"
        image_configured = True
    else:
        image_provider = "none"
        image_configured = False

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
        "image_base_url": image_base or None,
        "image_model": (
            os.getenv("MOOD_BOARD_IMAGE_MODEL")
            if image_base
            else ("dall-e-3" if openai_key else None)
        ),
    }
