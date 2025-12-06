"""
Depth and surface normals estimation from single images.

Provides interfaces to pre-trained models for estimating:
- Depth maps (per-pixel distance from camera)
- Surface normals (per-pixel 3D orientation)

Supported models:
- ZoeDepth: State-of-the-art metric depth (recommended)
- MiDaS v3: Fast, robust relative depth (fallback)
- Omnidata: High-quality surface normals (recommended)
- Gradient-based: Fast normals from depth (fallback)

References:
- Bhat et al. "ZoeDepth: Zero-shot Transfer by Combining Relative
  and Metric Depth" (arXiv 2023)
- Eftekhar et al. "Omnidata: A Scalable Pipeline for Making
  Multi-Task Mid-Level Vision Datasets" (ICCV 2021)
"""

import logging
from typing import Any

import cv2
import numpy as np

logger = logging.getLogger(__name__)


# Global model caches
_zoedepth_model = None
_midas_model = None
_omnidata_normals_model = None


def _get_zoedepth_model(device: str = "cpu"):
    """Load and cache ZoeDepth model."""
    global _zoedepth_model

    if _zoedepth_model is not None:
        return _zoedepth_model

    try:
        import torch

        logger.info("Loading ZoeDepth model...")

        # Try to load ZoeDepth from torch hub
        try:
            _zoedepth_model = torch.hub.load(
                "isl-org/ZoeDepth",
                "ZoeD_NK",  # ZoeDepth with NYU+KITTI training
                pretrained=True,
            )
            _zoedepth_model.eval()
            _zoedepth_model = _zoedepth_model.to(device)
            logger.info("ZoeDepth model loaded successfully")
            return _zoedepth_model
        except Exception as e:
            logger.warning(f"Could not load ZoeDepth from hub: {e}")
            return None

    except ImportError:
        logger.warning("PyTorch not available for ZoeDepth")
        return None


def _get_midas_model(device: str = "cpu"):
    """Load and cache MiDaS v3 model (fallback for ZoeDepth)."""
    global _midas_model

    if _midas_model is not None:
        return _midas_model

    try:
        import torch

        logger.info("Loading MiDaS v3 model...")

        try:
            _midas_model = torch.hub.load(
                "intel-isl/MiDaS",
                "DPT_Large",  # Best quality
                pretrained=True,
            )
            _midas_model.eval()
            _midas_model = _midas_model.to(device)
            logger.info("MiDaS model loaded successfully")
            return _midas_model
        except Exception as e:
            logger.warning(f"Could not load MiDaS: {e}")
            return None

    except ImportError:
        logger.warning("PyTorch not available for MiDaS")
        return None


def _get_omnidata_model(device: str = "cpu"):
    """Load and cache Omnidata normals model."""
    global _omnidata_normals_model

    if _omnidata_normals_model is not None:
        return _omnidata_normals_model

    try:
        import torch

        logger.info("Loading Omnidata normals model...")

        # Omnidata models via torch hub
        try:
            _omnidata_normals_model = torch.hub.load(
                "EPFL-VILAB/omnidata",
                "normals",
                pretrained=True,
            )
            _omnidata_normals_model.eval()
            _omnidata_normals_model = _omnidata_normals_model.to(device)
            logger.info("Omnidata normals model loaded successfully")
            return _omnidata_normals_model
        except Exception as hub_error:
            logger.warning(f"Could not load Omnidata from hub: {hub_error}")

            # Try alternative: DPT-based normals from timm
            try:
                from transformers import DPTForDepthEstimation

                # DPT can also do normals
                _omnidata_normals_model = DPTForDepthEstimation.from_pretrained("Intel/dpt-large")
                _omnidata_normals_model.eval()
                _omnidata_normals_model = _omnidata_normals_model.to(device)
                logger.info("Loaded DPT as normals fallback")
                return _omnidata_normals_model
            except Exception:
                pass

            return None

    except ImportError:
        logger.warning("PyTorch not available for Omnidata")
        return None


def _estimate_depth_zoedepth(
    image_bgr: np.ndarray,
    model,
    device: str = "cpu",
) -> np.ndarray:
    """Run ZoeDepth inference."""
    import torch

    height, width = image_bgr.shape[:2]

    # Convert BGR to RGB
    image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)

    # ZoeDepth expects PIL or numpy RGB
    with torch.no_grad():
        depth = model.infer_pil(image_rgb)

    # Normalize to 0-1 (ZoeDepth outputs metric depth)
    depth_np = depth.cpu().numpy() if hasattr(depth, "cpu") else np.array(depth)
    depth_norm = (depth_np - depth_np.min()) / (depth_np.max() - depth_np.min() + 1e-8)

    # Invert so closer = 1
    depth_norm = 1.0 - depth_norm

    return depth_norm.astype(np.float32)


