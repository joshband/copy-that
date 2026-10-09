"""
FastAPI Router for Spacing Token Extraction

Provides REST API endpoints for spacing token extraction with streaming support.
Follows the pattern of colors.py for color extraction.
"""

import ipaddress
import json
import logging
import os
import socket
from collections.abc import AsyncGenerator
from typing import Any
from urllib.parse import urlparse

import requests
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from jsonschema import ValidationError

from copy_that.application.concurrency import extract_slot
from copy_that.application.cost_tracker import cost_tracker
from copy_that.application.execution.async_executor import AsyncExecutor
from copy_that.application.perf import track_perf
from copy_that.application.ports.layout_tokens import LayoutTokenRepository
from copy_that.application.ports.projects import ProjectRepository
from copy_that.application.ports.spacing_tokens import SpacingTokenRepository
from copy_that.application.spacing_models import (
    SpacingToken as SpacingTokenModel,
)
from copy_that.core_tokens.adapters.w3c import tokens_to_w3c_flat
from copy_that.design_tokens.validation import validate_w3c_export
from copy_that.extractors.spacing.cv_extractor import CVSpacingExtractor
from copy_that.infrastructure.cache.extraction_cache import compute_input_hash, get_extraction_cache
from copy_that.infrastructure.security.rate_limiter import rate_limit
from copy_that.interfaces.api import dependencies as deps
from copy_that.interfaces.api.utils import enforce_payload_size, sanitize_json_value
from copy_that.services import spacing_pipeline
from copy_that.services.spacing_models import (
    BatchExtractionResponse,
    BatchSpacingExtractionRequest,
    SpacingExtractionRequest,
    SpacingExtractionResponse,
)
from copy_that.services.spacing_models import SpacingCommonValue as SpacingCommonValue
from copy_that.services.spacing_models import SpacingTokenResponse as SpacingTokenResponse
from copy_that.services.spacing_pipeline import (
    _build_spacing_repo as _build_spacing_repo,
)
from copy_that.services.spacing_pipeline import (
    _cv_spacing_is_fallback as _cv_spacing_is_fallback,
)
from copy_that.services.spacing_pipeline import (
    _elevation_tokens_from_result as _elevation_tokens_from_result,
)
from copy_that.services.spacing_pipeline import (
    _failed_extractors_payload as _failed_extractors_payload,
)
from copy_that.services.spacing_pipeline import (
    _layout_tokens_from_spacing as _layout_tokens_from_spacing,
)
from copy_that.services.spacing_pipeline import (
    _merge_spacing as _merge_spacing,
)
from copy_that.services.spacing_pipeline import (
    _merged_spacing_confidence as _merged_spacing_confidence,
)
from copy_that.services.spacing_pipeline import (
    _normalize_spacing_tokens as _normalize_spacing_tokens,
)
from copy_that.services.spacing_pipeline import (
    _persist_spacing_extraction as _persist_spacing_extraction,
)
from copy_that.services.spacing_pipeline import (
    _result_to_response as _result_to_response,
)
from copy_that.services.spacing_pipeline import (
    _shape_tokens_from_graph as _shape_tokens_from_graph,
)
from copy_that.services.spacing_pipeline import (
    _spacing_artifacts_from_result as _spacing_artifacts_from_result,
)
from copy_that.services.spacing_pipeline import (
    _spacing_attributes as _spacing_attributes,
)
from copy_that.services.spacing_pipeline import (
    _spacing_result_from_orchestrated_tokens as _spacing_result_from_orchestrated_tokens,
)
from copy_that.services.spacing_pipeline import (
    get_extractor as get_extractor,
)
from copy_that.services.spacing_service import build_spacing_repo_from_db

SpacingToken = SpacingTokenModel

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/api/v1/spacing",
    tags=["spacing"],
    responses={404: {"description": "Not found"}},
)

ALLOWED_IMAGE_SCHEMES = {"http", "https"}
MAX_IMAGE_BYTES = int(os.getenv("MAX_IMAGE_BYTES", str(8 * 1024 * 1024)))


