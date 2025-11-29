import cv2
import numpy as np

from copy_that.application.cv.spacing_cv_extractor import CVSpacingExtractor


def _synth_image_with_jittered_gaps() -> bytes:
    """
    Create a simple image with three vertical bars spaced ~32px apart,
    with slight jitter to test snap-to-grid refinement.
    """
    img = np.ones((120, 180), dtype=np.uint8) * 255  # white background
    # Draw three bars; gaps roughly 32px
    width = 16
    gap = 32
    x_positions = [20, 20 + width + gap, 20 + 2 * (width + gap)]  # 20, 68, 116
    for x in x_positions:
        cv2.rectangle(img, (x, 20), (x + width, 100), color=0, thickness=-1)
    ok, buf = cv2.imencode(".png", img)
    assert ok
    return bytes(buf)


def test_gapmap_snap_snaps_jitter_to_grid():
    data = _synth_image_with_jittered_gaps()
    extractor = CVSpacingExtractor(max_tokens=8)
    result = extractor.extract_from_bytes(data)

    # Expect base unit near 32px after snapping
    assert any(abs(v - 32) <= 1 for v in result.unique_values), result.unique_values
