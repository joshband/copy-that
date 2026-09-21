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

from copy_that.application.ai_shadow_extractor import AIShadowExtractor
from copy_that.application.concurrency import extract_slot
from copy_that.extractors.color.cv_extractor import CVColorExtractor
from copy_that.extractors.spacing.cv_extractor import CVSpacingExtractor
from copy_that.application.execution.async_executor import AsyncExecutor
from copy_that.application.openai_color_extractor import OpenAIColorExtractor
from copy_that.application.ports.color_token_records import ColorTokenRepository
from copy_that.application.ports.projects import ProjectRepository
from copy_that.application.ports.shadow_tokens import ShadowTokenRepository
from copy_that.application.ports.snapshots import SnapshotRepository
from copy_that.application.ports.spacing_tokens import SpacingTokenRepository
from copy_that.application.quality import (
    QualityTier,
    color_model_for_quality,
    spacing_model_for_quality,
)
from copy_that.application.spacing_extractor import AISpacingExtractor
from copy_that.domain.color_tokens import ColorTokenCreate
from copy_that.domain.shadows import ShadowTokenCreate
from copy_that.domain.spacing_tokens import SpacingTokenCreate
from copy_that.infrastructure.security.rate_limiter import rate_limit
from copy_that.interfaces.api import dependencies as deps
from copy_that.interfaces.api.utils import enforce_payload_size, sanitize_numbers

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
    quality: str = Field("standard", description="Extraction quality: fast|standard|premium")


@router.post("/stream")
async def extract_stream(
    request: MultiExtractRequest,
    project_repo: ProjectRepository = Depends(deps.get_project_repo),
    color_repo: ColorTokenRepository = Depends(deps.get_color_token_repo),
    spacing_repo: SpacingTokenRepository = Depends(deps.get_spacing_repo),
    shadow_repo: ShadowTokenRepository = Depends(deps.get_shadow_repo),
    snapshot_repo: SnapshotRepository = Depends(deps.get_snapshot_repo),
    async_executor: AsyncExecutor = Depends(deps.get_async_executor),
    _rate_limit: None = Depends(rate_limit(requests=5, seconds=60)),
) -> StreamingResponse:
    """Stream CV-first then AI refinement for requested token types."""

    async def sse() -> AsyncGenerator[str, None]:
        try:
            enforce_payload_size(request.image_base64)
            # Validate project if provided
            if request.project_id is not None:
                project = await project_repo.get(project_id=request.project_id)
                if not project:
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

            async with extract_slot():
                # CV color
                cv_color_result = CVColorExtractor(
                    max_colors=request.max_colors
                ).extract_from_base64(request.image_base64)
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
                tier = QualityTier.from_str(request.quality)
                color_task = async_executor.run(
                    lambda: OpenAIColorExtractor(
                        model=color_model_for_quality(tier)
                    ).extract_colors_from_base64(
                        request.image_base64,
                        media_type=request.image_media_type or "image/png",
                        max_colors=request.max_colors,
                    )
                )
                spacing_task = async_executor.run(
                    lambda: AISpacingExtractor(
                        model=spacing_model_for_quality(tier)
                    ).extract_spacing_from_base64(
                        request.image_base64.split(",")[1]
                        if "," in request.image_base64
                        else request.image_base64,
                        request.image_media_type or "image/png",
                        request.max_spacing_tokens,
                    )
                )
                shadow_task = async_executor.run(
                    lambda: AIShadowExtractor().extract_shadows(
                        base64_image=request.image_base64.split(",")[1]
                        if "," in request.image_base64
                        else request.image_base64,
                        media_type=request.image_media_type or "image/png",
                    )
                )

                ai_color_result, ai_spacing_result, ai_shadow_result = await asyncio.gather(
                    color_task, spacing_task, shadow_task
                )

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

            yield send(
                "token",
                {
                    "type": "shadow",
                    "source": "ai",
                    "tokens": [s.model_dump() for s in ai_shadow_result.shadows],
                },
                {
                    "extraction_confidence": ai_shadow_result.extraction_confidence,
                    "extractor": ai_shadow_result.extractor_used,
                },
            )

            # Persist if project_id provided
            if request.project_id:
                await _persist_color_tokens(color_repo, request.project_id, ai_color_result.colors)
                await _persist_spacing_tokens(
                    spacing_repo, request.project_id, ai_spacing_result.tokens
                )
                await _persist_shadow_tokens(
                    shadow_repo, request.project_id, ai_shadow_result.shadows
                )
                await _persist_snapshot(
                    snapshot_repo,
                    request.project_id,
                    ai_color_result.colors,
                    ai_spacing_result.tokens,
                    ai_shadow_result.shadows,
                    {
                        "extractor": "openai+cv+claude",
                        "token_counts": {
                            "colors": len(ai_color_result.colors),
                            "spacing": len(ai_spacing_result.tokens),
                            "shadows": len(ai_shadow_result.shadows),
                        },
                    },
                )

            yield send(
                "complete",
                {
                    "status": "ok",
                    "color_count": len(ai_color_result.colors),
                    "spacing_count": len(ai_spacing_result.tokens),
                    "shadow_count": len(ai_shadow_result.shadows),
                },
            )
        except Exception as exc:  # noqa: BLE001
            logger.exception("Multi-extract failed")
            yield f"event: error\ndata: {json.dumps({'error': str(exc)})}\n\n"

    return StreamingResponse(
        sse(), media_type="text/event-stream", headers={"Cache-Control": "no-cache"}
    )


