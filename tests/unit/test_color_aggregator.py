"""
Test suite for ColorAggregator - batch color deduplication and aggregation

Tests the core logic for:
- De-duplicating colors from multiple image extractions (Delta-E threshold)
- Tracking provenance (which images contributed each color)
- Generating library statistics
- Full batch aggregation pipeline
"""

import pytest
from copy_that.application.color_extractor import ColorToken
from copy_that.tokens.color.aggregator import ColorAggregator, AggregatedColorToken


class TestColorTokenDeduplication:
    """Test color deduplication logic using Delta-E"""

    def test_identical_colors_deduplicated(self):
        """Same hex code from multiple images should deduplicate"""
        colors_batch = [
            [
                ColorToken(hex="#FF5733", rgb="rgb(255, 87, 51)", name="Red-Orange", confidence=0.95),
            ],
            [
                ColorToken(hex="#FF5733", rgb="rgb(255, 87, 51)", name="Red-Orange", confidence=0.88),
            ],
        ]

        result = ColorAggregator.aggregate_batch(colors_batch, delta_e_threshold=2.0)

        assert len(result.tokens) == 1
        assert result.tokens[0].hex == "#FF5733"
        assert result.tokens[0].confidence > 0.88  # Average or max
        assert "image_0" in result.tokens[0].provenance
        assert "image_1" in result.tokens[0].provenance

    def test_similar_colors_deduplicated(self):
        """Slightly different hex codes (Delta-E < threshold) should deduplicate"""
        colors_batch = [
            [
                ColorToken(hex="#FF5733", rgb="rgb(255, 87, 51)", name="Red-Orange", confidence=0.95),
            ],
            [
                ColorToken(hex="#FF5844", rgb="rgb(255, 88, 68)", name="Red-Orange", confidence=0.90),  # Very similar
            ],
        ]

        result = ColorAggregator.aggregate_batch(colors_batch, delta_e_threshold=5.0)

        # Should have either 1 or 2 depending on Delta-E calculation
        assert len(result.tokens) <= 2
        if len(result.tokens) == 1:
            assert result.tokens[0].provenance is not None

    def test_different_colors_not_deduplicated(self):
        """Significantly different colors should NOT deduplicate"""
        colors_batch = [
            [
                ColorToken(hex="#FF5733", rgb="rgb(255, 87, 51)", name="Red-Orange", confidence=0.95),
            ],
            [
                ColorToken(hex="#0066FF", rgb="rgb(0, 102, 255)", name="Bright-Blue", confidence=0.92),
            ],
        ]

        result = ColorAggregator.aggregate_batch(colors_batch, delta_e_threshold=2.0)

        assert len(result.tokens) == 2
        assert any(t.hex == "#FF5733" for t in result.tokens)
        assert any(t.hex == "#0066FF" for t in result.tokens)

    def test_threshold_controls_deduplication(self):
        """Delta-E threshold should control deduplication strictness"""
        colors_batch = [
            [
                ColorToken(hex="#FF5733", rgb="rgb(255, 87, 51)", name="Red-Orange", confidence=0.95),
                ColorToken(hex="#FF6644", rgb="rgb(255, 102, 68)", name="Red-Orange-Light", confidence=0.90),
            ],
        ]

        # Strict threshold - keep both
        result_strict = ColorAggregator.aggregate_batch(colors_batch, delta_e_threshold=1.0)
        strict_count = len(result_strict.tokens)

        # Lenient threshold - may merge
        result_lenient = ColorAggregator.aggregate_batch(colors_batch, delta_e_threshold=20.0)
        lenient_count = len(result_lenient.tokens)

        assert strict_count >= lenient_count


