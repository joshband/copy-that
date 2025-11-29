import io
import random

import numpy as np
from PIL import Image

from copy_that.application.cv.color_cv_extractor import CVColorExtractor


def make_noisy_blocks() -> bytes:
    bg = (240, 240, 240)
    accent = (255, 120, 0)
    arr = np.full((120, 120, 3), bg, dtype=np.uint8)
    arr[40:80, 10:110] = accent
    # sprinkle noise
    for _ in range(200):
        x = random.randint(0, 119)
        y = random.randint(0, 119)
        arr[y, x] = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    img = Image.fromarray(arr, mode="RGB")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def test_superpixel_palette_reduces_noise():
    data = make_noisy_blocks()
    extractor = CVColorExtractor(max_colors=6, use_superpixels=True)
    result = extractor.extract_from_bytes(data)
    # Expect bg + accent dominate, with few clusters
    assert len(result.colors) <= 4
    hexes = [c.hex.lower() for c in result.colors]
    assert any("#f0f0f0" in hx or hx.startswith("#ef") for hx in hexes)
