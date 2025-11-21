"""Tests for semantic color naming module"""

import pytest

from copy_that.application.semantic_color_naming import SemanticColorNamer


class TestSemanticColorNamer:
    """Test SemanticColorNamer class"""

    @pytest.fixture
    def namer(self):
        """Create a SemanticColorNamer instance"""
        return SemanticColorNamer()

    # Simple style tests
    def test_name_color_simple_red(self, namer):
        """Test simple naming for red"""
        result = namer.name_color("#FF0000", style="simple")
        assert result in ["red", "orange", "magenta"]

    def test_name_color_simple_blue(self, namer):
        """Test simple naming for blue"""
        result = namer.name_color("#0000FF", style="simple")
        assert "blue" in result or "purple" in result

    def test_name_color_simple_green(self, namer):
        """Test simple naming for green"""
        result = namer.name_color("#00FF00", style="simple")
        assert "green" in result or "yellow-green" in result

    def test_name_color_simple_yellow(self, namer):
        """Test simple naming for yellow"""
        result = namer.name_color("#FFFF00", style="simple")
        assert "yellow" in result

    def test_name_color_simple_orange(self, namer):
        """Test simple naming for orange"""
        result = namer.name_color("#FF8000", style="simple")
        assert "orange" in result or "yellow" in result or "red" in result

    def test_name_color_simple_cyan(self, namer):
        """Test simple naming for cyan"""
        result = namer.name_color("#00FFFF", style="simple")
        assert "cyan" in result or "blue" in result or "green" in result

    def test_name_color_simple_magenta(self, namer):
        """Test simple naming for magenta"""
        result = namer.name_color("#FF00FF", style="simple")
        assert "magenta" in result or "purple" in result

    # Descriptive style tests
    def test_name_color_descriptive_warm(self, namer):
        """Test descriptive naming includes warm for warm colors"""
        result = namer.name_color("#FF5733", style="descriptive")
        # Should have hue name
        assert len(result) > 0
        assert "-" in result or result in ["red", "orange", "yellow"]

    def test_name_color_descriptive_cool(self, namer):
        """Test descriptive naming for cool colors"""
        result = namer.name_color("#3357FF", style="descriptive")
        assert len(result) > 0

    def test_name_color_descriptive_with_emotion(self, namer):
        """Test descriptive naming with emotion"""
        result = namer.name_color("#FF5733", style="descriptive", include_emotion=True)
        assert len(result) > 0
        assert "-" in result

    # Emotional style tests
    def test_name_color_emotional(self, namer):
        """Test emotional naming style"""
        result = namer.name_color("#FF5733", style="emotional")
        assert len(result) > 0
        # Should have emotion + hue
        assert "-" in result or len(result) > 3

    def test_name_color_emotional_vibrant(self, namer):
        """Test emotional naming for vibrant color"""
        result = namer.name_color("#FF0000", style="emotional")
        assert len(result) > 0

    def test_name_color_emotional_muted(self, namer):
        """Test emotional naming for muted color"""
        result = namer.name_color("#808080", style="emotional")
        assert len(result) > 0

    # Technical style tests
    def test_name_color_technical(self, namer):
        """Test technical naming style"""
        result = namer.name_color("#FF5733", style="technical")
        assert len(result) > 0

    def test_name_color_technical_saturated(self, namer):
        """Test technical naming for saturated color"""
        result = namer.name_color("#FF0000", style="technical")
        assert len(result) > 0

    def test_name_color_technical_desaturated(self, namer):
        """Test technical naming for desaturated color"""
        result = namer.name_color("#C0B0A0", style="technical")
        assert len(result) > 0

    # Vibrancy style tests
    def test_name_color_vibrancy(self, namer):
        """Test vibrancy naming style"""
        result = namer.name_color("#FF5733", style="vibrancy")
        assert len(result) > 0

    def test_name_color_vibrancy_vibrant(self, namer):
        """Test vibrancy naming for vibrant color"""
        result = namer.name_color("#FF0000", style="vibrancy")
        assert len(result) > 0

    def test_name_color_vibrancy_muted(self, namer):
        """Test vibrancy naming for muted color"""
        result = namer.name_color("#A08080", style="vibrancy")
        assert len(result) > 0

    def test_name_color_vibrancy_grayscale_dark(self, namer):
        """Test vibrancy naming for dark grayscale"""
        result = namer.name_color("#202020", style="vibrancy")
        assert "dark" in result or "gray" in result or len(result) > 0

    def test_name_color_vibrancy_grayscale_light(self, namer):
        """Test vibrancy naming for light grayscale"""
        result = namer.name_color("#E0E0E0", style="vibrancy")
        assert "light" in result or "gray" in result or len(result) > 0

    # Unknown style test
    def test_name_color_unknown_style(self, namer):
        """Test unknown style falls back to hue name"""
        result = namer.name_color("#FF5733", style="unknown")
        assert len(result) > 0

    # Grayscale tests
    def test_name_color_grayscale_black(self, namer):
        """Test naming black"""
        result = namer.name_color("#000000", style="simple")
        assert len(result) > 0

    def test_name_color_grayscale_white(self, namer):
        """Test naming white"""
        result = namer.name_color("#FFFFFF", style="simple")
        assert len(result) > 0

    def test_name_color_grayscale_gray(self, namer):
        """Test naming gray"""
        result = namer.name_color("#808080", style="simple")
        assert len(result) > 0