def _validate_image_url(url: str) -> str:
    parsed = urlparse(url)
    if parsed.scheme not in ALLOWED_IMAGE_SCHEMES:
        raise HTTPException(status_code=400, detail="Only http/https image URLs are allowed")
    if not parsed.netloc or not parsed.hostname:
        raise HTTPException(status_code=400, detail="Invalid image_url")

    try:
        records = socket.getaddrinfo(parsed.hostname, None)
    except socket.gaierror as exc:
        raise HTTPException(status_code=400, detail="Invalid image host") from exc

    for _, _, _, _, sockaddr in records:
        ip_str = sockaddr[0]
        ip = ipaddress.ip_address(ip_str)
        if ip.is_private or ip.is_loopback or ip.is_reserved or ip.is_multicast or ip.is_link_local:
            raise HTTPException(status_code=400, detail="Refusing private or internal image host")

    return parsed.geturl()


def _download_image_bytes(url: str) -> tuple[bytes, str]:
    safe_url = _validate_image_url(url)
    try:
        with requests.get(safe_url, timeout=15, stream=True) as resp:
            resp.raise_for_status()
            content_length = resp.headers.get("Content-Length")
            try:
                if content_length and int(content_length) > MAX_IMAGE_BYTES:
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail="Image too large",
                    )
            except ValueError:
                content_length = None
            buf = bytearray()
            for chunk in resp.iter_content(chunk_size=8192):
                if chunk:
                    buf.extend(chunk)
                if len(buf) > MAX_IMAGE_BYTES:
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail="Image too large",
                    )
            content_type = resp.headers.get("Content-Type", "image/png")
            return bytes(buf), content_type
    except HTTPException:
        raise
    except requests.RequestException as exc:
        logger.warning("Failed to download image %s: %s", url, exc)
        raise HTTPException(status_code=400, detail="Failed to fetch image_url") from exc


@router.get("/export/w3c")
async def export_spacing_w3c(
    project_id: int | None = None,
    validate: bool = Query(default=False, description="Validate output against W3C schemas"),
    spacing_repo: SpacingTokenRepository = Depends(deps.get_spacing_repo),
) -> dict[str, Any]:
    """Export spacing tokens (optionally by project) as W3C Design Tokens JSON."""
    tokens = await spacing_repo.list_all(project_id=project_id)
    namespace = (
        f"token/spacing/export/project/{project_id}"
        if project_id is not None
        else "token/spacing/export/all"
    )
    repo = build_spacing_repo_from_db(tokens, namespace=namespace)
    payload = sanitize_json_value(tokens_to_w3c_flat(repo))
    if validate:
        try:
            validate_w3c_export(payload)
        except ValidationError as exc:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"W3C export failed validation: {exc.message}",
            ) from exc
    return payload


# Endpoints


def _use_multi_extractor(request: SpacingExtractionRequest) -> bool:
    env_on = os.getenv("COPY_THAT_MULTI_EXTRACTOR", "0") == "1"
    return env_on or bool(getattr(request, "use_multi_extractor", False))


@router.post("/extract/multi", response_model=SpacingExtractionResponse)
async def extract_spacing_multi(
    request: SpacingExtractionRequest,
    spacing_repo: SpacingTokenRepository = Depends(deps.get_spacing_repo),
    layout_repo: LayoutTokenRepository = Depends(deps.get_layout_repo),
    async_executor: AsyncExecutor = Depends(deps.get_async_executor),
    _rate_limit: None = Depends(rate_limit(requests=10, seconds=60)),
) -> SpacingExtractionResponse:
    """Extract spacing via CV+AI multi-extractor orchestration (parallel, provenance)."""
    try:
        return await spacing_pipeline.extract_multi(
            request, spacing_repo, layout_repo, async_executor, _pipeline_dependencies()
        )
    except HTTPException:
        raise
    except spacing_pipeline.SpacingPipelineError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc
    except Exception as exc:
        logger.exception("Spacing multi-extractor extraction failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/extract", response_model=SpacingExtractionResponse)
