"""Comprehensive tests for color_utils module"""

import pytest

from copy_that.application.color_utils import (
    calculate_delta_e,
    calculate_wcag_contrast,
    color_similarity,
    compute_all_properties,
    ensure_displayable_color,
    find_nearest_color,
    get_closest_css_named,
    get_closest_web_safe,
    get_color_harmony,
    get_color_harmony_advanced,
    get_color_temperature,
    get_color_variant,
    get_lightness_level,
    get_perceptual_distance_summary,
    get_saturation_level,
    hex_to_hsl,
    hex_to_hsv,
    hex_to_rgb,
    is_color_in_gamut,
    is_neutral_color,
    is_wcag_compliant,
    match_color_to_palette,
    merge_similar_colors,
    rgb_to_hex,
    validate_cluster_homogeneity,
)


class TestColorConversions:
    """Test color space conversions"""

    def test_hex_to_rgb_red(self):
        """Test hex to RGB for red"""
        assert hex_to_rgb("#FF0000") == (255, 0, 0)

    def test_hex_to_rgb_green(self):
        """Test hex to RGB for green"""
        assert hex_to_rgb("#00FF00") == (0, 255, 0)

    def test_hex_to_rgb_blue(self):
        """Test hex to RGB for blue"""
        assert hex_to_rgb("#0000FF") == (0, 0, 255)

    def test_hex_to_rgb_white(self):
        """Test hex to RGB for white"""
        assert hex_to_rgb("#FFFFFF") == (255, 255, 255)

    def test_hex_to_rgb_black(self):
        """Test hex to RGB for black"""
        assert hex_to_rgb("#000000") == (0, 0, 0)

    def test_hex_to_rgb_lowercase(self):
        """Test hex to RGB with lowercase"""
        assert hex_to_rgb("#ff5733") == (255, 87, 51)

    def test_hex_to_rgb_no_hash(self):
        """Test hex to RGB without hash"""
        assert hex_to_rgb("FF5733") == (255, 87, 51)

    def test_rgb_to_hex(self):
        """Test RGB to hex conversion"""
        assert rgb_to_hex(255, 0, 0) == "#FF0000"
        assert rgb_to_hex(0, 255, 0) == "#00FF00"
        assert rgb_to_hex(0, 0, 255) == "#0000FF"

    def test_hex_to_hsl_red(self):
        """Test hex to HSL for red"""
        hsl = hex_to_hsl("#FF0000")
        assert "hsl(0," in hsl
        assert "100%" in hsl

    def test_hex_to_hsl_blue(self):
        """Test hex to HSL for blue"""
        hsl = hex_to_hsl("#0000FF")
        assert "hsl(240," in hsl

    def test_hex_to_hsv_red(self):
        """Test hex to HSV for red"""
        hsv = hex_to_hsv("#FF0000")
        assert "hsv(0," in hsv
        assert "100%" in hsv


class TestColorTemperature:
    """Test color temperature detection"""

    def test_warm_color_red(self):
        """Test that red is warm"""
        assert get_color_temperature("#FF0000") == "warm"

    def test_warm_color_orange(self):
        """Test that orange is warm"""
        assert get_color_temperature("#FF8000") == "warm"

    def test_cool_color_blue(self):
        """Test that blue is cool"""
        assert get_color_temperature("#0000FF") == "cool"

    def test_cool_color_cyan(self):
        """Test that cyan is cool"""
        assert get_color_temperature("#00FFFF") == "cool"

    def test_neutral_color_gray(self):
        """Test that gray is neutral"""
        assert get_color_temperature("#808080") == "neutral"

    def test_neutral_color_white(self):
        """Test that white is neutral"""
        assert get_color_temperature("#FFFFFF") == "neutral"


class TestSaturationLevel:
    """Test saturation level detection"""

    def test_vibrant_red(self):
        """Test that pure red is vibrant"""
        assert get_saturation_level("#FF0000") == "vibrant"

    def test_grayscale_gray(self):
        """Test that gray is grayscale"""
        assert get_saturation_level("#808080") == "grayscale"

    def test_grayscale_black(self):
        """Test that black is grayscale"""
        assert get_saturation_level("#000000") == "grayscale"

    def test_desaturated_color(self):
        """Test desaturated color"""
        # Light pink is typically desaturated
        result = get_saturation_level("#D0C0C0")
        assert result in ["desaturated", "muted", "grayscale"]

    def test_muted_color(self):
        """Test muted color"""
        result = get_saturation_level("#A08070")
        assert result in ["muted", "desaturated"]


