"""Optional DL-friendly layout detector with safe CPU fallback."""

from __future__ import annotations

import os
from typing import Any, Iterable

try:
    import cv2
    import numpy as np
except Exception:  # pragma: no cover - optional deps
    cv2 = None  # type: ignore[assignment]
    np = None  # type: ignore[assignment]


def _dl_enabled(enabled: bool | None) -> bool:
    env = os.getenv("ENABLE_DL_LAYOUT", os.getenv("ENABLE_LAYOUT_DETECTOR"))
    if enabled is not None:
        return enabled
    if env is None:
        return False
    return env not in {"0", "false", "False"}


def _to_gray(image: Any) -> Any:
    if cv2 is None or np is None:
        return None
    if isinstance(image, np.ndarray):
        if image.ndim == 2:
            return image
        if image.ndim == 3:
            return cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    try:
        # PIL Image
        return cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
    except Exception:  # pragma: no cover
        return None


def _contour_fallback(gray: Any) -> list[dict[str, Any]]:
    if gray is None or cv2 is None or np is None:
        return []
    try:
        blurred = cv2.GaussianBlur(gray, (3, 3), 0)
        _, binary = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    except Exception:  # pragma: no cover - cv edge cases
        return []
    regions: list[dict[str, Any]] = []
    for idx, contour in enumerate(contours):
        x, y, w, h = cv2.boundingRect(contour)
        if w * h < 50:
            continue
        regions.append(
            {
                "id": f"dl-{idx + 1}",
                "bbox": [int(x), int(y), int(w), int(h)],
                "type": "layout",
                "parent_id": None,
                "confidence": 0.35,
                "source": "dl-fallback",
            }
        )
    regions.sort(key=lambda r: r["bbox"][2] * r["bbox"][3], reverse=True)
    return regions


def _run_ultralytics(gray: Any, model_name: str = "yolov8n.pt") -> Iterable[dict[str, Any]]:
    try:
        from ultralytics import YOLO  # type: ignore
    except Exception:
        return []
    if gray is None:
        return []
    try:
        model = YOLO(model_name)
        results = model(gray)
    except Exception:
        return []
    detections: list[dict[str, Any]] = []
    for idx, result in enumerate(results):
        boxes = getattr(result, "boxes", None)
        if boxes is None:
            continue
        for jdx, box in enumerate(boxes):
            try:
                xyxy = box.xyxy[0].tolist()
                x1, y1, x2, y2 = map(int, xyxy)
                detections.append(
                    {
                        "id": f"dl-yolo-{idx}-{jdx}",
                        "bbox": [x1, y1, max(1, x2 - x1), max(1, y2 - y1)],
                        "type": "layout",
                        "parent_id": None,
                        "confidence": float(box.conf[0]) if getattr(box, "conf", None) is not None else 0.5,
                        "source": "dl-yolo",
                    }
                )
            except Exception:
                continue
    return detections


def detect_layout_primitives(image: Any, enabled: bool | None = None) -> list[dict[str, Any]]:
    """
    Optionally run a DL layout detector; fall back to cheap contour detection.

    Returns a list of dicts with keys: id, bbox, type, parent_id, confidence, source.
    """
    if not _dl_enabled(enabled):
        return []

    gray = _to_gray(image)

    # Try YOLO-style layout model first (optional dependency)
    yolo_regions = list(_run_ultralytics(gray))
    if yolo_regions:
        return yolo_regions

    # CPU-friendly fallback: contour-based layout primitives
    return _contour_fallback(gray)
