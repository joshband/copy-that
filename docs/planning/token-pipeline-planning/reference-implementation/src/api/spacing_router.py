"""
REFERENCE IMPLEMENTATION - FastAPI Router for Spacing Extraction

This is REFERENCE CODE for planning purposes. It demonstrates how to create
FastAPI endpoints for spacing token extraction with SSE streaming support.

NOTE: This code is not production-ready. It serves as a blueprint for
implementing spacing API endpoints in the actual codebase.

TODO: Integrate with existing copy_that.api module structure
TODO: Add authentication/authorization middleware
TODO: Add rate limiting for AI endpoints
TODO: Add database persistence integration
"""

import asyncio
import json
import logging
from typing import AsyncGenerator

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field, HttpUrl

# TODO: Update imports when integrated into main codebase
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from models.spacing_token import SpacingToken, SpacingExtractionResult, SpacingScale
from extractors.spacing_extractor import AISpacingExtractor
from extractors.batch_spacing_extractor import BatchSpacingExtractor
from aggregators.spacing_aggregator import SpacingAggregator, SpacingTokenLibrary

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/spacing",
    tags=["spacing"],
    responses={404: {"description": "Not found"}},
)


# Request/Response Models

class SpacingExtractionRequest(BaseModel):
    """Request model for single image spacing extraction."""

    image_url: HttpUrl = Field(..., description="URL of the image to analyze")
    max_tokens: int = Field(default=15, ge=1, le=50, description="Maximum spacing tokens to extract")


class BatchSpacingExtractionRequest(BaseModel):
    """Request model for batch spacing extraction."""

    image_urls: list[HttpUrl] = Field(..., min_length=1, max_length=20, description="List of image URLs")
    max_tokens: int = Field(default=15, ge=1, le=50, description="Max tokens per image")
    similarity_threshold: float = Field(default=10.0, ge=1.0, le=50.0, description="Percentage threshold for deduplication")


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


class BatchExtractionResponse(BaseModel):
    """Response model for batch extraction result."""

    tokens: list[SpacingTokenResponse]
    statistics: dict
    library_id: str | None = None  # If persisted


class StreamEvent(BaseModel):
    """Model for SSE stream events."""

    event: str
    data: dict


# Dependency for extractor instance
def get_extractor() -> AISpacingExtractor:
    """Dependency to get spacing extractor instance."""
    return AISpacingExtractor()


def get_batch_extractor() -> BatchSpacingExtractor:
    """Dependency to get batch spacing extractor instance."""
    return BatchSpacingExtractor(max_concurrent=3)


# Endpoints

@router.post("/extract", response_model=SpacingExtractionResponse)
async def extract_spacing(
    request: SpacingExtractionRequest,
    extractor: AISpacingExtractor = Depends(get_extractor)
) -> SpacingExtractionResponse:
    """
    Extract spacing tokens from a single image.

    Analyzes the image using Claude Sonnet 4.5 to identify spacing patterns
    and generate design tokens.

    Args:
        request: Extraction parameters
        extractor: AI extractor instance (injected)

    Returns:
        SpacingExtractionResponse with extracted tokens

    Raises:
        HTTPException: If extraction fails

    Example:
        POST /spacing/extract
        {
            "image_url": "https://example.com/design.png",
            "max_tokens": 15
        }
    """
    try:
        # Run extraction in thread pool (sync operation)
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: extractor.extract_spacing_from_image_url(
                str(request.image_url),
                request.max_tokens
            )
        )

        # Convert to response model
        return _result_to_response(result)

    except Exception as e:
        logger.error(f"Spacing extraction failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/extract/stream")
async def extract_spacing_streaming(
    request: SpacingExtractionRequest,
    extractor: AISpacingExtractor = Depends(get_extractor)
) -> StreamingResponse:
    """
    Extract spacing tokens with Server-Sent Events streaming.

    Returns real-time progress updates during extraction.

    Args:
        request: Extraction parameters
        extractor: AI extractor instance (injected)

    Returns:
        StreamingResponse with SSE events

    Events:
        - progress: Extraction progress updates
        - token: Individual token extracted
        - complete: Final result
        - error: Error occurred

    Example:
        POST /spacing/extract/stream
        {
            "image_url": "https://example.com/design.png"
        }

        Response (SSE):
        event: progress
        data: {"status": "downloading", "progress": 0.1}

        event: progress
        data: {"status": "analyzing", "progress": 0.5}

        event: token
        data: {"value_px": 16, "name": "spacing-md"}

        event: complete
        data: {"tokens": [...], "scale_system": "8pt"}
    """
    async def event_generator() -> AsyncGenerator[str, None]:
        try:
            # Emit start event
            yield _format_sse_event("progress", {
                "status": "started",
                "progress": 0.0,
                "message": "Starting extraction..."
            })

            # Download phase
            yield _format_sse_event("progress", {
                "status": "downloading",
                "progress": 0.2,
                "message": "Downloading image..."
            })

            # Run extraction
            loop = asyncio.get_event_loop()

            yield _format_sse_event("progress", {
                "status": "analyzing",
                "progress": 0.4,
                "message": "Analyzing with Claude Sonnet 4.5..."
            })

            result = await loop.run_in_executor(
                None,
                lambda: extractor.extract_spacing_from_image_url(
                    str(request.image_url),
                    request.max_tokens
                )
            )

            yield _format_sse_event("progress", {
                "status": "processing",
                "progress": 0.8,
                "message": "Processing tokens..."
            })

            # Emit individual tokens
            for token in result.tokens:
                yield _format_sse_event("token", {
                    "value_px": token.value_px,
                    "name": token.name,
                    "confidence": token.confidence,
                })

            # Emit complete
            response = _result_to_response(result)
            yield _format_sse_event("complete", response.model_dump())

        except Exception as e:
            logger.error(f"Streaming extraction failed: {e}")
            yield _format_sse_event("error", {
                "message": str(e),
                "type": type(e).__name__
            })

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