class TestLightnessLevel:
    """Test lightness level detection"""

    def test_light_white(self):
        """Test that white is light"""
        assert get_lightness_level("#FFFFFF") == "light"

    def test_dark_black(self):
        """Test that black is dark"""
        assert get_lightness_level("#000000") == "dark"

    def test_medium_gray(self):
        """Test that medium gray is medium"""
        assert get_lightness_level("#808080") == "medium"

    def test_light_yellow(self):
        """Test that yellow is light"""
        assert get_lightness_level("#FFFF00") == "light"


class TestNeutralColor:
    """Test neutral color detection"""

    def test_white_is_neutral(self):
        """Test that white is neutral"""
        assert is_neutral_color("#FFFFFF") is True

    def test_black_is_neutral(self):
        """Test that black is neutral"""
        assert is_neutral_color("#000000") is True

    def test_gray_is_neutral(self):
        """Test that gray is neutral"""
        assert is_neutral_color("#808080") is True

    def test_red_is_not_neutral(self):
        """Test that red is not neutral"""
        assert is_neutral_color("#FF0000") is False

    def test_blue_is_not_neutral(self):
        """Test that blue is not neutral"""
        assert is_neutral_color("#0000FF") is False


class TestColorInGamut:
    """Test color gamut detection"""

    def test_red_in_gamut(self):
        """Test that red is in gamut"""
        assert is_color_in_gamut("#FF0000") is True

    def test_white_in_gamut(self):
        """Test that white is in gamut"""
        assert is_color_in_gamut("#FFFFFF") is True

    def test_black_in_gamut(self):
        """Test that black is in gamut"""
        assert is_color_in_gamut("#000000") is True


class TestWCAGContrast:
    """Test WCAG contrast calculations"""

    def test_black_white_contrast(self):
        """Test maximum contrast between black and white"""
        contrast = calculate_wcag_contrast("#000000", "#FFFFFF")
        assert contrast >= 20.0  # Should be close to 21

    def test_same_color_contrast(self):
        """Test contrast of same color is 1"""
        contrast = calculate_wcag_contrast("#FF0000", "#FF0000")
        assert contrast == pytest.approx(1.0, abs=0.1)

    def test_wcag_compliant_aa_normal(self):
        """Test WCAG AA compliance for normal text"""
        # Black on white should pass
        assert is_wcag_compliant("#000000", "#FFFFFF", "AA", "normal") is True
        # Light gray on white should fail
        assert is_wcag_compliant("#CCCCCC", "#FFFFFF", "AA", "normal") is False

    def test_wcag_compliant_aaa(self):
        """Test WCAG AAA compliance"""
        # Black on white should pass AAA
        assert is_wcag_compliant("#000000", "#FFFFFF", "AAA", "normal") is True

    def test_wcag_compliant_large_text(self):
        """Test WCAG compliance for large text (lower threshold)"""
        # Lower contrast requirements for large text
        result = is_wcag_compliant("#666666", "#FFFFFF", "AA", "large")
        # Should pass for large text
        assert result is True


class TestColorVariants:
    """Test color variant generation"""

    def test_tint_makes_lighter(self):
        """Test that tint makes color lighter"""
        tint = get_color_variant("#FF0000", "tint", 0.5)
        # Tint should have higher RGB values
        r, g, b = hex_to_rgb(tint)
        assert r >= 255
        assert g > 0  # Mixed with white
        assert b > 0

    def test_shade_makes_darker(self):
        """Test that shade makes color darker"""
        shade = get_color_variant("#FF0000", "shade", 0.5)
        r, g, b = hex_to_rgb(shade)
        assert r < 255
        assert r > 0

    def test_tone_desaturates(self):
        """Test that tone desaturates color"""
        tone = get_color_variant("#FF0000", "tone", 0.5)
        r, g, b = hex_to_rgb(tone)
        # Should be less saturated (values closer together)
        assert g > 0 or b > 0


