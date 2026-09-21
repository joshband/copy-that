"""
Adapter implementations for shadow extraction.

Wraps existing shadow extractors to conform to ShadowExtractorProtocol.
"""

from __future__ import annotations

import asyncio
import base64
import logging
import time

from .ai_extractor import AIShadowExtractor
from .base import ExtractionResult
from .cv_extractor import CVShadowExtractor
from .token_bridge import extracted_to_shadow_style

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


class AIShadowExtractorAdapter:
    """Wraps AIShadowExtractor (Claude) for async extraction with protocol compliance"""

    def __init__(self):
        """Initialize the AI shadow adapter"""
        self.extractor = AIShadowExtractor()

    @property
    def name(self) -> str:
        """Extractor name for identification"""
        return "claude-shadow"

    async def extract(self, image_data: bytes) -> ExtractionResult:
        """
        Extract shadow tokens from image data using Claude.

        Args:
            image_data: Raw image bytes

        Returns:
            ExtractionResult with tokens and metadata
        """
        start_time = time.time()

        try:
            base64_image = base64.b64encode(image_data).decode("utf-8")
            media_type = _detect_media_type(image_data)

            loop = asyncio.get_running_loop()
            result = await loop.run_in_executor(
                None,
                self.extractor.extract_shadows,
                None,  # image_url
                base64_image,
                media_type,
            )

            raw = list(getattr(result, "shadows", []) or [])
            tokens = [extracted_to_shadow_style(t) for t in raw]

            execution_time_ms = (time.time() - start_time) * 1000
            confs = [t.confidence for t in tokens]
            confidence_range = (min(confs), max(confs)) if confs else (0.8, 0.95)

            return ExtractionResult(
                tokens=tokens,
                extractor_name=self.name,
                execution_time_ms=execution_time_ms,
                confidence_range=confidence_range,
            )

        except Exception as e:
            logger.error(f"AI shadow extraction failed: {e}")
            raise ValueError(f"Failed to extract shadows: {e}") from e


class CVShadowExtractorAdapter:
    """Wraps CVShadowExtractor for async extraction with protocol compliance"""

    def __init__(self):
        """Initialize the CV shadow adapter"""
        self.extractor = CVShadowExtractor()

    @property
    def name(self) -> str:
        """Extractor name for identification"""
        return "cv-shadow"

    async def extract(self, image_data: bytes) -> ExtractionResult:
        """
        Extract shadow tokens from image data using CV.

        Args:
            image_data: Raw image bytes

        Returns:
            ExtractionResult with tokens and metadata
        """
        start_time = time.time()

        try:
            base64_image = base64.b64encode(image_data).decode("utf-8")
            media_type = _detect_media_type(image_data)

            loop = asyncio.get_running_loop()
            result = await loop.run_in_executor(
                None,
                self.extractor.extract_shadows,
                base64_image,
                media_type,
            )

            raw = list(getattr(result, "shadows", []) or [])
            tokens = [extracted_to_shadow_style(t) for t in raw]

            execution_time_ms = (time.time() - start_time) * 1000
            live = float(getattr(result, "extraction_confidence", 0.0) or 0.0)
            token_confs = [float(t.confidence) for t in tokens]
            if token_confs:
                lo = min(min(token_confs), live) if live > 0 else min(token_confs)
                hi = max(max(token_confs), live) if live > 0 else max(token_confs)
                confidence_range = (round(lo, 3), round(hi, 3))
            elif live > 0:
                confidence_range = (round(live, 3), round(live, 3))
            else:
                confidence_range = (0.0, 0.0)

            return ExtractionResult(
                tokens=tokens,
                extractor_name=self.name,
                execution_time_ms=execution_time_ms,
                confidence_range=confidence_range,
            )

        except Exception as e:
            logger.error(f"CV shadow extraction failed: {e}")
            raise ValueError(f"Failed to extract shadows: {e}") from e


# Backward compatibility aliases
ClaudeShadowExtractorAdapter = AIShadowExtractorAdapter
CVShadowAdapter = CVShadowExtractorAdapter
