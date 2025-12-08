"""Intrinsic decomposition model wrapper (IntrinsicNet).

Provides a unified interface for intrinsic image decomposition.
Decomposes image into reflectance (color) and shading components.
"""

import logging

import numpy as np

logger = logging.getLogger(__name__)


class IntrinsicDecompositionModel:
    """Wrapper for intrinsic decomposition models.

    Decomposes image into:
    - Reflectance: The color/texture component (what the surface looks like)
    - Shading: The illumination component (how light affects the surface)

    Satisfies: image ≈ reflectance × shading
    """

    def __init__(self, device: str = "cuda"):
        """Initialize intrinsic decomposition model.

        Args:
            device: 'cuda' or 'cpu'
        """
        self.device = device
        self.model = None

    def load(self) -> None:
        """Load pre-trained intrinsic decomposition model.

        Raises:
            ImportError: If torch not installed
            RuntimeError: If model download fails
        """
        try:
            import torch
        except ImportError as e:
            raise ImportError(
                "PyTorch required for intrinsic decomposition. "
                "Install with: pip install torch torchvision"
            ) from e

        logger.info("Loading intrinsic decomposition model...")

        try:
            # IntrinsicNet placeholder - full implementation would load pre-trained weights
            # See: https://github.com/zmurez/IntrinsicNet
            import torch.nn as nn

            class IntrinsicNetPlaceholder(nn.Module):
                """Placeholder IntrinsicNet architecture."""

                def __init__(self):
                    super().__init__()
                    # Encoder
                    self.encoder = nn.Sequential(
                        nn.Conv2d(3, 64, kernel_size=3, padding=1),
                        nn.ReLU(inplace=True),
                        nn.Conv2d(64, 128, kernel_size=3, padding=1),
                        nn.ReLU(inplace=True),
                    )

                    # Reflectance decoder
                    self.reflectance_decoder = nn.Sequential(
                        nn.Conv2d(128, 64, kernel_size=3, padding=1),
                        nn.ReLU(inplace=True),
                        nn.Conv2d(64, 3, kernel_size=3, padding=1),
                        nn.Sigmoid(),  # Keep in [0, 1]
                    )

                    # Shading decoder
                    self.shading_decoder = nn.Sequential(
                        nn.Conv2d(128, 64, kernel_size=3, padding=1),
                        nn.ReLU(inplace=True),
                        nn.Conv2d(64, 1, kernel_size=3, padding=1),
                        nn.Sigmoid(),  # Keep in [0, 1]
                    )

                def forward(self, x: "torch.Tensor") -> tuple["torch.Tensor", "torch.Tensor"]:
                    """Forward pass returns (reflectance, shading)."""
                    features = self.encoder(x)
                    reflectance = self.reflectance_decoder(features)
                    shading = self.shading_decoder(features)
                    return reflectance, shading

            self.model = IntrinsicNetPlaceholder().to(self.device)
            self.model.eval()
            logger.info("Intrinsic decomposition model loaded successfully")

        except Exception as e:
            logger.error(f"Failed to load intrinsic decomposition model: {e}")
            raise RuntimeError(f"Failed to load intrinsic model: {e}") from e

    def infer(self, image: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """Decompose image into reflectance and shading.

        Args:
            image: RGB image as numpy array, shape (H, W, 3), values in [0, 1]

        Returns:
            Tuple of:
            - reflectance: (H, W, 3) color/texture component
            - shading: (H, W) grayscale illumination component

        Raises:
            RuntimeError: If model not loaded
            ValueError: If image format is invalid
        """
        if self.model is None:
            raise RuntimeError("Model not loaded. Call .load() first.")

        if not isinstance(image, np.ndarray):
            raise ValueError(f"Expected numpy array, got {type(image)}")
        if image.dtype != np.float32:
            raise ValueError(f"Expected float32, got {image.dtype}")
        if len(image.shape) != 3 or image.shape[2] != 3:
            raise ValueError(f"Expected (H, W, 3), got {image.shape}")

        import torch
        from PIL import Image

        h, w = image.shape[:2]

        # Convert numpy to PIL to tensor
        pil_image = Image.fromarray((image * 255).astype(np.uint8))
        tensor = torch.from_numpy(np.array(pil_image)).permute(2, 0, 1).float()
        tensor = tensor / 255.0  # Normalize to [0, 1]
        tensor = tensor.unsqueeze(0).to(self.device)

        # Inference
        with torch.no_grad():
            reflectance, shading = self.model(tensor)

        # Post-process
        reflectance_np = reflectance.squeeze(0).permute(1, 2, 0).cpu().numpy()
        shading_np = shading.squeeze(0).squeeze(0).cpu().numpy()  # Remove batch and channel dims

        # Ensure correct shapes and ranges
        reflectance_np = np.clip(reflectance_np, 0, 1).astype(np.float32)
        shading_np = np.clip(shading_np, 0, 1).astype(np.float32)

        return reflectance_np, shading_np

    def validate_decomposition(
        self,
        original: np.ndarray,
        reflectance: np.ndarray,
        shading: np.ndarray,
        tolerance: float = 0.15,
    ) -> dict:
        """Validate decomposition quality.

        Checks if: original ≈ reflectance × shading

        Args:
            original: Original image (H, W, 3)
            reflectance: Reflectance map (H, W, 3)
            shading: Shading map (H, W)
            tolerance: Max allowed MSE

        Returns:
            Dict with validation metrics
        """
        # Expand shading to match reflectance shape
        shading_expanded = np.expand_dims(shading, axis=2)
        reconstructed = reflectance * shading_expanded

        # Compute reconstruction error
        mse = np.mean((original - reconstructed) ** 2)
        mae = np.mean(np.abs(original - reconstructed))

        is_valid = mse < tolerance

        return {
            "mse": float(mse),
            "mae": float(mae),
            "is_valid": is_valid,
            "tolerance": tolerance,
        }

    def __repr__(self) -> str:
        """String representation."""
        return f"IntrinsicDecompositionModel(device={self.device})"


def load_intrinsic_model(device: str = "cuda") -> IntrinsicDecompositionModel:
    """Load an intrinsic decomposition model.

    Args:
        device: 'cuda' or 'cpu'

    Returns:
        Loaded IntrinsicDecompositionModel instance

    Example:
        >>> model = load_intrinsic_model(device="cuda")
        >>> reflectance, shading = model.infer(image)
    """
    model = IntrinsicDecompositionModel(device=device)
    model.load()
    return model
