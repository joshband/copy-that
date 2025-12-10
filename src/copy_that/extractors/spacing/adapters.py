"""
Adapter implementations for spacing extraction.

Wraps existing spacing extractors to conform to SpacingExtractorProtocol.
"""

import asyncio
import io
import logging
import time

from .base import ExtractionResult
from .cv_extractor import CVSpacingExtractor

logger = logging.getLogger(__name__)


class CVSpacingExtractorAdapter:
    """Wraps CVSpacingExtractor for async extraction with protocol compliance"""

    def __init__(self, max_tokens: int = 10):
        """
        Initialize the CV spacing adapter.

        Args:
            max_tokens: Maximum spacing tokens to extract
        """
        self.extractor = CVSpacingExtractor(max_tokens=max_tokens)
        self.max_tokens = max_tokens

    @property
    def name(self) -> str:
        """Extractor name for identification"""
        return "cv-spacing"

    async def extract(self, image_data: bytes) -> ExtractionResult:
        """
        Extract spacing tokens from image data.

        Args:
            image_data: Raw image bytes

        Returns:
            ExtractionResult with tokens and metadata
        """
        start_time = time.time()

        try:
            # Convert bytes to PIL Image
            from PIL import Image

            image = Image.open(io.BytesIO(image_data))

            # Run extraction in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, self.extractor.extract_spacing_tokens, image)

            if not result or not isinstance(result, list):
                result = []

            # Limit tokens
            tokens = result[: self.max_tokens] if isinstance(result, list) else []

            execution_time_ms = (time.time() - start_time) * 1000

            # Calculate confidence range
            # CV extractor doesn't provide confidence, so use default range
            confidence_range = (0.6, 0.85)

            return ExtractionResult(
                tokens=tokens,
                extractor_name=self.name,
                execution_time_ms=execution_time_ms,
                confidence_range=confidence_range,
            )

        except Exception as e:
            logger.error(f"CV spacing extraction failed: {e}")
            execution_time_ms = (time.time() - start_time) * 1000
            raise ValueError(f"Failed to extract spacing: {e}") from e


# Backward compatibility aliases
CVSpacingAdapter = CVSpacingExtractorAdapter
