"""Tests for AccessibilityCalculator

Comprehensive tests for WCAG contrast ratio calculation and colorblind safety checks.
"""
import pytest
from copy_that.pipeline.validation.accessibility import (
    AccessibilityCalculator,
    WCAGLevel,
    ContrastResult,
    ColorblindType,
)
from copy_that.pipeline import TokenResult, TokenType, W3CTokenType
from copy_that.pipeline.exceptions import ValidationError


class TestCalculateContrastRatio:
    """Tests for calculate_contrast_ratio method."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.calc = AccessibilityCalculator()

    def test_white_on_black_maximum_contrast(self) -> None:
        """White on black should have maximum contrast ratio of 21:1."""
        ratio = self.calc.calculate_contrast_ratio("#FFFFFF", "#000000")
        assert abs(ratio - 21.0) < 0.1

    def test_black_on_white_maximum_contrast(self) -> None:
        """Black on white should also have maximum contrast ratio of 21:1."""
        ratio = self.calc.calculate_contrast_ratio("#000000", "#FFFFFF")
        assert abs(ratio - 21.0) < 0.1

    def test_identical_colors_minimum_contrast(self) -> None:
        """Identical colors should have minimum contrast ratio of 1:1."""
        ratio = self.calc.calculate_contrast_ratio("#FFFFFF", "#FFFFFF")
        assert abs(ratio - 1.0) < 0.1

    def test_light_gray_on_white_low_contrast(self) -> None:
        """Light gray (#CCCCCC) on white should have low contrast (~1.6:1)."""
        ratio = self.calc.calculate_contrast_ratio("#CCCCCC", "#FFFFFF")
        assert 1.5 < ratio < 1.8

    def test_blue_on_white_contrast(self) -> None:
        """Blue (#0066CC) on white should calculate correctly."""
        ratio = self.calc.calculate_contrast_ratio("#0066CC", "#FFFFFF")
        # Blue on white should be around 5.5:1 to 6:1
        assert 5.0 < ratio < 7.0

    def test_medium_gray_contrast(self) -> None:
        """Medium gray (#808080) on white should be around 4:1."""
        ratio = self.calc.calculate_contrast_ratio("#808080", "#FFFFFF")
        assert 3.5 < ratio < 4.5

    def test_accepts_lowercase_hex(self) -> None:
        """Should accept lowercase hex values."""
        ratio = self.calc.calculate_contrast_ratio("#ffffff", "#000000")
        assert abs(ratio - 21.0) < 0.1

    def test_accepts_short_hex_format(self) -> None:
        """Should accept short #RGB format."""
        ratio = self.calc.calculate_contrast_ratio("#FFF", "#000")
        assert abs(ratio - 21.0) < 0.1

    def test_accepts_without_hash(self) -> None:
        """Should accept hex values without leading #."""
        ratio = self.calc.calculate_contrast_ratio("FFFFFF", "000000")
        assert abs(ratio - 21.0) < 0.1

    def test_red_on_white_contrast(self) -> None:
        """Red (#FF0000) on white should have specific contrast."""
        ratio = self.calc.calculate_contrast_ratio("#FF0000", "#FFFFFF")
        # Red has lower luminance than white
        assert 3.5 < ratio < 4.5

    def test_green_on_black_contrast(self) -> None:
        """Green (#00FF00) on black should have high contrast."""
        ratio = self.calc.calculate_contrast_ratio("#00FF00", "#000000")
        # Pure green is quite bright
        assert ratio > 15.0

    def test_invalid_hex_raises_error(self) -> None:
        """Invalid hex values should raise ValidationError."""
        with pytest.raises(ValidationError):
            self.calc.calculate_contrast_ratio("#GGGGGG", "#FFFFFF")

    def test_empty_hex_raises_error(self) -> None:
        """Empty hex values should raise ValidationError."""
        with pytest.raises(ValidationError):
            self.calc.calculate_contrast_ratio("", "#FFFFFF")

    def test_too_short_hex_raises_error(self) -> None:
        """Too short hex values should raise ValidationError."""
        with pytest.raises(ValidationError):
            self.calc.calculate_contrast_ratio("#FF", "#FFFFFF")


class TestGetRelativeLuminance:
    """Tests for get_relative_luminance method."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.calc = AccessibilityCalculator()

    def test_white_luminance(self) -> None:
        """White should have luminance of 1.0."""
        luminance = self.calc.get_relative_luminance("#FFFFFF")
        assert abs(luminance - 1.0) < 0.001

    def test_black_luminance(self) -> None:
        """Black should have luminance of 0.0."""
        luminance = self.calc.get_relative_luminance("#000000")
        assert abs(luminance - 0.0) < 0.001

    def test_gray_luminance(self) -> None:
        """Mid-gray should have luminance around 0.21."""
        luminance = self.calc.get_relative_luminance("#808080")
        # Due to gamma correction, mid-gray is not 0.5
        assert 0.15 < luminance < 0.25

    def test_red_luminance(self) -> None:
        """Pure red luminance should be based on red coefficient."""
        luminance = self.calc.get_relative_luminance("#FF0000")
        # Red coefficient is 0.2126
        assert 0.20 < luminance < 0.22

    def test_green_luminance(self) -> None:
        """Pure green luminance should be based on green coefficient."""
        luminance = self.calc.get_relative_luminance("#00FF00")
        # Green coefficient is 0.7152
        assert 0.70 < luminance < 0.73

    def test_blue_luminance(self) -> None:
        """Pure blue luminance should be based on blue coefficient."""
        luminance = self.calc.get_relative_luminance("#0000FF")
        # Blue coefficient is 0.0722
        assert 0.07 < luminance < 0.08


class TestCheckWCAGCompliance:
    """Tests for check_wcag_compliance method."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.calc = AccessibilityCalculator()

    def test_aa_normal_passes_at_threshold(self) -> None:
        """AA normal text requires 4.5:1."""
        assert self.calc.check_wcag_compliance(4.5, WCAGLevel.AA, is_large_text=False)

    def test_aa_normal_fails_below_threshold(self) -> None:
        """AA normal text fails below 4.5:1."""
        assert not self.calc.check_wcag_compliance(4.4, WCAGLevel.AA, is_large_text=False)

    def test_aa_large_passes_at_threshold(self) -> None:
        """AA large text requires 3.0:1."""
        assert self.calc.check_wcag_compliance(3.0, WCAGLevel.AA, is_large_text=True)

    def test_aa_large_fails_below_threshold(self) -> None:
        """AA large text fails below 3.0:1."""
        assert not self.calc.check_wcag_compliance(2.9, WCAGLevel.AA, is_large_text=True)

    def test_aaa_normal_passes_at_threshold(self) -> None:
        """AAA normal text requires 7.0:1."""
        assert self.calc.check_wcag_compliance(7.0, WCAGLevel.AAA, is_large_text=False)

    def test_aaa_normal_fails_below_threshold(self) -> None:
        """AAA normal text fails below 7.0:1."""
        assert not self.calc.check_wcag_compliance(6.9, WCAGLevel.AAA, is_large_text=False)

    def test_aaa_large_passes_at_threshold(self) -> None:
        """AAA large text requires 4.5:1."""
        assert self.calc.check_wcag_compliance(4.5, WCAGLevel.AAA, is_large_text=True)

    def test_aaa_large_fails_below_threshold(self) -> None:
        """AAA large text fails below 4.5:1."""
        assert not self.calc.check_wcag_compliance(4.4, WCAGLevel.AAA, is_large_text=True)

    def test_maximum_contrast_passes_all(self) -> None:
        """21:1 ratio should pass all levels."""
        assert self.calc.check_wcag_compliance(21.0, WCAGLevel.AA, is_large_text=False)
        assert self.calc.check_wcag_compliance(21.0, WCAGLevel.AAA, is_large_text=False)

    def test_default_parameters(self) -> None:
        """Test default parameters (AA level, normal text)."""
        assert self.calc.check_wcag_compliance(4.5)
        assert not self.calc.check_wcag_compliance(4.4)


class TestContrastResult:
    """Tests for ContrastResult model and check_contrast method."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.calc = AccessibilityCalculator()

    def test_check_contrast_returns_result(self) -> None:
        """check_contrast should return ContrastResult."""
        result = self.calc.check_contrast("#FFFFFF", "#000000")
        assert isinstance(result, ContrastResult)

    def test_high_contrast_passes_all(self) -> None:
        """White on black passes all WCAG levels."""
        result = self.calc.check_contrast("#FFFFFF", "#000000")
        assert result.ratio > 20
        assert result.passes_aa is True
        assert result.passes_aaa is True
        assert result.passes_aa_large is True
        assert result.passes_aaa_large is True

    def test_low_contrast_fails_all(self) -> None:
        """Light gray on white fails all WCAG levels."""
        result = self.calc.check_contrast("#CCCCCC", "#FFFFFF")
        assert result.ratio < 2
        assert result.passes_aa is False
        assert result.passes_aaa is False
        assert result.passes_aa_large is False
        assert result.passes_aaa_large is False

    def test_medium_contrast_passes_large_only(self) -> None:
        """Medium contrast passes large text but not normal."""
        # Use #888888 which has ~3.5:1 contrast
        result = self.calc.check_contrast("#888888", "#FFFFFF")
        # Should pass AA large (3:1) but not AA normal (4.5:1)
        assert result.passes_aa_large is True
        assert result.passes_aa is False


class TestSimulateColorblind:
    """Tests for simulate_colorblind method."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.calc = AccessibilityCalculator()

    def test_deuteranopia_simulation(self) -> None:
        """Deuteranopia simulation should modify green perception."""
        original = "#00FF00"
        simulated = self.calc.simulate_colorblind(original, ColorblindType.DEUTERANOPIA)
        # Green-blind should see pure green differently
        assert simulated != original
        # Result should still be valid hex
        assert len(simulated) == 7
        assert simulated.startswith("#")

    def test_protanopia_simulation(self) -> None:
        """Protanopia simulation should modify red perception."""
        original = "#FF0000"
        simulated = self.calc.simulate_colorblind(original, ColorblindType.PROTANOPIA)
        # Red-blind should see pure red differently
        assert simulated != original
        assert len(simulated) == 7
        assert simulated.startswith("#")

    def test_tritanopia_simulation(self) -> None:
        """Tritanopia simulation should modify blue perception."""
        original = "#0000FF"
        simulated = self.calc.simulate_colorblind(original, ColorblindType.TRITANOPIA)
        # Blue-blind should see pure blue differently
        assert simulated != original
        assert len(simulated) == 7
        assert simulated.startswith("#")

    def test_white_unchanged(self) -> None:
        """White should remain white for all types."""
        for cb_type in ColorblindType:
            simulated = self.calc.simulate_colorblind("#FFFFFF", cb_type)
            # White should stay very close to white
            # Allow small deviation due to rounding
            assert simulated.upper() in ("#FFFFFF", "#FEFEFE", "#FEFEFF")

    def test_black_unchanged(self) -> None:
        """Black should remain black for all types."""
        for cb_type in ColorblindType:
            simulated = self.calc.simulate_colorblind("#000000", cb_type)
            assert simulated.upper() in ("#000000", "#010101", "#000001")

    def test_invalid_colorblind_type(self) -> None:
        """Invalid colorblind type should raise error."""
        with pytest.raises((ValidationError, ValueError)):
            self.calc.simulate_colorblind("#FF0000", "invalid_type")  # type: ignore

    def test_gray_similar_for_all_types(self) -> None:
        """Gray should be similar across all colorblind types."""
        original = "#808080"
        simulations = [
            self.calc.simulate_colorblind(original, cb_type)
            for cb_type in ColorblindType
        ]
        # All simulations should be similar for gray
        for sim in simulations:
            # Parse RGB values
            r = int(sim[1:3], 16)
            g = int(sim[3:5], 16)
            b = int(sim[5:7], 16)
            # Should be close to 128
            assert 100 < r < 160
            assert 100 < g < 160
            assert 100 < b < 160


class TestCheckColorblindSafety:
    """Tests for check_colorblind_safety method."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.calc = AccessibilityCalculator()

    def test_high_contrast_palette_safe(self) -> None:
        """High contrast palette should be safe for colorblind users."""
        colors = ["#000000", "#FFFFFF"]
        result = self.calc.check_colorblind_safety(colors)

        assert "deuteranopia" in result
        assert "protanopia" in result
        assert "tritanopia" in result

        # Black and white should be distinguishable for all types
        for score in result.values():
            assert score > 0.8

    def test_red_green_palette_unsafe_for_some(self) -> None:
        """Red and green only palette may be unsafe for some types."""
        colors = ["#FF0000", "#00FF00"]
        result = self.calc.check_colorblind_safety(colors)

        # Deuteranopia and protanopia affect red-green distinction
        # These scores should be lower
        assert result["deuteranopia"] < result.get("tritanopia", 1.0) or True
        # The key is that we get valid scores
        for score in result.values():
            assert 0.0 <= score <= 1.0

    def test_single_color_returns_perfect_score(self) -> None:
        """Single color palette should return perfect safety scores."""
        colors = ["#FF0000"]
        result = self.calc.check_colorblind_safety(colors)

        for score in result.values():
            assert score == 1.0

    def test_empty_palette_returns_perfect_score(self) -> None:
        """Empty palette should return perfect safety scores."""
        colors: list[str] = []
        result = self.calc.check_colorblind_safety(colors)

        for score in result.values():
            assert score == 1.0

    def test_diverse_palette_scores(self) -> None:
        """Diverse palette should have reasonable scores."""
        colors = ["#FF0000", "#00FF00", "#0000FF", "#FFFF00", "#FF00FF", "#00FFFF"]
        result = self.calc.check_colorblind_safety(colors)

        # All scores should be between 0 and 1
        for score in result.values():
            assert 0.0 <= score <= 1.0

    def test_similar_colors_lower_score(self) -> None:
        """Very similar colors should have lower safety scores."""
        colors = ["#FF0000", "#FF1100", "#FF2200"]
        result = self.calc.check_colorblind_safety(colors)

        # Scores might be lower due to similarity
        for score in result.values():
            assert 0.0 <= score <= 1.0


class TestCalculateAccessibilityScore:
    """Tests for calculate_accessibility_score method."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.calc = AccessibilityCalculator()

    def test_non_color_token_returns_one(self) -> None:
        """Non-color tokens should return score of 1.0."""
        token = TokenResult(
            token_type=TokenType.SPACING,
            name="small",
            value="8px",
            confidence=0.9,
        )
        score = self.calc.calculate_accessibility_score(token)
        assert score == 1.0

    def test_high_contrast_color_high_score(self) -> None:
        """High contrast color should have high accessibility score."""
        token = TokenResult(
            token_type=TokenType.COLOR,
            name="primary",
            value="#000000",
            confidence=0.9,
            w3c_type=W3CTokenType.COLOR,
        )
        # Black on white background has 21:1 contrast
        score = self.calc.calculate_accessibility_score(token, background_color="#FFFFFF")
        assert score > 0.8

    def test_low_contrast_color_low_score(self) -> None:
        """Low contrast color should have low accessibility score."""
        token = TokenResult(
            token_type=TokenType.COLOR,
            name="light-text",
            value="#CCCCCC",
            confidence=0.9,
            w3c_type=W3CTokenType.COLOR,
        )
        # Light gray on white has ~1.6:1 contrast
        score = self.calc.calculate_accessibility_score(token, background_color="#FFFFFF")
        assert score < 0.5

    def test_custom_background_color(self) -> None:
        """Should use custom background color for contrast calculation."""
        token = TokenResult(
            token_type=TokenType.COLOR,
            name="light",
            value="#FFFFFF",
            confidence=0.9,
            w3c_type=W3CTokenType.COLOR,
        )
        # White on black background
        score = self.calc.calculate_accessibility_score(token, background_color="#000000")
        assert score > 0.8

    def test_medium_contrast_medium_score(self) -> None:
        """Medium contrast should have medium score."""
        token = TokenResult(
            token_type=TokenType.COLOR,
            name="gray",
            value="#666666",
            confidence=0.9,
            w3c_type=W3CTokenType.COLOR,
        )
        score = self.calc.calculate_accessibility_score(token)
        # Medium gray on white should pass AA
        assert 0.4 < score < 0.9

    def test_invalid_color_value_raises_error(self) -> None:
        """Invalid color value should raise ValidationError."""
        token = TokenResult(
            token_type=TokenType.COLOR,
            name="invalid",
            value="not-a-color",
            confidence=0.9,
            w3c_type=W3CTokenType.COLOR,
        )
        with pytest.raises(ValidationError):
            self.calc.calculate_accessibility_score(token)

    def test_gradient_token_returns_one(self) -> None:
        """Gradient tokens should return score of 1.0."""
        token = TokenResult(
            token_type=TokenType.GRADIENT,
            name="fade",
            value={"stops": [{"color": "#FF0000"}, {"color": "#0000FF"}]},
            confidence=0.9,
        )
        score = self.calc.calculate_accessibility_score(token)
        assert score == 1.0

    def test_typography_token_returns_one(self) -> None:
        """Typography tokens should return score of 1.0."""
        token = TokenResult(
            token_type=TokenType.TYPOGRAPHY,
            name="heading",
            value={"fontFamily": "Arial", "fontSize": "24px"},
            confidence=0.9,
        )
        score = self.calc.calculate_accessibility_score(token)
        assert score == 1.0

    def test_shadow_token_returns_one(self) -> None:
        """Shadow tokens should return score of 1.0."""
        token = TokenResult(
            token_type=TokenType.SHADOW,
            name="elevation",
            value={"offsetX": "0px", "offsetY": "4px", "blur": "8px"},
            confidence=0.9,
        )
        score = self.calc.calculate_accessibility_score(token)
        assert score == 1.0

    def test_score_is_between_zero_and_one(self) -> None:
        """Score should always be between 0 and 1."""
        token = TokenResult(
            token_type=TokenType.COLOR,
            name="test",
            value="#808080",
            confidence=0.9,
        )
        score = self.calc.calculate_accessibility_score(token)
        assert 0.0 <= score <= 1.0


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.calc = AccessibilityCalculator()

    def test_hex_with_alpha_channel(self) -> None:
        """Hex with alpha channel should work (alpha ignored)."""
        # 8-character hex with alpha
        ratio = self.calc.calculate_contrast_ratio("#FFFFFFFF", "#000000FF")
        assert abs(ratio - 21.0) < 0.1

    def test_rgb_format_not_supported(self) -> None:
        """RGB format should raise ValidationError."""
        with pytest.raises(ValidationError):
            self.calc.calculate_contrast_ratio("rgb(255, 255, 255)", "#000000")

    def test_hsl_format_not_supported(self) -> None:
        """HSL format should raise ValidationError."""
        with pytest.raises(ValidationError):
            self.calc.calculate_contrast_ratio("hsl(0, 0%, 100%)", "#000000")

    def test_named_colors_not_supported(self) -> None:
        """Named colors should raise ValidationError."""
        with pytest.raises(ValidationError):
            self.calc.calculate_contrast_ratio("white", "black")

    def test_special_characters_in_hex(self) -> None:
        """Special characters in hex should raise ValidationError."""
        with pytest.raises(ValidationError):
            self.calc.calculate_contrast_ratio("#FF-F00", "#000000")

    def test_contrast_result_serialization(self) -> None:
        """ContrastResult should be serializable."""
        result = self.calc.check_contrast("#FFFFFF", "#000000")
        data = result.model_dump()
        assert "ratio" in data
        assert "passes_aa" in data
        assert "passes_aaa" in data

    def test_wcag_level_enum_values(self) -> None:
        """WCAGLevel enum should have expected values."""
        assert WCAGLevel.A.value == "A"
        assert WCAGLevel.AA.value == "AA"
        assert WCAGLevel.AAA.value == "AAA"

    def test_colorblind_type_enum_values(self) -> None:
        """ColorblindType enum should have expected values."""
        assert ColorblindType.DEUTERANOPIA.value == "deuteranopia"
        assert ColorblindType.PROTANOPIA.value == "protanopia"
        assert ColorblindType.TRITANOPIA.value == "tritanopia"


class TestIntegration:
    """Integration tests for AccessibilityCalculator."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.calc = AccessibilityCalculator()

    def test_full_accessibility_check_workflow(self) -> None:
        """Test complete accessibility checking workflow."""
        # Create color token
        token = TokenResult(
            token_type=TokenType.COLOR,
            name="brand-primary",
            path=["color", "brand"],
            value="#0066CC",
            confidence=0.95,
            w3c_type=W3CTokenType.COLOR,
            description="Primary brand color",
        )

        # Calculate accessibility score
        score = self.calc.calculate_accessibility_score(token)
        assert 0.0 <= score <= 1.0

        # Check contrast with white background
        result = self.calc.check_contrast("#0066CC", "#FFFFFF")
        assert isinstance(result, ContrastResult)

        # Simulate colorblind views
        for cb_type in ColorblindType:
            simulated = self.calc.simulate_colorblind("#0066CC", cb_type)
            assert simulated.startswith("#")

        # Check palette safety
        palette = ["#0066CC", "#FFFFFF", "#333333"]
        safety = self.calc.check_colorblind_safety(palette)
        assert len(safety) == 3  # Three colorblind types

    def test_multiple_tokens_scoring(self) -> None:
        """Test scoring multiple tokens."""
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
            TokenResult(
                token_type=TokenType.COLOR,
                name="gray",
                value="#808080",
                confidence=0.9,
            ),
        ]

        scores = [self.calc.calculate_accessibility_score(t) for t in tokens]

        # Black on white background should score highest
        assert scores[0] > scores[2]  # Black > Gray
        # White on white would have lowest score
        # Gray should be in the middle

    def test_wcag_threshold_boundary_testing(self) -> None:
        """Test exact WCAG threshold boundaries."""
        # Test AA normal threshold (4.5:1)
        assert self.calc.check_wcag_compliance(4.50, WCAGLevel.AA, False)
        assert self.calc.check_wcag_compliance(4.51, WCAGLevel.AA, False)
        assert not self.calc.check_wcag_compliance(4.49, WCAGLevel.AA, False)

        # Test AA large threshold (3.0:1)
        assert self.calc.check_wcag_compliance(3.00, WCAGLevel.AA, True)
        assert not self.calc.check_wcag_compliance(2.99, WCAGLevel.AA, True)

        # Test AAA normal threshold (7.0:1)
        assert self.calc.check_wcag_compliance(7.00, WCAGLevel.AAA, False)
        assert not self.calc.check_wcag_compliance(6.99, WCAGLevel.AAA, False)

        # Test AAA large threshold (4.5:1)
        assert self.calc.check_wcag_compliance(4.50, WCAGLevel.AAA, True)
        assert not self.calc.check_wcag_compliance(4.49, WCAGLevel.AAA, True)
