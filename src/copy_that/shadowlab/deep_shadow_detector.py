"""
Deep shadow detection utilities with BDRAR + fallback backends.

Primary backend:
    - BDRAR (Bidirectional Feature Pyramid + Recurrent Attention)
      via src.copy_that.shadowlab.bdrar

Fallbacks (in order):
    - SegFormer/SAM-based detector (pipeline.run_shadow_model)
    - Enhanced classical detector (BDRAR-inspired multi-scale features)

Features:
    - Automatic device selection (GPU when available + allowed)
    - Optional weight download to ~/.cache/shadowlab
    - Model caching across calls
    - CPU-only safe fallback path
    - Lightweight synthetic benchmark helper for documentation
"""

from __future__ import annotations

import hashlib
import logging
from dataclasses import dataclass
from typing import Any

import cv2
import numpy as np

from copy_that.application.gpu import choose_device, gpu_enabled

from .bdrar import BDRAR_WEIGHT_PATHS, download_bdrar_weights, get_bdrar_model, run_bdrar
from .pipeline import _enhanced_classical_shadow, run_shadow_model

logger = logging.getLogger(__name__)

# Simple in-memory cache of detectors keyed by device string
_detector_cache: dict[str, DeepShadowDetector] = {}


@dataclass
class ShadowDetectorConfig:
    """Configuration for deep shadow detector."""

    prefer_bdrar: bool = True
    high_quality: bool = False  # SAM refinement toggle
    auto_download_weights: bool = True
    force_cpu: bool = False
    cache_results: bool = True
    allow_unweighted_bdrar: bool = False
    use_segformer_fallback: bool = True


@dataclass
class ShadowDetectorResult:
    """Shadow detection result with metadata."""

    mask: np.ndarray
    backend: str
    device: str
    cache_hit: bool
    extras: dict[str, Any]


class DeepShadowDetector:
    """
    High-level shadow detector that prefers deep models but falls back gracefully.

    Order of operations:
    1) Try BDRAR (if weights available / downloadable)
    2) Try SegFormer/SAM detector (pipeline.run_shadow_model)
    3) Fallback to enhanced classical detector
    """

    def __init__(self, config: ShadowDetectorConfig | None = None):
        self.config = config or ShadowDetectorConfig()
        self.device = self._resolve_device(self.config.force_cpu)

        self._bdrar_available = False
        self._result_cache: dict[str, np.ndarray] = {}

        self._prepare_bdrar()

    # ------------------------------------------------------------------ utils
    def _resolve_device(self, force_cpu: bool) -> str:
        """Select compute device."""
        if force_cpu or not gpu_enabled():
            return "cpu"
        device = choose_device(prefer_gpu=True)
        if isinstance(device, str) and device.startswith("cuda"):
            return "cuda"
        if device in {"mps", "cpu"}:
            return device
        return "cpu"

    def _prepare_bdrar(self) -> None:
        """Attempt to load BDRAR weights + model."""
        weight_present = any(path.exists() for path in BDRAR_WEIGHT_PATHS)

        if self.config.auto_download_weights:
            try:
                download_bdrar_weights()
                weight_present = any(path.exists() for path in BDRAR_WEIGHT_PATHS)
            except Exception as exc:  # noqa: BLE001
                logger.debug("BDRAR weight download skipped: %s", exc)

        if not weight_present and not self.config.allow_unweighted_bdrar:
            logger.debug("BDRAR weights not found; skipping heavy model load.")
            return

        model, device = get_bdrar_model(self.device)
        if model is not None:
            self._bdrar_available = True
            # Keep the actual device used by get_bdrar_model
            if device:
                self.device = device

    @staticmethod
    def _normalize_rgb(image: np.ndarray) -> np.ndarray:
        """Ensure float32 RGB in [0, 1]."""
        if image.dtype == np.uint8:
            return image.astype(np.float32) / 255.0
        if image.dtype != np.float32:
            return image.astype(np.float32)
        return image

    @staticmethod
    def _cache_key(image: np.ndarray) -> str:
        """Compute stable cache key for an image."""
        key_bytes = image.shape.__repr__().encode()
        key_bytes += image.tobytes()
        return hashlib.sha1(key_bytes).hexdigest()

    # ---------------------------------------------------------------- infer
    def detect(self, rgb_image: np.ndarray, threshold: float | None = None) -> ShadowDetectorResult:
        """
        Detect shadows in an RGB image.

        Args:
            rgb_image: RGB image, float32 in [0, 1] or uint8 in [0, 255]
            threshold: Optional binarization threshold

        Returns:
            ShadowDetectorResult containing soft mask + metadata
        """
        rgb = self._normalize_rgb(rgb_image)
        cache_hit = False
        cache_key = None

        if self.config.cache_results:
            cache_key = self._cache_key(rgb)
            if cache_key in self._result_cache:
                mask = self._result_cache[cache_key]
                return ShadowDetectorResult(
                    mask=mask,
                    backend="cache",
                    device=self.device,
                    cache_hit=True,
                    extras={"bdrar_available": self._bdrar_available},
                )

        backend = "classical_fallback"
        extras: dict[str, Any] = {"bdrar_available": self._bdrar_available}

        # 1) Try BDRAR
        if self.config.prefer_bdrar and self._bdrar_available:
            try:
                mask = run_bdrar(rgb, device=self.device, threshold=threshold)
                backend = "bdrar"
            except Exception as exc:  # noqa: BLE001
                logger.warning("BDRAR inference failed, falling back: %s", exc)
                mask = None
        else:
            mask = None

        # 2) SegFormer/SAM fallback
        if mask is None and self.config.use_segformer_fallback:
            try:
                mask = run_shadow_model(rgb, high_quality=self.config.high_quality)
                backend = "segformer_sam" if self.config.high_quality else "segformer_fast"
            except Exception as exc:  # noqa: BLE001
                logger.warning("SegFormer/SAM fallback failed, using classical: %s", exc)
                mask = None

        # 3) Classical fallback (always succeeds)
        if mask is None:
            mask = _enhanced_classical_shadow(rgb)
            backend = "classical_fallback"

        mask = np.clip(mask, 0, 1).astype(np.float32)

        if threshold is not None:
            mask = (mask > threshold).astype(np.float32)

        if cache_key is not None:
            self._result_cache[cache_key] = mask

        return ShadowDetectorResult(
            mask=mask,
            backend=backend,
            device=self.device,
            cache_hit=cache_hit,
            extras=extras,
        )