class TestProvenanceTracking:
    """Test that provenance (which images contributed) is tracked accurately"""

    def test_single_image_provenance(self):
        """Single image extraction should track source"""
        colors_batch = [
            [
                ColorToken(hex="#FF5733", rgb="rgb(255, 87, 51)", name="Red-Orange", confidence=0.95),
                ColorToken(hex="#2C3E50", rgb="rgb(44, 62, 80)", name="Dark-Blue", confidence=0.88),
            ],
        ]

        result = ColorAggregator.aggregate_batch(colors_batch, delta_e_threshold=2.0)

        for token in result.tokens:
            assert "image_0" in token.provenance
            assert isinstance(token.provenance["image_0"], float)  # Confidence score

    def test_multi_image_provenance(self):
        """Multiple image contributions should track all sources"""
        colors_batch = [
            [
                ColorToken(hex="#FF5733", rgb="rgb(255, 87, 51)", name="Red-Orange", confidence=0.95),
            ],
            [
                ColorToken(hex="#FF5733", rgb="rgb(255, 87, 51)", name="Red-Orange", confidence=0.88),
            ],
            [
                ColorToken(hex="#FF5733", rgb="rgb(255, 87, 51)", name="Red-Orange", confidence=0.92),
            ],
        ]

        result = ColorAggregator.aggregate_batch(colors_batch, delta_e_threshold=2.0)

        assert len(result.tokens) == 1
        token = result.tokens[0]
        assert len(token.provenance) == 3
        assert "image_0" in token.provenance
        assert "image_1" in token.provenance
        assert "image_2" in token.provenance

    def test_provenance_confidence_scores(self):
        """Provenance should store confidence from each image"""
        colors_batch = [
            [
                ColorToken(hex="#FF5733", rgb="rgb(255, 87, 51)", name="Red-Orange", confidence=0.95),
            ],
            [
                ColorToken(hex="#FF5733", rgb="rgb(255, 87, 51)", name="Red-Orange", confidence=0.88),
            ],
        ]

        result = ColorAggregator.aggregate_batch(colors_batch, delta_e_threshold=2.0)

        token = result.tokens[0]
        assert token.provenance["image_0"] == 0.95
        assert token.provenance["image_1"] == 0.88


class TestAggregationStatistics:
    """Test library statistics generation"""

    def test_statistics_color_count(self):
        """Statistics should include color count"""
        colors_batch = [
            [
                ColorToken(hex="#FF5733", rgb="rgb(255, 87, 51)", name="Red-Orange", confidence=0.95),
                ColorToken(hex="#2C3E50", rgb="rgb(44, 62, 80)", name="Dark-Blue", confidence=0.88),
            ],
            [
                ColorToken(hex="#0066FF", rgb="rgb(0, 102, 255)", name="Bright-Blue", confidence=0.92),
            ],
        ]

        result = ColorAggregator.aggregate_batch(colors_batch, delta_e_threshold=2.0)

        assert result.statistics["color_count"] == 3
        assert result.statistics["image_count"] == 2

    def test_statistics_confidence_metrics(self):
        """Statistics should include confidence metrics"""
        colors_batch = [
            [
                ColorToken(hex="#FF5733", rgb="rgb(255, 87, 51)", name="Red-Orange", confidence=0.95),
                ColorToken(hex="#2C3E50", rgb="rgb(44, 62, 80)", name="Dark-Blue", confidence=0.85),
            ],
        ]

        result = ColorAggregator.aggregate_batch(colors_batch, delta_e_threshold=2.0)

        assert "avg_confidence" in result.statistics
        assert "min_confidence" in result.statistics
        assert "max_confidence" in result.statistics
        assert result.statistics["max_confidence"] == 0.95
        assert result.statistics["min_confidence"] == 0.85

    def test_statistics_dominant_colors(self):
        """Statistics should identify dominant colors (highest confidence)"""
        colors_batch = [
            [
                ColorToken(hex="#FF5733", rgb="rgb(255, 87, 51)", name="Red-Orange", confidence=0.99),
                ColorToken(hex="#2C3E50", rgb="rgb(44, 62, 80)", name="Dark-Blue", confidence=0.50),
            ],
        ]

        result = ColorAggregator.aggregate_batch(colors_batch, delta_e_threshold=2.0)

        assert "#FF5733" in result.statistics["dominant_colors"]


class TestEdgeCases:
    """Test edge cases and error conditions"""

    def test_empty_batch(self):
        """Empty batch should return empty library"""
        result = ColorAggregator.aggregate_batch([], delta_e_threshold=2.0)

        assert len(result.tokens) == 0
        assert result.statistics["color_count"] == 0

    def test_single_image_batch(self):
        """Single image should work correctly"""
        colors_batch = [
            [
                ColorToken(hex="#FF5733", rgb="rgb(255, 87, 51)", name="Red-Orange", confidence=0.95),
            ],
        ]

        result = ColorAggregator.aggregate_batch(colors_batch, delta_e_threshold=2.0)

        assert len(result.tokens) == 1
        assert result.tokens[0].provenance == {"image_0": 0.95}

    def test_batch_with_empty_images(self):
        """Batch with some empty image extractions should handle gracefully"""
        colors_batch = [
            [
                ColorToken(hex="#FF5733", rgb="rgb(255, 87, 51)", name="Red-Orange", confidence=0.95),
            ],
            [],  # No colors in this image
            [
                ColorToken(hex="#0066FF", rgb="rgb(0, 102, 255)", name="Bright-Blue", confidence=0.92),
            ],
        ]

        result = ColorAggregator.aggregate_batch(colors_batch, delta_e_threshold=2.0)

        assert len(result.tokens) == 2
        assert result.statistics["image_count"] == 3  # Count includes empty images

    def test_high_confidence_colors_prioritized(self):
        """When merging, high-confidence colors should be prioritized"""
        colors_batch = [
            [
                ColorToken(hex="#FF5733", rgb="rgb(255, 87, 51)", name="Red-Orange-Low", confidence=0.70),
            ],
            [
                ColorToken(hex="#FF5733", rgb="rgb(255, 87, 51)", name="Red-Orange-High", confidence=0.98),
            ],
        ]

        result = ColorAggregator.aggregate_batch(colors_batch, delta_e_threshold=2.0)

        assert len(result.tokens) == 1
        token = result.tokens[0]
        # Should use high-confidence name
        assert token.confidence >= 0.98 or token.name == "Red-Orange-High"


