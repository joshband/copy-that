"""CV/heuristic border, radius, and strokeStyle signals from screenshots.

Phase 3: classical OpenCV contours — not a learned model. Emits descriptor
dicts that :mod:`border_derive` / :mod:`stroke_style_derive` turn into tokens.
"""

from __future__ import annotations

from base64 import b64decode
from typing import Any

from copy_that.layoutlab.shape_inference import (
    estimate_border_width,
    estimate_corner_radius,
    estimate_stroke_style,
)

# Prefer extract over P2c synth when confidence meets this bar.
BORDER_EXTRACT_CONFIDENCE_THRESHOLD = 0.55

try:
    import cv2
    import numpy as np
except Exception:  # pragma: no cover - optional at import time
    cv2 = None  # type: ignore[assignment]
    np = None  # type: ignore[assignment]


def _decode_image(input_data: str | bytes) -> Any | None:
    if np is None or cv2 is None:
        return None
    raw = input_data
    if isinstance(raw, str):
        if raw.startswith("data:"):
            raw = raw.split(",", 1)[-1]
        try:
            raw = b64decode(raw)
        except Exception:
            return None
    if not isinstance(raw, (bytes, bytearray)):
        return None
    arr = np.frombuffer(raw, dtype=np.uint8)
    return cv2.imdecode(arr, cv2.IMREAD_UNCHANGED)


def _roi_masks(image: Any, max_regions: int = 8) -> list[Any]:
    """Find rectangular-ish regions suitable for border/radius heuristics."""
    assert cv2 is not None and np is not None
    if image.ndim == 2:
        gray = image
    elif image.shape[2] == 4:
        gray = cv2.cvtColor(image, cv2.COLOR_BGRA2GRAY)
    else:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    h, w = gray.shape[:2]
    min_area = max(64, (h * w) // 400)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 50, 150)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    masks: list[Any] = []
    scored: list[tuple[float, Any]] = []
    for contour in contours:
        area = float(cv2.contourArea(contour))
        if area < min_area:
            continue
        x, y, rw, rh = cv2.boundingRect(contour)
        if rw < 8 or rh < 8:
            continue
        # Prefer near-rectangular UI chrome
        peri = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, 0.04 * peri, True)
        rectness = 1.0 if len(approx) in (4, 5, 6, 8) else 0.5
        score = area * rectness
        pad = 2
        x0, y0 = max(0, x - pad), max(0, y - pad)
        x1, y1 = min(w, x + rw + pad), min(h, y + rh + pad)
        roi = gray[y0:y1, x0:x1]
        if roi.size == 0:
            continue
        _, mask = cv2.threshold(roi, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        scored.append((score, mask))

    scored.sort(key=lambda item: item[0], reverse=True)
    for _, mask in scored[:max_regions]:
        masks.append(mask)
    return masks


def extract_border_signals_from_image(
    input_data: str | bytes,
    *,
    confidence_threshold: float = BORDER_EXTRACT_CONFIDENCE_THRESHOLD,
) -> list[dict[str, Any]]:
    """Return border/radius/stroke descriptors from screenshot bytes.

    Each descriptor is a plain dict (not a Token) with keys:
    ``kind`` (``border_width`` | ``corner_radius`` | ``stroke_style``),
    ``value``, ``confidence``, ``source``.
    """
    image = _decode_image(input_data)
    if image is None:
        return []

    widths: set[int] = set()
    radii: set[int] = set()
    style_votes: dict[str, list[float]] = {"solid": [], "dashed": []}

    for mask in _roi_masks(image):
        width = estimate_border_width(mask)
        radius = estimate_corner_radius(mask)
        style, style_conf = estimate_stroke_style(mask)
        if width > 0:
            widths.add(int(width))
        if radius > 0:
            radii.add(int(radius))
        if style in style_votes:
            style_votes[style].append(float(style_conf))

    signals: list[dict[str, Any]] = []
    for idx, width in enumerate(sorted(widths), start=1):
        conf = 0.7 if width <= 8 else 0.6
        if conf < confidence_threshold:
            continue
        signals.append(
            {
                "kind": "border_width",
                "id": f"layout.border.cv-{idx}",
                "value": width,
                "confidence": conf,
                "source": "cv",
            }
        )
    for idx, radius in enumerate(sorted(radii), start=1):
        conf = 0.65
        if conf < confidence_threshold:
            continue
        signals.append(
            {
                "kind": "corner_radius",
                "id": f"layout.radius.cv-{idx}",
                "value": radius,
                "confidence": conf,
                "source": "cv",
            }
        )

    best_style = "solid"
    best_conf = 0.4
    for style, confs in style_votes.items():
        if not confs:
            continue
        mean_conf = sum(confs) / len(confs)
        if mean_conf > best_conf or (mean_conf == best_conf and style == "dashed"):
            best_style = style
            best_conf = mean_conf
    if best_conf >= confidence_threshold:
        signals.append(
            {
                "kind": "stroke_style",
                "id": f"strokeStyle.{best_style}",
                "value": best_style,
                "confidence": round(best_conf, 3),
                "source": "cv",
            }
        )
    return signals
