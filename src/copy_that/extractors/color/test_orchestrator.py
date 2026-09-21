"""Test suite for MultiExtractorOrchestrator"""

import pytest

from copy_that.extractors.color.base import ExtractionResult
from copy_that.extractors.color.extractor import ExtractedColorToken
from copy_that.extractors.color.orchestrator import MultiExtractorOrchestrator
from copy_that.tokens.color.aggregator import ColorAggregator


class MockExtractor:
    """Mock extractor for testing"""

    def __init__(self, name: str, colors: list[ExtractedColorToken] | None = None):
        self._name = name
        self._colors = colors or [
            ExtractedColorToken(
                hex="#FF0000",
                rgb="rgb(255, 0, 0)",
                name="Red",
                confidence=0.95,
            )
        ]

    @property
    def name(self) -> str:
        return self._name

    async def extract(self, image_data: bytes) -> ExtractionResult:
        """Mock extraction"""
        return ExtractionResult(
            colors=self._colors,
            extractor_name=self.name,
            execution_time_ms=100.0,
            confidence_range=(0.85, 0.95),
        )


class FailingExtractor:
    """Mock extractor that fails"""

    def __init__(self, name: str):
        self._name = name

    @property
    def name(self) -> str:
        return self._name

    async def extract(self, image_data: bytes) -> ExtractionResult:
        """Fails extraction"""
        raise RuntimeError(f"Intentional failure from {self.name}")


@pytest.mark.asyncio
async def test_orchestrator_runs_extractors_in_parallel():
    """Test that orchestrator runs multiple extractors"""
    # Create mock extractors
    extractors = [
        MockExtractor("extractor1"),
        MockExtractor("extractor2"),
    ]

    aggregator = ColorAggregator(delta_e_threshold=2.3)
    orchestrator = MultiExtractorOrchestrator(extractors, aggregator)

    # Run orchestration
    result = await orchestrator.extract_all(b"test_image", "test_image_1")

    # Verify results
    assert result.aggregated_colors is not None
    assert len(result.extraction_results) == 2
    assert len(result.failed_extractors) == 0
    assert result.total_time_ms > 0
    assert result.overall_confidence > 0


@pytest.mark.asyncio
async def test_orchestrator_graceful_degradation():
    """Test that orchestrator continues when one extractor fails"""
    # Create mix of good and failing extractors
    extractors = [
        MockExtractor("good_extractor"),
        FailingExtractor("bad_extractor"),
    ]

    aggregator = ColorAggregator(delta_e_threshold=2.3)
    orchestrator = MultiExtractorOrchestrator(extractors, aggregator)

    # Run orchestration
    result = await orchestrator.extract_all(b"test_image", "test_image_1")

    # Verify results
    assert result.aggregated_colors is not None
    assert len(result.extraction_results) == 1  # Only good extractor
    assert len(result.failed_extractors) == 1  # One failure
    assert result.failed_extractors[0][0] == "bad_extractor"


@pytest.mark.asyncio
async def test_orchestrator_aggregates_colors():
    """Test that orchestrator aggregates colors from multiple extractors"""
    # Create extractors with different colors
    red_color = ExtractedColorToken(
        hex="#FF0000", rgb="rgb(255, 0, 0)", name="Red", confidence=0.95
    )
    blue_color = ExtractedColorToken(
        hex="#0000FF", rgb="rgb(0, 0, 255)", name="Blue", confidence=0.90
    )

    extractors = [
        MockExtractor("extractor1", [red_color]),
        MockExtractor("extractor2", [blue_color]),
    ]

    aggregator = ColorAggregator(delta_e_threshold=2.3)
    orchestrator = MultiExtractorOrchestrator(extractors, aggregator)

    # Run orchestration
    result = await orchestrator.extract_all(b"test_image", "test_image_1")

    # Verify aggregation
    assert result.aggregated_colors is not None
    # Should have 2 unique colors (red and blue are very different)
    assert len(result.extraction_results) == 2
    assert len(result.aggregated_colors) >= 2


@pytest.mark.asyncio
async def test_orchestrator_tracks_failures():
    """Test that orchestrator tracks failed extractors"""
    extractors = [
        FailingExtractor("bad1"),
        FailingExtractor("bad2"),
    ]

    aggregator = ColorAggregator(delta_e_threshold=2.3)
    orchestrator = MultiExtractorOrchestrator(extractors, aggregator)

    # Run orchestration
    result = await orchestrator.extract_all(b"test_image", "test_image_1")

    # Verify all failures tracked
    assert len(result.failed_extractors) == 2
    assert result.extraction_results == []


@pytest.mark.asyncio
async def test_orchestrator_safe_mode():
    """Test safe mode doesn't raise exceptions"""
    extractors = [FailingExtractor("bad")]

    aggregator = ColorAggregator(delta_e_threshold=2.3)
    orchestrator = MultiExtractorOrchestrator(extractors, aggregator)

    # Safe mode should not raise
    result = await orchestrator.extract_all_safe(b"test_image", "test_image_1")

    # Verify no exceptions raised
    assert result is not None
    assert len(result.failed_extractors) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
