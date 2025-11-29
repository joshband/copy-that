import numpy as np
import pytest

try:
    import cv2
except Exception:  # pragma: no cover
    cv2 = None  # type: ignore

from copy_that.application.cv.spacing_cv_extractor import CVSpacingExtractor
from copy_that.application.spacing_utils import (
    cluster_spacing_values,
    spacing_tokens_from_values,
)


def test_cluster_spacing_values_merges_nearby():
    values = [4, 8, 8, 9, 16]
    clustered = cluster_spacing_values(values, tolerance=0.15)
    assert clustered == [4, 8, 16]


def test_spacing_tokens_from_values_outputs_dimensions():
    values = [7, 8, 15, 16]
    tokens = spacing_tokens_from_values(values)
    assert list(tokens.keys()) == ["spacing.1", "spacing.2", "spacing.3"]
    assert tokens["spacing.2"]["$value"]["unit"] == "px"
    assert tokens["spacing.2"]["$type"] == "dimension"


@pytest.mark.skipif(cv2 is None, reason="OpenCV not available")
def test_cv_spacing_matches_known_gap():
    gap_px = 22  # CV extractor tends to quantize this fixture to ~22px
    width, height = 400, 120
    img = np.ones((height, width), dtype=np.uint8) * 255
    x = 20
    rect_w = 40
    for _ in range(3):
        cv2.rectangle(img, (x, 20), (x + rect_w, 100), (0,), thickness=-1)
        x += rect_w + gap_px
    ok, buf = cv2.imencode(".png", img)
    assert ok
    data = buf.tobytes()

    extractor = CVSpacingExtractor(expected_base_px=gap_px)
    result = extractor.extract_from_bytes(data)

    assert any(abs(v - gap_px) <= 1 for v in result.unique_values)
    if result.base_alignment:
        assert result.base_alignment.get("within_tolerance") is True