class TestWebSafeColors:
    """Test web-safe color matching"""

    def test_closest_web_safe_red(self):
        """Test closest web-safe for red"""
        result = get_closest_web_safe("#FF0000")
        assert result == "#FF0000"

    def test_closest_web_safe_arbitrary(self):
        """Test closest web-safe for arbitrary color"""
        result = get_closest_web_safe("#F15925")
        # Should round to nearest web-safe values
        assert result.startswith("#")
        assert len(result) == 7


class TestCSSNamedColors:
    """Test CSS named color matching"""

    def test_closest_css_named_red(self):
        """Test closest CSS named for red"""
        result = get_closest_css_named("#FF0000")
        assert result == "red"

    def test_closest_css_named_blue(self):
        """Test closest CSS named for blue"""
        result = get_closest_css_named("#0000FF")
        assert result == "blue"

    def test_closest_css_named_arbitrary(self):
        """Test closest CSS named for arbitrary color"""
        result = get_closest_css_named("#F15925")
        assert result is not None
        assert isinstance(result, str)


class TestDeltaE:
    """Test Delta E calculations"""

    def test_delta_e_identical_colors(self):
        """Test Delta E for identical colors is 0"""
        de = calculate_delta_e("#FF0000", "#FF0000")
        assert de == pytest.approx(0.0, abs=0.1)

    def test_delta_e_similar_colors(self):
        """Test Delta E for similar colors is small"""
        de = calculate_delta_e("#FF0000", "#FF0001")
        assert de < 5.0

    def test_delta_e_different_colors(self):
        """Test Delta E for different colors is large"""
        de = calculate_delta_e("#FF0000", "#00FF00")
        assert de > 50.0


class TestColorSimilarity:
    """Test color similarity functions"""

    def test_color_similarity_identical(self):
        """Test identical colors are similar"""
        assert color_similarity("#FF0000", "#FF0000", threshold=5.0) is True

    def test_color_similarity_different(self):
        """Test different colors are not similar"""
        assert color_similarity("#FF0000", "#00FF00", threshold=10.0) is False

    def test_color_similarity_near(self):
        """Test near colors are similar"""
        assert color_similarity("#FF0000", "#FF0001", threshold=5.0) is True


class TestFindNearestColor:
    """Test find nearest color in palette"""

    def test_find_nearest_exact_match(self):
        """Test finding exact match in palette"""
        palette = {"red": "#FF0000", "green": "#00FF00", "blue": "#0000FF"}
        name, de = find_nearest_color("#FF0000", palette)
        assert name == "red"
        assert de < 1.0

    def test_find_nearest_close_match(self):
        """Test finding close match in palette"""
        palette = {"red": "#FF0000", "green": "#00FF00"}
        name, de = find_nearest_color("#FF0001", palette)
        assert name == "red"
        assert de < 5.0


class TestMergeSimilarColors:
    """Test merging similar colors"""

    def test_merge_identical_colors(self):
        """Test merging identical colors"""
        colors = ["#FF0000", "#FF0000", "#FF0000"]
        merged = merge_similar_colors(colors, threshold=5.0)
        assert len(merged) == 1

    def test_merge_different_colors(self):
        """Test different colors remain separate"""
        colors = ["#FF0000", "#00FF00", "#0000FF"]
        merged = merge_similar_colors(colors, threshold=5.0)
        assert len(merged) == 3

    def test_merge_empty_list(self):
        """Test merging empty list"""
        merged = merge_similar_colors([], threshold=5.0)
        assert merged == []


class TestValidateClusterHomogeneity:
    """Test cluster homogeneity validation"""

    def test_homogeneous_cluster(self):
        """Test homogeneous cluster passes"""
        cluster = ["#FF0000", "#FF0001", "#FF0002"]
        assert validate_cluster_homogeneity(cluster, max_internal_de=15.0) is True

    def test_heterogeneous_cluster(self):
        """Test heterogeneous cluster fails"""
        cluster = ["#FF0000", "#00FF00", "#0000FF"]
        assert validate_cluster_homogeneity(cluster, max_internal_de=15.0) is False

    def test_single_color_cluster(self):
        """Test single color cluster passes"""
        cluster = ["#FF0000"]
        assert validate_cluster_homogeneity(cluster, max_internal_de=15.0) is True


