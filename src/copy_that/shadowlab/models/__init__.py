"""Model wrappers for shadow extraction pipeline.

Provides unified interfaces for:
- Shadow detection (DSDNet/BDRAR)
- Depth estimation (MiDaS v3)
- Intrinsic decomposition (IntrinsicNet)
"""

from .depth_model import DepthEstimationModel, load_depth_model
from .intrinsic_model import IntrinsicDecompositionModel, load_intrinsic_model
from .shadow_model import ShadowDetectionModel, load_shadow_model

__all__ = [
    "ShadowDetectionModel",
    "load_shadow_model",
    "DepthEstimationModel",
    "load_depth_model",
    "IntrinsicDecompositionModel",
    "load_intrinsic_model",
]
