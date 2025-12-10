"""
Base protocol and result types for spacing extraction.

Defines the interface for spacing extractors to enable swappable implementations.
"""

from dataclasses import dataclass
from typing import Protocol

from .models import SpacingToken


@dataclass
class ExtractionResult:
    """Standard result wrapper for spacing extraction"""

    tokens: list[SpacingToken]
    extractor_name: str
    execution_time_ms: float
    confidence_range: tuple[float, float]  # (min, max)


class SpacingExtractorProtocol(Protocol):
    """Protocol for spacing extractors - enables duck typing"""

    name: str

    async def extract(self, image_data: bytes) -> ExtractionResult:
        """
        Extract spacing tokens from image data.

        Args:
            image_data: Raw image bytes (PNG, JPEG, GIF, WebP)

        Returns:
            ExtractionResult with tokens and metadata
        """
        ...
