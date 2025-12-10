"""Test suite for SpacingExtractionOrchestrator"""

import pytest

from .base import ExtractionResult
from .models import SpacingToken
from .orchestrator import SpacingAggregator, SpacingExtractionOrchestrator


class MockExtractor:
    """Mock extractor for testing"""

    def __init__(self, name: str, tokens: list[SpacingToken] | None = None):
        self._name = name
        self._tokens = tokens or [
            SpacingToken(
                value_px=16,
                name="spacing-md",
                confidence=0.95,
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
    # Create mock extractors
    extractors = [
        MockExtractor("extractor1"),
        MockExtractor("extractor2"),
    ]

    aggregator = SpacingAggregator(pixel_distance_threshold=4.0)
    orchestrator = SpacingExtractionOrchestrator(extractors, aggregator)

    # Run orchestration
    result = await orchestrator.extract_all(b"test_image", "test_image_1")

    # Verify results
    assert result.aggregated_tokens is not None
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

    aggregator = SpacingAggregator(pixel_distance_threshold=4.0)
    orchestrator = SpacingExtractionOrchestrator(extractors, aggregator)

    # Run orchestration
    result = await orchestrator.extract_all(b"test_image", "test_image_1")

    # Verify results
    assert result.aggregated_tokens is not None
    assert len(result.extraction_results) == 1  # Only good extractor
    assert len(result.failed_extractors) == 1  # One failure
    assert result.failed_extractors[0][0] == "bad_extractor"


@pytest.mark.asyncio
async def test_orchestrator_aggregates_tokens():
    """Test that orchestrator aggregates tokens from multiple extractors"""
    # Create extractors with different spacing values
    token_16 = SpacingToken(value_px=16, name="spacing-md", confidence=0.95)
    token_32 = SpacingToken(value_px=32, name="spacing-lg", confidence=0.90)

    extractors = [
        MockExtractor("extractor1", [token_16]),
        MockExtractor("extractor2", [token_32]),
    ]

    aggregator = SpacingAggregator(pixel_distance_threshold=4.0)
    orchestrator = SpacingExtractionOrchestrator(extractors, aggregator)

    # Run orchestration
    result = await orchestrator.extract_all(b"test_image", "test_image_1")

    # Verify aggregation
    assert result.aggregated_tokens is not None
    # Should have 2 unique spacing values (16 and 32 are >4px apart)
    assert len(result.extraction_results) == 2
    assert len(result.aggregated_tokens) == 2


@pytest.mark.asyncio
async def test_orchestrator_deduplicates_similar_tokens():
    """Test that similar spacing tokens are deduplicated"""
    # Create extractors with similar spacing values (within 4px threshold)
    token_16 = SpacingToken(value_px=16, name="spacing-16", confidence=0.95)
    token_18 = SpacingToken(value_px=18, name="spacing-18", confidence=0.90)

    extractors = [
        MockExtractor("extractor1", [token_16]),
        MockExtractor("extractor2", [token_18]),
    ]

    aggregator = SpacingAggregator(pixel_distance_threshold=4.0)
    orchestrator = SpacingExtractionOrchestrator(extractors, aggregator)

    # Run orchestration
    result = await orchestrator.extract_all(b"test_image", "test_image_1")

    # Should deduplicate to 1 token (16 and 18 are within 4px)
    assert len(result.aggregated_tokens) == 1
    # Should keep the higher confidence one (16 with 0.95)
    assert result.aggregated_tokens[0].value_px == 16


@pytest.mark.asyncio
async def test_orchestrator_tracks_failures():
    """Test that orchestrator tracks failed extractors"""
    extractors = [
        FailingExtractor("bad1"),
        FailingExtractor("bad2"),
    ]

    aggregator = SpacingAggregator(pixel_distance_threshold=4.0)
    orchestrator = SpacingExtractionOrchestrator(extractors, aggregator)

    # Run orchestration
    result = await orchestrator.extract_all(b"test_image", "test_image_1")

    # Verify all failures tracked
    assert len(result.failed_extractors) == 2
    assert result.extraction_results == []


@pytest.mark.asyncio
async def test_orchestrator_safe_mode():
    """Test safe mode doesn't raise exceptions"""
    extractors = [FailingExtractor("bad")]

    aggregator = SpacingAggregator(pixel_distance_threshold=4.0)
    orchestrator = SpacingExtractionOrchestrator(extractors, aggregator)

    # Safe mode should not raise
    result = await orchestrator.extract_all_safe(b"test_image", "test_image_1")

    # Verify no exceptions raised
    assert result is not None
    assert len(result.failed_extractors) == 1


@pytest.mark.asyncio
async def test_aggregator_deduplication_logic():
    """Test SpacingAggregator deduplication logic"""
    aggregator = SpacingAggregator(pixel_distance_threshold=4.0)

    # Create tokens with various spacing values
    tokens1 = [
        SpacingToken(value_px=8, name="spacing-8", confidence=0.90),
        SpacingToken(value_px=16, name="spacing-16", confidence=0.95),
    ]
    tokens2 = [
        SpacingToken(value_px=10, name="spacing-10", confidence=0.85),  # Similar to 8
        SpacingToken(value_px=32, name="spacing-32", confidence=0.92),  # Different
    ]

    tokens_by_extractor = [tokens1, tokens2]
    aggregated = aggregator.aggregate_tokens(tokens_by_extractor)

    # Should have 3 unique tokens: 8 (merged with 10), 16, 32
    assert len(aggregated) == 3

    # Find the 8px token (highest confidence from merge)
    token_8 = next(t for t in aggregated if t.value_px == 8)
    assert token_8.confidence >= 0.90

    # Verify provenance tracking
    assert "extractor_sources" in token_8.extraction_metadata
    assert len(token_8.extraction_metadata["extractor_sources"]) >= 1


@pytest.mark.asyncio
async def test_aggregator_confidence_boosting():
    """Test that confidence is boosted when multiple extractors find same token"""
    aggregator = SpacingAggregator(pixel_distance_threshold=4.0)

    # Create identical tokens from two extractors
    tokens1 = [SpacingToken(value_px=16, name="spacing-16", confidence=0.80)]
    tokens2 = [SpacingToken(value_px=16, name="spacing-16-dup", confidence=0.75)]

    aggregated = aggregator.aggregate_tokens([tokens1, tokens2])

    # Should have 1 token with boosted confidence
    assert len(aggregated) == 1
    # Confidence should be boosted: 0.80 + 0.75 * 0.1 = 0.875
    assert aggregated[0].confidence > 0.80


@pytest.mark.asyncio
async def test_orchestrator_provenance_tracking():
    """Test that tokens track which extractors found them"""
    # Create extractors with overlapping tokens
    token_16_a = SpacingToken(value_px=16, name="spacing-16-a", confidence=0.95)
    token_16_b = SpacingToken(value_px=17, name="spacing-16-b", confidence=0.90)  # Similar

    extractors = [
        MockExtractor("extractor1", [token_16_a]),
        MockExtractor("extractor2", [token_16_b]),
    ]

    aggregator = SpacingAggregator(pixel_distance_threshold=4.0)
    orchestrator = SpacingExtractionOrchestrator(extractors, aggregator)

    result = await orchestrator.extract_all(b"test_image", "test_image_1")

    # Should have 1 deduplicated token
    assert len(result.aggregated_tokens) == 1

    # Check provenance tracking
    token = result.aggregated_tokens[0]
    assert "extractor_sources" in token.extraction_metadata
    # Should list both extractor indices
    assert len(token.extraction_metadata["extractor_sources"]) == 2


@pytest.mark.asyncio
async def test_aggregator_empty_input():
    """Test aggregator handles empty input gracefully"""
    aggregator = SpacingAggregator(pixel_distance_threshold=4.0)

    # Empty token list
    result = aggregator.aggregate_tokens([])
    assert result == []

    # List with empty sublists
    result = aggregator.aggregate_tokens([[], []])
    assert result == []


@pytest.mark.asyncio
async def test_aggregator_single_extractor():
    """Test aggregator works with single extractor"""
    aggregator = SpacingAggregator(pixel_distance_threshold=4.0)

    tokens = [
        SpacingToken(value_px=8, name="spacing-8", confidence=0.90),
        SpacingToken(value_px=16, name="spacing-16", confidence=0.95),
    ]

    result = aggregator.aggregate_tokens([tokens])
    assert len(result) == 2
    assert all(t.value_px in [8, 16] for t in result)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
