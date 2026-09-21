"""Dark-blob shadow CV is opt-in; default path uses classical CSS synthesis."""

from __future__ import annotations

import base64
import io

import numpy as np
import pytest
from PIL import Image

from copy_that.extractors.shadow.cv_extractor import CVShadowExtractor, _parse_css_layer


def _png_b64(color: tuple[int, int, int] = (30, 30, 30), size: tuple[int, int] = (64, 64)) -> str:
    img = Image.new("RGB", size, color=color)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("ascii")


def _gradient_png_b64() -> str:
    """Soft dark→light gradient so classical cues have non-zero area."""
    arr = np.zeros((96, 96, 3), dtype=np.uint8)
    for y in range(96):
        v = int(40 + (y / 95.0) * 180)
        arr[y, :, :] = (v, v, v)
    # Dark blob offset from edges
    arr[20:50, 20:50, :] = 20
    img = Image.fromarray(arr, mode="RGB")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("ascii")


def test_dark_blob_shadow_cv_disabled_by_default_uses_classical(monkeypatch):
    monkeypatch.delenv("ENABLE_DARK_BLOB_SHADOW_CV", raising=False)
    result = CVShadowExtractor().extract_shadows(_gradient_png_b64())
    assert result.extractor_used in {"cv_classical_css", "cv_classical_empty"}
    assert result.extractor_used != "cv_dark_blob_opt_in"
    if result.shadow_count > 0:
        assert all(s.semantic_name.startswith("shadow-") for s in result.shadows)
        assert result.opacity_tokens


def test_dark_blob_shadow_cv_opt_in(monkeypatch):
    monkeypatch.setenv("ENABLE_DARK_BLOB_SHADOW_CV", "1")
    result = CVShadowExtractor().extract_shadows(_png_b64())
    assert result.extractor_used == "cv_dark_blob_opt_in"
    # Solid dark panel should be rejected by area/variance guards
    assert result.shadow_count == 0


def test_parse_css_layer_subtle():
    tok = _parse_css_layer("0px 2px 4px rgba(0, 0, 0, 0.25)", "subtle", 0.5)
    assert tok is not None
    assert tok.x_offset == 0.0
    assert tok.y_offset == 2.0
    assert tok.blur_radius == 4.0
    assert tok.opacity == pytest.approx(0.25)
    assert tok.color_hex == "#000000"
    assert tok.semantic_name == "shadow-subtle"
