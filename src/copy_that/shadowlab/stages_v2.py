"""
Five-stage shadow pipeline (simplified).

Consolidates the 8-stage pipeline into 5 focused stages:
1. Input & Illumination - Load image, compute illumination-invariant view
2. Classical Detection - Fast heuristic shadow candidates
3. ML Shadow Mask - Neural network shadow detection
4. Depth & Lighting - Geometry estimation and light fitting
5. Fusion & Tokens - Combine signals, generate tokens

Dropped: MSR intrinsic decomposition (weak quality, adds complexity)
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
    run_midas_depth,
    run_shadow_model,
)

# ============================================================================
# STAGE 1: Input & Illumination
# ============================================================================


def stage_01_input_illumination(
    image_path: str, target_size: tuple[int, int] | None = None
) -> tuple[ShadowStageResult, list[ShadowVisualLayer], dict[str, np.ndarray]]:
    """
    Stage 1: Input & Illumination.

    Load image and compute illumination-invariant view in one step.

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

    # Compute illumination map
    illumination_map = illumination_invariant_v(rgb_image)

    # Metrics
    metrics = {
        "width": float(rgb_image.shape[1]),
        "height": float(rgb_image.shape[0]),
        "mean_illumination": float(np.mean(illumination_map)),
        "std_illumination": float(np.std(illumination_map)),
    }

    # Artifacts
    artifacts = {"rgb_image": rgb_image, "illumination_map": illumination_map}

    # Stage result
    stage = ShadowStageResult(
        id="shadow_stage_01_input",
        name="Input & Illumination",
        description="Load image and extract illumination structure",
        inputs=["image_path"],
        outputs=["rgb_image", "illumination_map"],
        metrics=metrics,
        artifacts={
            "rgb_image": "Original RGB image",
            "illumination_map": "Illumination-invariant view",
        },
        stage_narrative=(
            "We load the image and immediately compute an illumination-invariant view "
            "that emphasizes brightness variations. This isolates lighting from color, "
            "making shadow regions easier to detect."
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
        ),
        ShadowVisualLayer(
            id="shadow_viz_01_illumination",
            stage_id="shadow_stage_01_input",
            type=VisualLayerType.GRAYSCALE_MAP,
            source_artifact="illumination_map",
            render_params=RenderParams(opacity=1.0),
            ui=UIConfig(
                title="Illumination View", subtitle="Brightness emphasis", default_visible=False
            ),
        ),
    ]

    return stage, visual_layers, artifacts


# ============================================================================
# STAGE 2: Classical Detection
# ============================================================================


