"""Depth estimation model wrapper (MiDaS v3).

Provides a unified interface for MiDaS depth estimation.
Supports DPT_Large (best), DPT_Hybrid (balanced), and MiDaS_small (fast).
"""

import logging

import numpy as np

logger = logging.getLogger(__name__)


class DepthEstimationModel:
    """Wrapper for MiDaS depth estimation models.

    Supports:
    - DPT_Large (best quality, ~1.5s/image, 12GB VRAM)
    - DPT_Hybrid (balanced, ~0.8s/image, 8GB VRAM) ← RECOMMENDED
    - MiDaS_small (fast, ~0.3s/image, 2GB VRAM)
    """

    def __init__(self, model_type: str = "DPT_Hybrid", device: str = "cuda"):
        """Initialize depth estimation model.

        Args:
            model_type: One of 'DPT_Large', 'DPT_Hybrid', 'MiDaS_small'
            device: 'cuda' or 'cpu'
        """
        self.model_type = model_type
        self.device = device
        self.model = None
        self.transform = None
        self._validate_model_type()

    def _validate_model_type(self) -> None:
        """Validate model type is supported."""
        valid_types = {"DPT_Large", "DPT_Hybrid", "MiDaS_small"}
        if self.model_type not in valid_types:
            raise ValueError(
                f"Model type '{self.model_type}' not supported. "
                f"Choose from: {', '.join(valid_types)}"
            )

    def load(self) -> None:
        """Load pre-trained MiDaS model from torch.hub.

        Raises:
            ImportError: If torch not installed
            RuntimeError: If model download fails
        """
        try:
            import torch
        except ImportError as e:
            raise ImportError(
                "PyTorch required for depth estimation. Install with: pip install torch torchvision"
            ) from e

        logger.info(f"Loading MiDaS {self.model_type} model...")

        try:
            self.model = torch.hub.load("intel-isl/MiDaS", self.model_type, pretrained=True).to(
                self.device
            )
            self.model.eval()

            # Load transforms
            midas_transforms = torch.hub.load("intel-isl/MiDaS", "transforms")

            if self.model_type == "DPT_Large" or self.model_type == "DPT_Hybrid":
                self.transform = midas_transforms.dpt_transform
            else:  # MiDaS_small
                self.transform = midas_transforms.small_transform

            logger.info(f"MiDaS {self.model_type} loaded successfully")

        except Exception as e:
            logger.error(f"Failed to load MiDaS {self.model_type}: {e}")
            raise RuntimeError(
                f"Failed to load MiDaS model: {e}. "
                "Check internet connection and torch.hub availability."
            ) from e

    def infer(self, image: np.ndarray) -> np.ndarray:
        """Estimate depth from image.

        Args:
            image: RGB image as numpy array, shape (H, W, 3), values in [0, 1]

        Returns:
            Depth map, shape (H, W), normalized to [0, 1]
            (farther regions have higher values)

        Raises:
            RuntimeError: If model not loaded
            ValueError: If image format is invalid
        """
        if self.model is None or self.transform is None:
            raise RuntimeError("Model not loaded. Call .load() first.")

        if not isinstance(image, np.ndarray):
            raise ValueError(f"Expected numpy array, got {type(image)}")
        if image.dtype != np.float32:
            raise ValueError(f"Expected float32, got {image.dtype}")
        if len(image.shape) != 3 or image.shape[2] != 3:
            raise ValueError(f"Expected (H, W, 3), got {image.shape}")

        import torch
        import torch.nn.functional as F
        from PIL import Image

        h, w = image.shape[:2]

        # Convert numpy to PIL for transforms
        pil_image = Image.fromarray((image * 255).astype(np.uint8))

        # Apply transforms
        input_batch = self.transform(pil_image).to(self.device)

        # Inference
        with torch.no_grad():
            depth = self.model(input_batch)

            # Resize to original size
            depth = F.interpolate(
                depth.unsqueeze(1),
                size=(h, w),
                mode="bicubic",
                align_corners=False,
            ).squeeze()

        # Normalize to [0, 1]
        depth_np = depth.cpu().numpy().astype(np.float32)
        depth_min = depth_np.min()
        depth_max = depth_np.max()

        if depth_max > depth_min:
            depth_normalized = (depth_np - depth_min) / (depth_max - depth_min)
        else:
            depth_normalized = np.zeros_like(depth_np)

        return depth_normalized

    def __repr__(self) -> str:
        """String representation."""
        return f"DepthEstimationModel(type={self.model_type}, device={self.device})"


def load_depth_model(model_type: str = "DPT_Hybrid", device: str = "cuda") -> DepthEstimationModel:
    """Load a MiDaS depth estimation model.

    Args:
        model_type: One of 'DPT_Large', 'DPT_Hybrid', 'MiDaS_small'
        device: 'cuda' or 'cpu'

    Returns:
        Loaded DepthEstimationModel instance

    Example:
        >>> model = load_depth_model("DPT_Hybrid", device="cuda")
        >>> depth_map = model.infer(image)
    """
    model = DepthEstimationModel(model_type=model_type, device=device)
    model.load()
    return model
