"""TDD Tests for ColorAide Tier 1 Features: Gamut Mapping & Palette Matching"""


class TestGamutMapping:
    """Test suite for gamut mapping with .fit()"""

    def test_srgb_colors_remain_unchanged(self):
        """RED: Colors already in sRGB should remain the same."""
        from copy_that.application.color_utils import ensure_displayable_color

        result = ensure_displayable_color("#FF0000")
        assert result.upper() == "#FF0000"

    def test_white_remains_unchanged(self):
        """RED: White should remain unchanged."""
        from copy_that.application.color_utils import ensure_displayable_color

        result = ensure_displayable_color("#FFFFFF")
        assert result.upper() == "#FFFFFF"

    def test_black_remains_unchanged(self):
        """RED: Black should remain unchanged."""
        from copy_that.application.color_utils import ensure_displayable_color

        result = ensure_displayable_color("#000000")
        assert result.upper() == "#000000"

    def test_neutral_colors_in_gamut(self):
        """RED: All neutral/gray colors should be in sRGB."""
        from copy_that.application.color_utils import ensure_displayable_color

        neutrals = ["#808080", "#C0C0C0", "#404040"]
        for neutral in neutrals:
            result = ensure_displayable_color(neutral)
            assert isinstance(result, str)
            assert result.startswith("#")
            assert len(result) == 7

    def test_primary_colors_in_gamut(self):
        """RED: Primary colors should be in sRGB."""
        from copy_that.application.color_utils import ensure_displayable_color

        primaries = ["#FF0000", "#00FF00", "#0000FF"]
        for primary in primaries:
            result = ensure_displayable_color(primary)
            assert result.upper() == primary.upper()

    def test_output_is_valid_hex(self):
        """RED: Output should always be valid hex."""
        from copy_that.application.color_utils import ensure_displayable_color

        colors = ["#F15925", "#3B5E4C", "#EBCF7E"]
        for color in colors:
            result = ensure_displayable_color(color)
            assert isinstance(result, str)
            assert result.startswith("#")
            assert len(result) == 7

    def test_gamut_parameter_srgb(self):
        """RED: Explicit sRGB gamut parameter should work."""
        from copy_that.application.color_utils import ensure_displayable_color

        result = ensure_displayable_color("#FF0000", gamut="srgb")
        assert result.upper() == "#FF0000"

    def test_gamut_parameter_p3(self):
        """RED: Display P3 gamut parameter should work."""
        from copy_that.application.color_utils import ensure_displayable_color

        result = ensure_displayable_color("#FF0000", gamut="p3")
        assert isinstance(result, str)
        assert result.startswith("#")

    def test_gamut_parameter_rec2020(self):
        """RED: Rec2020 gamut parameter should work."""
        from copy_that.application.color_utils import ensure_displayable_color

        result = ensure_displayable_color("#FF0000", gamut="rec2020")
        assert isinstance(result, str)
        assert result.startswith("#")


