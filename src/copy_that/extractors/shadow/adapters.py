"""
Adapter implementations for shadow extraction.

Wraps existing shadow extractors to conform to ShadowExtractorProtocol.
"""

import asyncio
import base64
import logging
import time

from .ai_extractor import AIShadowExtractor
from .base import ExtractionResult
from .cv_extractor import CVShadowExtractor

logger = logging.getLogger(__name__)


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
            # Convert to base64
            base64_image = base64.b64encode(image_data).decode("utf-8")

            # Run extraction in thread pool
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                self.extractor.extract_shadows,
                None,  # image_url
                base64_image,
                "image/png",  # media_type
            )

            # Extract shadow styles from result
            tokens = []
            if hasattr(result, "shadows") and result.shadows:
                tokens = result.shadows

            execution_time_ms = (time.time() - start_time) * 1000
            confidence_range = (0.8, 0.95)

            return ExtractionResult(
                tokens=tokens,
                extractor_name=self.name,
                execution_time_ms=execution_time_ms,
                confidence_range=confidence_range,
            )

        except Exception as e:
            logger.error(f"AI shadow extraction failed: {e}")
            execution_time_ms = (time.time() - start_time) * 1000
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
            # Convert to base64
            base64_image = base64.b64encode(image_data).decode("utf-8")

            # Run extraction in thread pool
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                self.extractor.extract_shadows,
                base64_image,
                "image/png",  # media_type
            )

            # Extract shadow styles from result
            tokens = []
            if hasattr(result, "shadows") and result.shadows:
                tokens = result.shadows

            execution_time_ms = (time.time() - start_time) * 1000
            confidence_range = (0.6, 0.85)

            return ExtractionResult(
                tokens=tokens,
                extractor_name=self.name,
                execution_time_ms=execution_time_ms,
                confidence_range=confidence_range,
            )

        except Exception as e:
            logger.error(f"CV shadow extraction failed: {e}")
            execution_time_ms = (time.time() - start_time) * 1000
            raise ValueError(f"Failed to extract shadows: {e}") from e


# Backward compatibility aliases
ClaudeShadowExtractorAdapter = AIShadowExtractorAdapter
CVShadowAdapter = CVShadowExtractorAdapter