def _json_or_none(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, str):
        return value
    return json.dumps(value)


async def _persist_color_tokens(
    repo: ColorTokenRepository, project_id: int, tokens: list[Any]
) -> None:
    creates = [_to_color_create(token) for token in tokens]
    await repo.record_extraction(
        project_id=project_id,
        source_url="multi-extract",
        tokens=creates,
        result_data={"color_count": len(tokens)},
    )


async def _persist_spacing_tokens(
    repo: SpacingTokenRepository, project_id: int, tokens: list[Any]
) -> None:
    creates = [_to_spacing_create(token) for token in tokens]
    await repo.record_extraction(
        project_id=project_id,
        source_url="multi-extract",
        tokens=creates,
        result_data={"spacing_count": len(tokens)},
    )


async def _persist_shadow_tokens(
    repo: ShadowTokenRepository, project_id: int, shadows: list[Any]
) -> None:
    if not shadows:
        return
    creates = [_to_shadow_create(shadow) for shadow in shadows]
    await repo.record_extraction(project_id=project_id, source_url="multi-extract", shadows=creates)


async def _persist_snapshot(
    repo: SnapshotRepository,
    project_id: int,
    colors: list[Any],
    spacings: list[Any],
    shadows: list[Any] | None = None,
    meta: dict[str, Any] | None = None,
) -> None:
    payload: dict[str, Any] = {
        "colors": [c.model_dump() for c in colors],
        "spacing": [t.model_dump() for t in spacings],
        "shadows": [s.model_dump() for s in (shadows or [])],
        "meta": meta or {},
    }
    await repo.create(
        project_id=project_id,
        version=1,
        data=json.dumps(sanitize_numbers(payload)),
    )


