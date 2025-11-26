"""Shared preprocessing utilities for CV pipelines."""

from __future__ import annotations

import io
from pathlib import Path
from typing import Any

import cv2
import numpy as np
from PIL import Image, ImageOps

MAX_DIM = 1024


def preprocess_image(path_or_bytes: str | bytes | bytearray) -> dict[str, Any]:
    """Load an image, normalize orientation, and provide PIL + OpenCV views."""
    pil_image = _load_pil_image(path_or_bytes)
    pil_image = ImageOps.exif_transpose(pil_image)
    pil_image = _downsample_pil(pil_image, MAX_DIM)

    cv_bgr = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
    cv_gray = cv2.cvtColor(cv_bgr, cv2.COLOR_BGR2GRAY)
    cv_gray = cv2.GaussianBlur(cv_gray, (3, 3), 0)

    return {
        "pil_image": pil_image,
        "cv_bgr": cv_bgr,
        "cv_gray": cv_gray,
    }


def _load_pil_image(path_or_bytes: str | bytes | bytearray) -> Image.Image:
    if isinstance(path_or_bytes, (bytes, bytearray)):
        return Image.open(io.BytesIO(path_or_bytes)).convert("RGB")
    path = Path(path_or_bytes)
    if not path.exists():
        raise FileNotFoundError(path)
    return Image.open(path).convert("RGB")


def _downsample_pil(image: Image.Image, max_dim: int) -> Image.Image:
    width, height = image.size
    scale = min(1.0, max_dim / max(width, height))
    if scale >= 1.0:
        return image
    new_size = (int(width * scale), int(height * scale))
    return image.resize(new_size, Image.Resampling.LANCZOS)
