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
