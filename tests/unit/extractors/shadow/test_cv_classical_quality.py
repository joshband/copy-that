"""Classical CSS shadow synthesis quality fixtures."""

from __future__ import annotations

import base64
import io

import numpy as np
import pytest
from PIL import Image, ImageDraw, ImageFilter

from copy_that.extractors.shadow.cv_extractor import (
    CVShadowExtractor,
    _roles_for_density,
)


def _b64_png(arr: np.ndarray) -> str:
    img = Image.fromarray(arr, mode="RGB")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("ascii")


def _flat_panel_b64() -> str:
    return _b64_png(np.full((96, 96, 3), 220, dtype=np.uint8))


def _soft_card_shadow_b64() -> str:
    """Light card on pale ground with a soft bottom/right drop shadow."""
    canvas = Image.new("RGB", (160, 160), color=(245, 245, 248))
    shadow = Image.new("RGBA", (160, 160), (0, 0, 0, 0))
    draw = ImageDraw.Draw(shadow)
    draw.rounded_rectangle((38, 42, 128, 132), radius=10, fill=(0, 0, 0, 90))
    shadow = shadow.filter(ImageFilter.GaussianBlur(radius=6))
    canvas = Image.alpha_composite(canvas.convert("RGBA"), shadow).convert("RGB")
    card = ImageDraw.Draw(canvas)
    card.rounded_rectangle((32, 32, 120, 120), radius=10, fill=(255, 255, 255))
    buf = io.BytesIO()
    canvas.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("ascii")


def _heavy_cast_shadow_b64() -> str:
    """Large dark cast region under a bright lit band (heavy coverage)."""
    arr = np.full((128, 128, 3), 210, dtype=np.uint8)
    arr[55:120, 20:110, :] = 35
    # Soft edge
    arr[50:55, 20:110, :] = 90
    return _b64_png(arr)


@pytest.mark.parametrize(
    ("density", "area", "expected"),
    [
        ("sparse", 0.05, ("subtle",)),
        ("moderate", 0.12, ("subtle", "medium")),
        ("heavy", 0.4, ("subtle", "medium", "strong")),
        ("full", 0.8, ("subtle", "medium", "strong")),
    ],
)
def test_roles_for_density(density, area, expected):
    assert _roles_for_density(density, area) == expected


def test_flat_panel_yields_empty_classical(monkeypatch):
    monkeypatch.delenv("ENABLE_DARK_BLOB_SHADOW_CV", raising=False)
    result = CVShadowExtractor().extract_shadows(_flat_panel_b64())
    assert result.extractor_used == "cv_classical_empty"
    assert result.shadow_count == 0
    assert result.opacity_tokens == []
    assert result.product_message == "No elevation detected"
    assert "No elevation detected" in result.warnings


def test_soft_card_yields_subtle_or_medium(monkeypatch):
    monkeypatch.delenv("ENABLE_DARK_BLOB_SHADOW_CV", raising=False)
    result = CVShadowExtractor().extract_shadows(_soft_card_shadow_b64())
    assert result.extractor_used == "cv_classical_css"
    assert result.shadow_count >= 1
    names = {s.semantic_name for s in result.shadows}
    assert "shadow-subtle" in names
    assert "shadow-strong" not in names or result.shadow_count <= 2
    assert all(0.0 < s.opacity <= 0.5 for s in result.shadows)
    assert result.opacity_tokens
    assert result.extraction_confidence >= 0.35


def test_heavy_cast_can_include_strong(monkeypatch):
    monkeypatch.delenv("ENABLE_DARK_BLOB_SHADOW_CV", raising=False)
    result = CVShadowExtractor().extract_shadows(_heavy_cast_shadow_b64())
    assert result.extractor_used in {"cv_classical_css", "cv_classical_empty"}
    if result.extractor_used == "cv_classical_css":
        names = [s.semantic_name for s in result.shadows]
        assert names[0] == "shadow-subtle"
        assert result.shadow_count <= 3
        # Stronger coverage should not invent inset/text shadows
        assert all(not s.is_inset and not s.affects_text for s in result.shadows)
