"""Test suite for TypographyExtractionOrchestrator"""

import pytest

from .ai_extractor import ExtractedTypographyToken
from .base import ExtractionResult
from .orchestrator import TypographyAggregator, TypographyExtractionOrchestrator


class MockExtractor:
    """Mock extractor for testing"""

    def __init__(self, name: str, tokens: list[ExtractedTypographyToken] | None = None):
        self._name = name
        self._tokens = tokens or [
            ExtractedTypographyToken(
                font_family="Inter",
                font_weight=400,
                font_size=16,
                line_height=1.5,
                semantic_role="body",
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
    extractors = [
        MockExtractor("extractor1"),
        MockExtractor("extractor2"),
    ]

    aggregator = TypographyAggregator(font_size_threshold=3)
    orchestrator = TypographyExtractionOrchestrator(extractors, aggregator)

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

    aggregator = TypographyAggregator(font_size_threshold=3)
    orchestrator = TypographyExtractionOrchestrator(extractors, aggregator)

    result = await orchestrator.extract_all(b"test_image", "test_image_1")

    assert result.aggregated_tokens is not None
    assert len(result.extraction_results) == 1
    assert len(result.failed_extractors) == 1
    assert result.failed_extractors[0][0] == "bad_extractor"


@pytest.mark.asyncio
async def test_orchestrator_aggregates_tokens():
    """Test that orchestrator aggregates tokens from multiple extractors"""
    token_body = ExtractedTypographyToken(
        font_family="Inter",
        font_weight=400,
        font_size=16,
        line_height=1.5,
        semantic_role="body",
        confidence=0.95,
    )
    token_heading = ExtractedTypographyToken(
        font_family="Inter",
        font_weight=700,
        font_size=32,
        line_height=1.2,
        semantic_role="heading",
        confidence=0.90,
    )

    extractors = [
        MockExtractor("extractor1", [token_body]),
        MockExtractor("extractor2", [token_heading]),
    ]

    aggregator = TypographyAggregator(font_size_threshold=3)
    orchestrator = TypographyExtractionOrchestrator(extractors, aggregator)

    result = await orchestrator.extract_all(b"test_image", "test_image_1")

    assert result.aggregated_tokens is not None
    assert len(result.extraction_results) == 2
    assert len(result.aggregated_tokens) == 2


@pytest.mark.asyncio
async def test_orchestrator_deduplicates_similar_tokens():
    """Test that similar typography tokens are deduplicated"""
    token_16 = ExtractedTypographyToken(
        font_family="Inter",
        font_weight=400,
        font_size=16,
        line_height=1.5,
        semantic_role="body",
        confidence=0.95,
    )
    token_18 = ExtractedTypographyToken(
        font_family="Inter",
        font_weight=400,
        font_size=18,  # Within 3px threshold
        line_height=1.5,
        semantic_role="body",
        confidence=0.90,
    )

    extractors = [
        MockExtractor("extractor1", [token_16]),
        MockExtractor("extractor2", [token_18]),
    ]

    aggregator = TypographyAggregator(font_size_threshold=3)
    orchestrator = TypographyExtractionOrchestrator(extractors, aggregator)

    result = await orchestrator.extract_all(b"test_image", "test_image_1")

    # Should deduplicate to 1 token
    assert len(result.aggregated_tokens) == 1
    # Should keep the higher confidence one (16px with 0.95)
    assert result.aggregated_tokens[0].font_size == 16


@pytest.mark.asyncio
async def test_orchestrator_tracks_failures():
    """Test that orchestrator tracks failed extractors"""
    extractors = [
        FailingExtractor("bad1"),
        FailingExtractor("bad2"),
    ]

    aggregator = TypographyAggregator(font_size_threshold=3)
    orchestrator = TypographyExtractionOrchestrator(extractors, aggregator)

    result = await orchestrator.extract_all(b"test_image", "test_image_1")

    assert len(result.failed_extractors) == 2
    assert result.extraction_results == []


@pytest.mark.asyncio
async def test_orchestrator_safe_mode():
    """Test safe mode doesn't raise exceptions"""
    extractors = [FailingExtractor("bad")]

    aggregator = TypographyAggregator(font_size_threshold=3)
    orchestrator = TypographyExtractionOrchestrator(extractors, aggregator)

    result = await orchestrator.extract_all_safe(b"test_image", "test_image_1")

    assert result is not None
    assert len(result.failed_extractors) == 1


@pytest.mark.asyncio
async def test_aggregator_similarity_logic():
    """Test TypographyAggregator similarity logic"""
    aggregator = TypographyAggregator(font_size_threshold=3)

    # Similar tokens (same family, weight, size within threshold, same role)
    token1 = ExtractedTypographyToken(
        font_family="Inter",
        font_weight=400,
        font_size=16,
        line_height=1.5,
        semantic_role="body",
        confidence=0.95,
    )
    token2 = ExtractedTypographyToken(
        font_family="Inter",
        font_weight=400,
        font_size=18,  # Within 3px
        line_height=1.5,
        semantic_role="body",
        confidence=0.90,
    )

    assert aggregator._are_similar(token1, token2)


@pytest.mark.asyncio
async def test_aggregator_different_family():
    """Test that different font families are not deduplicated"""
    aggregator = TypographyAggregator(font_size_threshold=3)

    token1 = ExtractedTypographyToken(
        font_family="Inter",
        font_weight=400,
        font_size=16,
        line_height=1.5,
        semantic_role="body",
        confidence=0.95,
    )
    token2 = ExtractedTypographyToken(
        font_family="Roboto",  # Different family
        font_weight=400,
        font_size=16,
        line_height=1.5,
        semantic_role="body",
        confidence=0.90,
    )

    assert not aggregator._are_similar(token1, token2)


@pytest.mark.asyncio
async def test_aggregator_different_weight():
    """Test that different font weights are not deduplicated"""
    aggregator = TypographyAggregator(font_size_threshold=3)

    token1 = ExtractedTypographyToken(
        font_family="Inter",
        font_weight=400,
        font_size=16,
        line_height=1.5,
        semantic_role="body",
        confidence=0.95,
    )
    token2 = ExtractedTypographyToken(
        font_family="Inter",
        font_weight=700,  # Different weight
        font_size=16,
        line_height=1.5,
        semantic_role="body",
        confidence=0.90,
    )

    assert not aggregator._are_similar(token1, token2)


@pytest.mark.asyncio
async def test_aggregator_provenance_tracking():
    """Test that tokens track which extractors found them"""
    aggregator = TypographyAggregator(font_size_threshold=3)

    token1 = ExtractedTypographyToken(
        font_family="Inter",
        font_weight=400,
        font_size=16,
        line_height=1.5,
        semantic_role="body",
        confidence=0.95,
    )
    token2 = ExtractedTypographyToken(
        font_family="Inter",
        font_weight=400,
        font_size=17,  # Similar
        line_height=1.5,
        semantic_role="body",
        confidence=0.90,
    )

    aggregated = aggregator.aggregate_tokens([[token1], [token2]])

    # Should have 1 deduplicated token
    assert len(aggregated) == 1

    # Check provenance tracking
    token = aggregated[0]
    assert "extractor_sources" in token.extraction_metadata
    assert len(token.extraction_metadata["extractor_sources"]) == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