class TestPaletteMatching:
    """Test suite for color-to-palette matching"""

    def test_match_identical_color(self):
        """RED: Should match color to itself perfectly."""
        from copy_that.application.color_utils import match_color_to_palette

        palette = ["#FF0000", "#0000FF", "#00FF00"]
        result = match_color_to_palette("#FF0000", palette)
        assert result.upper() == "#FF0000"

    def test_match_similar_to_palette(self):
        """RED: Should match similar color to nearest palette entry."""
        from copy_that.application.color_utils import match_color_to_palette

        palette = ["#FF0000", "#0000FF", "#00FF00"]
        result = match_color_to_palette("#FF1111", palette)
        assert result.upper() == "#FF0000"

    def test_match_returns_distance_when_requested(self):
        """RED: Should return (hex, distance) tuple when return_distance=True."""
        from copy_that.application.color_utils import match_color_to_palette

        palette = ["#FF0000", "#0000FF", "#00FF00"]
        result = match_color_to_palette("#FF0000", palette, return_distance=True)
        assert isinstance(result, tuple)
        assert len(result) == 2
        hex_color, distance = result
        assert hex_color.upper() == "#FF0000"
        assert isinstance(distance, float)
        assert distance < 0.1

    def test_match_distance_is_zero_for_identical(self):
        """RED: Distance should be ~0 for identical colors."""
        from copy_that.application.color_utils import match_color_to_palette

        palette = ["#FF0000"]
        _, distance = match_color_to_palette("#FF0000", palette, return_distance=True)
        assert distance < 0.01

    def test_match_distance_increases_with_difference(self):
        """RED: Distance should increase as colors become less similar."""
        from copy_that.application.color_utils import match_color_to_palette

        palette = ["#FF0000"]

        _, d_identical = match_color_to_palette("#FF0000", palette, return_distance=True)
        _, d_slightly_different = match_color_to_palette("#FF1111", palette, return_distance=True)
        _, d_very_different = match_color_to_palette("#0000FF", palette, return_distance=True)

        assert d_identical < d_slightly_different < d_very_different

    def test_match_empty_palette_returns_target(self):
        """RED: Empty palette should return target color gracefully."""
        from copy_that.application.color_utils import match_color_to_palette

        result = match_color_to_palette("#FF0000", [])
        assert result.upper() == "#FF0000"

    def test_match_single_color_palette(self):
        """RED: Should match to only color in palette."""
        from copy_that.application.color_utils import match_color_to_palette

        result = match_color_to_palette("#0000FF", ["#FF0000"])
        assert result.upper() == "#FF0000"

    def test_match_multiple_options_returns_nearest(self):
        """RED: Should return nearest color from multiple options."""
        from copy_that.application.color_utils import match_color_to_palette

        palette = ["#FF0000", "#0000FF", "#00FF00", "#FFFF00"]
        result = match_color_to_palette("#FF6600", palette)
        assert result.upper() == "#FF0000"

    def test_match_complementary_colors(self):
        """RED: Complementary colors should match to appropriate palette entry."""
        from copy_that.application.color_utils import match_color_to_palette

        palette = ["#FF0000", "#00FF00", "#0000FF"]
        result = match_color_to_palette("#00FFFF", palette)
        # Cyan should match to green or blue, not red
        assert result.upper() in ["#00FF00", "#0000FF"]
        assert result.upper() != "#FF0000"

    def test_match_all_output_valid_hex(self):
        """RED: All matched colors should be valid hex."""
        from copy_that.application.color_utils import match_color_to_palette

        palette = ["#F15925", "#3B5E4C", "#EBCF7E", "#2E4053"]
        test_colors = ["#FF0000", "#00FF00", "#0000FF", "#FFFF00"]

        for test_color in test_colors:
            result = match_color_to_palette(test_color, palette)
            assert isinstance(result, str)
            assert result.startswith("#")
            assert len(result) == 7
            assert result.upper() in [c.upper() for c in palette]


class TestIntegrationGamutAndMatching:
    """Integration tests combining gamut mapping with palette matching"""

    def test_workflow_ensure_then_match(self):
        """RED: Ensure displayable, then match to palette."""
        from copy_that.application.color_utils import (
            ensure_displayable_color,
            match_color_to_palette,
        )

        palette = ["#FF0000", "#0000FF", "#00FF00"]

        color = "#FF5555"
        displayable = ensure_displayable_color(color)
        matched = match_color_to_palette(displayable, palette)

        assert isinstance(matched, str)
        assert matched.upper() in [c.upper() for c in palette]

    def test_design_system_standardization(self):
        """RED: Use case - standardize extracted colors to design system palette."""
        from copy_that.application.color_utils import (
            ensure_displayable_color,
            match_color_to_palette,
        )

        design_system = [
            "#F44336",  # Red
            "#2196F3",  # Blue
            "#4CAF50",  # Green
            "#FF9800",  # Orange
            "#9C27B0",  # Purple
        ]

        extracted_colors = [
            "#F44334",  # Slightly different red
            "#2196F2",  # Slightly different blue
            "#FF9801",  # Slightly different orange
        ]

        for extracted in extracted_colors:
            displayable = ensure_displayable_color(extracted)
            standardized, distance = match_color_to_palette(
                displayable, design_system, return_distance=True
            )
            assert standardized.upper() in [c.upper() for c in design_system]
            assert distance < 5.0
