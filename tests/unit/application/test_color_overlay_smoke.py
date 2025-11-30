import base64

import numpy as np

from copy_that.application.cv.debug_color import generate_debug_overlay


def test_color_overlay_smoke():
    # Simple 2x2 image to ensure overlay returns base64 string and not error
    bgr = np.array([[[0, 0, 0], [255, 255, 255]], [[255, 0, 0], [0, 255, 0]]], dtype=np.uint8)
    overlay_b64 = generate_debug_overlay(
        bgr, background_hex="#000000", text_hexes=["#ffffff"], palette_hexes=["#000000", "#ffffff"]
    )
    assert overlay_b64 is not None
    # validate base64 decodes
    decoded = base64.b64decode(overlay_b64)
    assert len(decoded) > 0
