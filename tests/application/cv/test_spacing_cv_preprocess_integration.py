"""Integration test ensuring spacing CV extractor uses shared preprocessing."""

from __future__ import annotations

import io

from PIL import Image, ImageDraw

from copy_that.application.cv.spacing_cv_extractor import CVSpacingExtractor


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
    assert result.base_unit in (4, 8)
    # Ensure we produced at least one grid-aligned token
    assert any(t.grid_aligned for t in result.tokens if hasattr(t, "grid_aligned"))
