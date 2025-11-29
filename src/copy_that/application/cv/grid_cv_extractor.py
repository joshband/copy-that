"""
Grid inference utilities for spacing analysis.
"""

from __future__ import annotations

from collections.abc import Iterable
from statistics import median


def infer_grid_from_bboxes(
    bboxes: Iterable[tuple[int, int, int, int]],
    canvas_width: int,
    tolerance_ratio: float = 0.05,
) -> dict[str, float | int] | None:
    """
    Infer column count, gutter, and margins from bounding boxes.

    Args:
        bboxes: iterable of (x, y, w, h)
        canvas_width: width of the analyzed canvas/image
        tolerance_ratio: grouping tolerance relative to canvas width

    Returns:
        Dict with columns/gutter/margins/confidence or None if insufficient data.
    """

    boxes = [box for box in bboxes if box[2] > 4 and box[3] > 4]
    if len(boxes) < 2 or canvas_width <= 0:
        return None

    tolerance = max(8, int(canvas_width * tolerance_ratio))
    groups: list[dict[str, float | list[tuple[int, int, int, int]]]] = []

    for x, y, w, h in sorted(boxes, key=lambda b: b[0]):
        center = x + w / 2.0
        placed = False
        for group in groups:
            if abs(center - group["center"]) <= tolerance:  # type: ignore[index]
                group["center"] = (group["center"] * len(group["boxes"]) + center) / (
                    len(group["boxes"]) + 1
                )
                group["min_left"] = min(group["min_left"], x)
                group["max_right"] = max(group["max_right"], x + w)
                group["boxes"].append((x, y, w, h))
                placed = True
                break
        if not placed:
            groups.append(
                {
                    "center": center,
                    "min_left": x,
                    "max_right": x + w,
                    "boxes": [(x, y, w, h)],
                }
            )

    if len(groups) < 2:
        return None

    groups.sort(key=lambda g: g["center"])  # type: ignore[index]
    gutter_values: list[float] = []
    for idx in range(len(groups) - 1):
        right = groups[idx]["max_right"]
        left = groups[idx + 1]["min_left"]
        gutter = left - right
        if gutter > 0:
            gutter_values.append(gutter)

    if not gutter_values:
        return None

    margin_left = max(0, min(g["min_left"] for g in groups))
    margin_right = max(0, canvas_width - max(g["max_right"] for g in groups))

    total_boxes = len(boxes)
    grouped_boxes = sum(len(g["boxes"]) for g in groups)
    confidence = min(1.0, grouped_boxes / max(total_boxes, 1))

    return {
        "columns": len(groups),
        "gutter_px": int(round(median(gutter_values))),
        "margin_left": int(round(margin_left)),
        "margin_right": int(round(margin_right)),
        "confidence": round(confidence, 4),
    }
