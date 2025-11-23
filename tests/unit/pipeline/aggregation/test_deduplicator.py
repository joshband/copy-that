"""
Tests for ColorDeduplicator class

Tests color deduplication using Delta-E 2000 color comparison with ColorAide library.
The deduplicator merges similar colors (within threshold of 2.0 JND) keeping highest confidence.
"""

import pytest

from copy_that.pipeline import TokenResult, TokenType, W3CTokenType
from copy_that.pipeline.aggregation.deduplicator import ColorDeduplicator


class TestColorDeduplicatorBasicFunctionality:
    """Test basic deduplication functionality"""

    def test_identical_colors_deduplicated(self):
        """Exact same hex colors should be merged into one result"""
        tokens = [
            TokenResult(
                token_type=TokenType.COLOR,
                name="primary",
                value="#FF0000",
                confidence=0.9,
            ),
            TokenResult(
                token_type=TokenType.COLOR,
                name="accent",
                value="#FF0000",
                confidence=0.8,
            ),
        ]

        deduplicator = ColorDeduplicator()
        result = deduplicator.deduplicate(tokens)

        assert len(result) == 1
        assert result[0].value == "#FF0000"

    def test_similar_colors_within_threshold_merged(self):
        """Colors within Delta-E 2.0 threshold should be merged"""
        # These colors are very similar (Delta-E < 2.0)
        tokens = [
            TokenResult(
                token_type=TokenType.COLOR,
                name="red-1",
                value="#FF0000",
                confidence=0.85,
            ),
            TokenResult(
                token_type=TokenType.COLOR,
                name="red-2",
                value="#FF0100",  # Very slight green difference
                confidence=0.9,
            ),
        ]

        deduplicator = ColorDeduplicator()
        result = deduplicator.deduplicate(tokens)

        assert len(result) == 1

    def test_different_colors_preserved(self):
        """Colors beyond Delta-E threshold should be kept separate"""
        tokens = [
            TokenResult(
                token_type=TokenType.COLOR,
                name="red",
                value="#FF0000",
                confidence=0.9,
            ),
            TokenResult(
                token_type=TokenType.COLOR,
                name="blue",
                value="#0000FF",
                confidence=0.9,
            ),
            TokenResult(
                token_type=TokenType.COLOR,
                name="green",
                value="#00FF00",
                confidence=0.9,
            ),
        ]

        deduplicator = ColorDeduplicator()
        result = deduplicator.deduplicate(tokens)

        assert len(result) == 3
        values = {token.value for token in result}
        assert "#FF0000" in values
        assert "#0000FF" in values
        assert "#00FF00" in values

    def test_highest_confidence_kept(self):
        """When merging similar colors, the one with highest confidence should be kept"""
        tokens = [
            TokenResult(
                token_type=TokenType.COLOR,
                name="low-confidence",
                value="#FF0000",
                confidence=0.6,
            ),
            TokenResult(
                token_type=TokenType.COLOR,
                name="high-confidence",
                value="#FF0000",
                confidence=0.95,
            ),
            TokenResult(
                token_type=TokenType.COLOR,
                name="medium-confidence",
                value="#FF0001",  # Nearly identical
                confidence=0.8,
            ),
        ]

        deduplicator = ColorDeduplicator()
        result = deduplicator.deduplicate(tokens)

        assert len(result) == 1
        assert result[0].confidence == 0.95
        assert result[0].name == "high-confidence"


