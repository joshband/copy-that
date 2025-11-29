from __future__ import annotations

import base64
from collections.abc import Callable, Iterable
from io import BytesIO
from types import ModuleType
from typing import TYPE_CHECKING, Any, cast

import numpy as np
from numpy.typing import NDArray
from PIL import Image, ImageDraw

cv2_module: ModuleType | None = None
try:
    import cv2 as _cv2_module  # type: ignore[import-not-found]
except Exception:  # pragma: no cover
    cv2_module = None
else:
    cv2_module = _cv2_module
cv2: ModuleType | None = cv2_module

if TYPE_CHECKING:
    pass

mark_boundaries: Callable[..., Any] | None
slic: Callable[..., Any] | None

try:
    from skimage.segmentation import (
        mark_boundaries as _mark_boundaries,
    )  # type: ignore[import-not-found]
    from skimage.segmentation import (
        slic as _slic,
    )
except Exception:  # pragma: no cover
    mark_boundaries = None
    slic = None
else:
    mark_boundaries = _mark_boundaries
    slic = _slic


def _to_rgb(image_bgr: NDArray[np.uint8]) -> NDArray[np.uint8]:
    if cv2 is not None:
        return cast(NDArray[np.uint8], cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB))
    return image_bgr[..., ::-1]


def generate_debug_overlay(
    image_bgr: NDArray[np.uint8],
    *,
    background_hex: str | None = None,
    text_hexes: Iterable[str] | None = None,
) -> str | None:
    """Create a quick diagnostic overlay for QA."""
    text_hexes = list(text_hexes or [])
    try:
        rgb = _to_rgb(image_bgr)
        overlay = rgb
        if slic is not None and mark_boundaries is not None:
            labels = slic(rgb, n_segments=120, compactness=18, start_label=1)
            overlay_float = mark_boundaries(rgb, labels, color=(1, 0, 0), mode="thick")
            overlay = (overlay_float * 255).astype(np.uint8)
        pil = Image.fromarray(overlay)
        draw = ImageDraw.Draw(pil, "RGBA")

        badge_lines = []
        if background_hex:
            badge_lines.append(f"BG {background_hex}")
        if text_hexes:
            badge_lines.append(f"Text {', '.join(text_hexes[:2])}")

        if badge_lines:
            padding = 10
            badge_w = 220
            badge_h = 16 * len(badge_lines) + padding * 2
            rect = (8, 8, 8 + badge_w, 8 + badge_h)
            draw.rectangle(rect, fill=(0, 0, 0, 120), outline=(255, 255, 255, 60))
            y = 8 + padding
            for line in badge_lines:
                draw.text((16, y), line, fill=(255, 255, 255, 230))
                y += 16

        buf = BytesIO()
        pil.save(buf, format="PNG")
        return base64.b64encode(buf.getvalue()).decode("utf-8")
    except Exception:
        return None
