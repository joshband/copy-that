"""
FastAPI Router for Spacing Token Extraction

Provides REST API endpoints for spacing token extraction with streaming support.
Follows the pattern of colors.py for color extraction.
"""

import asyncio
import base64
import json
import logging
import math
from collections.abc import AsyncGenerator, Sequence
from dataclasses import asdict, is_dataclass
from typing import Any

import requests
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field, HttpUrl
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from copy_that.application import spacing_utils as su
from copy_that.application.cv.spacing_cv_extractor import CVSpacingExtractor
from copy_that.application.spacing_extractor import AISpacingExtractor
from copy_that.application.spacing_models import (
    SpacingExtractionResult,
    SpacingScale,
)
from copy_that.domain.models import ExtractionJob, Project, SpacingToken
from copy_that.infrastructure.database import get_db
from copy_that.services.spacing_service import build_spacing_repo_from_db
from copy_that.tokens.spacing.aggregator import SpacingAggregator
from core.tokens.adapters.w3c import tokens_to_w3c
from core.tokens.model import Token
from core.tokens.repository import InMemoryTokenRepository, TokenRepository
from core.tokens.spacing import make_spacing_token

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/api/v1/spacing",
    tags=["spacing"],
    responses={404: {"description": "Not found"}},
)


def _sanitize_json_value(value: Any) -> Any:
    if isinstance(value, dict):
        return {k: _sanitize_json_value(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_sanitize_json_value(v) for v in value]
    if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
        return None
    return value


@router.get("/export/w3c")
async def export_spacing_w3c(
    project_id: int | None = None, db: AsyncSession = Depends(get_db)
) -> dict[str, Any]:
    """Export spacing tokens (optionally by project) as W3C Design Tokens JSON."""
    query = select(SpacingToken)
    if project_id is not None:
        query = query.where(SpacingToken.project_id == project_id)
    result = await db.execute(query)
    tokens = result.scalars().all()
    namespace = (
        f"token/spacing/export/project/{project_id}"
        if project_id is not None
        else "token/spacing/export/all"
    )
    repo = build_spacing_repo_from_db(tokens, namespace=namespace)
    return _sanitize_json_value(tokens_to_w3c(repo))


# Request/Response Models


class SpacingExtractionRequest(BaseModel):
    """Request model for single image spacing extraction."""

    image_url: HttpUrl | None = Field(None, description="URL of the image to analyze")
    image_base64: str | None = Field(
        None, description="Base64 image payload (data URL payload without the prefix)"
    )
    image_media_type: str | None = Field(
        "image/png", description="Media type for base64 image (e.g., image/png)"
    )
    project_id: int | None = Field(None, description="Optional project to persist tokens")
    max_tokens: int = Field(
        default=15, ge=1, le=50, description="Maximum spacing tokens to extract"
    )


class BatchSpacingExtractionRequest(BaseModel):
    """Request model for batch spacing extraction."""

    image_urls: list[HttpUrl] = Field(
        ..., min_length=1, max_length=20, description="List of image URLs"
    )
    max_tokens: int = Field(default=15, ge=1, le=50, description="Max tokens per image")
    similarity_threshold: float = Field(
        default=10.0, ge=1.0, le=50.0, description="Percentage threshold for deduplication"
    )


class SpacingTokenResponse(BaseModel):
    """Response model for a single spacing token."""

    value_px: int
    value_rem: float
    name: str
    confidence: float
    semantic_role: str | None = None
    spacing_type: str | None = None
    role: str | None = None
    grid_aligned: bool | None = None
    tailwind_class: str | None = None


class SpacingExtractionResponse(BaseModel):
    """Response model for spacing extraction result."""

    tokens: list[SpacingTokenResponse]
    scale_system: str
    base_unit: int
    grid_compliance: float
    extraction_confidence: float
    unique_values: list[int]
    min_spacing: int
    max_spacing: int
    design_tokens: dict[str, Any] | None = None


class BatchExtractionResponse(BaseModel):
    """Response model for batch extraction result."""

    tokens: list[SpacingTokenResponse]
    statistics: dict
    library_id: str | None = None
    design_tokens: dict[str, Any] | None = None


# Dependency for extractor instance
def get_extractor() -> AISpacingExtractor:
    """Get spacing extractor instance."""
    return AISpacingExtractor()


# Endpoints


@router.post("/extract", response_model=SpacingExtractionResponse)
async def extract_spacing(
    request: SpacingExtractionRequest, db: AsyncSession = Depends(get_db)
) -> SpacingExtractionResponse:
    """
    Extract spacing tokens from a single image.

    Analyzes the image using Claude Sonnet 4.5 to identify spacing patterns
    and generate design tokens.

    Args:
        request: Extraction parameters

    Returns:
        SpacingExtractionResponse with extracted tokens

    Raises:
        HTTPException: If extraction fails

    Example:
        POST /api/v1/spacing/extract
        {
            "image_url": "https://example.com/design.png",
            "max_tokens": 15
        }
    """
    try:
        extractor = get_extractor()

        # CV-first
        cv_b64 = None
        if request.image_base64:
            cv_result = CVSpacingExtractor(max_tokens=request.max_tokens).extract_from_base64(
                request.image_base64
            )
        elif request.image_url:
            import base64

            resp = requests.get(str(request.image_url), timeout=30)
            resp.raise_for_status()
            cv_b64 = base64.b64encode(resp.content).decode("utf-8")
            cv_result = CVSpacingExtractor(max_tokens=request.max_tokens).extract_from_base64(
                cv_b64
            )
        else:
            raise HTTPException(status_code=400, detail="Provide image_url or image_base64")

        # AI refinement (non-blocking failure)
        loop = asyncio.get_event_loop()
        try:
            ai_result = await loop.run_in_executor(
                None,
                lambda: extractor.extract_spacing_from_base64(
                    request.image_base64 or cv_b64 or "",
                    request.image_media_type or "image/png",
                    request.max_tokens,
                ),
            )
            merged = _merge_spacing(cv_result, ai_result)
        except Exception as e:  # noqa: BLE001
            logger.warning(f"AI spacing refinement failed, using CV only: {e}")
            merged = cv_result

        # Persist extraction job + tokens
        job = ExtractionJob(
            project_id=request.project_id or 0,
            source_url=str(request.image_url) if request.image_url else "base64_upload",
            extraction_type="spacing",
            status="completed",
            result_data=json.dumps({"token_count": len(merged.tokens)}),
        )
        db.add(job)
        await db.flush()

        for t in merged.tokens:
            db.add(
                SpacingToken(
                    project_id=request.project_id or 0,
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

        namespace = f"token/spacing/project/{request.project_id or 0}/job/{job.id}"
        return _result_to_response(merged, namespace=namespace)

    except Exception as e:
        logger.error(f"Spacing extraction failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/extract-streaming")
async def extract_spacing_streaming(request: SpacingExtractionRequest) -> StreamingResponse:
    """
    Extract spacing tokens with Server-Sent Events streaming.

    Returns real-time progress updates during extraction.

    Args:
        request: Extraction parameters

    Returns:
        StreamingResponse with SSE events

    Events:
        - progress: Extraction progress updates
        - token: Individual token extracted
        - complete: Final result
        - error: Error occurred

    Example:
        POST /api/v1/spacing/extract-streaming
        {
            "image_url": "https://example.com/design.png"
        }
    """

    async def event_generator() -> AsyncGenerator[str, None]:
        try:
            extractor = get_extractor()

            # Emit start event
            yield _format_sse_event(
                "progress",
                {"status": "started", "progress": 0.0, "message": "Starting extraction..."},
            )

            # Download phase
            yield _format_sse_event(
                "progress",
                {"status": "downloading", "progress": 0.2, "message": "Downloading image..."},
            )

            # Run extraction
            loop = asyncio.get_event_loop()

            yield _format_sse_event(
                "progress",
                {
                    "status": "analyzing",
                    "progress": 0.4,
                    "message": "Analyzing with Claude Sonnet 4.5...",
                },
            )

            result = await loop.run_in_executor(
                None,
                lambda: extractor.extract_spacing_from_image_url(
                    str(request.image_url), request.max_tokens
                ),
            )

            yield _format_sse_event(
                "progress",
                {"status": "processing", "progress": 0.8, "message": "Processing tokens..."},
            )

            # Emit individual tokens
            for token in result.tokens:
                yield _format_sse_event(
                    "token",
                    {
                        "value_px": token.value_px,
                        "name": token.name,
                        "confidence": token.confidence,
                    },
                )

            # Emit complete
            response = _result_to_response(result)
            yield _format_sse_event("complete", response.model_dump())

        except Exception as e:
            logger.error(f"Streaming extraction failed: {e}")
            yield _format_sse_event("error", {"message": str(e), "type": type(e).__name__})

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )


@router.post("/batch-extract", response_model=BatchExtractionResponse)
async def extract_spacing_batch(request: BatchSpacingExtractionRequest) -> BatchExtractionResponse:
    """
    Extract and aggregate spacing tokens from multiple images.

    Processes multiple images in parallel with controlled concurrency,
    then aggregates and deduplicates the results.

    Args:
        request: Batch extraction parameters

    Returns:
        BatchExtractionResponse with aggregated tokens

    Example:
        POST /api/v1/spacing/batch-extract
        {
            "image_urls": [
                "https://example.com/page1.png",
                "https://example.com/page2.png"
            ],
            "max_tokens": 15,
            "similarity_threshold": 10.0
        }
    """
    try:
        extractor = get_extractor()
        loop = asyncio.get_event_loop()

        # Extract from each image (CV first, then AI merge)
        all_tokens = []
        for url in request.image_urls:
            try:
                # Download
                resp = requests.get(str(url), timeout=30)
                resp.raise_for_status()
                cv_b64 = base64.b64encode(resp.content).decode("utf-8")
                cv_result = CVSpacingExtractor(max_tokens=request.max_tokens).extract_from_base64(
                    cv_b64
                )
                ai_result = await loop.run_in_executor(
                    None,
                    lambda u=str(url): extractor.extract_spacing_from_image_url(
                        u, request.max_tokens
                    ),
                )
                merged = _merge_spacing(cv_result, ai_result)
                all_tokens.append(merged.tokens)
            except Exception as e:
                logger.warning(f"Batch spacing extraction failed for {url}: {e}")
                continue

        # Aggregate results
        library = SpacingAggregator.aggregate_batch(all_tokens, request.similarity_threshold)

        # Suggest roles
        library = SpacingAggregator.suggest_token_roles(library)

        # Convert to response
        token_responses = [
            SpacingTokenResponse(
                value_px=t.value_px,
                value_rem=t.value_rem,
                name=t.name,
                confidence=t.confidence,
                semantic_role=t.semantic_role,
                spacing_type=t.spacing_type,
                role=t.role,
                grid_aligned=t.grid_aligned,
            )
            for t in library.tokens
        ]

        repo = _build_spacing_repo(library.tokens, namespace="token/spacing/batch/library")
        return BatchExtractionResponse(
            tokens=token_responses,
            statistics=library.statistics,
            design_tokens=tokens_to_w3c(repo),
        )

    except Exception as e:
        logger.error(f"Batch extraction failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/scales")
async def get_supported_scales() -> dict:
    """
    Get list of supported spacing scale systems.

    Returns:
        Dict with scale system information
    """
    return {
        "scales": [
            {
                "id": "4pt",
                "name": "4-Point Grid",
                "description": "4, 8, 12, 16, 20... (linear with base 4)",
                "base_unit": 4,
            },
            {
                "id": "8pt",
                "name": "8-Point Grid",
                "description": "8, 16, 24, 32... (linear with base 8)",
                "base_unit": 8,
            },
            {
                "id": "golden",
                "name": "Golden Ratio",
                "description": "Each step is 1.618x the previous",
                "base_unit": None,
            },
            {
                "id": "fibonacci",
                "name": "Fibonacci",
                "description": "1, 2, 3, 5, 8, 13, 21...",
                "base_unit": None,
            },
        ]
    }


@router.get("/projects/{project_id}/spacing")
async def get_project_spacing(project_id: int, db: AsyncSession = Depends(get_db)):
    """Return spacing tokens for a project."""
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Project {project_id} not found"
        )
    result = await db.execute(
        select(SpacingToken)
        .where(SpacingToken.project_id == project_id)
        .order_by(SpacingToken.created_at.desc())
    )
    tokens = result.scalars().all()
    return [
        {
            "id": t.id,
            "project_id": t.project_id,
            "extraction_job_id": t.extraction_job_id,
            "value_px": t.value_px,
            "name": t.name,
            "semantic_role": t.semantic_role,
            "spacing_type": t.spacing_type,
            "category": t.category,
            "confidence": t.confidence,
            "usage": json.loads(t.usage) if t.usage else None,
            "created_at": t.created_at.isoformat(),
        }
        for t in tokens
    ]


# Helper functions


def _spacing_attributes(token: Any) -> dict[str, Any]:
    if hasattr(token, "model_dump"):
        data = token.model_dump(exclude_none=True)
    elif is_dataclass(token):
        data = asdict(token)
    else:
        data = {k: v for k, v in vars(token).items() if not k.startswith("_")}
    value_px = data.get("value_px", token.value_px)
    data["value_px"] = value_px
    data.setdefault("value_rem", getattr(token, "value_rem", round(value_px / 16, 4)))
    return data


def _build_spacing_repo(
    tokens: Sequence[Any],
    namespace: str = "token/spacing/api",
    layout_tokens: Sequence[Token] | None = None,
) -> TokenRepository:
    repo = InMemoryTokenRepository()
    for index, token in enumerate(tokens, start=1):
        attributes = _spacing_attributes(token)
        value_px = attributes["value_px"]
        value_rem = attributes["value_rem"]
        repo.upsert_token(
            make_spacing_token(
                f"{namespace}/{index:02d}",
                value_px,
                value_rem,
                attributes,
            )
        )
    for extra in layout_tokens or []:
        repo.upsert_token(extra)
    return repo


def _layout_tokens_from_spacing(
    result: SpacingExtractionResult, namespace: str = "token/spacing/api"
) -> list[Token]:
    """
    Heuristic grid/layout tokens derived from clustered spacing values.
    """
    values = result.unique_values or [t.value_px for t in result.tokens]
    values = [v for v in values if v is not None]
    if not values:
        return []
    sorted_vals = sorted(set(values))
    base_unit = result.base_unit or su.detect_base_unit(sorted_vals)
    gutter = sorted_vals[len(sorted_vals) // 2]
    margin = sorted_vals[-1]
    columns = 12
    tokens: list[Token] = []
    tokens.append(
        Token(
            id=f"{namespace}/layout/gutter",
            type="spacing",
            value={"px": gutter},
            attributes={"role": "gutter", "$type": "dimension", "base_unit": base_unit},
        )
    )
    tokens.append(
        Token(
            id=f"{namespace}/layout/margin",
            type="spacing",
            value={"px": margin},
            attributes={"role": "margin", "$type": "dimension", "base_unit": base_unit},
        )
    )
    tokens.append(
        Token(
            id=f"{namespace}/layout/gridColumns",
            type="spacing",
            value={"px": columns},
            attributes={"role": "grid_columns"},
        )
    )
    return tokens


def _result_to_response(
    result: SpacingExtractionResult, namespace: str = "token/spacing/api"
) -> SpacingExtractionResponse:
    """Convert extraction result to response model."""
    token_responses = [
        SpacingTokenResponse(
            value_px=t.value_px,
            value_rem=t.value_rem,
            name=t.name,
            confidence=t.confidence,
            semantic_role=t.semantic_role,
            spacing_type=t.spacing_type.value if t.spacing_type else None,
            grid_aligned=t.grid_aligned,
            tailwind_class=t.tailwind_class,
        )
        for t in result.tokens
    ]

    layout_tokens = _layout_tokens_from_spacing(result, namespace=namespace)
    repo = _build_spacing_repo(result.tokens, namespace, layout_tokens=layout_tokens)

    return SpacingExtractionResponse(
        tokens=token_responses,
        scale_system=result.scale_system.value,
        base_unit=result.base_unit,
        grid_compliance=result.grid_compliance,
        extraction_confidence=result.extraction_confidence,
        unique_values=result.unique_values,
        min_spacing=result.min_spacing,
        max_spacing=result.max_spacing,
        design_tokens=tokens_to_w3c(repo),
    )


def _normalize_spacing_tokens(
    tokens: list[Any], fallback_scale: Any
) -> tuple[list[SpacingToken], int | None, float | None, Any]:
    """Cluster spacing values and re-label tokens to a normalized scale."""
    values = [t.value_px for t in tokens if getattr(t, "value_px", 0) > 0]
    clustered = su.cluster_spacing_values(values, tolerance=0.12)
    if not clustered:
        return tokens, None, None, fallback_scale

    base_unit, base_confidence = su.infer_base_spacing(clustered)
    scale_system_raw = su.detect_scale_system(clustered)
    try:
        scale_system = SpacingScale(scale_system_raw) if scale_system_raw else fallback_scale
    except Exception:
        scale_system = fallback_scale

    normalized: list[SpacingToken] = []
    for idx, val in enumerate(clustered):
        source = min(tokens, key=lambda t: abs(t.value_px - val))
        props, meta = su.compute_all_spacing_properties_with_metadata(val, clustered)
        normalized.append(
            SpacingToken(
                value_px=val,
                name=source.name or f"spacing-{idx}",
                semantic_role=source.semantic_role,
                spacing_type=source.spacing_type,
                category=source.category or "merged",
                confidence=max(getattr(source, "confidence", 0.6), 0.6),
                usage=getattr(source, "usage", []),
                scale_position=idx,
                base_unit=base_unit,
                scale_system=scale_system or getattr(source, "scale_system", fallback_scale),
                grid_aligned=props.get("grid_aligned"),
                grid_deviation_px=props.get("grid_deviation_px"),
                responsive_scales=props.get("responsive_scales"),
                extraction_metadata={
                    **(getattr(source, "extraction_metadata", {}) or {}),
                    "clustered_from": sorted(set(values)),
                    "base_unit_confidence": base_confidence,
                    "properties_meta": meta,
                },
            )
        )

    return normalized, base_unit, base_confidence, scale_system


def _merge_spacing(
    cv: SpacingExtractionResult, ai: SpacingExtractionResult
) -> SpacingExtractionResult:
    """Merge AI tokens onto CV tokens by value/name to avoid duplicates."""
    ai_by_value = {(t.value_px, t.name): t for t in ai.tokens}
    merged_tokens = list(ai.tokens)
    for t in cv.tokens:
        key = (t.value_px, t.name)
        if key not in ai_by_value:
            merged_tokens.append(t)

    normalized_tokens, base_unit, base_confidence, scale_system = _normalize_spacing_tokens(
        merged_tokens, ai.scale_system or cv.scale_system
    )

    grid_compliance = sum(1 for t in normalized_tokens if getattr(t, "grid_aligned", False)) / max(
        len(normalized_tokens), 1
    )

    unique_values = sorted({t.value_px for t in normalized_tokens})

    return SpacingExtractionResult(
        tokens=normalized_tokens,
        scale_system=scale_system or ai.scale_system or cv.scale_system,
        base_unit=base_unit or ai.base_unit or cv.base_unit,
        base_unit_confidence=base_confidence or ai.base_unit_confidence or cv.base_unit_confidence,
        grid_compliance=grid_compliance or ai.grid_compliance or cv.grid_compliance,
        extraction_confidence=ai.extraction_confidence or cv.extraction_confidence,
        unique_values=unique_values,
        min_spacing=min(unique_values) if unique_values else ai.min_spacing or cv.min_spacing,
        max_spacing=max(unique_values) if unique_values else ai.max_spacing or cv.max_spacing,
    )


def _format_sse_event(event: str, data: dict) -> str:
    """Format data as Server-Sent Event."""
    json_data = json.dumps(data)
    return f"event: {event}\ndata: {json_data}\n\n"
