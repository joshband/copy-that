"""Tests for CVSpacingExtractor graceful fallback."""

from copy_that.application.cv import spacing_cv_extractor
from copy_that.application.cv.spacing_cv_extractor import CVSpacingExtractor


def test_cvspacing_fallback_without_opencv(monkeypatch):
    """If cv2 is missing, extractor should return deterministic fallback tokens."""
    monkeypatch.setattr(spacing_cv_extractor, "cv2", None)
    extractor = CVSpacingExtractor()
    result = extractor.extract_from_bytes(b"")
    assert result.tokens  # fallback tokens exist
    assert result.base_unit == 4
    assert result.scale_system == "4pt"


def test_cvspacing_detects_baseline_token(monkeypatch):
    class DummyGray:
        shape = (120, 320)

        # emulate numpy sliceability
        def __getitem__(self, key):
            return None

    dummy_gray = DummyGray()
    monkeypatch.setattr(
        spacing_cv_extractor, "preprocess_image", lambda data: {"cv_gray": dummy_gray}
    )
    monkeypatch.setattr(
        spacing_cv_extractor,
        "components_to_bboxes",
        lambda gray: [(0, 0, 30, 10), (10, 20, 36, 12), (6, 40, 34, 10), (5, 60, 30, 10)],
    )
    monkeypatch.setattr(
        spacing_cv_extractor,
        "gaps_from_bboxes",
        lambda bboxes, **kwargs: ([8, 16, 24], []),
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
        spacing_cv_extractor, "preprocess_image", lambda data: {"cv_gray": dummy_gray}
    )
    boxes = [
        (0, 0, 80, 60),
        (10, 10, 50, 20),
        (100, 0, 80, 60),
        (110, 12, 40, 22),
        (210, 0, 80, 60),
        (220, 12, 40, 22),
    ]
    monkeypatch.setattr(spacing_cv_extractor, "components_to_bboxes", lambda gray: boxes)
    monkeypatch.setattr(
        spacing_cv_extractor,
        "gaps_from_bboxes",
        lambda bboxes, **kwargs: ([12, 18, 24], [20]),
    )
    monkeypatch.setattr(
        spacing_cv_extractor,
        "infer_grid_from_bboxes",
        lambda bboxes, canvas_width: {
            "columns": 3,
            "gutter_px": 20,
            "margin_left": 12,
            "margin_right": 18,
            "confidence": 0.8,
        },
    )
    extractor = CVSpacingExtractor(max_tokens=4)
    result = extractor.extract_from_bytes(b"bytes")
    assert result.component_spacing_metrics
    first = result.component_spacing_metrics[0]
    assert first["padding"]["left"] > 0
    assert result.grid_detection is not None
    assert result.grid_detection["columns"] == 3
