"""Cheap OCR text-box detection and masking for UI screenshot CV.

Research-backed fast path: detect text → mask glyphs → then run non-text
geometry / palette CV so anti-aliased letter edges do not pollute spacing
components or color clusters.

Soft-fails when pytesseract / Tesseract are unavailable (returns inputs unchanged).
"""

from __future__ import annotations

import logging
from typing import Any

import numpy as np
from numpy.typing import NDArray

logger = logging.getLogger(__name__)

NumericArray = NDArray[np.integer[Any] | np.floating[Any]]
BBox = tuple[int, int, int, int]


def detect_text_boxes(
    image: Any,
    *,
    min_confidence: float = 40.0,
    min_height: int = 6,
) -> list[BBox]:
    """Return OCR word/line boxes as (x, y, w, h) in image coordinates.

    Accepts a PIL Image or HxW / HxWxC numpy array.
    """
    try:
        import pytesseract
        from PIL import Image
    except Exception as exc:  # pragma: no cover - optional dep
        logger.debug("text_mask: OCR unavailable (%s)", exc)
        return []

    try:
        if hasattr(image, "convert"):
            pil = image.convert("RGB")
        else:
            arr = np.asarray(image)
            if arr.ndim == 2:
                pil = Image.fromarray(arr.astype("uint8"), mode="L").convert("RGB")
            elif arr.ndim == 3 and arr.shape[2] >= 3:
                # Assume BGR from OpenCV when channel order unknown; convert via RGB guess
                rgb = arr[:, :, ::-1] if arr.shape[2] == 3 else arr[:, :, :3]
                pil = Image.fromarray(rgb.astype("uint8"), mode="RGB")
            else:
                return []

        data = pytesseract.image_to_data(pil, output_type=pytesseract.Output.DICT)
        boxes: list[BBox] = []
        n = len(data.get("text") or [])
        for i in range(n):
            text = (data["text"][i] or "").strip()
            if not text:
                continue
            try:
                conf = float(data["conf"][i])
            except (TypeError, ValueError):
                conf = -1.0
            if conf < min_confidence:
                continue
            x, y, w, h = (
                int(data["left"][i]),
                int(data["top"][i]),
                int(data["width"][i]),
                int(data["height"][i]),
            )
            if w <= 1 or h < min_height:
                continue
            boxes.append((x, y, w, h))
        return boxes
    except Exception as exc:  # pragma: no cover - OCR runtime issues
        logger.debug("text_mask: OCR failed (%s)", exc)
        return []


def apply_text_mask(
    cv_bgr: NumericArray,
    cv_gray: NumericArray,
    boxes: list[BBox] | None = None,
    *,
    pad: int = 1,
) -> tuple[NumericArray, NumericArray, list[BBox]]:
    """Fill OCR text boxes with local median color so CC / palette ignore glyphs.

    If ``boxes`` is None, runs :func:`detect_text_boxes` on ``cv_bgr``.
    Returns (masked_bgr, masked_gray, boxes_used).
    """
    if cv_bgr is None or cv_gray is None:
        return cv_bgr, cv_gray, []

    used = list(boxes) if boxes is not None else detect_text_boxes(cv_bgr)
    if not used:
        return cv_bgr, cv_gray, []

    masked_bgr = np.array(cv_bgr, copy=True)
    h, w = masked_bgr.shape[:2]

    for x, y, bw, bh in used:
        x0 = max(0, x - pad)
        y0 = max(0, y - pad)
        x1 = min(w, x + bw + pad)
        y1 = min(h, y + bh + pad)
        if x1 <= x0 or y1 <= y0:
            continue
        # Expand ring for median fill (outside the glyph when possible)
        rx0 = max(0, x0 - 2)
        ry0 = max(0, y0 - 2)
        rx1 = min(w, x1 + 2)
        ry1 = min(h, y1 + 2)
        ring = masked_bgr[ry0:ry1, rx0:rx1]
        if ring.size == 0:
            continue
        fill = np.median(ring.reshape(-1, ring.shape[-1]), axis=0).astype(masked_bgr.dtype)
        masked_bgr[y0:y1, x0:x1] = fill

    try:
        import cv2

        masked_gray = cv2.cvtColor(masked_bgr, cv2.COLOR_BGR2GRAY)
        masked_gray = cv2.GaussianBlur(masked_gray, (3, 3), 0)
    except Exception:
        masked_gray = np.array(cv_gray, copy=True)
        for x, y, bw, bh in used:
            x0 = max(0, x - pad)
            y0 = max(0, y - pad)
            x1 = min(w, x + bw + pad)
            y1 = min(h, y + bh + pad)
            if x1 <= x0 or y1 <= y0:
                continue
            masked_gray[y0:y1, x0:x1] = int(np.median(masked_gray[y0:y1, x0:x1]))

    return masked_bgr, masked_gray, used


def preprocess_with_text_mask(path_or_bytes: str | bytes | bytearray) -> dict[str, Any]:
    """Shared preprocess + optional text mask for color/spacing happy paths."""
    from .preprocess import preprocess_image

    views = preprocess_image(path_or_bytes)
    masked_bgr, masked_gray, boxes = apply_text_mask(views["cv_bgr"], views["cv_gray"])
    views["cv_bgr"] = masked_bgr
    views["cv_gray"] = masked_gray
    views["text_boxes"] = boxes
    views["text_masked"] = bool(boxes)
    return views
