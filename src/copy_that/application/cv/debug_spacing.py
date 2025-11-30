from __future__ import annotations

import base64
from collections.abc import Iterable
from io import BytesIO

import numpy as np
from numpy.typing import NDArray
from PIL import Image

try:
    import cv2  # type: ignore[import-not-found]
except Exception:  # pragma: no cover
    cv2 = None  # type: ignore[assignment]


def generate_spacing_overlay(
    gray: NDArray[np.uint8],
    bboxes: Iterable[tuple[int, int, int, int]],
    *,
    base_unit: int | None = None,
    guides: list[tuple[tuple[int, int], tuple[int, int]]] | None = None,
    baseline_spacing: int | None = None,
) -> str | None:
    """
    Draw spacing diagnostics: component boxes, guides, baseline lines.
    Returns base64 PNG.
    """
    if cv2 is None:
        return None
    try:
        canvas = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
        bboxes = list(bboxes)
        # Draw bboxes
        for idx, (x, y, w, h) in enumerate(bboxes):
            cv2.rectangle(canvas, (x, y), (x + w, y + h), (96, 165, 255), 2)
            cv2.putText(
                canvas,
                str(idx),
                (x + 4, y + 16),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 0, 0),
                2,
                cv2.LINE_AA,
            )
        # Draw guides
        if guides:
            for p1, p2 in guides:
                cv2.line(canvas, p1, p2, (255, 120, 0), 2, cv2.LINE_AA)
        # Draw baseline rhythm
        if baseline_spacing and baseline_spacing > 0:
            h, w = canvas.shape[:2]
            for y in range(0, h, baseline_spacing):
                cv2.line(canvas, (0, y), (w, y), (120, 255, 120), 1, cv2.LINE_AA)
        # Draw base grid
        if base_unit and base_unit > 0:
            h, w = canvas.shape[:2]
            for x in range(0, w, base_unit):
                cv2.line(canvas, (x, 0), (x, h), (220, 220, 220), 1, cv2.LINE_AA)

        pil = Image.fromarray(cv2.cvtColor(canvas, cv2.COLOR_BGR2RGB))
        buf = BytesIO()
        pil.save(buf, format="PNG")
        return base64.b64encode(buf.getvalue()).decode("utf-8")
    except Exception:
        return None