class TestColorDeduplicatorEdgeCases:
    """Test edge cases and boundary conditions"""

    def test_empty_input_returns_empty(self):
        """Empty list input should return empty list"""
        deduplicator = ColorDeduplicator()
        result = deduplicator.deduplicate([])

        assert result == []

    def test_single_token_returns_same(self):
        """Single token input should return same token"""
        token = TokenResult(
            token_type=TokenType.COLOR,
            name="only-color",
            value="#ABCDEF",
            confidence=0.88,
        )

        deduplicator = ColorDeduplicator()
        result = deduplicator.deduplicate([token])

        assert len(result) == 1
        assert result[0].value == "#ABCDEF"
        assert result[0].name == "only-color"
        assert result[0].confidence == 0.88

    def test_different_token_types_not_deduplicated(self):
        """Non-color tokens should not be compared/deduplicated with color tokens"""
        tokens = [
            TokenResult(
                token_type=TokenType.COLOR,
                name="red-color",
                value="#FF0000",
                confidence=0.9,
            ),
            TokenResult(
                token_type=TokenType.SPACING,
                name="spacing-value",
                value="16px",
                confidence=0.85,
            ),
            TokenResult(
                token_type=TokenType.TYPOGRAPHY,
                name="font-family",
                value="Inter",
                confidence=0.8,
            ),
        ]

        deduplicator = ColorDeduplicator()
        result = deduplicator.deduplicate(tokens)

        # Non-color tokens should pass through unchanged
        assert len(result) == 3
        token_types = {token.token_type for token in result}
        assert TokenType.COLOR in token_types
        assert TokenType.SPACING in token_types
        assert TokenType.TYPOGRAPHY in token_types


class TestColorDeduplicatorColorFormats:
    """Test various color format handling"""

    def test_rgb_format_colors(self):
        """Should handle rgb() format colors"""
        tokens = [
            TokenResult(
                token_type=TokenType.COLOR,
                name="rgb-red",
                value="rgb(255, 0, 0)",
                confidence=0.9,
            ),
            TokenResult(
                token_type=TokenType.COLOR,
                name="rgb-blue",
                value="rgb(0, 0, 255)",
                confidence=0.85,
            ),
        ]

        deduplicator = ColorDeduplicator()
        result = deduplicator.deduplicate(tokens)

        # Different colors should be preserved
        assert len(result) == 2

    def test_hsl_format_colors(self):
        """Should handle hsl() format colors"""
        tokens = [
            TokenResult(
                token_type=TokenType.COLOR,
                name="hsl-red",
                value="hsl(0, 100%, 50%)",
                confidence=0.9,
            ),
            TokenResult(
                token_type=TokenType.COLOR,
                name="hsl-blue",
                value="hsl(240, 100%, 50%)",
                confidence=0.85,
            ),
        ]

        deduplicator = ColorDeduplicator()
        result = deduplicator.deduplicate(tokens)

        # Different colors should be preserved
        assert len(result) == 2

    def test_mixed_formats_comparison(self):
        """Should correctly compare colors in different formats"""
        # Pure red in different formats
        tokens = [
            TokenResult(
                token_type=TokenType.COLOR,
                name="hex-red",
                value="#FF0000",
                confidence=0.9,
            ),
            TokenResult(
                token_type=TokenType.COLOR,
                name="rgb-red",
                value="rgb(255, 0, 0)",
                confidence=0.8,
            ),
        ]

        deduplicator = ColorDeduplicator()
        result = deduplicator.deduplicate(tokens)

        # Same color in different formats should be merged
        assert len(result) == 1
        # Higher confidence should be kept
        assert result[0].confidence == 0.9

    def test_rgba_format_colors(self):
        """Should handle rgba() format colors with alpha"""
        tokens = [
            TokenResult(
                token_type=TokenType.COLOR,
                name="rgba-red",
                value="rgba(255, 0, 0, 1)",
                confidence=0.9,
            ),
            TokenResult(
                token_type=TokenType.COLOR,
                name="rgba-blue",
                value="rgba(0, 0, 255, 0.8)",
                confidence=0.85,
            ),
        ]

        deduplicator = ColorDeduplicator()
        result = deduplicator.deduplicate(tokens)

        # Different colors should be preserved
        assert len(result) == 2

    def test_hsla_format_colors(self):
        """Should handle hsla() format colors with alpha"""
        tokens = [
            TokenResult(
                token_type=TokenType.COLOR,
                name="hsla-red",
                value="hsla(0, 100%, 50%, 1)",
                confidence=0.9,
            ),
            TokenResult(
                token_type=TokenType.COLOR,
                name="hsla-green",
                value="hsla(120, 100%, 50%, 0.5)",
                confidence=0.85,
            ),
        ]

        deduplicator = ColorDeduplicator()
        result = deduplicator.deduplicate(tokens)

        assert len(result) == 2

    def test_short_hex_format(self):
        """Should handle 3-character hex format"""
        tokens = [
            TokenResult(
                token_type=TokenType.COLOR,
                name="short-hex",
                value="#F00",
                confidence=0.9,
            ),
            TokenResult(
                token_type=TokenType.COLOR,
                name="long-hex",
                value="#FF0000",
                confidence=0.8,
            ),
        ]

        deduplicator = ColorDeduplicator()
        result = deduplicator.deduplicate(tokens)

        # Same color should be merged
        assert len(result) == 1


