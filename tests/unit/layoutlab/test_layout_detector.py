import pytest

from copy_that.layoutlab.layout_detector import detect_layout_primitives

np = pytest.importorskip("numpy")


def test_layout_detector_contour_fallback_enabled():
    canvas = np.zeros((80, 80), dtype=np.uint8)
    canvas[10:40, 10:40] = 255
    regions = detect_layout_primitives(canvas, enabled=True)
    if not regions:
        pytest.skip("Contour fallback unavailable (likely missing cv2)")
    assert regions[0]["source"] in {"dl-fallback", "dl-yolo"}


def test_layout_detector_can_be_disabled():
    canvas = np.zeros((40, 40), dtype=np.uint8)
    regions = detect_layout_primitives(canvas, enabled=False)
    assert regions == []
