"""
Adapter implementations for typography extraction.

Wraps existing typography extractors to conform to TypographyExtractorProtocol.
"""

from __future__ import annotations

import asyncio
import base64
import logging
import time

from .ai_extractor import AITypographyExtractor
from .base import ExtractionResult
from .cv_extractor import CVTypographyExtractor

logger = logging.getLogger(__name__)


def _detect_media_type(image_data: bytes) -> str:
    if image_data.startswith(b"\x89PNG"):
        return "image/png"
    if image_data.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    if image_data.startswith(b"GIF87a") or image_data.startswith(b"GIF89a"):
        return "image/gif"
    if image_data.startswith(b"RIFF") and b"WEBP" in image_data[:20]:
        return "image/webp"
    return "image/png"


def _confidence_range_from_tokens(tokens: list, default: tuple[float, float]) -> tuple[float, float]:
    confs = [float(t.confidence) for t in tokens if getattr(t, "confidence", None) is not None]
    if not confs:
        return default
    return (round(min(confs), 3), round(max(confs), 3))


class AITypographyExtractorAdapter:
    """Wraps AITypographyExtractor (Claude) for async extraction with protocol compliance"""

    def __init__(self):
        """Initialize the AI typography adapter"""
        self.extractor = AITypographyExtractor()

    @property
    def name(self) -> str:
        """Extractor name for identification"""
        return "claude-typography"

    async def extract(self, image_data: bytes) -> ExtractionResult:
        """
        Extract typography tokens from image data using Claude.

        Args:
            image_data: Raw image bytes (JPEG, PNG, GIF, WebP)

        Returns:
            ExtractionResult with tokens and metadata
        """
        start_time = time.time()

        try:
            b64 = base64.standard_b64encode(image_data).decode("utf-8")
            media_type = _detect_media_type(image_data)
            loop = asyncio.get_running_loop()
            result = await loop.run_in_executor(
                None,
                lambda: self.extractor.extract_typography_from_base64(b64, media_type),
            )
            tokens = list(getattr(result, "tokens", []) or [])
            if not isinstance(tokens, list):
                tokens = []

            execution_time_ms = (time.time() - start_time) * 1000
            confidence_range = _confidence_range_from_tokens(tokens, (0.8, 0.95))

            return ExtractionResult(
                tokens=tokens,
                extractor_name=self.name,
                execution_time_ms=execution_time_ms,
                confidence_range=confidence_range,
            )

        except Exception as e:
            logger.error(f"AI typography extraction failed: {e}")
            raise ValueError(f"Failed to extract typography: {e}") from e


class CVTypographyExtractorAdapter:
    """Wraps CVTypographyExtractor (OCR) with live token confidence ranges."""

    def __init__(self):
        self.extractor = CVTypographyExtractor()

    @property
    def name(self) -> str:
        return "cv-typography"

    async def extract(self, image_data: bytes) -> ExtractionResult:
        start_time = time.time()
        try:
            tokens = await self.extractor.extract(image_data)
            if not isinstance(tokens, list):
                tokens = []
            execution_time_ms = (time.time() - start_time) * 1000
            confidence_range = _confidence_range_from_tokens(tokens, (0.35, 0.7))
            return ExtractionResult(
                tokens=tokens,
                extractor_name=self.name,
                execution_time_ms=execution_time_ms,
                confidence_range=confidence_range,
            )
        except Exception as e:
            logger.error(f"CV typography extraction failed: {e}")
            raise ValueError(f"Failed to extract typography: {e}") from e


# Backward compatibility aliases
ClaudeTypographyExtractorAdapter = AITypographyExtractorAdapter
