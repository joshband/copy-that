"""
LayoutParser + OCR text detection (optional).

Provides:
- Image mode heuristic (ui_screenshot | photo | ai_panel)
- Text block detection via LayoutParser AutoLayoutModel
- OCR via TesseractAgent
- Plausibility filtering for stylized/photographic panels
"""

from __future__ import annotations

import logging
import os
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any, Literal

import numpy as np
from numpy.typing import NDArray
from PIL import Image

logger = logging.getLogger(__name__)

ImageMode = Literal["ui_screenshot", "photo", "ai_panel"]


def _try_import_layoutparser() -> Any:
    try:
        import layoutparser as lp  # type: ignore
    except Exception as exc:  # pragma: no cover - optional dep
        raise RuntimeError(
            'layoutparser not installed. Install with `pip install "layoutparser[layoutmodels]"` '
            "and ensure Tesseract is available."
        ) from exc
    return lp


NumericArray = NDArray[np.integer[Any] | np.floating[Any]]


def _edge_density_score(gray: NumericArray) -> float:
    try:
        import cv2
    except Exception:  # pragma: no cover
        return 0.0
    edges = cv2.Canny(gray, 80, 180)
    return float(np.mean(edges > 0))


def detect_image_mode(image: Image.Image | NumericArray) -> ImageMode:
    """Cheap heuristic to pick image mode."""
    if isinstance(image, Image.Image):
        gray = np.array(image.convert("L"))
    else:
        gray = image if len(image.shape) == 2 else image[..., 0]
    density = _edge_density_score(gray)
    # More clean edges → likely UI screenshot
    if density < 0.05:
        return "photo"
    if 0.05 <= density <= 0.12:
        return "ai_panel"
    return "ui_screenshot"


@dataclass(slots=True)
class TextToken:
    id: str
    bbox: tuple[int, int, int, int]
    text: str
    score: float
    source: str = "layoutparser"
    type: str = "text"


def _is_plausible_text(text: str, image_mode: ImageMode) -> bool:
    cleaned = (text or "").strip()
    if len(cleaned) < 2:
        return False
    letters = sum(c.isalpha() for c in cleaned)
    ratio = letters / max(len(cleaned), 1)
    long_words = [w for w in cleaned.split() if sum(c.isalpha() for c in w) >= 3]
    if image_mode in ("photo", "ai_panel"):
        return bool(long_words) and ratio > 0.5
    return ratio > 0.3


def run_layoutparser_text(
    image: Image.Image,
    image_mode: ImageMode = "ui_screenshot",
    enabled: bool | None = None,
) -> list[TextToken]:
    """Detect text regions with LayoutParser + Tesseract."""
    allow = (
        enabled
        if enabled is not None
        else os.getenv("ENABLE_LAYOUTPARSER_TEXT", "0")
        not in {
            "0",
            "false",
            "False",
        }
    )
    if not allow:
        return []
    try:
        lp = _try_import_layoutparser()
    except Exception as exc:  # pragma: no cover - optional dep
        logger.warning("LayoutParser disabled: %s", exc)
        return []
    try:
        model = lp.AutoLayoutModel("lp://PubLayNet/efficientdet")
        layout = model.detect(image)
        ocr_agent = lp.TesseractAgent(languages="eng")
    except Exception as exc:  # pragma: no cover - heavy dep issues
        logger.warning("LayoutParser/Tesseract unavailable: %s", exc)
        return []

    tokens: list[TextToken] = []
    for idx, block in enumerate(layout):
        if block.type not in ("Text", "Title"):
            # Keep graphics only for strict UI
            if image_mode == "ui_screenshot" and block.type in ("Figure", "Image"):
                x1, y1, x2, y2 = block.coordinates
                tokens.append(
                    TextToken(
                        id=f"graphic-{idx + 1}",
                        bbox=(int(x1), int(y1), int(x2 - x1), int(y2 - y1)),
                        text="",
                        score=float(block.score or 0.5),
                        type="graphic",
                        source="layoutparser",
                    )
                )
            continue
        try:
            cropped = block.crop_image(image)
            text = ocr_agent.detect(cropped) or ""
        except Exception:
            continue
        if not _is_plausible_text(text, image_mode):
            continue
        x1, y1, x2, y2 = block.coordinates
        bbox = (int(x1), int(y1), int(x2 - x1), int(y2 - y1))
        tokens.append(
            TextToken(
                id=f"text-{idx + 1}",
                bbox=bbox,
                text=text.strip(),
                score=float(block.score or 0.6),
                source="layoutparser",
            )
        )
    return tokens


def attach_text_to_components(
    components: Sequence[dict[str, Any]],
    text_tokens: Sequence[TextToken],
    iou_threshold: float = 0.35,
) -> tuple[list[dict[str, Any]], list[TextToken]]:
    """Attach text to nearest component if IoU passes threshold."""
    updated = [dict(c) for c in components]
    residual: list[TextToken] = []

    def iou(box_a: tuple[int, int, int, int], box_b: tuple[int, int, int, int]) -> float:
        ax, ay, aw, ah = box_a
        bx, by, bw, bh = box_b
        ax2, ay2, bx2, by2 = ax + aw, ay + ah, bx + bw, by + bh
        inter_x1, inter_y1 = max(ax, bx), max(ay, by)
        inter_x2, inter_y2 = min(ax2, bx2), min(ay2, by2)
        inter_w, inter_h = max(0, inter_x2 - inter_x1), max(0, inter_y2 - inter_y1)
        inter_area = inter_w * inter_h
        if inter_area <= 0:
            return 0.0
        area_a = aw * ah
        area_b = bw * bh
        return inter_area / float(area_a + area_b - inter_area + 1e-6)

    for token in text_tokens:
        best_idx = None
        best_iou = 0.0
        for idx, comp in enumerate(updated):
            box = comp.get("box") or comp.get("bbox")
            if not box or len(box) != 4:
                continue
            overlap = iou(tuple(box), token.bbox)
            if overlap > best_iou:
                best_iou = overlap
                best_idx = idx
        if best_idx is not None and best_iou >= iou_threshold:
            comp = updated[best_idx]
            existing = comp.get("text")
            if existing:
                comp["text"] = f"{existing} | {token.text}"
            else:
                comp["text"] = token.text
            comp["text_confidence"] = token.score
        else:
            residual.append(token)

    return updated, residual