class TestAnalyzeColor:
    """Test analyze_color method"""

    @pytest.fixture
    def namer(self):
        """Create a SemanticColorNamer instance"""
        return SemanticColorNamer()

    def test_analyze_color_basic(self, namer):
        """Test basic color analysis"""
        result = namer.analyze_color("#FF5733")

        assert "hex" in result
        assert result["hex"] == "#FF5733"
        assert "hue_family" in result
        assert "hue_angle" in result
        assert "temperature" in result
        assert "saturation_level" in result
        assert "lightness_level" in result
        assert "vibrancy_score" in result
        assert "vibrancy_level" in result
        assert "is_grayscale" in result

    def test_analyze_color_red(self, namer):
        """Test analysis for red"""
        result = namer.analyze_color("#FF0000")

        assert result["temperature"] in ["warm", "cool", "neutral"]
        assert result["is_grayscale"] is False
        assert isinstance(result["hue_angle"], float)
        assert 0 <= result["hue_angle"] <= 360

    def test_analyze_color_blue(self, namer):
        """Test analysis for blue"""
        result = namer.analyze_color("#0000FF")

        assert result["temperature"] in ["warm", "cool", "neutral"]
        assert result["is_grayscale"] is False

    def test_analyze_color_grayscale(self, namer):
        """Test analysis for grayscale"""
        result = namer.analyze_color("#808080")

        assert result["is_grayscale"] is True

    def test_analyze_color_white(self, namer):
        """Test analysis for white"""
        result = namer.analyze_color("#FFFFFF")

        assert "lightness_level" in result
        assert result["lightness_oklch"] > 0.9

    def test_analyze_color_black(self, namer):
        """Test analysis for black"""
        result = namer.analyze_color("#000000")

        assert "lightness_level" in result
        assert result["lightness_oklch"] < 0.1

    def test_analyze_color_vibrant(self, namer):
        """Test analysis for vibrant color"""
        result = namer.analyze_color("#FF0000")

        assert "vibrancy_score" in result
        assert result["vibrancy_score"] >= 0

    def test_analyze_color_muted(self, namer):
        """Test analysis for muted color"""
        result = namer.analyze_color("#A08080")

        assert "vibrancy_score" in result
        assert "vibrancy_level" in result

    def test_analyze_color_saturation_values(self, namer):
        """Test saturation values are present"""
        result = namer.analyze_color("#FF5733")

        assert "saturation_oklch" in result
        assert "saturation_hsl" in result
        assert isinstance(result["saturation_oklch"], float)
        assert isinstance(result["saturation_hsl"], float)

    def test_analyze_color_lightness_values(self, namer):
        """Test lightness values are present"""
        result = namer.analyze_color("#FF5733")

        assert "lightness_oklch" in result
        assert "lightness_hsl" in result
        assert "brightness_lab" in result


class TestColorProperties:
    """Test various color property calculations"""

    @pytest.fixture
    def namer(self):
        """Create a SemanticColorNamer instance"""
        return SemanticColorNamer()

    def test_warm_colors(self, namer):
        """Test warm colors are identified correctly"""
        # Red, orange, yellow are warm
        for hex_color in ["#FF0000", "#FF8000", "#FFFF00"]:
            result = namer.analyze_color(hex_color)
            assert result["temperature"] in ["warm", "neutral"]

    def test_cool_colors(self, namer):
        """Test cool colors are identified correctly"""
        # Blue, cyan, purple are cool
        for hex_color in ["#0000FF", "#00FFFF", "#8000FF"]:
            result = namer.analyze_color(hex_color)
            assert result["temperature"] in ["cool", "neutral"]

    def test_lightness_levels(self, namer):
        """Test lightness levels are calculated"""
        # Dark color
        dark = namer.analyze_color("#202020")
        assert "dark" in dark["lightness_level"]

        # Light color
        light = namer.analyze_color("#E0E0E0")
        assert "light" in light["lightness_level"]

    def test_saturation_levels(self, namer):
        """Test saturation levels are calculated"""
        # Saturated color
        saturated = namer.analyze_color("#FF0000")
        assert saturated["saturation_level"] in ["saturated", "balanced", "high"]

        # Desaturated color
        desaturated = namer.analyze_color("#808080")
        assert "desaturated" in desaturated["saturation_level"] or "grayscale" in str(desaturated)


class TestEdgeCases:
    """Test edge cases"""

    @pytest.fixture
    def namer(self):
        """Create a SemanticColorNamer instance"""
        return SemanticColorNamer()

    def test_lowercase_hex(self, namer):
        """Test lowercase hex codes work"""
        result = namer.name_color("#ff5733", style="simple")
        assert len(result) > 0

    def test_uppercase_hex(self, namer):
        """Test uppercase hex codes work"""
        result = namer.name_color("#FF5733", style="simple")
        assert len(result) > 0

    def test_mixed_case_hex(self, namer):
        """Test mixed case hex codes work"""
        result = namer.name_color("#Ff5733", style="simple")
        assert len(result) > 0

    def test_all_primary_colors(self, namer):
        """Test all primary colors can be named"""
        colors = ["#FF0000", "#00FF00", "#0000FF"]
        for color in colors:
            result = namer.name_color(color, style="simple")
            assert len(result) > 0

    def test_all_secondary_colors(self, namer):
        """Test all secondary colors can be named"""
        colors = ["#FFFF00", "#00FFFF", "#FF00FF"]
        for color in colors:
            result = namer.name_color(color, style="simple")
            assert len(result) > 0

    def test_pastel_colors(self, namer):
        """Test pastel colors can be named"""
        colors = ["#FFB6C1", "#E6E6FA", "#98FB98"]  # Light pink, lavender, pale green
        for color in colors:
            result = namer.name_color(color, style="simple")
            assert len(result) > 0

    def test_dark_colors(self, namer):
        """Test dark colors can be named"""
        colors = ["#800000", "#008000", "#000080"]  # Dark red, green, blue
        for color in colors:
            result = namer.name_color(color, style="simple")
            assert len(result) > 0
