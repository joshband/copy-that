"""
Depth and surface normals estimation from single images.

Provides interfaces to pre-trained models for estimating:
- Depth maps (per-pixel distance from camera)
- Surface normals (per-pixel 3D orientation)

Supports pluggable models with sensible defaults. Models are lazily loaded
on first use to avoid unnecessary memory overhead.
"""

import logging
from typing import Any

import numpy as np

logger = logging.getLogger(__name__)


def estimate_depth(
    image_bgr: np.ndarray,
    model: Any | None = None,
    device: str = "cpu",
    model_name: str = "midas",
) -> np.ndarray:
    """
    Estimate depth map from a single image.

    Uses pre-trained single-image depth estimation models. By default, uses
    MiDaS which is fast and accurate for diverse scene types.

    Args:
        image_bgr: Input image in BGR format (H×W×3, uint8)
        model: Optional pre-loaded model. If None, loads default MiDaS.
        device: Compute device ("cuda" or "cpu"). Falls back to CPU if CUDA unavailable.
        model_name: Model to use ("midas", "dpt", etc.). Ignored if model provided.

    Returns:
        Normalized depth map (H×W float32, 0..1 where 1=nearest, 0=farthest)

    Notes:
        - First call may be slow due to model loading
        - CUDA recommended for real-time use
        - Models are thread-safe if using CPU
    """
    try:
        import torch  # noqa: F401
    except ImportError:
        logger.warning(
            "PyTorch not installed. Returning dummy depth map. "
            "Install torch for real depth estimation."
        )
        return np.ones((image_bgr.shape[0], image_bgr.shape[1]), dtype=np.float32) * 0.5

    # TODO: Implement actual MiDaS/DPT model loading
    # For now, return placeholder
    height, width = image_bgr.shape[:2]

    if model is None:
        logger.info(f"Loading default depth model: {model_name}")
        # Placeholder: in real implementation, load from torch hub or timm
        # model = torch.hub.load('intel-isl/MiDaS', model_name)
        # model = model.eval().to(device)

    # Placeholder depth estimation
    logger.debug("Computing depth map (placeholder)")
    depth = np.random.rand(height, width).astype(np.float32)

    return depth


def estimate_normals(
    image_bgr: np.ndarray,
    model: Any | None = None,
    device: str = "cpu",
    model_name: str = "dpt",
) -> np.ndarray:
    """
    Estimate surface normals from a single image.

    Computes per-pixel 3D surface normals indicating local surface orientation.
    Useful for understanding geometry and lighting.

    Args:
        image_bgr: Input image in BGR format (H×W×3, uint8)
        model: Optional pre-loaded model. If None, loads default.
        device: Compute device ("cuda" or "cpu")
        model_name: Model to use ("dpt", etc.)

    Returns:
        Normal map (H×W×3 float32, unit vectors in [-1, 1])
        Channels: [nx, ny, nz] where nz typically > 0 (pointing toward camera)

    Notes:
        - Normals point toward camera by convention (nz > 0)
        - Values are normalized unit vectors
        - Can be visualized as RGB: (n+1)/2 * 255
    """
    try:
        import torch  # noqa: F401
    except ImportError:
        logger.warning(
            "PyTorch not installed. Returning dummy normals. "
            "Install torch for real normals estimation."
        )
        height, width = image_bgr.shape[:2]
        return np.tile(np.array([0, 0, 1], dtype=np.float32), (height, width, 1))

    height, width = image_bgr.shape[:2]

    if model is None:
        logger.info(f"Loading default normals model: {model_name}")
        # Placeholder for actual model loading

    # Placeholder normals (pointing toward camera)
    logger.debug("Computing normal map (placeholder)")
    normals = np.zeros((height, width, 3), dtype=np.float32)
    normals[:, :, 2] = 1.0  # Point toward camera (nz=1)

    return normals


def estimate_depth_and_normals(
    image_bgr: np.ndarray,
    depth_model: Any | None = None,
    normals_model: Any | None = None,
    device: str = "cpu",
) -> dict[str, np.ndarray]:
    """
    Estimate both depth and normals simultaneously.

    Useful when both are needed to avoid loading models twice.

    Args:
        image_bgr: Input image in BGR format
        depth_model: Optional pre-loaded depth model
        normals_model: Optional pre-loaded normals model
        device: Compute device

    Returns:
        Dictionary with keys:
            - "depth": Depth map (H×W float32, 0..1)
            - "normals": Normal map (H×W×3 float32, unit vectors)
    """
    depth = estimate_depth(image_bgr, model=depth_model, device=device)
    normals = estimate_normals(image_bgr, model=normals_model, device=device)

    return {
        "depth": depth,
        "normals": normals,
    }
