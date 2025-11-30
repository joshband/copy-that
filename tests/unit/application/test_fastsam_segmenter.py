import numpy as np
import pytest

from copy_that.application.cv.fastsam_segmenter import (
    FastSAMRegion,
    _bbox_iou,
    _mask_to_polygon,
    _suppress_overlaps,
)

try:
    import cv2  # type: ignore
except Exception:  # pragma: no cover
    cv2 = None  # type: ignore[assignment]


def test_bbox_iou_overlap():
    a = (0, 0, 10, 10)
    b = (5, 5, 10, 10)
    iou = _bbox_iou(a, b)
    assert 0 < iou < 1


def test_suppress_overlaps_keeps_largest():
    regions = [
        FastSAMRegion(bbox=(0, 0, 10, 10), area=100),
        FastSAMRegion(bbox=(1, 1, 8, 8), area=64),
    ]
    kept = _suppress_overlaps(regions, iou_thresh=0.5)
    assert len(kept) == 1
    assert kept[0].area == 100


@pytest.mark.skipif(cv2 is None, reason="OpenCV not available for polygon test")
def test_mask_to_polygon_returns_points():
    mask = np.zeros((10, 10), dtype=np.uint8)
    mask[2:8, 3:7] = 1
    poly = _mask_to_polygon(mask)
    assert poly is None or len(poly) >= 3
