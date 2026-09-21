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
        # distanceTransform expects 8-bit single-channel images.
        # Values are distance-to-background (≈ half-stroke); double the medial
        # distance to recover full stroke width for outlined shapes.
        dt = cv2.distanceTransform(arr, cv2.DIST_L2, 3)
        positive = dt[arr > 0]
        if positive.size == 0:
            return 0
        half_width = float(np.percentile(cast(Any, positive), 50))
        return max(0, int(round(half_width * 2)))
    except Exception:  # pragma: no cover - cv edge cases
        return 0


def estimate_stroke_style(mask: Any) -> tuple[str, float]:
    """Heuristic solid vs dashed stroke from a binary outline mask.

    Samples edge occupancy along the outer contour. Periodic gaps → ``dashed``;
    continuous edge → ``solid``. Returns ``(style, confidence)``.
    """
    if np is None or mask is None:
        return "solid", 0.4
    arr = np.array(mask)
    if arr.ndim > 2:
        arr = arr[..., 0]
    arr = (arr > 0).astype(np.uint8)
    if arr.max() == 0:
        return "solid", 0.4

    if cv2 is None:
        return "solid", 0.4
    try:
        contours, _ = cv2.findContours(arr, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        if not contours:
            return "solid", 0.4
        contour = max(contours, key=cv2.contourArea)
        if len(contour) < 24:
            return "solid", 0.45

        # Flatten to a 1-D occupancy signal around the perimeter
        pts = contour.reshape(-1, 2)
        # Subsample for stability
        step = max(1, len(pts) // 128)
        sampled = pts[::step]
        if len(sampled) < 16:
            return "solid", 0.45

        # Local neighbourhood occupancy: dashed edges have periodic low-density spans
        h, w = arr.shape[:2]
        occupancy: list[float] = []
        for x, y in sampled:
            x0, x1 = max(0, x - 1), min(w, x + 2)
            y0, y1 = max(0, y - 1), min(h, y + 2)
            patch = arr[y0:y1, x0:x1]
            occupancy.append(float(patch.mean()) if patch.size else 0.0)

        signal = np.array(occupancy, dtype=np.float64)
        # Binary gaps: below half the mean counts as a gap sample
        threshold = max(0.15, float(signal.mean()) * 0.5)
        gaps = signal < threshold
        gap_ratio = float(gaps.mean())

        # Count gap runs (dash segments)
        runs = 0
        in_gap = False
        for is_gap in gaps:
            if is_gap and not in_gap:
                runs += 1
                in_gap = True
            elif not is_gap:
                in_gap = False

        # Dashed: several gap runs and material gap ratio, but not mostly empty
        if runs >= 4 and 0.12 <= gap_ratio <= 0.55:
            # Higher run count / mid gap ratio → higher confidence
            conf = min(0.92, 0.55 + 0.05 * min(runs, 8) + 0.2 * (1.0 - abs(gap_ratio - 0.35)))
            return "dashed", float(conf)
        # Continuous outline
        conf = min(0.9, 0.55 + 0.35 * (1.0 - gap_ratio))
        return "solid", float(conf)
    except Exception:  # pragma: no cover - cv edge cases
        return "solid", 0.4