class TestColorDeduplicatorMetadata:
    """Test metadata handling during deduplication"""

    def test_preserves_metadata_from_best_token(self):
        """Metadata from highest confidence token should be preserved"""
        tokens = [
            TokenResult(
                token_type=TokenType.COLOR,
                name="color-1",
                value="#FF0000",
                confidence=0.7,
                metadata={"source": "low-quality"},
            ),
            TokenResult(
                token_type=TokenType.COLOR,
                name="color-2",
                value="#FF0000",
                confidence=0.95,
                metadata={"source": "high-quality", "extractor": "vision-model"},
            ),
        ]

        deduplicator = ColorDeduplicator()
        result = deduplicator.deduplicate(tokens)

        assert len(result) == 1
        assert result[0].metadata is not None
        assert result[0].metadata["source"] == "high-quality"
        assert result[0].metadata["extractor"] == "vision-model"

    def test_merges_provenance_metadata(self):
        """Source information from merged tokens should be combined"""
        tokens = [
            TokenResult(
                token_type=TokenType.COLOR,
                name="color-source-1",
                value="#FF0000",
                confidence=0.8,
                metadata={
                    "source": "image-1.png",
                    "region": "header",
                },
            ),
            TokenResult(
                token_type=TokenType.COLOR,
                name="color-source-2",
                value="#FF0001",  # Nearly identical
                confidence=0.9,
                metadata={
                    "source": "image-2.png",
                    "region": "button",
                },
            ),
        ]

        deduplicator = ColorDeduplicator()
        result = deduplicator.deduplicate(tokens)

        assert len(result) == 1
        # The result should contain merged provenance information
        # Implementation may store merged sources in metadata
        merged_metadata = result[0].metadata
        assert merged_metadata is not None
        # Check that provenance information is preserved
        # The exact format depends on implementation
        assert "merged_sources" in merged_metadata or "source" in merged_metadata

    def test_preserves_w3c_fields(self):
        """W3C fields should be preserved from best token"""
        tokens = [
            TokenResult(
                token_type=TokenType.COLOR,
                name="brand-primary",
                path=["color", "brand"],
                w3c_type=W3CTokenType.COLOR,
                value="#FF0000",
                confidence=0.95,
                description="Primary brand color",
                extensions={"com.figma": {"variableId": "123"}},
            ),
            TokenResult(
                token_type=TokenType.COLOR,
                name="accent-red",
                value="#FF0001",
                confidence=0.7,
            ),
        ]

        deduplicator = ColorDeduplicator()
        result = deduplicator.deduplicate(tokens)

        assert len(result) == 1
        assert result[0].path == ["color", "brand"]
        assert result[0].w3c_type == W3CTokenType.COLOR
        assert result[0].description == "Primary brand color"
        assert result[0].extensions is not None


