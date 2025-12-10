"""
Base protocol and result types for shadow extraction.

Defines the interface for shadow extractors to enable swappable implementations.
"""

from dataclasses import dataclass
from typing import Protocol

from .extractor import ShadowStyle


@dataclass
class ExtractionResult:
    """Standard result wrapper for shadow extraction"""

    tokens: list[ShadowStyle]
    extractor_name: str
    execution_time_ms: float
    confidence_range: tuple[float, float]  # (min, max)


class ShadowExtractorProtocol(Protocol):
    """Protocol for shadow extractors - enables duck typing"""

    name: str

    async def extract(self, image_data: bytes) -> ExtractionResult:
        """
        Extract shadow tokens from image data.

        Args:
            image_data: Raw image bytes (PNG, JPEG, GIF, WebP)

        Returns:
            ExtractionResult with tokens and metadata
        """
        ...
