from copy_that.application.cv.grid_cv_extractor import infer_grid_from_bboxes


def test_infer_grid_from_bboxes_detects_columns():
    boxes = [
        (10, 10, 40, 30),
        (20, 60, 40, 30),
        (110, 12, 38, 35),
        (120, 70, 36, 32),
        (210, 18, 34, 30),
    ]
    result = infer_grid_from_bboxes(boxes, canvas_width=320, tolerance_ratio=0.1)
    assert result is not None
    assert result["columns"] == 3
    assert result["gutter_px"] > 0
    assert result["margin_left"] >= 0
