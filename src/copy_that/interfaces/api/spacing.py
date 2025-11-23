"""
FastAPI Router for Spacing Token Extraction

Provides REST API endpoints for spacing token extraction with streaming support.
Follows the pattern of colors.py for color extraction.
"""

import asyncio
import json
import logging
from collections.abc import AsyncGenerator

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field, HttpUrl

from copy_that.application.spacing_extractor import AISpacingExtractor
from copy_that.application.spacing_models import SpacingExtractionResult
from copy_that.tokens.spacing.aggregator import SpacingAggregator

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/api/v1/spacing",
    tags=["spacing"],
    responses={404: {"description": "Not found"}},
)


# Request/Response Models


class SpacingExtractionRequest(BaseModel):
    """Request model for single image spacing extraction."""

    image_url: HttpUrl = Field(..., description="URL of the image to analyze")
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


class BatchExtractionResponse(BaseModel):
    """Response model for batch extraction result."""

    tokens: list[SpacingTokenResponse]
    statistics: dict
    library_id: str | None = None


# Dependency for extractor instance
def get_extractor() -> AISpacingExtractor:
    """Get spacing extractor instance."""
    return AISpacingExtractor()


# Endpoints


@router.post("/extract", response_model=SpacingExtractionResponse)
async def extract_spacing(request: SpacingExtractionRequest) -> SpacingExtractionResponse:
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

        # Run extraction in thread pool (sync operation)
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: extractor.extract_spacing_from_image_url(
                str(request.image_url), request.max_tokens
            ),
        )

        # Convert to response model
        return _result_to_response(result)

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

        # Extract from each image
        all_tokens = []
        for url in request.image_urls:
            result = await loop.run_in_executor(
                None,
                lambda u=str(url): extractor.extract_spacing_from_image_url(u, request.max_tokens),
            )
            all_tokens.append(result.tokens)

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

        return BatchExtractionResponse(
            tokens=token_responses,
            statistics=library.statistics,
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
