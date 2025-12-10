"""Test suite for ShadowExtractionOrchestrator"""

import pytest

from .base import ExtractionResult
from .extractor import ShadowStyle
from .orchestrator import ShadowAggregator, ShadowExtractionOrchestrator


class MockExtractor:
    """Mock extractor for testing"""

    def __init__(self, name: str, tokens: list[ShadowStyle] | None = None):
        self._name = name
        self._tokens = tokens or [
            ShadowStyle(
                color="#000000",
                opacity=0.25,
                x=0.0,
                y=4.0,
                blur=8.0,
                spread=0.0,
            )
        ]

    @property
    def name(self) -> str:
        return self._name

    async def extract(self, image_data: bytes) -> ExtractionResult:
        """Mock extraction"""
        return ExtractionResult(
            tokens=self._tokens,
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
    extractors = [
        MockExtractor("extractor1"),
        MockExtractor("extractor2"),
    ]

    aggregator = ShadowAggregator(distance_threshold=5.0)
    orchestrator = ShadowExtractionOrchestrator(extractors, aggregator)

    result = await orchestrator.extract_all(b"test_image", "test_image_1")

    assert result.aggregated_tokens is not None
    assert len(result.extraction_results) == 2
    assert len(result.failed_extractors) == 0
    assert result.total_time_ms > 0
    assert result.overall_confidence > 0


@pytest.mark.asyncio
async def test_orchestrator_graceful_degradation():
    """Test that orchestrator continues when one extractor fails"""
    extractors = [
        MockExtractor("good_extractor"),
        FailingExtractor("bad_extractor"),
    ]

    aggregator = ShadowAggregator(distance_threshold=5.0)
    orchestrator = ShadowExtractionOrchestrator(extractors, aggregator)

    result = await orchestrator.extract_all(b"test_image", "test_image_1")

    assert result.aggregated_tokens is not None
    assert len(result.extraction_results) == 1
    assert len(result.failed_extractors) == 1
    assert result.failed_extractors[0][0] == "bad_extractor"


@pytest.mark.asyncio
async def test_orchestrator_aggregates_tokens():
    """Test that orchestrator aggregates tokens from multiple extractors"""
    shadow1 = ShadowStyle(
        color="#000000",
        opacity=0.25,
        x=0.0,
        y=4.0,
        blur=8.0,
        spread=0.0,
    )
    shadow2 = ShadowStyle(
        color="#000000",
        opacity=0.50,
        x=0.0,
        y=8.0,
        blur=16.0,
        spread=0.0,
    )

    extractors = [
        MockExtractor("extractor1", [shadow1]),
        MockExtractor("extractor2", [shadow2]),
    ]

    aggregator = ShadowAggregator(distance_threshold=5.0)
    orchestrator = ShadowExtractionOrchestrator(extractors, aggregator)

    result = await orchestrator.extract_all(b"test_image", "test_image_1")

    assert result.aggregated_tokens is not None
    assert len(result.extraction_results) == 2
    # Shadows are different enough to not be deduplicated
    assert len(result.aggregated_tokens) == 2


@pytest.mark.asyncio
async def test_orchestrator_deduplicates_similar_shadows():
    """Test that similar shadow tokens are deduplicated"""
    shadow1 = ShadowStyle(
        color="#000000",
        opacity=0.25,
        x=0.0,
        y=4.0,
        blur=8.0,
        spread=0.0,
    )
    shadow2 = ShadowStyle(
        color="#000000",
        opacity=0.25,
        x=0.0,
        y=5.0,  # Within threshold
        blur=8.0,
        spread=0.0,
    )

    extractors = [
        MockExtractor("extractor1", [shadow1]),
        MockExtractor("extractor2", [shadow2]),
    ]

    aggregator = ShadowAggregator(distance_threshold=5.0)
    orchestrator = ShadowExtractionOrchestrator(extractors, aggregator)

    result = await orchestrator.extract_all(b"test_image", "test_image_1")

    # Should deduplicate to 1 shadow (distance is 1.0, within 5.0 threshold)
    assert len(result.aggregated_tokens) == 1


@pytest.mark.asyncio
async def test_orchestrator_tracks_failures():
    """Test that orchestrator tracks failed extractors"""
    extractors = [
        FailingExtractor("bad1"),
        FailingExtractor("bad2"),
    ]

    aggregator = ShadowAggregator(distance_threshold=5.0)
    orchestrator = ShadowExtractionOrchestrator(extractors, aggregator)

    result = await orchestrator.extract_all(b"test_image", "test_image_1")

    assert len(result.failed_extractors) == 2
    assert result.extraction_results == []


@pytest.mark.asyncio
async def test_orchestrator_safe_mode():
    """Test safe mode doesn't raise exceptions"""
    extractors = [FailingExtractor("bad")]

    aggregator = ShadowAggregator(distance_threshold=5.0)
    orchestrator = ShadowExtractionOrchestrator(extractors, aggregator)

    result = await orchestrator.extract_all_safe(b"test_image", "test_image_1")

    assert result is not None
    assert len(result.failed_extractors) == 1


@pytest.mark.asyncio
async def test_aggregator_distance_calculation():
    """Test ShadowAggregator distance calculation"""
    aggregator = ShadowAggregator(distance_threshold=5.0)

    shadow1 = ShadowStyle(color="#000000", opacity=0.25, x=0.0, y=0.0, blur=8.0, spread=0.0)
    shadow2 = ShadowStyle(color="#000000", opacity=0.25, x=3.0, y=4.0, blur=8.0, spread=0.0)

    # Distance should be sqrt(3^2 + 4^2) = 5.0
    distance = aggregator._calculate_distance(shadow1, shadow2)
    assert distance == 5.0


@pytest.mark.asyncio
async def test_aggregator_similarity_different_color():
    """Test that shadows with different colors are not deduplicated"""
    aggregator = ShadowAggregator(distance_threshold=5.0)

    shadow1 = ShadowStyle(color="#000000", opacity=0.25, x=0.0, y=4.0, blur=8.0, spread=0.0)
    shadow2 = ShadowStyle(
        color="#FF0000",  # Different color
        opacity=0.25,
        x=0.0,
        y=4.0,
        blur=8.0,
        spread=0.0,
    )

    assert not aggregator._are_similar(shadow1, shadow2)


@pytest.mark.asyncio
async def test_aggregator_similarity_different_opacity():
    """Test that shadows with different opacity are not deduplicated"""
    aggregator = ShadowAggregator(distance_threshold=5.0)

    shadow1 = ShadowStyle(color="#000000", opacity=0.25, x=0.0, y=4.0, blur=8.0, spread=0.0)
    shadow2 = ShadowStyle(
        color="#000000",
        opacity=0.75,  # Different opacity (>0.05 threshold)
        x=0.0,
        y=4.0,
        blur=8.0,
        spread=0.0,
    )

    assert not aggregator._are_similar(shadow1, shadow2)


@pytest.mark.asyncio
async def test_aggregator_provenance_tracking():
    """Test that shadows track which extractors found them"""
    aggregator = ShadowAggregator(distance_threshold=5.0)

    shadow1 = ShadowStyle(color="#000000", opacity=0.25, x=0.0, y=4.0, blur=8.0, spread=0.0)
    shadow2 = ShadowStyle(
        color="#000000",
        opacity=0.25,
        x=0.0,
        y=5.0,
        blur=8.0,
        spread=0.0,  # Similar
    )

    aggregated = aggregator.aggregate_tokens([[shadow1], [shadow2]])

    # Should have 1 deduplicated shadow
    assert len(aggregated) == 1

    # Check provenance tracking
    shadow = aggregated[0]
    assert hasattr(shadow, "extraction_metadata")
    assert "extractor_sources" in shadow.extraction_metadata
    assert len(shadow.extraction_metadata["extractor_sources"]) == 2


@pytest.mark.asyncio
async def test_aggregator_empty_input():
    """Test aggregator handles empty input gracefully"""
    aggregator = ShadowAggregator(distance_threshold=5.0)

    # Empty token list
    result = aggregator.aggregate_tokens([])
    assert result == []

    # List with empty sublists
    result = aggregator.aggregate_tokens([[], []])
    assert result == []


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