def _to_color_create(token: Any) -> ColorTokenCreate:
    data = token.model_dump(exclude_none=True) if hasattr(token, "model_dump") else {}
    return ColorTokenCreate(
        hex=getattr(token, "hex", None) or data.get("hex") or "#000000",
        rgb=getattr(token, "rgb", None) or data.get("rgb") or "",
        hsl=data.get("hsl", getattr(token, "hsl", None)),
        hsv=data.get("hsv", getattr(token, "hsv", None)),
        name=getattr(token, "name", None) or data.get("name") or "",
        design_intent=data.get("design_intent", getattr(token, "design_intent", None)),
        semantic_names=_json_or_none(
            data.get("semantic_names", getattr(token, "semantic_names", None))
        ),
        extraction_metadata=_json_or_none(
            data.get("extraction_metadata", getattr(token, "extraction_metadata", None))
        ),
        category=data.get("category", getattr(token, "category", None)),
        confidence=float(data.get("confidence", getattr(token, "confidence", 0.0)) or 0.0),
        harmony=data.get("harmony", getattr(token, "harmony", None)),
        temperature=data.get("temperature", getattr(token, "temperature", None)),
        saturation_level=data.get("saturation_level", getattr(token, "saturation_level", None)),
        lightness_level=data.get("lightness_level", getattr(token, "lightness_level", None)),
        usage=_json_or_none(data.get("usage", getattr(token, "usage", None))),
        count=data.get("count", getattr(token, "count", None)),
        prominence_percentage=data.get(
            "prominence_percentage", getattr(token, "prominence_percentage", None)
        ),
        wcag_contrast_on_white=data.get(
            "wcag_contrast_on_white", getattr(token, "wcag_contrast_on_white", None)
        ),
        wcag_contrast_on_black=data.get(
            "wcag_contrast_on_black", getattr(token, "wcag_contrast_on_black", None)
        ),
        wcag_aa_compliant_text=data.get(
            "wcag_aa_compliant_text", getattr(token, "wcag_aa_compliant_text", None)
        ),
        wcag_aaa_compliant_text=data.get(
            "wcag_aaa_compliant_text", getattr(token, "wcag_aaa_compliant_text", None)
        ),
        wcag_aa_compliant_normal=data.get(
            "wcag_aa_compliant_normal", getattr(token, "wcag_aa_compliant_normal", None)
        ),
        wcag_aaa_compliant_normal=data.get(
            "wcag_aaa_compliant_normal", getattr(token, "wcag_aaa_compliant_normal", None)
        ),
        colorblind_safe=data.get("colorblind_safe", getattr(token, "colorblind_safe", None)),
        tint_color=data.get("tint_color", getattr(token, "tint_color", None)),
        shade_color=data.get("shade_color", getattr(token, "shade_color", None)),
        tone_color=data.get("tone_color", getattr(token, "tone_color", None)),
        closest_web_safe=data.get("closest_web_safe", getattr(token, "closest_web_safe", None)),
        closest_css_named=data.get("closest_css_named", getattr(token, "closest_css_named", None)),
        delta_e_to_dominant=data.get(
            "delta_e_to_dominant", getattr(token, "delta_e_to_dominant", None)
        ),
        is_neutral=data.get("is_neutral", getattr(token, "is_neutral", None)),
        background_role=data.get("background_role", getattr(token, "background_role", None)),
        foreground_role=data.get("foreground_role", getattr(token, "foreground_role", None)),
        contrast_category=data.get("contrast_category", getattr(token, "contrast_category", None)),
        harmony_confidence=data.get(
            "harmony_confidence", getattr(token, "harmony_confidence", None)
        ),
        hue_angles=_json_or_none(data.get("hue_angles", getattr(token, "hue_angles", None))),
        is_accent=data.get("is_accent", getattr(token, "is_accent", None)),
        state_variants=_json_or_none(
            data.get("state_variants", getattr(token, "state_variants", None))
        ),
        kmeans_cluster_id=data.get("kmeans_cluster_id", getattr(token, "kmeans_cluster_id", None)),
        sam_segmentation_mask=_json_or_none(
            data.get("sam_segmentation_mask", getattr(token, "sam_segmentation_mask", None))
        ),
        clip_embeddings=_json_or_none(
            data.get("clip_embeddings", getattr(token, "clip_embeddings", None))
        ),
        histogram_significance=data.get(
            "histogram_significance", getattr(token, "histogram_significance", None)
        ),
        library_id=data.get("library_id", getattr(token, "library_id", None)),
        role=data.get("role", getattr(token, "role", None)),
        provenance=_json_or_none(data.get("provenance", getattr(token, "provenance", None))),
    )


def _to_spacing_create(token: Any) -> SpacingTokenCreate:
    spacing_type = getattr(getattr(token, "spacing_type", None), "value", None) or getattr(
        token, "spacing_type", None
    )
    return SpacingTokenCreate(
        value_px=getattr(token, "value_px", 0),
        name=getattr(token, "name", ""),
        semantic_role=getattr(token, "semantic_role", None),
        spacing_type=spacing_type,
        category=getattr(token, "category", None),
        confidence=getattr(token, "confidence", None),
        usage=_json_or_none(getattr(token, "usage", None)),
    )


def _to_shadow_create(token: Any) -> ShadowTokenCreate:
    return ShadowTokenCreate(
        x_offset=getattr(token, "x_offset", 0.0),
        y_offset=getattr(token, "y_offset", 0.0),
        blur_radius=getattr(token, "blur_radius", 0.0),
        spread_radius=getattr(token, "spread_radius", 0.0),
        color_hex=getattr(token, "color_hex", "#000000"),
        opacity=getattr(token, "opacity", 1.0),
        name=getattr(token, "semantic_name", None) or getattr(token, "name", ""),
        shadow_type=getattr(token, "shadow_type", None),
        semantic_role="inset" if getattr(token, "is_inset", False) else "drop",
        confidence=float(getattr(token, "confidence", 0.0) or 0.0),
        extraction_metadata=_json_or_none(
            {
                "is_inset": getattr(token, "is_inset", False),
                "affects_text": getattr(token, "affects_text", False),
            }
        ),
    )