@router.post("/extract/batch", response_model=BatchExtractionResponse)
async def extract_spacing_batch(
    request: BatchSpacingExtractionRequest,
    batch_extractor: BatchSpacingExtractor = Depends(get_batch_extractor)
) -> BatchExtractionResponse:
    """
    Extract and aggregate spacing tokens from multiple images.

    Processes multiple images in parallel with controlled concurrency,
    then aggregates and deduplicates the results.

    Args:
        request: Batch extraction parameters
        batch_extractor: Batch extractor instance (injected)

    Returns:
        BatchExtractionResponse with aggregated tokens

    Example:
        POST /spacing/extract/batch
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
        # Convert URLs to strings
        image_urls = [str(url) for url in request.image_urls]

        # Run batch extraction
        tokens, statistics = await batch_extractor.extract_batch(
            image_urls,
            request.max_tokens,
            request.similarity_threshold
        )

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
            for t in tokens
        ]

        return BatchExtractionResponse(
            tokens=token_responses,
            statistics=statistics,
        )

    except Exception as e:
        logger.error(f"Batch extraction failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/extract/batch/stream")
async def extract_spacing_batch_streaming(
    request: BatchSpacingExtractionRequest,
    batch_extractor: BatchSpacingExtractor = Depends(get_batch_extractor)
) -> StreamingResponse:
    """
    Extract spacing from multiple images with SSE progress streaming.

    Provides real-time updates for each image being processed.

    Args:
        request: Batch extraction parameters
        batch_extractor: Batch extractor instance

    Returns:
        StreamingResponse with progress events

    Events:
        - progress: Overall batch progress
        - image_start: Starting processing of an image
        - image_complete: Finished processing an image
        - aggregating: Aggregation phase started
        - complete: Final aggregated result
    """
    async def event_generator() -> AsyncGenerator[str, None]:
        try:
            total = len(request.image_urls)

            yield _format_sse_event("progress", {
                "status": "started",
                "total_images": total,
                "progress": 0.0
            })

            image_urls = [str(url) for url in request.image_urls]

            # Define progress callback
            async def progress_callback(current: int, total: int, status: str):
                yield _format_sse_event("progress", {
                    "current": current,
                    "total": total,
                    "status": status,
                    "progress": current / total if total > 0 else 0
                })

            # Run extraction with progress
            tokens, statistics = await batch_extractor.extract_batch_with_progress(
                image_urls,
                request.max_tokens,
                request.similarity_threshold,
                progress_callback=None  # TODO: Implement async callback properly
            )

            yield _format_sse_event("aggregating", {
                "status": "Aggregating results...",
                "progress": 0.9
            })

            # Convert to response
            token_responses = [
                {
                    "value_px": t.value_px,
                    "value_rem": t.value_rem,
                    "name": t.name,
                    "confidence": t.confidence,
                    "role": t.role,
                }
                for t in tokens
            ]

            yield _format_sse_event("complete", {
                "tokens": token_responses,
                "statistics": statistics,
                "progress": 1.0
            })

        except Exception as e:
            logger.error(f"Streaming batch extraction failed: {e}")
            yield _format_sse_event("error", {
                "message": str(e),
                "type": type(e).__name__
            })

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


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
                "base_unit": 4
            },
            {
                "id": "8pt",
                "name": "8-Point Grid",
                "description": "8, 16, 24, 32... (linear with base 8)",
                "base_unit": 8
            },
            {
                "id": "golden",
                "name": "Golden Ratio",
                "description": "Each step is 1.618x the previous",
                "base_unit": None
            },
            {
                "id": "fibonacci",
                "name": "Fibonacci",
                "description": "1, 2, 3, 5, 8, 13, 21...",
                "base_unit": None
            },
        ]
    }


# Helper functions

def _result_to_response(result: SpacingExtractionResult) -> SpacingExtractionResponse:
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

    return SpacingExtractionResponse(
        tokens=token_responses,
        scale_system=result.scale_system.value,
        base_unit=result.base_unit,
        grid_compliance=result.grid_compliance,
        extraction_confidence=result.extraction_confidence,
        unique_values=result.unique_values,
        min_spacing=result.min_spacing,
        max_spacing=result.max_spacing,
    )


def _format_sse_event(event: str, data: dict) -> str:
    """Format data as Server-Sent Event."""
    json_data = json.dumps(data)
    return f"event: {event}\ndata: {json_data}\n\n"


# Include router in main app
# TODO: Add to main FastAPI app in copy_that/api/main.py
# from copy_that.api.spacing_router import router as spacing_router
# app.include_router(spacing_router)
