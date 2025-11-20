"""TDD Tests for Delta-E Color Distance and Merging"""

import pytest


class TestDeltaEDistance:
    """Test suite for perceptual color distance calculations."""

    def test_delta_e_2000_identical_colors(self):
        """RED: Identical colors should have Delta-E of ~0."""
        from copy_that.application.delta_e import delta_e_2000

        result = delta_e_2000("#FF0000", "#FF0000")
        assert result < 0.01  # Essentially zero, accounting for float precision

    def test_delta_e_2000_different_colors(self):
        """RED: Different colors should have Delta-E > 0."""
        from copy_that.application.delta_e import delta_e_2000

        result = delta_e_2000("#FF0000", "#0000FF")
        assert result > 20  # Very different colors

    def test_delta_e_2000_accepts_hex_inputs(self):
        """RED: Should accept hex color inputs."""
        from copy_that.application.delta_e import delta_e_2000

        result_hex = delta_e_2000("#FF0000", "#00FF00")

        # Should work with hex inputs
        assert isinstance(result_hex, float)
        assert result_hex > 0

    def test_delta_e_76_faster_than_2000(self):
        """RED: Delta-E 76 should be available as faster alternative."""
        from copy_that.application.delta_e import delta_e_76

        result = delta_e_76("#FF0000", "#00FF00")
        assert isinstance(result, float)
        assert result > 0


class TestColorMerging:
    """Test suite for merging similar colors."""

    def test_merge_similar_colors_basic(self):
        """RED: Should merge colors within threshold."""
        from copy_that.application.delta_e import merge_similar_colors

        colors = ["#FF0000", "#FF0001", "#FF0002"]  # Very similar reds
        result = merge_similar_colors(colors, threshold=1.0)

        # Should merge nearly identical colors
        assert len(result) <= len(colors)
        assert all(isinstance(c, str) and c.startswith("#") for c in result)

    def test_merge_similar_colors_keeps_different(self):
        """RED: Should keep colors that are sufficiently different."""
        from copy_that.application.delta_e import merge_similar_colors

        colors = ["#FF0000", "#0000FF"]  # Very different colors
        result = merge_similar_colors(colors, threshold=15.0)

        # Should keep both colors as they're different
        assert len(result) == 2

    def test_merge_similar_colors_threshold_parameter(self):
        """RED: Threshold parameter should control merge aggressiveness."""
        from copy_that.application.delta_e import merge_similar_colors

        colors = ["#FF0000", "#FF1111", "#0000FF"]

        result_strict = merge_similar_colors(colors, threshold=5.0)
        result_loose = merge_similar_colors(colors, threshold=30.0)

        # Stricter threshold should result in more colors
        assert len(result_strict) >= len(result_loose)

    def test_merge_similar_colors_metric_parameter(self):
        """RED: Should support different Delta-E metrics."""
        from copy_that.application.delta_e import merge_similar_colors

        colors = ["#FF0000", "#FF0011", "#0000FF"]

        result_2000 = merge_similar_colors(colors, metric="2000")
        result_76 = merge_similar_colors(colors, metric="76")

        # Both should return lists
        assert isinstance(result_2000, list)
        assert isinstance(result_76, list)

    def test_merge_similar_colors_empty_list(self):
        """RED: Should handle empty color list."""
        from copy_that.application.delta_e import merge_similar_colors

        result = merge_similar_colors([], threshold=15.0)
        assert result == []

    def test_merge_similar_colors_single_color(self):
        """RED: Should handle single color gracefully."""
        from copy_that.application.delta_e import merge_similar_colors

        colors = ["#FF0000"]
        result = merge_similar_colors(colors, threshold=15.0)

        assert len(result) == 1
        assert result[0] == "#FF0000"

    def test_merge_similar_colors_preserves_valid_hex(self):
        """RED: Merged colors should be valid hex."""
        from copy_that.application.delta_e import merge_similar_colors

        colors = ["#FF0000", "#FF0022", "#00FF00", "#0000FF"]
        result = merge_similar_colors(colors, threshold=25.0)

        for color in result:
            assert isinstance(color, str)
            assert color.startswith("#")
            assert len(color) == 7
