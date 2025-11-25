'"""Unit tests for spacing token generators."""'

from copy_that.generators.spacing_css_generator import SpacingCSSGenerator
from copy_that.generators.spacing_html_demo_generator import SpacingHTMLDemoGenerator
from copy_that.generators.spacing_react_generator import SpacingReactGenerator
from copy_that.generators.spacing_w3c_generator import SpacingW3CGenerator
from copy_that.tokens.spacing.aggregator import AggregatedSpacingToken, SpacingTokenLibrary


def _library_with_token() -> SpacingTokenLibrary:
    token = AggregatedSpacingToken(
        value_px=8,
        name="spacing-xs",
        confidence=0.85,
        semantic_role="padding",
        grid_aligned=True,
        base_unit=4,
        role="xs",
        merged_values=[8],
    )
    token.provenance = {"image_0": 0.85}
    token.responsive_scales = {"md": 12, "lg": 16}
    token.scale_position = 0
    library = SpacingTokenLibrary(tokens=[token])
    library.statistics = {
        "spacing_count": 1,
        "scale_system": "4pt",
        "base_unit": 4,
        "grid_compliance": 0.95,
    }
    return library


def test_spacing_css_generator_includes_variables_and_comments():
    library = _library_with_token()
    css = SpacingCSSGenerator(library).generate()
    assert "--spacing-xs: 8px;" in css
    assert "--spacing-xs-rem: 0.5rem;" in css
    assert "Spacing Scale - 4pt (1 values)" in css
    assert "confidence: 0.85" in css

    responsive = SpacingCSSGenerator(library).generate_with_breakpoints()
    assert "@media (min-width: 768px)" in responsive or "@media (min-width: 992px)" in responsive

    utilities = SpacingCSSGenerator(library).generate_utility_classes()
    assert ".p-xs" in utilities
    assert ".m-xs" in utilities


def test_spacing_html_generator_contains_cards_and_stats():
    library = _library_with_token()
    html = SpacingHTMLDemoGenerator(library).generate()
    assert "Spacing Token Library" in html
    assert "spacing-xs" in html
    assert "grid_template_columns" not in html  # ensure layout is as expected
    assert "scale-visual" in html


def test_spacing_react_generator_exports_and_helpers():
    library = _library_with_token()
    react_ts = SpacingReactGenerator(library).generate()
    assert "export const spacing" in react_ts
    assert "getSpacingRem" in react_ts
    assert "confidence: 0.85" in react_ts
    assert "xs:" in react_ts


def test_spacing_w3c_generator_builds_json_with_extensions():
    library = _library_with_token()
    w3c = SpacingW3CGenerator(library).generate()
    assert '"spacing"' in w3c
    assert '"$value": "8px"' in w3c
    assert '"rem": "0.5rem"' in w3c
    assert '"confidence": 0.85' in w3c
    assert '"scale_system": "4pt"' in w3c
