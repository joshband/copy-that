"""Tests for CVSpacingExtractor graceful fallback and happy-path defaults."""

import pytest

pytest.importorskip("PIL")

from copy_that.extractors.spacing import cv_extractor as spacing_mod
from copy_that.extractors.spacing.cv_extractor import CVSpacingExtractor


def test_cvspacing_fallback_without_opencv(monkeypatch):
    """If cv2 is missing, extractor should return low-confidence fallback tokens."""
    monkeypatch.setattr(spacing_mod, "cv2", None)
    extractor = CVSpacingExtractor()
    result = extractor.extract_from_bytes(b"")
    assert result.tokens
    assert result.base_unit == 4
    assert result.scale_system == "4pt"
    assert result.extraction_confidence <= 0.2
    assert result.tokens[0].extraction_metadata["source"] == "cv_fallback"
    assert result.tokens[0].extraction_metadata["measured"] is False


def test_cvspacing_ml_defaults_off(monkeypatch):
    monkeypatch.delenv("FASTSAM_ENABLED", raising=False)
    monkeypatch.delenv("ENABLE_UIED", raising=False)
    monkeypatch.delenv("ENABLE_SPACING_DEPTH", raising=False)
    extractor = CVSpacingExtractor()
    assert extractor._fastsam_enabled is False
    assert extractor._uied_enabled is False
    assert extractor._depth_enabled is False


def test_cvspacing_ml_opt_in(monkeypatch):
    monkeypatch.setenv("FASTSAM_ENABLED", "1")
    monkeypatch.setenv("ENABLE_UIED", "true")
    monkeypatch.setenv("ENABLE_SPACING_DEPTH", "1")
    extractor = CVSpacingExtractor()
    assert extractor._fastsam_enabled is True
    assert extractor._uied_enabled is True
    assert extractor._depth_enabled is True


def test_cvspacing_detects_baseline_token(monkeypatch):
    class DummyGray:
        shape = (120, 320)

        def __getitem__(self, key):
            return None

    dummy_gray = DummyGray()
    monkeypatch.setattr(
        spacing_mod, "preprocess_image", lambda data: {"cv_gray": dummy_gray, "cv_bgr": dummy_gray}
    )
    monkeypatch.setattr(spacing_mod, "apply_text_mask", lambda bgr, gray: (bgr, gray, []))
    monkeypatch.setattr(spacing_mod, "bounding_boxes_from_contours", lambda gray, min_area=256: [])
    monkeypatch.setattr(
        spacing_mod,
        "components_to_bboxes",
        lambda gray: [(0, 0, 30, 10), (10, 20, 36, 12), (6, 40, 34, 10), (5, 60, 30, 10)],
    )
    monkeypatch.setattr(
        spacing_mod,
        "gaps_from_bboxes",
        lambda bboxes, **kwargs: ([8, 16, 24], []),
    )
    monkeypatch.setattr(CVSpacingExtractor, "_detect_guides", lambda self, gray: [])
    monkeypatch.setattr(
        CVSpacingExtractor, "_snap_gaps_to_guides", lambda self, gray, gaps: list(gaps)
    )
    extractor = CVSpacingExtractor(max_tokens=4)
    result = extractor.extract_from_bytes(b"raw")
    baseline_tokens = [t for t in result.tokens if t.name == "spacing-baseline"]
    assert baseline_tokens, "baseline token should be present"
    assert result.baseline_spacing is not None
    assert result.baseline_spacing["value_px"] == baseline_tokens[0].value_px


def test_cvspacing_component_metrics_and_grid(monkeypatch):
    class DummyGray:
        shape = (200, 360)

    dummy_gray = DummyGray()
    monkeypatch.setattr(
        spacing_mod, "preprocess_image", lambda data: {"cv_gray": dummy_gray, "cv_bgr": dummy_gray}
    )
    monkeypatch.setattr(spacing_mod, "apply_text_mask", lambda bgr, gray: (bgr, gray, []))
    monkeypatch.setattr(spacing_mod, "bounding_boxes_from_contours", lambda gray, min_area=256: [])
    boxes = [
        (0, 0, 80, 60),
        (10, 10, 50, 20),
        (100, 0, 80, 60),
        (110, 12, 40, 22),
        (210, 0, 80, 60),
        (220, 12, 40, 22),
    ]
    monkeypatch.setattr(spacing_mod, "components_to_bboxes", lambda gray: boxes)
    monkeypatch.setattr(
        spacing_mod,
        "gaps_from_bboxes",
        lambda bboxes, **kwargs: ([12, 18, 24], [20]),
    )
    monkeypatch.setattr(
        spacing_mod,
        "infer_grid_from_bboxes",
        lambda bboxes, canvas_width: {
            "columns": 3,
            "gutter_px": 20,
            "margin_left": 12,
            "margin_right": 18,
        },
    )
    monkeypatch.setattr(CVSpacingExtractor, "_detect_guides", lambda self, gray: [])
    monkeypatch.setattr(
        CVSpacingExtractor, "_snap_gaps_to_guides", lambda self, gray, gaps: list(gaps)
    )
    monkeypatch.setattr(
        CVSpacingExtractor,
        "_infer_component_spacing_metrics",
        lambda self, *a, **k: [],
    )
    extractor = CVSpacingExtractor(max_tokens=6)
    result = extractor.extract_from_bytes(b"raw")
    assert result.tokens
    assert result.extraction_confidence > 0.2
