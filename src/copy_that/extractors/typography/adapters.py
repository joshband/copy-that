"""
Adapter implementations for typography extraction.

Wraps existing typography extractors to conform to TypographyExtractorProtocol.
"""

import asyncio
import logging
import time

from .ai_extractor import AITypographyExtractor
from .base import ExtractionResult

logger = logging.getLogger(__name__)


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
            # Run extraction in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            tokens = await loop.run_in_executor(
                None, self.extractor.extract_typography_from_bytes, image_data
            )

            if not isinstance(tokens, list):
                tokens = []

            execution_time_ms = (time.time() - start_time) * 1000

            # Claude provides high-confidence results
            confidence_range = (0.8, 0.95)

            return ExtractionResult(
                tokens=tokens,
                extractor_name=self.name,
                execution_time_ms=execution_time_ms,
                confidence_range=confidence_range,
            )

        except Exception as e:
            logger.error(f"AI typography extraction failed: {e}")
            execution_time_ms = (time.time() - start_time) * 1000
            raise ValueError(f"Failed to extract typography: {e}") from e


# Backward compatibility aliases
ClaudeTypographyExtractorAdapter = AITypographyExtractorAdapter
