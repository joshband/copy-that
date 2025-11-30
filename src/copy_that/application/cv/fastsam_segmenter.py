"""
FastSAM integration (optional).

Provides a thin wrapper that returns mask regions and bounding boxes. If FastSAM
or its dependencies are missing, the segmenter will raise RuntimeError; callers
should catch and degrade gracefully.
"""

from __future__ import annotations

import logging
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any

try:
    import cv2
except Exception:  # pragma: no cover - optional dependency handled upstream
    cv2 = None  # type: ignore[assignment]
import numpy as np
from numpy.typing import NDArray
from PIL import Image

logger = logging.getLogger(__name__)


NumericArray = NDArray[np.number[Any]]
MaskArray = NDArray[np.bool_] | NumericArray


def _mask_to_bbox(mask: MaskArray) -> tuple[int, int, int, int]:
    ys, xs = np.where(mask > 0)
    if len(xs) == 0 or len(ys) == 0:
        return (0, 0, 0, 0)
    x1, x2 = int(xs.min()), int(xs.max())
    y1, y2 = int(ys.min()), int(ys.max())
    return (x1, y1, x2 - x1 + 1, y2 - y1 + 1)


@dataclass(slots=True)
class FastSAMRegion:
    bbox: tuple[int, int, int, int]
    area: int
    polygon: list[tuple[int, int]] | None = None
    mask: MaskArray | None = None


class FastSAMSegmenter:
    """Lazy-initialized FastSAM wrapper."""

    def __init__(self, model_path: str, device: str = "cpu") -> None:
        try:
            from ultralytics import FastSAM  # type: ignore
        except Exception as exc:  # pragma: no cover
            raise RuntimeError(
                "FastSAM/ultralytics not installed. Install with `pip install ultralytics` "
                "and provide FASTSAM_MODEL_PATH."
            ) from exc
        self._FastSAM = FastSAM
        self.model_path = model_path
        self.device = device
        self._model: Any | None = None

    def _load(self) -> Any:
        if self._model is None:
            self._model = self._FastSAM(self.model_path)
        return self._model

    def segment(
        self,
        image: Image.Image | NumericArray,
        conf: float = 0.4,
        iou: float = 0.9,
        imgsz: int = 640,
        min_area: int = 150,
        overlap_iou: float = 0.9,
    ) -> list[FastSAMRegion]:
        model = self._load()
        if isinstance(image, Image.Image):
            np_img: NumericArray = np.array(image.convert("RGB"))
        else:
            np_img = image
        try:
            # Ultralytics-style invocation; results[0].masks.data is torch.Tensor
            results = model(np_img, retina_masks=True, conf=conf, iou=iou, imgsz=imgsz)
            if not results:
                return []
            pred = results[0]
            masks = getattr(pred, "masks", None)
            if masks is None or masks.data is None:
                return []
            data: NDArray[np.number[Any]] = masks.data.cpu().numpy()
        except Exception as exc:  # pragma: no cover - relies on external lib
            logger.warning("FastSAM inference failed: %s", exc)
            return []

        regions: list[FastSAMRegion] = []
        for mask in data:
            bbox = _mask_to_bbox(mask)
            area = int(mask.sum())
            if area < min_area or bbox[2] <= 0 or bbox[3] <= 0:
                continue
            polygon = _mask_to_polygon(mask)
            regions.append(FastSAMRegion(bbox=bbox, area=area, polygon=polygon, mask=mask))
        return _suppress_overlaps(regions, overlap_iou)


def filter_regions(regions: Iterable[FastSAMRegion], min_area: int = 150) -> list[FastSAMRegion]:
    return [r for r in regions if r.area >= min_area and r.bbox[2] > 0 and r.bbox[3] > 0]


def _mask_to_polygon(mask: MaskArray, epsilon_ratio: float = 0.01) -> list[tuple[int, int]] | None:
    if cv2 is None:
        return None
    try:
        contours, _ = cv2.findContours(
            mask.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        if not contours:
            return None
        largest = max(contours, key=cv2.contourArea)
        perimeter = cv2.arcLength(largest, True)
        epsilon = epsilon_ratio * perimeter
        approx = cv2.approxPolyDP(largest, epsilon, True)
        coords: list[list[float]] = np.reshape(approx, (-1, 2)).tolist()
        return [(int(x), int(y)) for x, y in coords]
    except Exception:  # pragma: no cover - CV-dependent
        return None


def _bbox_iou(a: tuple[int, int, int, int], b: tuple[int, int, int, int]) -> float:
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    ax2, ay2 = ax + aw, ay + ah
    bx2, by2 = bx + bw, by + bh
    inter_x1, inter_y1 = max(ax, bx), max(ay, by)
    inter_x2, inter_y2 = min(ax2, bx2), min(ay2, by2)
    inter_w = max(0, inter_x2 - inter_x1)
    inter_h = max(0, inter_y2 - inter_y1)
    inter_area = inter_w * inter_h
    if inter_area <= 0:
        return 0.0
    area_a = aw * ah
    area_b = bw * bh
    return inter_area / float(area_a + area_b - inter_area + 1e-6)


def _suppress_overlaps(regions: list[FastSAMRegion], iou_thresh: float) -> list[FastSAMRegion]:
    if not regions:
        return regions
    regions = sorted(regions, key=lambda r: r.area, reverse=True)
    kept: list[FastSAMRegion] = []
    for r in regions:
        if any(_bbox_iou(r.bbox, k.bbox) > iou_thresh for k in kept):
            continue
        kept.append(r)
    return kept
