import numpy as np

from copy_that.application import color_utils


def test_dominant_colors_single_color():
    region = np.full((10, 10, 3), fill_value=[255, 0, 0], dtype=np.uint8)
    palette = color_utils.dominant_colors_from_region(region, max_colors=2)
    assert palette
    assert palette[0]["hex"].lower().startswith("#f8")  # quantized red
    assert len(palette) == 1 or palette[1]["prominence"] < 0.1


def test_dominant_colors_gradient_two_colors():
    region = np.zeros((10, 10, 3), dtype=np.uint8)
    region[:5, :, :] = [0, 0, 255]  # blue
    region[5:, :, :] = [0, 255, 255]  # cyan

    palette = color_utils.dominant_colors_from_region(region, max_colors=2)
    assert len(palette) >= 2
    hexes = {p["hex"].lower() for p in palette}
    assert "#0000f8" in hexes  # quantized blue
    assert "#00f8f8" in hexes  # quantized cyan