class TestEnsureDisplayableColor:
    """Test ensuring colors are displayable"""

    def test_displayable_red(self):
        """Test red remains displayable"""
        result = ensure_displayable_color("#FF0000")
        assert result.upper() == "#FF0000"

    def test_displayable_white(self):
        """Test white remains displayable"""
        result = ensure_displayable_color("#FFFFFF")
        assert result.upper() == "#FFFFFF"


class TestMatchColorToPalette:
    """Test matching colors to palette"""

    def test_match_exact(self):
        """Test exact match in palette"""
        palette = ["#FF0000", "#00FF00", "#0000FF"]
        result = match_color_to_palette("#FF0000", palette)
        assert result.upper() == "#FF0000"

    def test_match_with_distance(self):
        """Test match with distance returned"""
        palette = ["#FF0000", "#00FF00", "#0000FF"]
        result, distance = match_color_to_palette("#FF0001", palette, return_distance=True)
        assert result.upper() == "#FF0000"
        assert distance < 5.0

    def test_match_empty_palette(self):
        """Test match with empty palette"""
        result = match_color_to_palette("#FF0000", [])
        assert result == "#FF0000"


class TestColorHarmony:
    """Test color harmony detection"""

    def test_harmony_no_palette(self):
        """Test harmony with no palette returns None"""
        result = get_color_harmony("#FF0000", None)
        assert result is None

    def test_harmony_small_palette(self):
        """Test harmony with small palette"""
        result = get_color_harmony("#FF0000", ["#FF0001"])
        assert result is None

    def test_harmony_complementary(self):
        """Test complementary harmony detection"""
        result = get_color_harmony("#FF0000", ["#FF0000", "#00FFFF"])
        assert result in ["complementary", "split-complementary", "triadic", "tetradic"]


class TestColorHarmonyAdvanced:
    """Test advanced color harmony detection"""

    def test_advanced_harmony_no_palette(self):
        """Test advanced harmony with no palette"""
        result = get_color_harmony_advanced("#FF0000", None)
        assert result == "monochromatic"

    def test_advanced_harmony_with_metadata(self):
        """Test advanced harmony with metadata"""
        palette = ["#FF0000", "#00FF00", "#0000FF"]
        result = get_color_harmony_advanced("#FF0000", palette, return_metadata=True)
        assert isinstance(result, dict)
        assert "harmony" in result
        assert "confidence" in result


class TestPerceptualDistanceSummary:
    """Test perceptual distance summary"""

    def test_summary_single_color(self):
        """Test summary with single color"""
        summary = get_perceptual_distance_summary(["#FF0000"])
        assert summary["mean"] == 0
        assert summary["max"] == 0

    def test_summary_multiple_colors(self):
        """Test summary with multiple colors"""
        colors = ["#FF0000", "#00FF00", "#0000FF"]
        summary = get_perceptual_distance_summary(colors)
        assert summary["mean"] > 0
        assert summary["max"] > 0
        assert "std" in summary
        assert "count" in summary


class TestComputeAllProperties:
    """Test compute all properties function"""

    def test_compute_all_properties_basic(self):
        """Test computing all properties for a color"""
        props = compute_all_properties("#FF5733")

        assert "hsl" in props
        assert "hsv" in props
        assert "temperature" in props
        assert "saturation_level" in props
        assert "lightness_level" in props
        assert "is_neutral" in props
        assert "wcag_contrast_on_white" in props
        assert "wcag_contrast_on_black" in props
        assert "tint_color" in props
        assert "shade_color" in props
        assert "tone_color" in props
        assert "closest_web_safe" in props
        assert "closest_css_named" in props

    def test_compute_all_properties_with_dominant(self):
        """Test computing all properties with dominant colors"""
        dominant = ["#FF0000", "#00FF00"]
        props = compute_all_properties("#FF5733", dominant)

        assert "delta_e_to_dominant" in props
        assert props["delta_e_to_dominant"] >= 0

    def test_compute_all_properties_red(self):
        """Test properties for red"""
        props = compute_all_properties("#FF0000")

        assert props["temperature"] == "warm"
        assert props["saturation_level"] == "vibrant"
        assert props["is_neutral"] is False