def stage_02_classical(
    illumination_map: np.ndarray, threshold_percentile: float = 20.0
) -> tuple[ShadowStageResult, list[ShadowVisualLayer], dict[str, np.ndarray]]:
    """
    Stage 2: Classical Shadow Detection.

    Fast heuristic shadow candidates using morphology and thresholding.

    Args:
        illumination_map: From Stage 1
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
        id="shadow_stage_02_classical",
        name="Classical Detection",
        description="Fast heuristic shadow detection",
        inputs=["illumination_map"],
        outputs=["candidate_mask"],
        metrics=metrics,
        artifacts={"candidate_mask": "Soft shadow candidates"},
        stage_narrative=(
            "Classical algorithms make a fast first pass, highlighting dark regions "
            "that could plausibly be shadows. This provides a baseline before neural "
            "network refinement."
        ),
        duration_ms=1000.0 * (time.time() - start_time),
    )

    # Visual layers
    visual_layers = [
        ShadowVisualLayer(
            id="shadow_viz_02_candidates",
            stage_id="shadow_stage_02_classical",
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
# STAGE 3: ML Shadow Mask
# ============================================================================


def stage_03_ml_shadow(
    rgb_image: np.ndarray, high_quality: bool = True
) -> tuple[ShadowStageResult, list[ShadowVisualLayer], dict[str, np.ndarray]]:
    """
    Stage 3: ML Shadow Mask.

    Neural network shadow detection with SAM + BDRAR-style features.

    Args:
        rgb_image: From Stage 1
        high_quality: Use SAM boundary refinement (slower but better)

    Returns:
        (stage_result, visual_layers, artifacts)
    """
    start_time = time.time()

    # Run shadow model
    ml_shadow_mask = run_shadow_model(rgb_image, high_quality=high_quality)

    # Metrics
    metrics = {
        "ml_coverage": float(np.mean(ml_shadow_mask)),
        "ml_density": float(np.sum(ml_shadow_mask > 0.5) / ml_shadow_mask.size),
        "high_quality": float(high_quality),
    }

    # Artifacts
    artifacts = {"ml_shadow_mask": ml_shadow_mask}

    # Stage result
    stage = ShadowStageResult(
        id="shadow_stage_03_ml_mask",
        name="ML Shadow Mask",
        description="Neural network shadow detection",
        inputs=["rgb_image"],
        outputs=["ml_shadow_mask"],
        metrics=metrics,
        artifacts={"ml_shadow_mask": "ML-predicted shadow probabilities"},
        stage_narrative=(
            "A trained shadow-detection model identifies patterns too nuanced for "
            "classical methods—soft penumbras, textured surfaces, and stylized shading. "
            "This yields a probability map for each pixel being in shadow."
        ),
        duration_ms=1000.0 * (time.time() - start_time),
    )

    # Visual layers
    visual_layers = [
        ShadowVisualLayer(
            id="shadow_viz_03_ml_mask",
            stage_id="shadow_stage_03_ml_mask",
            type=VisualLayerType.HEATMAP,
            source_artifact="ml_shadow_mask",
            render_params=RenderParams(colormap="viridis", opacity=0.8, value_range=[0, 1]),
            ui=UIConfig(title="AI Shadow Mask", subtitle="Neural prediction", default_visible=True),
        )
    ]

    return stage, visual_layers, artifacts


# ============================================================================
# STAGE 4: Depth & Lighting
# ============================================================================


def stage_04_depth_lighting(
    rgb_image: np.ndarray, illumination_map: np.ndarray
) -> tuple[ShadowStageResult, list[ShadowVisualLayer], dict[str, np.ndarray]]:
    """
    Stage 4: Depth & Lighting.

    Estimate scene geometry and fit directional light.

    Args:
        rgb_image: From Stage 1
        illumination_map: From Stage 1 (used as shading proxy)

    Returns:
        (stage_result, visual_layers, artifacts)
    """
    start_time = time.time()

    # Depth estimation
    depth_map = run_midas_depth(rgb_image)

    # Normal estimation from depth
    normal_map, normal_map_rgb = depth_to_normals(depth_map)

    # Use illumination map as shading proxy (simpler than MSR)
    shading_proxy = illumination_map

    # Fit light direction
    light_direction = fit_directional_light(normal_map, shading_proxy)

    # Compute consistency error
    predicted_shading = np.clip(np.dot(normal_map, light_direction), 0, 1)
    lighting_error_map = np.abs(predicted_shading - shading_proxy)

    # Light angles
    azimuth_deg, elevation_deg = light_dir_to_angles(light_direction)

    # Metrics
    metrics = {
        "depth_mean": float(np.mean(depth_map)),
        "depth_std": float(np.std(depth_map)),
        "light_azimuth": float(azimuth_deg),
        "light_elevation": float(elevation_deg),
        "consistency_rmse": float(np.sqrt(np.mean(lighting_error_map**2))),
    }

    # Artifacts
    artifacts = {
        "depth_map": depth_map,
        "normal_map": normal_map,
        "normal_map_rgb": normal_map_rgb,
        "light_direction": light_direction,
        "lighting_error_map": lighting_error_map,
    }

    # Stage result
    stage = ShadowStageResult(
        id="shadow_stage_04_geometry",
        name="Depth & Lighting",
        description="Estimate geometry and fit light direction",
        inputs=["rgb_image", "illumination_map"],
        outputs=["depth_map", "normal_map", "light_direction"],
        metrics=metrics,
        artifacts={
            "depth_map": "Single-image depth estimate",
            "normal_map_rgb": "Surface normal visualization",
            "lighting_error_map": "Lighting consistency error",
        },
        stage_narrative=(
            "We estimate depth and surface normals from the image, then fit a directional "
            "light model. This reveals where light comes from and highlights areas where "
            "shadows violate physical lighting—common in AI-generated images."
        ),
        duration_ms=1000.0 * (time.time() - start_time),
    )

    # Visual layers
    visual_layers = [
        ShadowVisualLayer(
            id="shadow_viz_04_depth",
            stage_id="shadow_stage_04_geometry",
            type=VisualLayerType.DEPTH,
            source_artifact="depth_map",
            render_params=RenderParams(colormap="viridis", opacity=1.0, value_range=[0, 1]),
            ui=UIConfig(title="Depth Map", subtitle="Distance estimation", default_visible=True),
        ),
        ShadowVisualLayer(
            id="shadow_viz_04_normals",
            stage_id="shadow_stage_04_geometry",
            type=VisualLayerType.NORMAL,
            source_artifact="normal_map_rgb",
            render_params=RenderParams(opacity=1.0),
            ui=UIConfig(
                title="Surface Normals", subtitle="RGB-coded directions", default_visible=False
            ),
        ),
        ShadowVisualLayer(
            id="shadow_viz_04_consistency",
            stage_id="shadow_stage_04_geometry",
            type=VisualLayerType.HEATMAP,
            source_artifact="lighting_error_map",
            render_params=RenderParams(colormap="hot", opacity=0.9, value_range=[0, 0.5]),
            ui=UIConfig(
                title="Lighting Error",
                subtitle="Red = physically implausible",
                default_visible=False,
            ),
        ),
    ]

    return stage, visual_layers, artifacts


# ============================================================================
# STAGE 5: Fusion & Tokens
# ============================================================================


def stage_05_fusion(
    candidate_mask: np.ndarray,
    ml_shadow_mask: np.ndarray,
    illumination_map: np.ndarray,
    light_direction: np.ndarray,
    lighting_error_map: np.ndarray,
    rgb_image: np.ndarray,
) -> tuple[ShadowStageResult, list[ShadowVisualLayer], dict[str, np.ndarray], any]:
    """
    Stage 5: Fusion & Token Generation.

    Combine all signals into final shadow map and generate tokens.

    Args:
        candidate_mask: From Stage 2
        ml_shadow_mask: From Stage 3
        illumination_map: From Stage 1 (shading proxy)
        light_direction: From Stage 4
        lighting_error_map: From Stage 4
        rgb_image: From Stage 1

    Returns:
        (stage_result, visual_layers, artifacts, shadow_tokens)
    """
    start_time = time.time()

    # Invert illumination to get shadow-like signal (dark = shadow)
    shading_signal = 1.0 - illumination_map

    # Fuse masks
    fused_mask = fuse_shadow_masks(
        classical=candidate_mask,
        ml_mask=ml_shadow_mask,
        shading=shading_signal,
        classical_weight=0.25,
        ml_weight=0.55,
        shading_weight=0.20,
    )

    # Compute physics consistency from error map
    consistency_score = 1.0 - np.clip(np.mean(lighting_error_map), 0, 1)

    # Compute shadow tokens
    shadow_tokens = compute_shadow_tokens(
        fused_mask=fused_mask,
        shading=shading_signal,
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
        id="shadow_stage_05_tokens",
        name="Fusion & Tokens",
        description="Final shadow map and metrics",
        inputs=["candidate_mask", "ml_shadow_mask", "illumination_map", "light_direction"],
        outputs=["final_shadow_mask", "shadow_tokens"],
        metrics=metrics,
        artifacts={
            "final_shadow_mask": "Final fused shadow mask",
            "shadow_overlay": "Visualization on original",
        },
        stage_narrative=(
            "Classical heuristics, neural predictions, and lighting analysis are merged "
            "into a single coherent result. The final shadow map and tokens summarize "
            "coverage, strength, softness, and lighting direction."
        ),
        duration_ms=1000.0 * (time.time() - start_time),
    )

    # Visual layers
    visual_layers = [
        ShadowVisualLayer(
            id="shadow_viz_05_final_mask",
            stage_id="shadow_stage_05_tokens",
            type=VisualLayerType.HEATMAP,
            source_artifact="final_shadow_mask",
            render_params=RenderParams(colormap="RdYlBu_r", opacity=1.0, value_range=[0, 1]),
            ui=UIConfig(title="Final Shadow Map", subtitle="Fused mask", default_visible=True),
        ),
        ShadowVisualLayer(
            id="shadow_viz_05_overlay",
            stage_id="shadow_stage_05_tokens",
            type=VisualLayerType.RGB,
            source_artifact="shadow_overlay",
            render_params=RenderParams(opacity=1.0),
            ui=UIConfig(title="Shadow Overlay", subtitle="On original image", default_visible=True),
        ),
    ]

    return stage, visual_layers, artifacts, shadow_tokens


# ============================================================================
# CONVENIENCE: Run full pipeline
# ============================================================================


def run_pipeline_v2(
    image_path: str,
    target_size: tuple[int, int] | None = None,
    high_quality: bool = True,
) -> dict:
    """
    Run the simplified 5-stage shadow pipeline.

    Args:
        image_path: Path to input image
        target_size: Optional resize dimensions
        high_quality: Use SAM boundary refinement

    Returns:
        Dictionary with all stage results, artifacts, and tokens
    """
    all_stages = []
    all_layers = []
    all_artifacts = {}

    # Stage 1: Input & Illumination
    s1, l1, a1 = stage_01_input_illumination(image_path, target_size)
    all_stages.append(s1)
    all_layers.extend(l1)
    all_artifacts.update(a1)

    # Stage 2: Classical Detection
    s2, l2, a2 = stage_02_classical(a1["illumination_map"])
    all_stages.append(s2)
    all_layers.extend(l2)
    all_artifacts.update(a2)

    # Stage 3: ML Shadow Mask
    s3, l3, a3 = stage_03_ml_shadow(a1["rgb_image"], high_quality=high_quality)
    all_stages.append(s3)
    all_layers.extend(l3)
    all_artifacts.update(a3)

    # Stage 4: Depth & Lighting
    s4, l4, a4 = stage_04_depth_lighting(a1["rgb_image"], a1["illumination_map"])
    all_stages.append(s4)
    all_layers.extend(l4)
    all_artifacts.update(a4)

    # Stage 5: Fusion & Tokens
    s5, l5, a5, shadow_tokens = stage_05_fusion(
        candidate_mask=a2["candidate_mask"],
        ml_shadow_mask=a3["ml_shadow_mask"],
        illumination_map=a1["illumination_map"],
        light_direction=a4["light_direction"],
        lighting_error_map=a4["lighting_error_map"],
        rgb_image=a1["rgb_image"],
    )
    all_stages.append(s5)
    all_layers.extend(l5)
    all_artifacts.update(a5)

    # Total duration
    total_ms = sum(s.duration_ms for s in all_stages)

    return {
        "stages": all_stages,
        "visual_layers": all_layers,
        "artifacts": all_artifacts,
        "shadow_tokens": shadow_tokens,
        "total_duration_ms": total_ms,
    }
