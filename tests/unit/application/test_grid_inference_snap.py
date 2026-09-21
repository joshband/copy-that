from copy_that.application import spacing_utils as su


def test_infer_grid_from_components_uses_repetition_and_gutter():
    boxes = [
        (0, 0, 20, 10),
        (40, 0, 20, 10),
        (80, 0, 20, 10),
    ]
    grid = su.infer_grid_from_components(boxes, canvas_width=140)
    assert grid["gutter_px"] in {20, 40}
    assert grid["columns"] >= 2
    assert grid["margin_left"] == 0


def test_snap_gaps_to_grid_snaps_within_tolerance():
    gaps = [19.2, 20.8, 5]
    snapped = su.snap_gaps_to_grid(gaps, gutter=20, tolerance=1.0)
    assert snapped[0] == 20
    assert snapped[1] == 20
    assert snapped[2] == 5