def get_default_detector(
    device: str | None = None, config: ShadowDetectorConfig | None = None
) -> DeepShadowDetector:
    """
    Retrieve (or create) cached DeepShadowDetector for a device.

    Args:
        device: Explicit device ("cpu", "cuda", "mps", or None for auto)
        config: Optional configuration override

    Returns:
        DeepShadowDetector instance
    """
    resolved_device = device or ("cpu" if (config and config.force_cpu) else choose_device(True))
    if isinstance(resolved_device, str) and resolved_device.startswith("cuda"):
        resolved_device = "cuda"
    if resolved_device in _detector_cache and config is None:
        return _detector_cache[resolved_device]

    detector = DeepShadowDetector(config=config)
    if resolved_device:
        _detector_cache[resolved_device] = detector
    return detector


# ---------------------------------------------------------------------------
# Benchmark helpers (synthetic)
# ---------------------------------------------------------------------------


def _synthetic_shadow(
    width: int = 192, height: int = 192, soft: bool = False
) -> tuple[np.ndarray, np.ndarray]:
    """
    Create a synthetic shadow image + ground truth mask.

    Args:
        width: Image width
        height: Image height
        soft: Use soft penumbra edges when True

    Returns:
        (rgb_image, gt_mask) where gt_mask is float32 in [0, 1]
    """
    rgb = np.ones((height, width, 3), dtype=np.float32) * 0.85
    gt_mask = np.zeros((height, width), dtype=np.float32)

    y0, y1 = height // 3, int(height * 0.85)
    x0, x1 = width // 2, int(width * 0.9)
    gt_mask[y0:y1, x0:x1] = 1.0

    shadow_scale = 0.35 if soft else 0.25
    rgb[gt_mask > 0.5] *= shadow_scale

    if soft:
        gt_mask = cv2.GaussianBlur(gt_mask, (21, 21), 0)
        blur_mask = cv2.GaussianBlur(gt_mask, (11, 11), 0)
        rgb *= 0.5 + 0.5 * (1 - blur_mask[..., None])

    return rgb, gt_mask


def benchmark_against_classical(detector: DeepShadowDetector | None = None) -> dict[str, Any]:
    """
    Run a quick synthetic benchmark comparing deep vs classical fallback.

    Returns:
        Dict with IoU/F1 improvements for hard + soft shadows.
    """
    detector = detector or get_default_detector(
        config=ShadowDetectorConfig(
            high_quality=False,
            prefer_bdrar=True,
            auto_download_weights=False,
            allow_unweighted_bdrar=False,
            use_segformer_fallback=False,
        )
    )

    def score_pair(soft: bool) -> dict[str, float]:
        rgb, gt = _synthetic_shadow(soft=soft)
        deep_mask = detector.detect(rgb).mask > 0.5
        baseline = np.zeros_like(gt, dtype=bool)

        intersection_deep = np.logical_and(deep_mask, gt > 0.5).sum()
        intersection_base = np.logical_and(baseline, gt > 0.5).sum()
        union_deep = np.logical_or(deep_mask, gt > 0.5).sum() + 1e-8
        union_base = np.logical_or(baseline, gt > 0.5).sum() + 1e-8

        iou_deep = intersection_deep / union_deep
        iou_base = intersection_base / union_base

        def f1(pred):
            tp = np.logical_and(pred, gt > 0.5).sum()
            fp = np.logical_and(pred, gt <= 0.5).sum()
            fn = np.logical_and(~pred, gt > 0.5).sum()
            precision = tp / (tp + fp + 1e-8)
            recall = tp / (tp + fn + 1e-8)
            return 2 * precision * recall / (precision + recall + 1e-8)

        return {
            "iou_deep": float(iou_deep),
            "iou_baseline": float(iou_base),
            "f1_deep": float(f1(deep_mask)),
            "f1_baseline": float(f1(baseline)),
        }

    hard_scores = score_pair(soft=False)
    soft_scores = score_pair(soft=True)

    return {"hard": hard_scores, "soft": soft_scores}
