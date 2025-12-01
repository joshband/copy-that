"""
Multi-token extraction with CV-first + AI refinement and SSE streaming.
"""

import asyncio
import json
import logging
from collections.abc import AsyncGenerator, Sequence
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from copy_that.application.cv.color_cv_extractor import CVColorExtractor
from copy_that.application.cv.spacing_cv_extractor import CVSpacingExtractor
from copy_that.application.openai_color_extractor import OpenAIColorExtractor
from copy_that.application.spacing_extractor import AISpacingExtractor
from copy_that.domain.models import (
    ColorToken,
    ExtractionJob,
    Project,
    ProjectSnapshot,
    SpacingToken,
)
from copy_that.infrastructure.database import get_db
from copy_that.interfaces.api.utils import sanitize_numbers

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/extract", tags=["multi-extract"])


class MultiExtractRequest(BaseModel):
    image_base64: str = Field(..., description="Data URL or raw base64 image")
    image_media_type: str | None = Field("image/png", description="Media type for image")
    project_id: int | None = Field(None, description="Optional project to persist tokens")
    token_types: Sequence[str] = Field(
        default_factory=lambda: ["color", "spacing"],
        description="List of token types to extract",
    )
    max_colors: int = 12
    max_spacing_tokens: int = 20


@router.post("/stream")
async def extract_stream(
    request: MultiExtractRequest, db: AsyncSession = Depends(get_db)
) -> StreamingResponse:
    """Stream CV-first then AI refinement for requested token types."""

    async def sse() -> AsyncGenerator[str, None]:
        try:
            # Validate project if provided
            if request.project_id is not None:
                res = await db.execute(select(Project).where(Project.id == request.project_id))
                if not res.scalar_one_or_none():
                    raise HTTPException(
                        status_code=404, detail=f"Project {request.project_id} not found"
                    )

            def send(
                event: str, data: dict[str, Any], metadata: dict[str, Any] | None = None
            ) -> str:
                payload = dict(data)
                if metadata:
                    payload["metadata"] = metadata
                clean = sanitize_numbers(payload)
                return f"event: {event}\ndata: {json.dumps(clean, allow_nan=False)}\n\n"

            # CV color
            cv_color_result = CVColorExtractor(max_colors=request.max_colors).extract_from_base64(
                request.image_base64
            )
            yield send(
                "token",
                {
                    "type": "color",
                    "source": "cv",
                    "tokens": [c.model_dump() for c in cv_color_result.colors],
                },
            )

            # CV spacing
            cv_spacing_result = CVSpacingExtractor(
                max_tokens=request.max_spacing_tokens
            ).extract_from_base64(request.image_base64)
            yield send(
                "token",
                {
                    "type": "spacing",
                    "source": "cv",
                    "tokens": [t.model_dump() for t in cv_spacing_result.tokens],
                },
                {
                    "base_unit": cv_spacing_result.base_unit,
                    "base_unit_confidence": cv_spacing_result.base_unit_confidence,
                },
            )

            # AI refinement (parallel)
            loop = asyncio.get_event_loop()
            color_task = loop.run_in_executor(
                None,
                lambda: OpenAIColorExtractor().extract_colors_from_base64(
                    request.image_base64,
                    media_type=request.image_media_type or "image/png",
                    max_colors=request.max_colors,
                ),
            )
            spacing_task = loop.run_in_executor(
                None,
                lambda: AISpacingExtractor().extract_spacing_from_base64(
                    request.image_base64.split(",")[1]
                    if "," in request.image_base64
                    else request.image_base64,
                    request.image_media_type or "image/png",
                    request.max_spacing_tokens,
                ),
            )

            ai_color_result, ai_spacing_result = await asyncio.gather(color_task, spacing_task)

            yield send(
                "token",
                {
                    "type": "color",
                    "source": "ai",
                    "tokens": [c.model_dump() for c in ai_color_result.colors],
                },
            )
            yield send(
                "token",
                {
                    "type": "spacing",
                    "source": "ai",
                    "tokens": [t.model_dump() for t in ai_spacing_result.tokens],
                },
                {
                    "base_unit": ai_spacing_result.base_unit,
                    "base_unit_confidence": ai_spacing_result.base_unit_confidence,
                },
            )

            # Persist if project_id provided
            if request.project_id:
                await _persist_color_tokens(db, request.project_id, ai_color_result.colors)
                await _persist_spacing_tokens(db, request.project_id, ai_spacing_result.tokens)
                await _persist_snapshot(
                    db,
                    request.project_id,
                    ai_color_result.colors,
                    ai_spacing_result.tokens,
                    {
                        "extractor": "openai+cv",
                        "token_counts": {
                            "colors": len(ai_color_result.colors),
                            "spacing": len(ai_spacing_result.tokens),
                        },
                    },
                )

            yield send(
                "complete",
                {
                    "status": "ok",
                    "color_count": len(ai_color_result.colors),
                    "spacing_count": len(ai_spacing_result.tokens),
                },
            )
        except Exception as exc:  # noqa: BLE001
            logger.error("Multi-extract failed: %s", exc)
            yield f"event: error\ndata: {json.dumps({'error': str(exc)})}\n\n"

    return StreamingResponse(
        sse(), media_type="text/event-stream", headers={"Cache-Control": "no-cache"}
    )


