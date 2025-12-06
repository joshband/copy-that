"""
Eight-stage pipeline implementations.

Each stage is a standalone function that:
1. Takes inputs from previous stages
2. Performs processing
3. Returns (ShadowStageResult, visual_layers, artifacts)
"""

import time

import cv2
import numpy as np

from .pipeline import (
    RenderParams,
    ShadowStageResult,
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

# ============================================================================
# STAGE 1: Input & Preprocessing
# ============================================================================


def stage_01_input(
    image_path: str, target_size: tuple[int, int] | None = None
) -> tuple[ShadowStageResult, list[ShadowVisualLayer], dict[str, np.ndarray]]:
    """
    Stage 1: Input & Preprocessing.

    Standardize input image and optionally segment.

    Args:
        image_path: Path to input image
        target_size: Optional (height, width) for resizing

    Returns:
        (stage_result, visual_layers, artifacts)
    """
    start_time = time.time()

    # Load image
    rgb_image = load_rgb(image_path)

    # Resize if needed
    if target_size:
        h, w = target_size
        rgb_image = cv2.resize(rgb_image, (w, h), interpolation=cv2.INTER_LANCZOS4)

    # Metrics
    metrics = {
        "width": float(rgb_image.shape[1]),
        "height": float(rgb_image.shape[0]),
        "channels": float(rgb_image.shape[2]) if rgb_image.ndim == 3 else 1.0,
    }

    # Artifacts
    artifacts = {"rgb_image": rgb_image}

    # Stage result
    stage = ShadowStageResult(
        id="shadow_stage_01_input",
        name="Input & Preprocessing",
        description="Normalize image and prepare for analysis",
        inputs=["image_path"],
        outputs=["rgb_image"],
        metrics=metrics,
        artifacts={"rgb_image": "Original RGB image"},
        stage_narrative=(
            "We begin by normalizing the image—resizing if needed, converting its color "
            "representation, and preparing a clean starting point before shadow analysis."
        ),
        duration_ms=1000.0 * (time.time() - start_time),
    )

    # Visual layers
    visual_layers = [
        ShadowVisualLayer(
            id="shadow_viz_01_original",
            stage_id="shadow_stage_01_input",
            type=VisualLayerType.RGB,
            source_artifact="rgb_image",
            render_params=RenderParams(opacity=1.0),
            ui=UIConfig(title="Original Image", subtitle="Input RGB", default_visible=True),
        )
    ]

    return stage, visual_layers, artifacts


# ============================================================================
# STAGE 2: Illumination-Invariant View
# ============================================================================


def stage_02_illumination(
    rgb_image: np.ndarray,
) -> tuple[ShadowStageResult, list[ShadowVisualLayer], dict[str, np.ndarray]]:
    """
    Stage 2: Illumination-Invariant View.

    Extract brightness channel to emphasize lighting structure.

    Args:
        rgb_image: RGB image from Stage 1

    Returns:
        (stage_result, visual_layers, artifacts)
    """
    start_time = time.time()

    # Compute illumination map
    illumination_map = illumination_invariant_v(rgb_image)

    # Metrics
    metrics = {
        "mean_illumination": float(np.mean(illumination_map)),
        "std_illumination": float(np.std(illumination_map)),
        "min_illumination": float(np.min(illumination_map)),
        "max_illumination": float(np.max(illumination_map)),
    }

    # Artifacts
    artifacts = {"illumination_map": illumination_map}

    # Stage result
    stage = ShadowStageResult(
        id="shadow_stage_02_invariant",
        name="Illumination-Invariant View",
        description="Extract brightness while reducing color noise",
        inputs=["rgb_image"],
        outputs=["illumination_map"],
        metrics=metrics,
        artifacts={"illumination_map": "Grayscale illumination map"},
        stage_narrative=(
            "To reason about shadows, we isolate illumination from color. This "
            "illumination-oriented view makes bright and dark regions far easier for "
            "both AI and humans to compare."
        ),
        duration_ms=1000.0 * (time.time() - start_time),
    )

    # Visual layers
    visual_layers = [
        ShadowVisualLayer(
            id="shadow_viz_02_illumination",
            stage_id="shadow_stage_02_invariant",
            type=VisualLayerType.GRAYSCALE_MAP,
            source_artifact="illumination_map",
            render_params=RenderParams(opacity=1.0),
            ui=UIConfig(
                title="Illumination View", subtitle="Brightness emphasis", default_visible=True
            ),
        )
    ]

    return stage, visual_layers, artifacts


# ============================================================================
# STAGE 3: Classical Shadow Candidates
# ============================================================================


def stage_03_candidates(
    illumination_map: np.ndarray, threshold_percentile: float = 20.0
) -> tuple[ShadowStageResult, list[ShadowVisualLayer], dict[str, np.ndarray]]:
    """
    Stage 3: Classical Shadow Candidates.

    Generate fast heuristic shadow estimates.

    Args:
        illumination_map: From Stage 2
        threshold_percentile: Darkness threshold

    Returns:
        (stage_result, visual_layers, artifacts)
    """
    start_time = time.time()

    # Classical candidates
    candidate_mask = classical_shadow_candidates(illumination_map, threshold_percentile)

    # Metrics
    metrics = {
        "candidate_coverage": float(np.mean(candidate_mask)),
        "candidate_density": float(np.sum(candidate_mask > 0.5) / candidate_mask.size),
    }

    # Artifacts
    artifacts = {"candidate_mask": candidate_mask}

    # Stage result
    stage = ShadowStageResult(
        id="shadow_stage_03_candidates",
        name="Classical Shadow Candidates",
        description="Fast heuristic shadow detection",
        inputs=["illumination_map"],
        outputs=["candidate_mask"],
        metrics=metrics,
        artifacts={"candidate_mask": "Soft shadow candidates"},
        stage_narrative=(
            "Before using heavier neural models, we allow classical algorithms to make "
            "the first guess. These fast heuristics highlight unusually dark regions that "
            "could plausibly be shadows."
        ),
        duration_ms=1000.0 * (time.time() - start_time),
    )

    # Visual layers
    visual_layers = [
        ShadowVisualLayer(
            id="shadow_viz_03_candidates",
            stage_id="shadow_stage_03_candidates",
            type=VisualLayerType.HEATMAP,
            source_artifact="candidate_mask",
            render_params=RenderParams(colormap="hot", opacity=0.7, value_range=[0, 1]),
            ui=UIConfig(
                title="Classical Candidates", subtitle="Heuristic detection", default_visible=True
            ),
        )
    ]

    return stage, visual_layers, artifacts


# ============================================================================
# STAGE 4: ML Shadow Mask
# ============================================================================


def stage_04_ml_mask(
    rgb_image: np.ndarray,
) -> tuple[ShadowStageResult, list[ShadowVisualLayer], dict[str, np.ndarray]]:
    """
    Stage 4: ML Shadow Mask.

    Predict refined shadow probability using trained model.

    Args:
        rgb_image: From Stage 1

    Returns:
        (stage_result, visual_layers, artifacts)
    """
    start_time = time.time()

    # Run shadow model
    ml_shadow_mask = run_shadow_model(rgb_image)

    # Metrics
    metrics = {
        "ml_coverage": float(np.mean(ml_shadow_mask)),
        "ml_density": float(np.sum(ml_shadow_mask > 0.5) / ml_shadow_mask.size),
    }

    # Artifacts
    artifacts = {"ml_shadow_mask": ml_shadow_mask}

    # Stage result
    stage = ShadowStageResult(
        id="shadow_stage_04_ml_mask",
        name="ML Shadow Mask",
        description="Neural network shadow detection",
        inputs=["rgb_image"],
        outputs=["ml_shadow_mask"],
        metrics=metrics,
        artifacts={"ml_shadow_mask": "ML-predicted shadow probabilities"},
        stage_narrative=(
            "A trained shadow-detection model identifies patterns too nuanced for "
            "classical methods—soft penumbras, textured surfaces, stylized shading, "
            "and more. This yields a probability map representing how likely each "
            "pixel is to be in shadow."
        ),
        duration_ms=1000.0 * (time.time() - start_time),
    )

    # Visual layers
    visual_layers = [
        ShadowVisualLayer(
            id="shadow_viz_04_ml_mask",
            stage_id="shadow_stage_04_ml_mask",
            type=VisualLayerType.HEATMAP,
            source_artifact="ml_shadow_mask",
            render_params=RenderParams(colormap="viridis", opacity=0.8, value_range=[0, 1]),
            ui=UIConfig(title="AI Shadow Mask", subtitle="Neural prediction", default_visible=True),
        )
    ]

    return stage, visual_layers, artifacts


# ============================================================================
# STAGE 5: Intrinsic Image Decomposition
# ============================================================================


def stage_05_intrinsic(
    rgb_image: np.ndarray,
) -> tuple[ShadowStageResult, list[ShadowVisualLayer], dict[str, np.ndarray]]:
    """
    Stage 5: Intrinsic Image Decomposition.

    Split image into reflectance and shading.

    Args:
        rgb_image: From Stage 1

    Returns:
        (stage_result, visual_layers, artifacts)
    """
    start_time = time.time()

    # Intrinsic decomposition
    reflectance_map, shading_map = run_intrinsic(rgb_image)

    # Metrics
    metrics = {
        "shading_mean": float(np.mean(shading_map)),
        "reflectance_mean": float(np.mean(reflectance_map)),
        "shading_contrast": float(np.std(shading_map)),
    }

    # Artifacts
    artifacts = {"reflectance_map": reflectance_map, "shading_map": shading_map}

    # Stage result
    stage = ShadowStageResult(
        id="shadow_stage_05_intrinsic",
        name="Intrinsic Image Decomposition",
        description="Separate reflectance from shading",
        inputs=["rgb_image"],
        outputs=["reflectance_map", "shading_map"],
        metrics=metrics,
        artifacts={
            "reflectance_map": "Material reflectance",
            "shading_map": "Illumination/shading",
        },
        stage_narrative=(
            "Intrinsic decomposition attempts to separate *what the surfaces are made of* "
            "from *how light hits them*. Shadows appear clearly in the shading map, while "
            "reflectance shows a cleaned, lighting-neutral view of the scene."
        ),
        duration_ms=1000.0 * (time.time() - start_time),
    )

    # Visual layers
    visual_layers = [
        ShadowVisualLayer(
            id="shadow_viz_05_reflectance",
            stage_id="shadow_stage_05_intrinsic",
            type=VisualLayerType.RGB,
            source_artifact="reflectance_map",
            render_params=RenderParams(opacity=1.0),
            ui=UIConfig(title="Reflectance", subtitle="Shadow-free colors", default_visible=True),
        ),
        ShadowVisualLayer(
            id="shadow_viz_05_shading",
            stage_id="shadow_stage_05_intrinsic",
            type=VisualLayerType.GRAYSCALE_MAP,
            source_artifact="shading_map",
            render_params=RenderParams(opacity=1.0),
            ui=UIConfig(title="Shading", subtitle="Illumination structure", default_visible=True),
        ),
    ]

    return stage, visual_layers, artifacts


# ============================================================================
# STAGE 6: Depth & Surface Normals
# ============================================================================


def stage_06_geometry(
    rgb_image: np.ndarray,
) -> tuple[ShadowStageResult, list[ShadowVisualLayer], dict[str, np.ndarray]]:
    """
    Stage 6: Depth & Surface Normals.

    Infer 3D geometry.

    Args:
        rgb_image: From Stage 1

    Returns:
        (stage_result, visual_layers, artifacts)
    """
    start_time = time.time()

    # Depth estimation
    depth_map = run_midas_depth(rgb_image)

    # Normal estimation from depth
    normal_map, normal_map_rgb = depth_to_normals(depth_map)

    # Metrics
    metrics = {"depth_mean": float(np.mean(depth_map)), "depth_std": float(np.std(depth_map))}

    # Artifacts
    artifacts = {"depth_map": depth_map, "normal_map": normal_map, "normal_map_rgb": normal_map_rgb}

    # Stage result
    stage = ShadowStageResult(
        id="shadow_stage_06_geometry",
        name="Depth & Surface Normals",
        description="Estimate scene geometry",
        inputs=["rgb_image"],
        outputs=["depth_map", "normal_map"],
        metrics=metrics,
        artifacts={
            "depth_map": "Single-image depth estimate",
            "normal_map": "Surface normal vectors",
            "normal_map_rgb": "Normal visualization",
        },
        stage_narrative=(
            "Although we have only a 2D image, we can approximate depth and surface tilt. "
            "This helps determine whether shadows make geometric sense and where light "
            "would realistically fall."
        ),
        duration_ms=1000.0 * (time.time() - start_time),
    )

    # Visual layers
    visual_layers = [
        ShadowVisualLayer(
            id="shadow_viz_06_depth",
            stage_id="shadow_stage_06_geometry",
            type=VisualLayerType.DEPTH,
            source_artifact="depth_map",
            render_params=RenderParams(colormap="viridis", opacity=1.0, value_range=[0, 1]),
            ui=UIConfig(title="Depth Map", subtitle="Distance estimation", default_visible=True),
        ),
        ShadowVisualLayer(
            id="shadow_viz_06_normals",
            stage_id="shadow_stage_06_geometry",
            type=VisualLayerType.NORMAL,
            source_artifact="normal_map_rgb",
            render_params=RenderParams(opacity=1.0),
            ui=UIConfig(
                title="Surface Normals", subtitle="RGB-coded directions", default_visible=True
            ),
        ),
    ]

    return stage, visual_layers, artifacts


# ============================================================================
# STAGE 7: Lighting Fit & Consistency
# ============================================================================


def stage_07_lighting(
    normal_map: np.ndarray, shading_map: np.ndarray
) -> tuple[ShadowStageResult, list[ShadowVisualLayer], dict[str, np.ndarray]]:
    """
    Stage 7: Lighting Fit & Consistency.

    Fit directional light and compute consistency errors.

    Args:
        normal_map: From Stage 6
        shading_map: From Stage 5

    Returns:
        (stage_result, visual_layers, artifacts)
    """
    start_time = time.time()

    # Fit light direction
    light_direction = fit_directional_light(normal_map, shading_map)

    # Compute consistency error
    if shading_map.ndim == 3:
        shading_gray = np.mean(shading_map, axis=2)
    else:
        shading_gray = shading_map

    # Predicted shading = N·L
    predicted_shading = np.dot(normal_map, light_direction)
    predicted_shading = np.clip(predicted_shading, 0, 1)

    # Error map
    lighting_error_map = np.abs(predicted_shading - shading_gray)

    # Light angles
    azimuth_deg, elevation_deg = light_dir_to_angles(light_direction)

    # Metrics
    metrics = {
        "light_azimuth": float(azimuth_deg),
        "light_elevation": float(elevation_deg),
        "consistency_rmse": float(np.sqrt(np.mean(lighting_error_map**2))),
        "consistency_mae": float(np.mean(lighting_error_map)),
    }

    # Artifacts
    artifacts = {"light_direction": light_direction, "lighting_error_map": lighting_error_map}

    # Stage result
    stage = ShadowStageResult(
        id="shadow_stage_07_lighting",
        name="Lighting Fit & Consistency",
        description="Estimate light direction and consistency",
        inputs=["normal_map", "shading_map"],
        outputs=["light_direction", "lighting_error_map"],
        metrics=metrics,
        artifacts={
            "light_direction": f"Light vector [{light_direction[0]:.3f}, {light_direction[1]:.3f}, {light_direction[2]:.3f}]",
            "lighting_error_map": "Consistency error visualization",
        },
        stage_narrative=(
            "Using the shading field and estimated surface normals, we fit a simple "
            "lighting model. This reveals the dominant light direction and highlights "
            "areas where the AI-generated image violates physical lighting—common in "
            "stylized Midjourney outputs."
        ),
        duration_ms=1000.0 * (time.time() - start_time),
    )

    # Visual layers
    visual_layers = [
        ShadowVisualLayer(
            id="shadow_viz_07_consistency",
            stage_id="shadow_stage_07_lighting",
            type=VisualLayerType.HEATMAP,
            source_artifact="lighting_error_map",
            render_params=RenderParams(colormap="hot", opacity=0.9, value_range=[0, 0.5]),
            ui=UIConfig(
                title="Lighting Consistency Error",
                subtitle="Red = physically implausible",
                default_visible=True,
            ),
        )
    ]

    return stage, visual_layers, artifacts


# ============================================================================
# STAGE 8: Fusion & Token Generation
# ============================================================================


def stage_08_tokens(
    candidate_mask: np.ndarray,
    ml_shadow_mask: np.ndarray,
    shading_map: np.ndarray,
    light_direction: np.ndarray,
    lighting_error_map: np.ndarray,
    rgb_image: np.ndarray,
) -> tuple[ShadowStageResult, list[ShadowVisualLayer], dict[str, np.ndarray]]:
    """
    Stage 8: Fusion & Token Generation.

    Produce final shadow map and tokens.

    Args:
        candidate_mask: From Stage 3
        ml_shadow_mask: From Stage 4
        shading_map: From Stage 5
        light_direction: From Stage 7
        lighting_error_map: From Stage 7
        rgb_image: From Stage 1

    Returns:
        (stage_result, visual_layers, artifacts)
    """
    start_time = time.time()

    # Fuse masks
    fused_mask = fuse_shadow_masks(
        classical=candidate_mask,
        ml_mask=ml_shadow_mask,
        shading=shading_map,
        classical_weight=0.3,
        ml_weight=0.5,
        shading_weight=0.2,
    )

    # Compute physics consistency from error map
    consistency_score = 1.0 - np.clip(np.mean(lighting_error_map), 0, 1)

    # Compute shadow tokens
    shadow_tokens = compute_shadow_tokens(
        fused_mask=fused_mask,
        shading=shading_map,
        light_direction=light_direction,
        physics_consistency=float(consistency_score),
    )

    # Create final shadow overlay (red mask on image)
    overlay = rgb_image.copy()
    red_mask = np.stack([fused_mask, np.zeros_like(fused_mask), np.zeros_like(fused_mask)], axis=2)
    overlay = np.clip(overlay * 0.7 + red_mask * 0.3, 0, 1)

    # Metrics
    metrics = {
        "final_coverage": float(shadow_tokens.coverage),
        "mean_strength": float(shadow_tokens.mean_strength),
        "edge_softness": float(shadow_tokens.edge_softness_mean),
        "physics_consistency": float(shadow_tokens.physics_consistency),
    }

    # Artifacts
    artifacts = {"final_shadow_mask": fused_mask, "shadow_overlay": overlay}

    # Stage result
    stage = ShadowStageResult(
        id="shadow_stage_08_tokens",
        name="Fusion & Token Generation",
        description="Produce final shadow map and metrics",
        inputs=["candidate_mask", "ml_shadow_mask", "shading_map", "light_direction"],
        outputs=["final_shadow_mask", "shadow_tokens"],
        metrics=metrics,
        artifacts={
            "final_shadow_mask": "Final fused shadow mask",
            "shadow_overlay": "Visualization on original",
        },
        stage_narrative=(
            "All signals—brightness heuristics, neural predictions, shading, geometry, "
            "and lighting—are merged into a single coherent result. The final shadow map "
            "and shadow tokens summarize coverage, strength, softness, lighting direction, "
            "and style."
        ),
        duration_ms=1000.0 * (time.time() - start_time),
    )

    # Visual layers
    visual_layers = [
        ShadowVisualLayer(
            id="shadow_viz_08_final_mask",
            stage_id="shadow_stage_08_tokens",
            type=VisualLayerType.HEATMAP,
            source_artifact="final_shadow_mask",
            render_params=RenderParams(colormap="RdYlBu_r", opacity=1.0, value_range=[0, 1]),
            ui=UIConfig(title="Final Shadow Map", subtitle="Fused mask", default_visible=True),
        ),
        ShadowVisualLayer(
            id="shadow_viz_08_overlay",
            stage_id="shadow_stage_08_tokens",
            type=VisualLayerType.RGB,
            source_artifact="shadow_overlay",
            render_params=RenderParams(opacity=1.0),
            ui=UIConfig(title="Shadow Overlay", subtitle="On original image", default_visible=True),
        ),
    ]

    return stage, visual_layers, artifacts, shadow_tokens
