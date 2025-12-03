"""
ShadowLab: Comprehensive shadow extraction and analysis library.

A Python library for extracting shadow information from images including:
- Classical CV-based shadow masks (illumination-invariant transforms + morphology)
- Deep-learning-based shadow detection
- Geometry estimates (depth + surface normals)
- Intrinsic image decomposition (reflectance + shading)
- Feature extraction and tokenization for design systems

Public API:
    analyze_image_for_shadows: High-level entrypoint for shadow analysis
    detect_shadows_classical: Classical CV-based shadow detection
    compute_shadow_features: Compute numeric shadow metrics
    quantize_shadow_tokens: Convert metrics to discrete design tokens
    visualize_shadow_analysis: Create multi-panel visualization
    compare_shadow_masks: Evaluate detection quality
"""

from .classical import ShadowClassicalConfig, detect_shadows_classical
from .eval import ShadowEvaluationMetrics, compare_shadow_masks
from .tokens import (
    ShadowFeatures,
    ShadowTokens,
    analyze_image_for_shadows,
    compute_shadow_features,
    quantize_shadow_tokens,
)
from .visualization import visualize_shadow_analysis

__all__ = [
    # Classical detection
    "ShadowClassicalConfig",
    "detect_shadows_classical",
    # Feature extraction & tokenization
    "ShadowFeatures",
    "ShadowTokens",
    "compute_shadow_features",
    "quantize_shadow_tokens",
    "analyze_image_for_shadows",
    # Visualization
    "visualize_shadow_analysis",
    # Evaluation
    "ShadowEvaluationMetrics",
    "compare_shadow_masks",
]
