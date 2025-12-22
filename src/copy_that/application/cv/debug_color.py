from __future__ import annotations

import base64
from collections.abc import Callable, Iterable, Sequence
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


def _hex_to_rgb(hex_val: str) -> tuple[int, int, int] | None:
    if not isinstance(hex_val, str):
        return None
    val = hex_val.strip().lstrip("#")
    if len(val) != 6:
        return None
    try:
        return tuple(int(val[i : i + 2], 16) for i in (0, 2, 4))
    except Exception:
        return None


def _palette_rgb(palette_hexes: Iterable[str]) -> list[tuple[int, int, int]]:
    palette: list[tuple[int, int, int]] = []
    for hx in palette_hexes:
        rgb = _hex_to_rgb(hx)
        if rgb:
            palette.append(rgb)
    return palette


def _compute_slic_labels(
    rgb: NDArray[np.uint8],
    *,
    n_segments: int = 120,
    compactness: int = 20,
    start_label: int = 0,
) -> NDArray[np.int_] | None:
    if slic is None:
        return None
    try:
        return slic(rgb, n_segments=n_segments, compactness=compactness, start_label=start_label)
    except Exception:
        return None


def generate_palette_strip(
    palette_hexes: Iterable[str], width: int = 320, height: int = 32
) -> str | None:
    palette = _palette_rgb(palette_hexes)
    if not palette:
        return None
    try:
        image = Image.new("RGB", (width, height), (255, 255, 255))
        draw = ImageDraw.Draw(image)
        step = width / len(palette)
        for idx, rgb in enumerate(palette):
            x0 = int(round(idx * step))
            x1 = int(round((idx + 1) * step))
            draw.rectangle([x0, 0, max(x1 - 1, x0), height], fill=rgb)
        return _encode_png(image)
    except Exception:
        return None


def generate_palette_histogram(
    palette_hexes: Iterable[str],
    weights: Sequence[float],
    width: int = 320,
    height: int = 80,
) -> str | None:
    palette = _palette_rgb(palette_hexes)
    if not palette:
        return None
    try:
        image = Image.new("RGB", (width, height), (255, 255, 255))
        draw = ImageDraw.Draw(image)
        bars = min(len(palette), len(weights))
        if bars == 0:
            return None
        max_weight = max(max(weights[:bars]), 1e-6)
        step = width / bars
        for idx in range(bars):
            rgb = palette[idx]
            weight = max(weights[idx], 0.0)
            bar_h = int(round((weight / max_weight) * (height - 8)))
            x0 = int(round(idx * step))
            x1 = int(round((idx + 1) * step))
            y0 = height - bar_h
            draw.rectangle([x0, y0, max(x1 - 1, x0), height], fill=rgb)
        return _encode_png(image)
    except Exception:
        return None


def generate_superpixel_boundaries(
    image_bgr: NDArray[np.uint8],
    *,
    n_segments: int = 120,
    compactness: int = 20,
) -> str | None:
    if slic is None or mark_boundaries is None:
        return None
    try:
        rgb = _to_rgb(image_bgr)
        labels = _compute_slic_labels(
            rgb, n_segments=n_segments, compactness=compactness, start_label=0
        )
        if labels is None:
            return None
        overlay_float = mark_boundaries(rgb, labels, color=(1, 1, 1), mode="thick")
        overlay = (overlay_float * 255).astype(np.uint8)
        return _encode_png(Image.fromarray(overlay))
    except Exception:
        return None


def generate_palette_assignment(
    image_bgr: NDArray[np.uint8],
    palette_hexes: Iterable[str],
    *,
    n_segments: int = 120,
    compactness: int = 20,
) -> str | None:
    palette = _palette_rgb(palette_hexes)
    if not palette:
        return None
    if slic is None:
        return None
    try:
        rgb = _to_rgb(image_bgr)
        labels = _compute_slic_labels(
            rgb, n_segments=n_segments, compactness=compactness, start_label=0
        )
        if labels is None:
            return None
        palette_arr = np.array(palette, dtype=np.float32)
        mapping = np.zeros((int(labels.max()) + 1, 3), dtype=np.uint8)
        for lbl in np.unique(labels):
            mask = labels == lbl
            mean_rgb = rgb[mask].mean(axis=0)
            idx = int(np.argmin(np.linalg.norm(palette_arr - mean_rgb, axis=1)))
            mapping[int(lbl)] = palette[idx]
        assigned = mapping[labels]
        return _encode_png(Image.fromarray(assigned))
    except Exception:
        return None


