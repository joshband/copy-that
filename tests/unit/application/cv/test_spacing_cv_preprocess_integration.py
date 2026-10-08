"""Integration test ensuring spacing CV extractor uses shared preprocessing."""

from __future__ import annotations

import io

from PIL import Image, ImageDraw

from copy_that.extractors.spacing.cv_extractor import CVSpacingExtractor


def _synthetic_spacing_image() -> bytes:
    """Create a simple image with two black rectangles to force detectable gaps."""
    img = Image.new("RGB", (200, 200), "white")
    draw = ImageDraw.Draw(img)
    draw.rectangle((10, 50, 40, 150), fill="black")
    draw.rectangle((100, 50, 130, 150), fill="black")
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return buffer.getvalue()


def test_spacing_cv_extractor_uses_preprocess_and_returns_tokens() -> None:
    data = _synthetic_spacing_image()
    extractor = CVSpacingExtractor(max_tokens=5)
    result = extractor.extract_from_bytes(data)

    assert result.tokens, "Expected spacing tokens from CV extractor"
    assert result.base_unit and result.base_unit > 0
    # Measured path should beat the honest 4pt fallback confidence.
    assert result.extraction_confidence >= 0.15


def test_spacing_cv_extractor_gap_regression() -> None:
    """
    Regression: ensure shared primitives produce stable spacing gaps.
    """
    data = _synthetic_spacing_image()
    extractor = CVSpacingExtractor(max_tokens=5)
    result = extractor.extract_from_bytes(data)

    assert result.tokens
    assert result.unique_values
    gap = result.unique_values[0]
    # Two 30px-wide bars with ~60px gutter on a 200px canvas.
    assert 40 <= gap <= 80
    assert result.base_unit and result.base_unit > 0
    assert any(t.value_px == gap for t in result.tokens)
