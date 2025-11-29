import cv2
import numpy as np

from cv_pipeline.primitives import components_to_bboxes, gaps_from_bboxes


def make_test_image() -> np.ndarray:
    canvas = np.full((140, 220), 255, dtype=np.uint8)
    cv2.rectangle(canvas, (10, 20), (70, 100), 0, -1)
    cv2.rectangle(canvas, (90, 30), (140, 95), 30, -1)
    cv2.rectangle(canvas, (160, 40), (210, 120), 0, -1)
    return canvas


def test_components_to_bboxes_detects_blocks():
    gray = make_test_image()
    boxes = components_to_bboxes(gray, min_area=200)
    assert len(boxes) == 3
    xs = [box[0] for box in boxes]
    assert xs == sorted(xs)
    widths = [box[2] for box in boxes]
    assert all(w > 30 for w in widths)


def test_gaps_from_bboxes_merges_near_values():
    bboxes = [
        (0, 0, 40, 40),
        (70, 0, 30, 42),
        (140, 2, 30, 38),
        (10, 90, 36, 30),
        (15, 150, 36, 32),
    ]
    x_gaps, y_gaps = gaps_from_bboxes(bboxes, axis_tolerance=3)
    assert x_gaps == [30, 40]
    assert y_gaps == [30, 50]