def _estimate_depth_midas(
    image_bgr: np.ndarray,
    model,
    device: str = "cpu",
) -> np.ndarray:
    """Run MiDaS inference."""
    import torch
    import torchvision.transforms as T

    height, width = image_bgr.shape[:2]

    # Convert BGR to RGB
    image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)

    # MiDaS transforms
    transform = T.Compose(
        [
            T.ToPILImage(),
            T.Resize(384),
            T.ToTensor(),
            T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ]
    )

    input_tensor = transform(image_rgb).unsqueeze(0).to(device)

    with torch.no_grad():
        prediction = model(input_tensor)

    # Resize back
    prediction = prediction.squeeze().cpu().numpy()
    depth = cv2.resize(prediction, (width, height))

    # Normalize to 0-1
    depth_norm = (depth - depth.min()) / (depth.max() - depth.min() + 1e-8)

    return depth_norm.astype(np.float32)


def _estimate_depth_gradient(image_bgr: np.ndarray) -> np.ndarray:
    """
    Gradient-based depth estimation fallback.

    Uses edge detection as a proxy for depth discontinuities.
    Very rough but works without models.
    """
    # Convert to grayscale
    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY).astype(np.float32) / 255.0

    # Blur to reduce noise
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # Use intensity as rough depth proxy (brighter = closer for many scenes)
    depth = blurred

    # Normalize
    depth = (depth - depth.min()) / (depth.max() - depth.min() + 1e-8)

    return depth.astype(np.float32)


def estimate_depth(
    image_bgr: np.ndarray,
    model: Any | None = None,
    device: str = "cpu",
    model_name: str = "zoedepth",
) -> np.ndarray:
    """
    Estimate depth map from a single image.

    Uses pre-trained single-image depth estimation models. By default, uses
    ZoeDepth which provides metric depth. Falls back to MiDaS if unavailable.

    Args:
        image_bgr: Input image in BGR format (H×W×3, uint8)
        model: Optional pre-loaded model. If None, loads default.
        device: Compute device ("cuda", "mps", or "cpu")
        model_name: Model to use ("zoedepth", "midas")

    Returns:
        Normalized depth map (H×W float32, 0..1 where 1=nearest, 0=farthest)

    Models (in order of preference):
        1. ZoeDepth: Metric depth, best quality
        2. MiDaS v3: Relative depth, fast and robust
        3. Gradient-based: Fallback when no models available
    """
    try:
        import torch
    except ImportError:
        logger.warning("PyTorch not installed, using gradient fallback")
        return _estimate_depth_gradient(image_bgr)

    # Determine device
    if (
        device == "cuda"
        and not torch.cuda.is_available()
        or device == "mps"
        and not torch.backends.mps.is_available()
    ):
        device = "cpu"

    # Try ZoeDepth first
    if model_name == "zoedepth" or model is None:
        zoedepth = _get_zoedepth_model(device)
        if zoedepth is not None:
            try:
                return _estimate_depth_zoedepth(image_bgr, zoedepth, device)
            except Exception as e:
                logger.warning(f"ZoeDepth inference failed: {e}")

    # Fall back to MiDaS
    midas = _get_midas_model(device)
    if midas is not None:
        try:
            return _estimate_depth_midas(image_bgr, midas, device)
        except Exception as e:
            logger.warning(f"MiDaS inference failed: {e}")

    # Final fallback: gradient-based
    logger.info("Using gradient-based depth fallback")
    return _estimate_depth_gradient(image_bgr)


def _estimate_normals_omnidata(
    image_bgr: np.ndarray,
    model,
    device: str = "cpu",
) -> np.ndarray:
    """Run Omnidata normals inference."""
    import torch
    import torchvision.transforms as T

    height, width = image_bgr.shape[:2]

    # Convert BGR to RGB
    image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)

    # Standard transforms
    transform = T.Compose(
        [
            T.ToPILImage(),
            T.Resize((384, 384)),
            T.ToTensor(),
            T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ]
    )

    input_tensor = transform(image_rgb).unsqueeze(0).to(device)

    with torch.no_grad():
        prediction = model(input_tensor)

    # Handle different output formats
    if hasattr(prediction, "predicted_depth"):
        # DPT format - derive normals from depth
        depth = prediction.predicted_depth.squeeze().cpu().numpy()
        depth = cv2.resize(depth, (width, height))
        normals = _normals_from_depth(depth)
    else:
        # Direct normals output
        normals = prediction.squeeze().permute(1, 2, 0).cpu().numpy()
        normals = cv2.resize(normals, (width, height))

    # Ensure unit vectors
    norm = np.linalg.norm(normals, axis=2, keepdims=True) + 1e-8
    normals = normals / norm

    return normals.astype(np.float32)