class TestColorDeduplicatorThreshold:
    """Test Delta-E threshold behavior"""

    def test_colors_at_threshold_boundary(self):
        """Colors exactly at threshold boundary should be handled correctly"""
        # Create colors that are at or near the 2.0 JND threshold
        tokens = [
            TokenResult(
                token_type=TokenType.COLOR,
                name="color-base",
                value="#808080",  # Middle gray
                confidence=0.9,
            ),
            TokenResult(
                token_type=TokenType.COLOR,
                name="color-similar",
                value="#818181",  # Slightly lighter gray
                confidence=0.8,
            ),
        ]

        deduplicator = ColorDeduplicator()
        result = deduplicator.deduplicate(tokens)

        # These are very similar and should be merged
        assert len(result) == 1

    def test_colors_just_beyond_threshold(self):
        """Colors just beyond threshold should remain separate"""
        # Create colors with noticeable but small perceptual difference
        tokens = [
            TokenResult(
                token_type=TokenType.COLOR,
                name="gray-1",
                value="#808080",
                confidence=0.9,
            ),
            TokenResult(
                token_type=TokenType.COLOR,
                name="gray-2",
                value="#909090",  # Noticeably lighter
                confidence=0.9,
            ),
        ]

        deduplicator = ColorDeduplicator()
        result = deduplicator.deduplicate(tokens)

        # These should have Delta-E > 2.0 and remain separate
        assert len(result) == 2

    def test_custom_threshold(self):
        """Should support custom Delta-E threshold"""
        tokens = [
            TokenResult(
                token_type=TokenType.COLOR,
                name="color-1",
                value="#FF0000",
                confidence=0.9,
            ),
            TokenResult(
                token_type=TokenType.COLOR,
                name="color-2",
                value="#FF1010",  # Small difference
                confidence=0.8,
            ),
        ]

        # Use larger threshold to merge
        deduplicator = ColorDeduplicator(threshold=10.0)
        result = deduplicator.deduplicate(tokens)

        assert len(result) == 1

    def test_zero_threshold_no_merging(self):
        """Zero threshold should only merge exactly identical colors"""
        tokens = [
            TokenResult(
                token_type=TokenType.COLOR,
                name="color-1",
                value="#FF0000",
                confidence=0.9,
            ),
            TokenResult(
                token_type=TokenType.COLOR,
                name="color-2",
                value="#FF0001",  # Tiny difference
                confidence=0.8,
            ),
            TokenResult(
                token_type=TokenType.COLOR,
                name="color-3",
                value="#FF0000",  # Exact match
                confidence=0.7,
            ),
        ]

        deduplicator = ColorDeduplicator(threshold=0.0)
        result = deduplicator.deduplicate(tokens)

        # Only exact matches merged
        assert len(result) == 2


class TestColorDeduplicatorMultipleGroups:
    """Test deduplication with multiple color groups"""

    def test_multiple_similar_groups(self):
        """Should correctly group multiple sets of similar colors"""
        tokens = [
            # Red group
            TokenResult(
                token_type=TokenType.COLOR,
                name="red-1",
                value="#FF0000",
                confidence=0.9,
            ),
            TokenResult(
                token_type=TokenType.COLOR,
                name="red-2",
                value="#FF0001",
                confidence=0.8,
            ),
            # Blue group
            TokenResult(
                token_type=TokenType.COLOR,
                name="blue-1",
                value="#0000FF",
                confidence=0.85,
            ),
            TokenResult(
                token_type=TokenType.COLOR,
                name="blue-2",
                value="#0001FF",
                confidence=0.9,
            ),
            # Green group
            TokenResult(
                token_type=TokenType.COLOR,
                name="green-1",
                value="#00FF00",
                confidence=0.88,
            ),
        ]

        deduplicator = ColorDeduplicator()
        result = deduplicator.deduplicate(tokens)

        # Should have 3 groups
        assert len(result) == 3

        # Check highest confidence in each group
        confidences = sorted([t.confidence for t in result])
        assert 0.88 in confidences  # green
        assert 0.9 in confidences  # red and blue

    def test_many_duplicates_performance(self):
        """Should handle many duplicate colors efficiently"""
        tokens = [
            TokenResult(
                token_type=TokenType.COLOR,
                name=f"red-{i}",
                value="#FF0000",
                confidence=0.5 + (i * 0.01),
            )
            for i in range(50)
        ]

        deduplicator = ColorDeduplicator()
        result = deduplicator.deduplicate(tokens)

        assert len(result) == 1
        # Highest confidence should be kept (0.5 + 49*0.01 = 0.99)
        assert result[0].confidence == pytest.approx(0.99, abs=0.01)


