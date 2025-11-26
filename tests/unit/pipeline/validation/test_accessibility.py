import pytest

from copy_that.pipeline import TokenResult, TokenType
from copy_that.pipeline.exceptions import ValidationError
from copy_that.pipeline.validation.accessibility import AccessibilityCalculator, ColorblindType


def _token(name: str, value: str) -> TokenResult:
    return TokenResult(
        token_type=TokenType.COLOR,
        name=name,
        value=value,
        confidence=0.9,
    )


def test_parse_hex_invalid_raises():
    calc = AccessibilityCalculator()
    with pytest.raises(ValidationError):
        calc.calculate_contrast_ratio("#ZZZZZZ", "#FFFFFF")


def test_contrast_ratio_extremes():
    calc = AccessibilityCalculator()
    # Black vs white -> max
    max_ratio = calc.calculate_contrast_ratio("#000000", "#FFFFFF")
    assert pytest.approx(21.0, rel=1e-3) == max_ratio

    # Same color -> 1.0
    same_ratio = calc.calculate_contrast_ratio("#123456", "#123456")
    assert same_ratio == pytest.approx(1.0)


def test_contrast_result_flags():
    calc = AccessibilityCalculator()
    result = calc.check_contrast("#000000", "#FFFFFF")
    assert result.passes_aa
    assert result.passes_aaa
    assert result.passes_aa_large
    assert result.passes_aaa_large


def test_colorblind_simulation_returns_hex():
    calc = AccessibilityCalculator()
    simulated = calc.simulate_colorblind("#FF0000", ColorblindType.PROTANOPIA)
    assert simulated.startswith("#")
    assert len(simulated) == 7


def test_colorblind_safety_scores_monotonic():
    calc = AccessibilityCalculator()
    palette = ["#FF0000", "#00FF00", "#0000FF"]
    safety = calc.check_colorblind_safety(palette)
    assert set(safety.keys()) == {t.value for t in ColorblindType}
    for score in safety.values():
        assert 0.0 <= score <= 1.0


def test_accessibility_score_raises_for_invalid_color():
    calc = AccessibilityCalculator()
    token = _token("invalid", "not-a-color")
    with pytest.raises(ValidationError):
        calc.calculate_accessibility_score(token)


def test_accessibility_score_returns_one_for_non_color():
    calc = AccessibilityCalculator()
    token = TokenResult(
        token_type=TokenType.SPACING,
        name="spacing",
        value=8,
        confidence=1.0,
    )
    assert calc.calculate_accessibility_score(token) == 1.0
