"""Base protocol and result types for color extractors

Defines the standard interface for color extractors to enable:
- Parallel execution of multiple extractors
- Consistent result aggregation
- Performance tracking
- Provenance tracking
"""

import time
from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from copy_that.extractors.color.extractor import ExtractedColorToken


@dataclass
class ExtractionResult:
    """Result from a single color extractor"""

    colors: list[ExtractedColorToken]
    extractor_name: str
    execution_time_ms: float
    confidence_range: tuple[float, float]


@runtime_checkable
class ColorExtractorProtocol(Protocol):
    """Protocol for color extractors - enables duck typing"""

    @property
    def name(self) -> str:
        """Extractor name for provenance tracking"""
        ...

    async def extract(self, image_data: bytes) -> ExtractionResult:
        """Extract colors from image bytes

        Args:
            image_data: Raw image bytes (PNG, JPG, etc.)

        Returns:
            ExtractionResult with colors and metadata

        Raises:
            Exception: Any extraction error (will be caught by orchestrator)
        """
        ...


class ColorExtractorBase:
    """Base class for color extractors (alternative to Protocol)"""

    @property
    def name(self) -> str:
        """Extractor name for provenance tracking"""
        raise NotImplementedError

    async def extract(self, image_data: bytes) -> ExtractionResult:
        """Extract colors from image bytes"""
        raise NotImplementedError

    async def extract_with_timing(self, image_data: bytes) -> ExtractionResult:
        """Helper to wrap extraction with timing"""
        start = time.time()
        colors = await self._do_extraction(image_data)
        duration_ms = (time.time() - start) * 1000

        confidence_values = [c.confidence for c in colors] if colors else [0.5]
        confidence_range = (min(confidence_values), max(confidence_values))

        return ExtractionResult(
            colors=colors,
            extractor_name=self.name,
            execution_time_ms=duration_ms,
            confidence_range=confidence_range,
        )

    async def _do_extraction(self, image_data: bytes) -> list[ExtractedColorToken]:
        """Override this method in subclasses"""
        raise NotImplementedError
