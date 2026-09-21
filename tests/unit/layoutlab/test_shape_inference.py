import pytest

from copy_that.layoutlab.shape_inference import (
    estimate_border_width,
    estimate_corner_radius,
    estimate_stroke_style,
)


def _deps():
    np = pytest.importorskip("numpy")
    cv2 = pytest.importorskip("cv2")
    return np, cv2


def test_estimate_corner_radius_positive():
    np, cv2 = _deps()
    mask = np.zeros((32, 32), dtype=np.uint8)
    # Rounded shape: draw filled circle plus a square to mimic a rounded card
    cv2.circle(mask, (8, 8), 8, 255, -1)
    cv2.rectangle(mask, (8, 0), (31, 31), 255, -1)
    radius = estimate_corner_radius(mask)
    assert radius > 0
    assert radius < 20


def test_estimate_border_width_positive():
    np, cv2 = _deps()
    mask = np.zeros((32, 32), dtype=np.uint8)
    cv2.rectangle(mask, (4, 4), (27, 27), 255, 3)
    width = estimate_border_width(mask)
    assert width >= 2
    assert width <= 6


def test_estimate_stroke_style_returns_solid_for_filled_rect():
    np, cv2 = _deps()
    mask = np.zeros((40, 40), dtype=np.uint8)
    cv2.rectangle(mask, (5, 5), (34, 34), 255, 2)
    style, conf = estimate_stroke_style(mask)
    assert style == "solid"
    assert 0.0 < conf <= 1.0
