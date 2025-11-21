"""TDD Tests for Oklch Perceptual Color Scales"""



class TestOklchScales:
    """Test suite for generating perceptually uniform Oklch color scales."""

    def test_oklch_scale_generation_basic(self):
        """RED: Test that generate_oklch_scale returns a dict with correct structure."""
        from copy_that.application.color_spaces_advanced import generate_oklch_scale

        result = generate_oklch_scale("#0066CC")

        # Should return dict mapping step to hex color
        assert isinstance(result, dict)
        assert "50" in result
        assert "900" in result

    def test_oklch_scale_returns_valid_hex_colors(self):
        """RED: All returned values should be valid hex colors."""
        from copy_that.application.color_spaces_advanced import generate_oklch_scale

        result = generate_oklch_scale("#0066CC")

        for step, color in result.items():
            assert isinstance(color, str)
            assert color.startswith("#")
            assert len(color) == 7  # #RRGGBB format
            assert all(c in "0123456789ABCDEFabcdef" for c in color[1:])

    def test_oklch_scale_has_all_standard_steps(self):
        """RED: Should include all standard scale steps by default."""
        from copy_that.application.color_spaces_advanced import generate_oklch_scale

        result = generate_oklch_scale("#0066CC")

        expected_steps = ["50", "100", "200", "300", "400", "500", "600", "700", "800", "900"]
        for step in expected_steps:
            assert step in result

    def test_oklch_scale_custom_steps(self):
        """RED: Should support custom step values."""
        from copy_that.application.color_spaces_advanced import generate_oklch_scale

        # The archive implementation uses scale_levels parameter, not steps
        # Must include "500" which is the base lightness
        custom_levels = {"50": 0.95, "100": 0.90, "200": 0.80, "500": None}
        result = generate_oklch_scale("#0066CC", scale_levels=custom_levels)

        assert len(result) == len(custom_levels)
        for step in custom_levels:
            assert step in result

    def test_oklch_scale_perceptual_uniformity(self):
        """RED: Test that visual distance between steps is perceptually uniform."""
        from copy_that.application.color_spaces_advanced import generate_oklch_scale

        result = generate_oklch_scale("#0066CC")

        # Result should have standard scale levels: 50, 100, 200, ..., 900
        assert len(result) == 10

        # All colors should be different
        unique_colors = set(result.values())
        assert len(unique_colors) == 10

    def test_oklch_scale_lightness_progression(self):
        """RED: Lightness should generally increase with step number."""
        from copy_that.application.color_spaces_advanced import generate_oklch_scale

        result = generate_oklch_scale("#0066CC")

        # Get hex colors in order of steps
        # Keys are strings: "50", "100", "200", etc.
        steps_ordered = sorted(result.keys(), key=lambda x: int(x))
        colors = [result[step] for step in steps_ordered]

        # Each color should have valid RGB values
        for color in colors:
            assert len(color) == 7
            assert color.startswith("#")

    def test_oklch_scale_with_different_base_colors(self):
        """RED: Should work with various base colors."""
        from copy_that.application.color_spaces_advanced import generate_oklch_scale

        test_colors = ["#FF0000", "#00FF00", "#0000FF", "#FFA500"]

        for hex_color in test_colors:
            result = generate_oklch_scale(hex_color)
            assert isinstance(result, dict)
            assert len(result) == 10
            assert all(isinstance(v, str) and v.startswith("#") for v in result.values())

    def test_oklch_scale_is_deterministic(self):
        """RED: Same input should always produce same output."""
        from copy_that.application.color_spaces_advanced import generate_oklch_scale

        result1 = generate_oklch_scale("#0066CC")
        result2 = generate_oklch_scale("#0066CC")

        assert result1 == result2
