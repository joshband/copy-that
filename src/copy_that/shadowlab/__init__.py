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
from .orchestrator import (
    ShadowPipelineOrchestrator,
    run_shadow_pipeline,
)

# Multi-stage pipeline (NEW)
from .pipeline import (
    BlendMode,
    LightDirection,
    RenderParams,
    ShadowClusterStats,
    ShadowPipeline,
    ShadowStageResult,
    ShadowTokenSet,
    ShadowVisualLayer,
    UIConfig,
    VisualLayerType,
    classical_shadow_candidates,
    compute_shadow_tokens,
    depth_to_normals,
    fit_directional_light,
    fuse_shadow_masks,
    illumination_invariant_v,
    light_dir_to_angles,
    load_rgb,
    run_intrinsic,
    run_midas_depth,
    run_shadow_model,
)
from .stages import (
    stage_01_input,
    stage_02_illumination,
    stage_03_candidates,
    stage_04_ml_mask,
    stage_05_intrinsic,
    stage_06_geometry,
    stage_07_lighting,
    stage_08_tokens,
)
from .tokens import (
    ShadowFeatures,
    ShadowTokens,
    analyze_image_for_shadows,
    compute_shadow_features,
    quantize_shadow_tokens,
)
from .visualization import visualize_shadow_analysis

__all__ = [
    # Classical detection (existing)
    "ShadowClassicalConfig",
    "detect_shadows_classical",
    # Feature extraction & tokenization (existing)
    "ShadowFeatures",
    "ShadowTokens",
    "compute_shadow_features",
    "quantize_shadow_tokens",
    "analyze_image_for_shadows",
    # Visualization (existing)
    "visualize_shadow_analysis",
    # Evaluation (existing)
    "ShadowEvaluationMetrics",
    "compare_shadow_masks",
    # Pipeline (NEW)
    "ShadowPipeline",
    "ShadowStageResult",
    "ShadowVisualLayer",
    "ShadowTokenSet",
    "VisualLayerType",
    "BlendMode",
    "RenderParams",
    "UIConfig",
    "LightDirection",
    "ShadowClusterStats",
    # Pipeline functions (NEW)
    "load_rgb",
    "illumination_invariant_v",
    "classical_shadow_candidates",
    "run_shadow_model",
    "run_midas_depth",
    "run_intrinsic",
    "depth_to_normals",
    "fit_directional_light",
    "light_dir_to_angles",
    "fuse_shadow_masks",
    "compute_shadow_tokens",
    # Stage functions (NEW)
    "stage_01_input",
    "stage_02_illumination",
    "stage_03_candidates",
    "stage_04_ml_mask",
    "stage_05_intrinsic",
    "stage_06_geometry",
    "stage_07_lighting",
    "stage_08_tokens",
    # Orchestration (NEW)
    "ShadowPipelineOrchestrator",
    "run_shadow_pipeline",
]
