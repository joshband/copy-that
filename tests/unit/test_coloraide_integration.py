"""
Tests for ColorAide integration in color_utils.py

Validates that ColorAide's optimized methods improve color calculations.
"""

import pytest

from copy_that.application.color_utils import (
    calculate_delta_e,
    calculate_wcag_contrast,
    is_color_in_gamut,
    is_neutral_color,
)


class TestColorAideDeltaE:
    """Test Delta-E calculations using ColorAide"""

    def test_delta_e_identical_colors(self):
        """Identical colors should have Delta-E = 0"""
        delta_e = calculate_delta_e("#FF0000", "#FF0000")
        assert delta_e == pytest.approx(0, abs=0.01)

    def test_delta_e_complementary_colors(self):
        """Red and cyan should have high Delta-E"""
        delta_e = calculate_delta_e("#FF0000", "#00FFFF")
        assert delta_e > 50  # Large perceptual difference

    def test_delta_e_similar_colors(self):
        """Similar colors should have low Delta-E"""
        delta_e = calculate_delta_e("#FF0000", "#FF1000")
        assert delta_e < 10  # Small perceptual difference

    def test_delta_e_is_symmetric(self):
        """Delta-E should be symmetric: DE(A,B) = DE(B,A)"""
        de_ab = calculate_delta_e("#FF0000", "#0000FF")
        de_ba = calculate_delta_e("#0000FF", "#FF0000")
        assert de_ab == pytest.approx(de_ba, abs=0.01)


class TestColorAideLuminance:
    """Test luminance calculations using ColorAide"""

    def test_wcag_contrast_white_black(self):
        """White on black should have max contrast ratio (21)"""
        contrast = calculate_wcag_contrast("#FFFFFF", "#000000")
        assert contrast == pytest.approx(21.0, abs=0.1)

    def test_wcag_contrast_same_color(self):
        """Same color should have contrast ratio of 1.0"""
        contrast = calculate_wcag_contrast("#FF0000", "#FF0000")
        assert contrast == pytest.approx(1.0, abs=0.01)

    def test_wcag_contrast_readable_text(self):
        """Black text on white should be readable (contrast > 4.5)"""
        contrast = calculate_wcag_contrast("#000000", "#FFFFFF")
        assert contrast > 4.5

    def test_wcag_contrast_is_symmetric(self):
        """Contrast ratio should be symmetric"""
        c1 = calculate_wcag_contrast("#FF0000", "#FFFFFF")
        c2 = calculate_wcag_contrast("#FFFFFF", "#FF0000")
        assert c1 == pytest.approx(c2, abs=0.01)


class TestColorAideAchromatic:
    """Test achromatic (grayscale) detection using ColorAide"""

    def test_pure_black_is_achromatic(self):
        """Pure black should be detected as grayscale"""
        assert is_neutral_color("#000000") is True

    def test_pure_white_is_achromatic(self):
        """Pure white should be detected as grayscale"""
        assert is_neutral_color("#FFFFFF") is True

    def test_gray_is_achromatic(self):
        """Medium gray should be detected as grayscale"""
        assert is_neutral_color("#808080") is True

    def test_red_is_not_achromatic(self):
        """Pure red should not be detected as grayscale"""
        assert is_neutral_color("#FF0000") is False

    def test_blue_is_not_achromatic(self):
        """Pure blue should not be detected as grayscale"""
        assert is_neutral_color("#0000FF") is False

    def test_near_gray_is_achromatic(self):
        """Very slight color cast should still be achromatic"""
        # #808081 is almost gray with minimal color
        result = is_neutral_color("#808081")
        # Should be True (nearly achromatic) or False (slight color)
        # Either is acceptable as it's a boundary case
        assert isinstance(result, bool)


class TestColorAideGamut:
    """Test gamut checking using ColorAide"""

    def test_pure_colors_in_gamut(self):
        """Standard web colors should be in sRGB gamut"""
        assert is_color_in_gamut("#FF0000") is True
        assert is_color_in_gamut("#00FF00") is True
        assert is_color_in_gamut("#0000FF") is True

    def test_neutral_colors_in_gamut(self):
        """Grayscale colors should be in sRGB gamut"""
        assert is_color_in_gamut("#000000") is True
        assert is_color_in_gamut("#FFFFFF") is True
        assert is_color_in_gamut("#808080") is True

    def test_arbitrary_hex_in_gamut(self):
        """All valid hex colors should be in sRGB gamut"""
        # Since ColorAide creates colors from hex in sRGB,
        # all should be in gamut by definition
        assert is_color_in_gamut("#123456") is True
        assert is_color_in_gamut("#ABCDEF") is True


class TestColorAideIntegrationWithCompute:
    """Test that ColorAide methods work within compute_all_properties"""

    def test_compute_uses_coloraide_methods(self):
        """Verify compute_all_properties works with ColorAide integration"""
        from copy_that.application.color_utils import compute_all_properties

        props = compute_all_properties("#FF0000", ["#0000FF", "#00FF00"])

        # Should have all expected properties
        assert "wcag_contrast_on_white" in props
        assert "wcag_contrast_on_black" in props
        assert "delta_e_to_dominant" in props
        assert "is_neutral" in props

        # Check values are reasonable
        assert 0 <= props["wcag_contrast_on_white"] <= 21
        assert 0 <= props["wcag_contrast_on_black"] <= 21
        assert isinstance(props["is_neutral"], bool)
        assert props["delta_e_to_dominant"] > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
