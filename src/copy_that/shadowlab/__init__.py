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
    run_shadow_model_with_sam,
)
# 8-stage pipeline (original)
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

# 5-stage pipeline (simplified, recommended)
from .stages_v2 import (
    run_pipeline_v2,
    stage_01_input_illumination,
    stage_02_classical,
    stage_03_ml_shadow,
    stage_04_depth_lighting,
    stage_05_fusion,
)

# Depth & normals estimation
from .depth_normals import (
    estimate_depth,
    estimate_depth_and_normals,
    estimate_normals,
)

# Intrinsic decomposition
from .intrinsic import (
    decompose_intrinsic,
    decompose_intrinsic_advanced,
    decompose_intrinsic_cgintrinsics,
    decompose_intrinsic_intrinsicnet,
    get_intrinsicnet_model,
)

# BDRAR shadow detection
from .bdrar import (
    get_bdrar_model,
    run_bdrar,
    download_bdrar_weights,
)

# Advanced analysis (multi-light, CLIP, LLaVA)
from .advanced import (
    AdvancedShadowAnalysis,
    LightSource,
    MultiLightResult,
    ShadowDescription,
    ShadowStyleEmbedding,
    extract_shadow_style_embedding,
    fit_multi_light_sources,
    generate_shadow_description,
    run_advanced_analysis,
)

# Token system integration
from .integration import ShadowTokenIntegration

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
    "run_shadow_model_with_sam",
    "run_midas_depth",
    "run_intrinsic",
    "depth_to_normals",
    "fit_directional_light",
    "light_dir_to_angles",
    "fuse_shadow_masks",
    "compute_shadow_tokens",
    # 8-stage functions (original)
    "stage_01_input",
    "stage_02_illumination",
    "stage_03_candidates",
    "stage_04_ml_mask",
    "stage_05_intrinsic",
    "stage_06_geometry",
    "stage_07_lighting",
    "stage_08_tokens",
    # 5-stage functions (simplified, recommended)
    "run_pipeline_v2",
    "stage_01_input_illumination",
    "stage_02_classical",
    "stage_03_ml_shadow",
    "stage_04_depth_lighting",
    "stage_05_fusion",
    # Depth & normals estimation
    "estimate_depth",
    "estimate_normals",
    "estimate_depth_and_normals",
    # Intrinsic decomposition
    "decompose_intrinsic",
    "decompose_intrinsic_advanced",
    "decompose_intrinsic_cgintrinsics",
    "decompose_intrinsic_intrinsicnet",
    "get_intrinsicnet_model",
    # BDRAR shadow detection
    "get_bdrar_model",
    "run_bdrar",
    "download_bdrar_weights",
    # Advanced analysis (multi-light, CLIP, LLaVA)
    "AdvancedShadowAnalysis",
    "LightSource",
    "MultiLightResult",
    "ShadowStyleEmbedding",
    "ShadowDescription",
    "fit_multi_light_sources",
    "extract_shadow_style_embedding",
    "generate_shadow_description",
    "run_advanced_analysis",
    # Token system integration
    "ShadowTokenIntegration",
    # Orchestration
    "ShadowPipelineOrchestrator",
    "run_shadow_pipeline",
]