def _normals_from_depth(depth: np.ndarray) -> np.ndarray:
    """
    Compute surface normals from depth map using gradients.

    Args:
        depth: Depth map (H×W float32)

    Returns:
        Normal map (H×W×3 float32, unit vectors)
    """
    # Compute gradients
    dz_dx = cv2.Sobel(depth, cv2.CV_32F, 1, 0, ksize=3)
    dz_dy = cv2.Sobel(depth, cv2.CV_32F, 0, 1, ksize=3)

    # Build normal vectors: n = (-dz/dx, -dz/dy, 1)
    height, width = depth.shape
    normals = np.zeros((height, width, 3), dtype=np.float32)
    normals[:, :, 0] = -dz_dx
    normals[:, :, 1] = -dz_dy
    normals[:, :, 2] = 1.0

    # Normalize to unit vectors
    norm = np.linalg.norm(normals, axis=2, keepdims=True) + 1e-8
    normals = normals / norm

    return normals


def estimate_normals(
    image_bgr: np.ndarray,
    model: Any | None = None,
    device: str = "cpu",
    model_name: str = "omnidata",
    depth: np.ndarray | None = None,
) -> np.ndarray:
    """
    Estimate surface normals from a single image.

    Uses pre-trained models or derives from depth. By default tries Omnidata.

    Args:
        image_bgr: Input image in BGR format (H×W×3, uint8)
        model: Optional pre-loaded model
        device: Compute device ("cuda", "mps", or "cpu")
        model_name: Model to use ("omnidata", "gradient")
        depth: Optional pre-computed depth map for gradient-based normals

    Returns:
        Normal map (H×W×3 float32, unit vectors in [-1, 1])
        Channels: [nx, ny, nz] where nz typically > 0 (pointing toward camera)

    Models (in order of preference):
        1. Omnidata: Direct normal estimation, best quality
        2. Depth-derived: Compute from depth gradients (fallback)
    """
    try:
        import torch
    except ImportError:
        logger.warning("PyTorch not installed, using depth-gradient fallback")
        if depth is None:
            depth = estimate_depth(image_bgr, device=device)
        return _normals_from_depth(depth)

    # Determine device
    if (
        device == "cuda"
        and not torch.cuda.is_available()
        or device == "mps"
        and not torch.backends.mps.is_available()
    ):
        device = "cpu"

    # Try Omnidata first
    if model_name == "omnidata" or model is None:
        omnidata = _get_omnidata_model(device)
        if omnidata is not None:
            try:
                return _estimate_normals_omnidata(image_bgr, omnidata, device)
            except Exception as e:
                logger.warning(f"Omnidata inference failed: {e}")

    # Fall back to depth-gradient
    logger.info("Using depth-gradient normals fallback")
    if depth is None:
        depth = estimate_depth(image_bgr, device=device)
    return _normals_from_depth(depth)


def estimate_depth_and_normals(
    image_bgr: np.ndarray,
    depth_model: Any | None = None,
    normals_model: Any | None = None,
    device: str = "cpu",
) -> dict[str, np.ndarray]:
    """
    Estimate both depth and normals efficiently.

    Computes depth first, then either uses dedicated normals model
    or derives normals from depth gradients.

    Args:
        image_bgr: Input image in BGR format
        depth_model: Optional pre-loaded depth model
        normals_model: Optional pre-loaded normals model
        device: Compute device

    Returns:
        Dictionary with keys:
            - "depth": Depth map (H×W float32, 0..1)
            - "normals": Normal map (H×W×3 float32, unit vectors)
            - "depth_model": Model used for depth
            - "normals_model": Model used for normals
    """
    # Estimate depth
    depth = estimate_depth(image_bgr, model=depth_model, device=device)

    # Estimate normals (pass depth for potential fallback)
    normals = estimate_normals(
        image_bgr,
        model=normals_model,
        device=device,
        depth=depth,
    )

    return {
        "depth": depth,
        "normals": normals,
    }
