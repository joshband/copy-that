"""
Unified depth + normal estimation with deep model preference and CPU fallback.

Backends:
    - Depth: ZoeDepth (preferred) → MiDaS → gradient heuristic
    - Normals: Omnidata normals (preferred) → depth gradients

Features:
    - Automatic device selection (GPU when available + allowed)
    - Model caching via depth_normals module
    - CPU-only safe fallback path for constrained environments
"""

from __future__ import annotations

import importlib.util
import logging
from dataclasses import dataclass
from typing import Any

import cv2
import numpy as np

from copy_that.application.gpu import choose_device, gpu_enabled

from .depth_normals import estimate_depth, estimate_normals

logger = logging.getLogger(__name__)

# Cached estimator instances keyed by device
_estimator_cache: dict[str, DepthAndNormalsEstimator] = {}


@dataclass
class DepthAndNormalsConfig:
    """Configuration for depth/normal estimation."""

    depth_preference: tuple[str, ...] = ("zoedepth", "midas")
    normals_preference: tuple[str, ...] = ("omnidata", "depth_gradient")
    force_cpu: bool = False
    color_space: str = "rgb"  # Input color ordering
    prefer_lightweight_on_cpu: bool = True


@dataclass
class DepthAndNormalsResult:
    """Depth and normals outputs with backend metadata."""

    depth: np.ndarray
    normals: np.ndarray
    normals_rgb: np.ndarray
    depth_backend: str
    normals_backend: str
    device: str
    extras: dict[str, Any]


class DepthAndNormalsEstimator:
    """Wraps depth_normals with device selection + backend metadata."""

    def __init__(self, config: DepthAndNormalsConfig | None = None):
        self.config = config or DepthAndNormalsConfig()
        self.device = self._resolve_device(self.config.force_cpu)

    # ------------------------------------------------------------------ utils
    def _resolve_device(self, force_cpu: bool) -> str:
        if force_cpu or not gpu_enabled():
            return "cpu"
        device = choose_device(prefer_gpu=True)
        if isinstance(device, str) and device.startswith("cuda"):
            return "cuda"
        if device in {"mps", "cpu"}:
            return device
        return "cpu"

    @staticmethod
    def _ensure_bgr_uint8(image: np.ndarray, color_space: str) -> np.ndarray:
        """Convert input image to BGR uint8 expected by depth_normals."""
        if image.ndim != 3 or image.shape[2] != 3:
            raise ValueError(f"Expected HxWx3 image, got shape {image.shape}")

        img = image
        if img.dtype == np.float32 or img.dtype == np.float64:
            img = np.clip(img, 0, 1)
            img = (img * 255).astype(np.uint8)
        elif img.dtype != np.uint8:
            img = img.astype(np.uint8)

        if color_space.lower() == "rgb":
            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

        return img

    @staticmethod
    def _torch_available() -> bool:
        spec = importlib.util.find_spec("torch")
        return spec is not None

    @staticmethod
    def _fast_depth_proxy(image_bgr: np.ndarray) -> np.ndarray:
        """Lightweight depth heuristic to avoid heavy model loads."""
        gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY).astype(np.float32) / 255.0
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        depth = (blurred - blurred.min()) / (blurred.max() - blurred.min() + 1e-8)
        return depth.astype(np.float32)

    @staticmethod
    def _normals_from_depth(depth: np.ndarray) -> np.ndarray:
        """Compute surface normals from depth via Sobel gradients."""
        grad_x = cv2.Sobel(depth, cv2.CV_32F, 1, 0, ksize=3)
        grad_y = cv2.Sobel(depth, cv2.CV_32F, 0, 1, ksize=3)
        normals = np.stack([-grad_x, -grad_y, np.ones_like(depth)], axis=2)
        norm = np.linalg.norm(normals, axis=2, keepdims=True) + 1e-8
        normals = normals / norm
        return normals.astype(np.float32)

    # ---------------------------------------------------------------- infer
    def estimate(self, image: np.ndarray) -> DepthAndNormalsResult:
        """Estimate depth + normals with fallback-aware metadata."""
        image_bgr = self._ensure_bgr_uint8(image, self.config.color_space)

        torch_ok = self._torch_available()
        extras: dict[str, Any] = {"torch_available": torch_ok}
        use_deep = torch_ok and not (self.device == "cpu" and self.config.prefer_lightweight_on_cpu)

        # Depth selection
        depth_backend = "gradient"
        if use_deep and "zoedepth" in self.config.depth_preference:
            depth_backend = "zoedepth"
            depth = estimate_depth(image_bgr, device=self.device, model_name="zoedepth")
        elif use_deep and "midas" in self.config.depth_preference:
            depth_backend = "midas"
            depth = estimate_depth(image_bgr, device=self.device, model_name="midas")
        else:
            depth_backend = "gradient"
            depth = self._fast_depth_proxy(image_bgr)

        # Normals selection
        normals_backend = "depth_gradient"
        use_normals_deep = torch_ok and not (
            self.device == "cpu" and self.config.prefer_lightweight_on_cpu
        )
        if use_normals_deep and "omnidata" in self.config.normals_preference:
            normals_backend = "omnidata"
            try:
                normals = estimate_normals(
                    image_bgr,
                    device=self.device,
                    model_name="omnidata",
                    depth=depth,
                )
            except Exception as exc:  # noqa: BLE001
                logger.warning("Omnidata normals failed, using depth gradients: %s", exc)
                normals_backend = "depth_gradient"
                normals = self._normals_from_depth(depth)
        else:
            normals_backend = "depth_gradient"
            normals = self._normals_from_depth(depth)

        normals_rgb = (normals + 1.0) / 2.0
        normals_rgb = np.clip(normals_rgb, 0, 1).astype(np.float32)

        return DepthAndNormalsResult(
            depth=depth.astype(np.float32),
            normals=normals.astype(np.float32),
            normals_rgb=normals_rgb,
            depth_backend=depth_backend,
            normals_backend=normals_backend,
            device=self.device,
            extras=extras,
        )


def get_default_depth_normals_estimator(
    device: str | None = None, config: DepthAndNormalsConfig | None = None
) -> DepthAndNormalsEstimator:
    """
    Retrieve cached DepthAndNormalsEstimator for given device.

    Args:
        device: Explicit device or None for auto
        config: Optional override configuration
    """
    resolved_device = device or ("cpu" if (config and config.force_cpu) else choose_device(True))
    if isinstance(resolved_device, str) and resolved_device.startswith("cuda"):
        resolved_device = "cuda"

    if resolved_device in _estimator_cache and config is None:
        return _estimator_cache[resolved_device]

    estimator = DepthAndNormalsEstimator(config=config)
    if resolved_device:
        _estimator_cache[resolved_device] = estimator
    return estimator