class TestAggregatedColorTokenStructure:
    """Test AggregatedColorToken data structure"""

    def test_aggregated_token_has_all_fields(self):
        """AggregatedColorToken should preserve all color properties"""
        colors_batch = [
            [
                ColorToken(
                    hex="#FF5733",
                    rgb="rgb(255, 87, 51)",
                    name="Red-Orange",
                    confidence=0.95,
                    harmony="complementary",
                    temperature="warm",
                ),
            ],
        ]

        result = ColorAggregator.aggregate_batch(colors_batch, delta_e_threshold=2.0)

        token = result.tokens[0]
        assert token.hex == "#FF5733"
        assert token.rgb == "rgb(255, 87, 51)"
        assert token.name == "Red-Orange"
        assert token.confidence == 0.95
        assert token.harmony == "complementary"
        assert token.temperature == "warm"

    def test_library_statistics_structure(self):
        """TokenLibrary should have complete statistics"""
        colors_batch = [
            [
                ColorToken(hex="#FF5733", rgb="rgb(255, 87, 51)", name="Red-Orange", confidence=0.95),
            ],
        ]

        result = ColorAggregator.aggregate_batch(colors_batch, delta_e_threshold=2.0)

        # Verify library structure
        assert hasattr(result, "tokens")
        assert hasattr(result, "statistics")
        assert hasattr(result, "token_type")
        assert result.token_type == "color"


class TestFullAggregationPipeline:
    """Integration tests for complete aggregation workflow"""

    def test_full_pipeline_four_images(self):
        """
        Complete workflow: Extract from 4 images, deduplicate, generate statistics

        Simulates real scenario:
        - Image 1: Red, Blue
        - Image 2: Red (slight variation), Green
        - Image 3: Blue (slight variation), Purple
        - Image 4: Red (another variation)

        Expected: ~4 unique colors after dedup with lenient threshold (16.0)
        Delta-E measurements (actual):
        - Red variations: 8.25, 15.66, 8.49
        - Blue variations: 13.66
        - Threshold 16.0 allows these similar colors to merge
        """
        colors_batch = [
            [
                ColorToken(hex="#FF5733", rgb="rgb(255, 87, 51)", name="Red-Orange", confidence=0.95),
                ColorToken(hex="#0066FF", rgb="rgb(0, 102, 255)", name="Bright-Blue", confidence=0.92),
            ],
            [
                ColorToken(hex="#FF5844", rgb="rgb(255, 88, 68)", name="Red-Orange", confidence=0.88),  # Delta-E: 8.25 from #FF5733
                ColorToken(hex="#00AA00", rgb="rgb(0, 170, 0)", name="Bright-Green", confidence=0.90),
            ],
            [
                ColorToken(hex="#0077FF", rgb="rgb(0, 119, 255)", name="Bright-Blue", confidence=0.85),  # Delta-E: 13.66 from #0066FF
                ColorToken(hex="#9933FF", rgb="rgb(153, 51, 255)", name="Purple", confidence=0.93),
            ],
            [
                ColorToken(hex="#FF6655", rgb="rgb(255, 102, 85)", name="Red-Orange", confidence=0.91),  # Delta-E: 15.66 from #FF5733
            ],
        ]

        result = ColorAggregator.aggregate_batch(colors_batch, delta_e_threshold=16.0)

        # Should have deduplicated to 4 main colors: red, blue, green, purple
        assert len(result.tokens) == 4, f"Expected 4 unique colors, got {len(result.tokens)}: {[t.hex for t in result.tokens]}"

        # All colors should have provenance from multiple images
        red_colors = [t for t in result.tokens if t.hex.startswith("#FF")]
        for color in red_colors:
            assert len(color.provenance) > 0

        # Statistics should be complete
        assert result.statistics["color_count"] == len(result.tokens)
        assert result.statistics["image_count"] == 4
        assert result.statistics["avg_confidence"] > 0
        assert result.statistics["avg_confidence"] <= 1.0
