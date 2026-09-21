"""
Base protocol and result types for typography extraction.

Defines the interface for typography extractors to enable swappable implementations.
"""

from dataclasses import dataclass
from typing import Protocol

from .ai_extractor import ExtractedTypographyToken


@dataclass
class ExtractionResult:
    """Standard result wrapper for typography extraction"""

    tokens: list[ExtractedTypographyToken]
    extractor_name: str
    execution_time_ms: float
    confidence_range: tuple[float, float]  # (min, max)


class TypographyExtractorProtocol(Protocol):
    """Protocol for typography extractors - enables duck typing"""

    name: str

    async def extract(self, image_data: bytes) -> ExtractionResult:
        """
        Extract typography tokens from image data.

        Args:
            image_data: Raw image bytes (PNG, JPEG, GIF, WebP)

        Returns:
            ExtractionResult with tokens and metadata
        """
        ...
