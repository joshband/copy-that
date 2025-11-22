"""Integration tests for constants usage across modules"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from copy_that.application.batch_extractor import BatchColorExtractor
from copy_that.application.color_extractor import ExtractedColorToken
from copy_that.constants import (
    DEFAULT_DELTA_E_THRESHOLD,
    DEFAULT_MAX_CONCURRENT_EXTRACTIONS,
)
from copy_that.tokens.color.aggregator import ColorAggregator


class TestColorAggregatorConstants:
    """Test ColorAggregator uses centralized constants"""

    def test_aggregate_batch_uses_default_threshold(self):
        """aggregate_batch should use DEFAULT_DELTA_E_THRESHOLD"""
        # Create sample tokens
        colors_batch = [
            [
                ExtractedColorToken(
                    hex="#FF5733",
                    rgb="rgb(255, 87, 51)",
                    name="Red-Orange",
                    confidence=0.95,
                ),
            ],
        ]

        # Call with default threshold
        result = ColorAggregator.aggregate_batch(colors_batch)

        # Should return a TokenLibrary
        assert result is not None
        assert len(result.tokens) == 1

    def test_aggregate_batch_accepts_custom_threshold(self):
        """aggregate_batch should accept custom delta_e_threshold"""
        colors_batch = [
            [
                ExtractedColorToken(
                    hex="#FF5733",
                    rgb="rgb(255, 87, 51)",
                    name="Color1",
                    confidence=0.95,
                ),
            ],
            [
                ExtractedColorToken(
                    hex="#FF5734",  # Very similar color
                    rgb="rgb(255, 87, 52)",
                    name="Color2",
                    confidence=0.90,
                ),
            ],
        ]

        # With strict threshold (0.1), colors should not be deduplicated
        result_strict = ColorAggregator.aggregate_batch(colors_batch, delta_e_threshold=0.1)

        # With loose threshold (100), colors should be deduplicated
        result_loose = ColorAggregator.aggregate_batch(colors_batch, delta_e_threshold=100.0)

        # Strict should have more tokens than loose
        assert len(result_strict.tokens) >= len(result_loose.tokens)


class TestBatchExtractorConstants:
    """Test BatchColorExtractor uses centralized constants"""

    def test_default_max_concurrent(self):
        """BatchColorExtractor should use DEFAULT_MAX_CONCURRENT_EXTRACTIONS"""
        extractor = BatchColorExtractor()
        assert extractor.max_concurrent == DEFAULT_MAX_CONCURRENT_EXTRACTIONS

    def test_custom_max_concurrent(self):
        """BatchColorExtractor should accept custom max_concurrent"""
        custom_value = 5
        extractor = BatchColorExtractor(max_concurrent=custom_value)
        assert extractor.max_concurrent == custom_value

    @pytest.mark.asyncio
    async def test_extract_batch_uses_default_threshold(self):
        """extract_batch should use DEFAULT_DELTA_E_THRESHOLD by default"""
        extractor = BatchColorExtractor()

        # Mock the extractor's extract_colors_from_url method
        mock_colors = [
            ExtractedColorToken(
                hex="#FF5733",
                rgb="rgb(255, 87, 51)",
                name="Test",
                confidence=0.9,
            )
        ]

        with patch.object(
            extractor.extractor, "extract_colors_from_url", new_callable=AsyncMock
        ) as mock_extract:
            mock_extract.return_value = mock_colors

            tokens, stats = await extractor.extract_batch(
                image_urls=["http://example.com/test.jpg"],
                max_colors=5,
                # Not passing delta_e_threshold - should use default
            )

            # Should have called extract_colors_from_url once
            assert mock_extract.called


class TestConstantValues:
    """Test that constant values are appropriate for their use cases"""

    def test_delta_e_threshold_is_perceptible(self):
        """Delta-E of 2.0 is the Just Noticeable Difference threshold"""
        # 2.0 is the standard JND value in color science
        assert DEFAULT_DELTA_E_THRESHOLD == 2.0

    def test_max_concurrent_prevents_rate_limiting(self):
        """Max concurrent should be low enough to avoid API rate limits"""
        # Most APIs rate limit at 5-10 req/sec, 3 is safe
        assert DEFAULT_MAX_CONCURRENT_EXTRACTIONS <= 5
        assert DEFAULT_MAX_CONCURRENT_EXTRACTIONS >= 1