def _encode_png(pil_image: Image.Image) -> str:
    buf = BytesIO()
    pil_image.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("utf-8")


def encode_pil_base64(pil_image: Image.Image) -> str:
    return _encode_png(pil_image)


def encode_rgb_base64(image_rgb: NDArray[np.uint8]) -> str:
    pil = Image.fromarray(image_rgb.astype(np.uint8))
    return _encode_png(pil)


def encode_bgr_base64(image_bgr: NDArray[np.uint8]) -> str:
    return encode_rgb_base64(_to_rgb(image_bgr))


def encode_gray_base64(image_gray: NDArray[np.uint8]) -> str:
    if image_gray.ndim == 3:
        image_gray = image_gray[:, :, 0]
    pil = Image.fromarray(image_gray.astype(np.uint8), mode="L")
    return _encode_png(pil)


def generate_background_sample_overlay(
    image_bgr: NDArray[np.uint8],
    rects: Iterable[dict[str, int]],
) -> str | None:
    try:
        rgb = _to_rgb(image_bgr)
        pil = Image.fromarray(rgb).convert("RGBA")
        draw = ImageDraw.Draw(pil, "RGBA")
        for rect in rects:
            x = int(rect.get("x", 0))
            y = int(rect.get("y", 0))
            w = int(rect.get("width", 0))
            h = int(rect.get("height", 0))
            if w <= 0 or h <= 0:
                continue
            draw.rectangle((x, y, x + w, y + h), outline=(255, 255, 255, 220), width=2)
            draw.rectangle((x, y, x + w, y + h), fill=(255, 255, 255, 40))
        return _encode_png(pil)
    except Exception:
        return None


def generate_debug_overlay(
    image_bgr: NDArray[np.uint8],
    *,
    background_hex: str | None = None,
    text_hexes: Iterable[str] | None = None,
    palette_hexes: Iterable[str] | None = None,
) -> str | None:
    """Create a diagnostic overlay with superpixel boundaries and palette hints."""
    text_hexes = list(text_hexes or [])
    palette_hexes = list(palette_hexes or [])
    try:
        rgb = _to_rgb(image_bgr)
        overlay = rgb

        # Colorize superpixel regions by mapping each label to nearest palette hex
        if slic is not None and mark_boundaries is not None and palette_hexes:
            labels = slic(rgb, n_segments=140, compactness=20, start_label=1)
            flat_palette = []
            for hx in palette_hexes:
                try:
                    hx = hx.strip()
                    flat_palette.append(tuple(int(hx[i : i + 2], 16) for i in (1, 3, 5)))
                except Exception:
                    continue
            flat_palette = [c for c in flat_palette if len(c) == 3]
            if flat_palette:
                colored = np.zeros_like(rgb)
                for lbl in np.unique(labels):
                    mask = labels == lbl
                    # Use average color of region to pick nearest palette entry
                    mean_rgb = rgb[mask].mean(axis=0)
                    closest = min(
                        flat_palette,
                        key=lambda c: float(
                            np.linalg.norm(mean_rgb - np.array(c, dtype=np.float32))
                        ),
                    )
                    colored[mask] = closest
                overlay_float = mark_boundaries(colored, labels, color=(1, 1, 1), mode="thick")
                overlay = (overlay_float * 255).astype(np.uint8)
        elif slic is not None and mark_boundaries is not None:
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
        if palette_hexes:
            badge_lines.append(f"Palette top: {', '.join(palette_hexes[:3])}")

        if badge_lines:
            padding = 10
            badge_w = 260
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
