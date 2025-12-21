"""Shape inference helpers for radius and border width from binary masks.

These routines avoid OCR/text and rely only on geometry. They are deterministic and
do not require heavy dependencies beyond NumPy.
"""

from __future__ import annotations

from typing import Any, cast

try:
    import numpy as np
except Exception:  # pragma: no cover - optional dependency
    np = None  # type: ignore[assignment]

try:
    import cv2
except Exception:  # pragma: no cover - optional dependency
    cv2 = None  # type: ignore[assignment]


def estimate_corner_radius(mask: Any) -> int:
    """Estimate a corner radius from a filled rounded-rectangle mask.

    Heuristic: examine contour points near the top-left corner and compute the
    median polar distance from that corner. Falls back to 0 if estimation fails.
    """

    if np is None or mask is None:
        return 0
    arr = np.array(mask)
    if arr.ndim > 2:
        arr = arr[..., 0]
    arr = (arr > 0).astype(np.uint8)
    if arr.max() == 0:
        return 0

    ys, xs = np.nonzero(arr)
    min_x, max_x = xs.min(), xs.max()
    min_y, max_y = ys.min(), ys.max()

    # Focus on the top-left quadrant to sample the rounded corner arc
    corner_mask = arr[
        min_y : min_y + (max_y - min_y) // 2 + 1, min_x : min_x + (max_x - min_x) // 2 + 1
    ]
    cy, cx = np.nonzero(corner_mask)
    if len(cx) == 0:
        return 0
    distances = np.sqrt(cx**2 + cy**2)
    if len(distances) == 0:
        return 0
    radius = float(np.median(distances))
    return int(round(radius))


def estimate_border_width(mask: Any) -> int:
    """Estimate border (stroke) width from a binary mask.

    Uses the distance transform to find the minimal distance of foreground pixels
    to background, which approximates stroke thickness for outlined shapes.
    Returns 0 when inference is impossible.
    """

    if np is None or mask is None:
        return 0
    arr = np.array(mask)
    if arr.ndim > 2:
        arr = arr[..., 0]
    arr = (arr > 0).astype(np.uint8)
    if arr.max() == 0:
        return 0

    if cv2 is None:
        return 0
    try:
        # distanceTransform expects 8-bit single-channel images
        dt = cv2.distanceTransform(arr, cv2.DIST_L2, 3)
        positive = dt[arr > 0]
        if positive.size == 0:
            return 0
        width = float(np.percentile(cast(Any, positive), 5))
        return max(0, int(round(width)))
    except Exception:  # pragma: no cover - cv edge cases
        return 0
