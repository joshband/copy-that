"""Unit tests for shared OCR text-mask helper."""

from __future__ import annotations

import numpy as np

from copy_that.extractors.cv.text_mask import apply_text_mask


def test_apply_text_mask_fills_provided_boxes():
    bgr = np.zeros((40, 60, 3), dtype=np.uint8)
    bgr[:] = (40, 80, 120)
    bgr[10:20, 15:35] = (220, 220, 220)
    gray = bgr[:, :, 0].copy()

    masked_bgr, masked_gray, used = apply_text_mask(bgr, gray, boxes=[(15, 10, 20, 10)])
    assert used == [(15, 10, 20, 10)]
    assert float(masked_bgr[12:18, 18:30].mean()) < 200
    assert masked_gray.shape == gray.shape


def test_apply_text_mask_noop_without_boxes():
    bgr = np.full((16, 16, 3), 90, dtype=np.uint8)
    gray = np.full((16, 16), 90, dtype=np.uint8)
    out_bgr, out_gray, used = apply_text_mask(bgr, gray, boxes=[])
    assert used == []
    np.testing.assert_array_equal(out_bgr, bgr)
    np.testing.assert_array_equal(out_gray, gray)


def test_apply_text_mask_detects_via_ocr_hook(monkeypatch):
    import copy_that.extractors.cv.text_mask as tm

    monkeypatch.setattr(tm, "detect_text_boxes", lambda *_a, **_k: [(2, 2, 4, 4)])
    bgr = np.full((20, 20, 3), 50, dtype=np.uint8)
    bgr[2:6, 2:6] = (250, 250, 250)
    gray = bgr[:, :, 0].copy()
    _bgr, _gray, used = apply_text_mask(bgr, gray, boxes=None)
    assert used == [(2, 2, 4, 4)]