async def extract_spacing(
    request: SpacingExtractionRequest,
    spacing_repo: SpacingTokenRepository = Depends(deps.get_spacing_repo),
    layout_repo: LayoutTokenRepository = Depends(deps.get_layout_repo),
    async_executor: AsyncExecutor = Depends(deps.get_async_executor),
    _rate_limit: None = Depends(rate_limit(requests=10, seconds=60)),
) -> SpacingExtractionResponse:
    """
    Extract spacing tokens from a single image.

    Analyzes the image using Claude to identify spacing patterns
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
    if _use_multi_extractor(request):
        return await extract_spacing_multi(
            request, spacing_repo, layout_repo, async_executor, _rate_limit
        )
    try:
        return await spacing_pipeline.extract_single(
            request, spacing_repo, layout_repo, async_executor, _pipeline_dependencies()
        )
    except Exception as exc:
        logger.exception("Spacing extraction failed")
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/extract-streaming")
async def extract_spacing_streaming(
    request: SpacingExtractionRequest,
    spacing_repo: SpacingTokenRepository = Depends(deps.get_spacing_repo),
    layout_repo: LayoutTokenRepository = Depends(deps.get_layout_repo),
    async_executor: AsyncExecutor = Depends(deps.get_async_executor),
    session=Depends(deps.get_db_session),
    _rate_limit: None = Depends(rate_limit(requests=10, seconds=60)),
) -> StreamingResponse:
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
    if not request.image_url:
        raise HTTPException(status_code=400, detail="image_url is required for streaming")
    safe_url = _validate_image_url(str(request.image_url))
    cost_headers = {"Cache-Control": "no-cache", "Connection": "keep-alive"}

    async def event_generator() -> AsyncGenerator[str, None]:
        async for event, data in spacing_pipeline.stream_events(
            request,
            safe_url,
            spacing_repo,
            layout_repo,
            async_executor,
            session,
            cost_headers,
            _pipeline_dependencies(),
        ):
            yield _format_sse_event(event, data)

    return StreamingResponse(
        event_generator(), media_type="text/event-stream", headers=cost_headers
    )


@router.post("/batch-extract", response_model=BatchExtractionResponse)
async def extract_spacing_batch(
    request: BatchSpacingExtractionRequest,
    async_executor: AsyncExecutor = Depends(deps.get_async_executor),
    _rate_limit: None = Depends(rate_limit(requests=5, seconds=60)),
) -> BatchExtractionResponse:
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
        return await spacing_pipeline.extract_batch(
            request, async_executor, _pipeline_dependencies()
        )
    except Exception as exc:
        logger.exception("Batch extraction failed")
        raise HTTPException(status_code=500, detail=str(exc))


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
async def get_project_spacing(
    project_id: int,
    project_repo: ProjectRepository = Depends(deps.get_project_repo),
    spacing_repo: SpacingTokenRepository = Depends(deps.get_spacing_repo),
):
    """Return spacing tokens for a project."""
    project = await project_repo.get(project_id=project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Project {project_id} not found"
        )
    tokens = await spacing_repo.list_by_project(project_id=project_id)
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


def _format_sse_event(event: str, data: dict) -> str:
    """Format data as Server-Sent Event."""
    json_data = json.dumps(data)
    return f"event: {event}\ndata: {json_data}\n\n"


def _pipeline_dependencies() -> spacing_pipeline.SpacingPipelineDependencies:
    return spacing_pipeline.SpacingPipelineDependencies(
        get_extractor=get_extractor,
        cv_extractor=CVSpacingExtractor,
        download_image=_download_image_bytes,
        validate_image_url=_validate_image_url,
        enforce_payload_size=enforce_payload_size,
        extract_slot=extract_slot,
        cache=get_extraction_cache,
        input_hash=compute_input_hash,
        track_perf=track_perf,
        cost_tracker=cost_tracker,
    )