async def _persist_color_tokens(db: AsyncSession, project_id: int, tokens: list[Any]) -> None:
    job: ExtractionJob
    job = ExtractionJob(
        project_id=project_id,
        source_url="multi-extract",
        extraction_type="color",
        status="completed",
        result_data=json.dumps({"color_count": len(tokens)}),
    )
    db.add(job)
    await db.flush()
    for c in tokens:
        db.add(
            ColorToken(
                project_id=project_id,
                extraction_job_id=job.id,
                hex=c.hex,
                rgb=c.rgb,
                name=c.name,
                design_intent=c.design_intent,
                semantic_names=json.dumps(c.semantic_names) if c.semantic_names else None,
                extraction_metadata=json.dumps(c.extraction_metadata)
                if c.extraction_metadata
                else None,
                confidence=c.confidence,
                harmony=c.harmony,
                usage=json.dumps(c.usage) if c.usage else None,
            )
        )
    await db.commit()


async def _persist_spacing_tokens(db: AsyncSession, project_id: int, tokens: list[Any]) -> None:
    job = ExtractionJob(
        project_id=project_id,
        source_url="multi-extract",
        extraction_type="spacing",
        status="completed",
        result_data=json.dumps({"spacing_count": len(tokens)}),
    )
    db.add(job)
    await db.flush()
    for t in tokens:
        db.add(
            SpacingToken(
                project_id=project_id,
                extraction_job_id=job.id,
                value_px=t.value_px,
                name=t.name,
                semantic_role=t.semantic_role,
                spacing_type=t.spacing_type.value
                if hasattr(t.spacing_type, "value")
                else t.spacing_type,
                category=t.category,
                confidence=t.confidence,
                usage=json.dumps(t.usage) if t.usage else None,
            )
        )
    await db.commit()


async def _persist_snapshot(
    db: AsyncSession,
    project_id: int,
    colors: list[Any],
    spacings: list[Any],
    meta: dict[str, Any] | None = None,
) -> None:
    """Persist an immutable snapshot blob for the project."""
    payload: dict[str, Any] = {
        "colors": [c.model_dump() for c in colors],
        "spacing": [t.model_dump() for t in spacings],
        "meta": meta or {},
    }
    snapshot = ProjectSnapshot(
        project_id=project_id,
        version=1,  # could be incremented per project in future
        data=json.dumps(sanitize_numbers(payload)),
    )
    db.add(snapshot)
    await db.commit()