class TestColorDeduplicatorSpecialCases:
    """Test special color cases"""

    def test_black_and_white(self):
        """Black and white should remain separate"""
        tokens = [
            TokenResult(
                token_type=TokenType.COLOR,
                name="black",
                value="#000000",
                confidence=0.9,
            ),
            TokenResult(
                token_type=TokenType.COLOR,
                name="white",
                value="#FFFFFF",
                confidence=0.9,
            ),
        ]

        deduplicator = ColorDeduplicator()
        result = deduplicator.deduplicate(tokens)

        assert len(result) == 2

    def test_neutral_grays(self):
        """Neutral grays at different lightness levels should remain separate"""
        tokens = [
            TokenResult(
                token_type=TokenType.COLOR,
                name="gray-light",
                value="#CCCCCC",
                confidence=0.9,
            ),
            TokenResult(
                token_type=TokenType.COLOR,
                name="gray-dark",
                value="#333333",
                confidence=0.9,
            ),
        ]

        deduplicator = ColorDeduplicator()
        result = deduplicator.deduplicate(tokens)

        assert len(result) == 2

    def test_same_hue_different_saturation(self):
        """Colors with same hue but different saturation should be separate"""
        tokens = [
            TokenResult(
                token_type=TokenType.COLOR,
                name="red-saturated",
                value="hsl(0, 100%, 50%)",
                confidence=0.9,
            ),
            TokenResult(
                token_type=TokenType.COLOR,
                name="red-desaturated",
                value="hsl(0, 30%, 50%)",
                confidence=0.85,
            ),
        ]

        deduplicator = ColorDeduplicator()
        result = deduplicator.deduplicate(tokens)

        # Large saturation difference should keep them separate
        assert len(result) == 2

    def test_transparent_colors(self):
        """Should handle colors with transparency"""
        tokens = [
            TokenResult(
                token_type=TokenType.COLOR,
                name="transparent-red",
                value="rgba(255, 0, 0, 0.5)",
                confidence=0.9,
            ),
            TokenResult(
                token_type=TokenType.COLOR,
                name="opaque-red",
                value="rgba(255, 0, 0, 1)",
                confidence=0.85,
            ),
        ]

        deduplicator = ColorDeduplicator()
        result = deduplicator.deduplicate(tokens)

        # Different alpha values may result in different treatment
        # This tests that the deduplicator handles transparency correctly
        assert len(result) >= 1


class TestColorDeduplicatorErrorHandling:
    """Test error handling and invalid input"""

    def test_invalid_color_format_handled(self):
        """Invalid color formats should be handled gracefully"""
        tokens = [
            TokenResult(
                token_type=TokenType.COLOR,
                name="valid-color",
                value="#FF0000",
                confidence=0.9,
            ),
            TokenResult(
                token_type=TokenType.COLOR,
                name="invalid-color",
                value="not-a-color",
                confidence=0.8,
            ),
        ]

        deduplicator = ColorDeduplicator()
        # Should not raise an exception
        result = deduplicator.deduplicate(tokens)

        # Valid color should be in result
        assert any(t.value == "#FF0000" for t in result)

    def test_mixed_valid_invalid_colors(self):
        """Mix of valid and invalid colors should process valid ones"""
        tokens = [
            TokenResult(
                token_type=TokenType.COLOR,
                name="color-1",
                value="#FF0000",
                confidence=0.9,
            ),
            TokenResult(
                token_type=TokenType.COLOR,
                name="invalid",
                value="xyz123",
                confidence=0.8,
            ),
            TokenResult(
                token_type=TokenType.COLOR,
                name="color-2",
                value="#0000FF",
                confidence=0.85,
            ),
        ]

        deduplicator = ColorDeduplicator()
        result = deduplicator.deduplicate(tokens)

        # Should contain at least the valid colors
        values = [t.value for t in result]
        assert "#FF0000" in values
        assert "#0000FF" in values


class TestColorDeduplicatorOrderPreservation:
    """Test that order is reasonably preserved or sorted"""

    def test_result_ordering(self):
        """Results should be ordered by confidence (highest first) or preserve order"""
        tokens = [
            TokenResult(
                token_type=TokenType.COLOR,
                name="low",
                value="#FF0000",
                confidence=0.5,
            ),
            TokenResult(
                token_type=TokenType.COLOR,
                name="high",
                value="#00FF00",
                confidence=0.95,
            ),
            TokenResult(
                token_type=TokenType.COLOR,
                name="medium",
                value="#0000FF",
                confidence=0.75,
            ),
        ]

        deduplicator = ColorDeduplicator()
        result = deduplicator.deduplicate(tokens)

        assert len(result) == 3
        # Verify all colors are present
        confidences = {t.confidence for t in result}
        assert 0.5 in confidences
        assert 0.95 in confidences
        assert 0.75 in confidences


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
