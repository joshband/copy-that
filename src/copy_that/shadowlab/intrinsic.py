"""
Intrinsic image decomposition: separating reflectance and shading.

Decomposes an image into:
- Reflectance (albedo): Material color/texture, illumination-invariant
- Shading: Per-pixel illumination/shadow information

This separation is fundamental for shadow analysis because shading directly
encodes shadow information.

Mathematical basis:
    Image ≈ Reflectance ⊙ Shading
    where ⊙ is element-wise multiplication

References:
    - Grosse et al. "Ground truth dataset and baseline evaluations for
      intrinsic image algorithms" (ICCV 2009)
    - Shi et al. "Learning intrinsic image decomposition from watching
      the world" (CVPR 2019)
"""

import logging
from typing import Any

import numpy as np

logger = logging.getLogger(__name__)


def decompose_intrinsic(
    image_bgr: np.ndarray,
    model: Any | None = None,
    device: str = "cpu",
) -> dict[str, np.ndarray]:
    """
    Decompose image into reflectance (albedo) and shading components.

    Separates illumination effects from material properties. Shading
    directly reveals shadow regions.

    Args:
        image_bgr: Input image in BGR format (H×W×3, uint8)
        model: Optional pre-loaded decomposition model. If None, loads default.
        device: Compute device ("cuda" or "cpu")

    Returns:
        Dictionary containing:
            - "reflectance": Albedo/material color (H×W×3 float32, 0..1)
            - "shading": Per-pixel illumination (H×W float32, 0..1)

    Notes:
        - Shading map is where shadows appear as values < 1.0
        - Multiplying reflectance * shading reconstructs the image
        - Useful for shadow detection (shading < threshold = shadow)
        - Models may be fine-tuned on specific datasets (indoor, outdoor, etc.)

    Example usage:
        >>> intrinsic = decompose_intrinsic(image)
        >>> shadow_mask = intrinsic["shading"] < 0.5  # Dark shading = shadow
    """
    try:
        import torch  # noqa: F401
    except ImportError:
        logger.warning(
            "PyTorch not installed. Returning dummy decomposition. "
            "Install torch for real intrinsic decomposition."
        )
        height, width = image_bgr.shape[:2]
        image_float = image_bgr.astype(np.float32) / 255.0
        reflectance = image_float
        shading = np.ones((height, width), dtype=np.float32)
        return {"reflectance": reflectance, "shading": shading}

    height, width = image_bgr.shape[:2]
    image_float = image_bgr.astype(np.float32) / 255.0

    if model is None:
        logger.info("Loading default intrinsic decomposition model")
        # TODO: Load pre-trained model
        # Consider options:
        # 1. Fine-tuned U-Net on MIT Intrinsic Image dataset
        # 2. Shi et al.'s self-supervised learning model
        # 3. Simple baseline: Gaussian blur as reflectance, high-pass as shading

    # Placeholder decomposition: use simple blur-based approach
    logger.debug("Computing intrinsic decomposition (placeholder)")

    # Simple approach: use bilateral filter for edge-preserving smoothing
    # Reflectance = smoothed version (removes shadows)
    import cv2

    reflectance_bgr = (
        cv2.bilateralFilter(
            (image_float * 255).astype(np.uint8),
            d=15,
            sigmaColor=75,
            sigmaSpace=75,
        ).astype(np.float32)
        / 255.0
    )

    # Shading = normalized ratio (how much darker is original vs reflectance)
    shading = np.clip(
        np.mean(image_float, axis=2) / (np.mean(reflectance_bgr, axis=2) + 1e-8),
        0,
        1,
    ).astype(np.float32)

    return {
        "reflectance": reflectance_bgr.astype(np.float32),
        "shading": shading.astype(np.float32),
    }


def decompose_intrinsic_advanced(
    image_bgr: np.ndarray,
    depth: np.ndarray | None = None,
    normals: np.ndarray | None = None,
    model: Any | None = None,
    device: str = "cpu",
) -> dict[str, Any]:
    """
    Advanced intrinsic decomposition using geometric priors (depth/normals).

    Incorporates estimated geometry to improve decomposition quality.
    Surfaces with similar normals should have consistent reflectance.

    Args:
        image_bgr: Input image
        depth: Optional depth map (H×W float32)
        normals: Optional surface normals (H×W×3 float32)
        model: Optional pre-loaded model
        device: Compute device

    Returns:
        Dictionary containing:
            - "reflectance": Albedo map (H×W×3 float32)
            - "shading": Illumination map (H×W float32)
            - "geometry_influence_score": How much geometry helped (0..1)
            - "confidence": Per-pixel decomposition confidence (H×W float32)
    """
    # Start with basic decomposition
    basic = decompose_intrinsic(image_bgr, model=model, device=device)

    if depth is None and normals is None:
        # No geometry available, return basic decomposition
        return {
            **basic,
            "geometry_influence_score": 0.0,
            "confidence": np.ones_like(basic["shading"]),
        }

    # TODO: Use geometry priors to refine decomposition
    # For now, return basic decomposition with markers

    height, width = image_bgr.shape[:2]
    confidence = np.ones((height, width), dtype=np.float32)

    return {
        "reflectance": basic["reflectance"],
        "shading": basic["shading"],
        "geometry_influence_score": 0.0,  # Placeholder
        "confidence": confidence,
    }
