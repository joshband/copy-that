#!/usr/bin/env python3
"""
Shadow Pipeline Visualization Demo

Generates visual outputs for each stage of the shadow extraction pipeline.
Run: uv run python scripts/shadow_pipeline_demo.py [optional_image_path]
"""

import sys
from pathlib import Path

import cv2
import numpy as np

from copy_that.shadowlab.pipeline import (
    classical_shadow_candidates,
    depth_to_normals,
    illumination_invariant_v,
    run_midas_depth,
    run_shadow_model,
)


def create_synthetic_shadow_image(size: int = 512) -> np.ndarray:
    """
    Create a synthetic image with clear shadow regions for testing.

    Creates a scene with:
    - Light gray background
    - A "sphere" (gradient circle)
    - A cast shadow extending from the sphere
    """
    h, w = size, size
    image = np.ones((h, w, 3), dtype=np.float32) * 0.85  # Light background

    # Add subtle texture/gradient to background
    y_grad = np.linspace(0.8, 0.9, h)[:, np.newaxis]
    image[:, :, 0] *= y_grad
    image[:, :, 1] *= y_grad
    image[:, :, 2] *= y_grad

    # Create sphere (bright object)
    cy, cx = h // 3, w // 2
    radius = size // 6
    y, x = np.ogrid[:h, :w]
    dist = np.sqrt((x - cx) ** 2 + (y - cy) ** 2)

    # Sphere with gradient shading
    sphere_mask = dist < radius
    sphere_shading = 1.0 - (dist[sphere_mask] / radius) * 0.3

    # Apply sphere color (warm white)
    for c in range(3):
        channel = image[:, :, c]
        channel[sphere_mask] = sphere_shading * (0.95 if c < 2 else 0.9)

    # Create cast shadow (ellipse extending from sphere)
    shadow_cy = int(cy + radius * 1.8)
    shadow_cx = int(cx + radius * 0.5)
    shadow_a = int(radius * 1.5)  # Semi-major axis
    shadow_b = int(radius * 0.6)  # Semi-minor axis

    # Elliptical shadow mask with soft edges
    shadow_dist = ((x - shadow_cx) / shadow_a) ** 2 + ((y - shadow_cy) / shadow_b) ** 2
    shadow_mask = shadow_dist < 1.0
    shadow_soft = np.clip(1.0 - shadow_dist, 0, 1)
    shadow_soft = shadow_soft**0.5  # Soften falloff

    # Apply shadow (darker, slightly blue-shifted)
    shadow_intensity = 0.4
    for c in range(3):
        channel = image[:, :, c]
        # Blue shift in shadow
        color_mult = 1.1 if c == 2 else 0.9
        channel[shadow_mask] = channel[shadow_mask] * (
            1 - shadow_soft[shadow_mask] * shadow_intensity * color_mult
        )

    # Add a second smaller object with shadow
    obj2_cy, obj2_cx = int(h * 0.6), int(w * 0.3)
    obj2_radius = size // 10
    obj2_dist = np.sqrt((x - obj2_cx) ** 2 + (y - obj2_cy) ** 2)
    obj2_mask = obj2_dist < obj2_radius

    # Red-ish cube approximation
    for c in range(3):
        color = [0.8, 0.3, 0.3][c]
        image[:, :, c][obj2_mask] = color

    # Shadow for second object
    shadow2_cy = int(obj2_cy + obj2_radius * 1.2)
    shadow2_cx = int(obj2_cx + obj2_radius * 0.3)
    shadow2_dist = ((x - shadow2_cx) / (obj2_radius * 1.2)) ** 2 + (
        (y - shadow2_cy) / (obj2_radius * 0.4)
    ) ** 2
    shadow2_mask = shadow2_dist < 1.0
    shadow2_soft = np.clip(1.0 - shadow2_dist, 0, 1) ** 0.5

    for c in range(3):
        channel = image[:, :, c]
        channel[shadow2_mask] *= 1 - shadow2_soft[shadow2_mask] * 0.35

    return np.clip(image, 0, 1).astype(np.float32)


def apply_colormap(gray: np.ndarray, colormap: int = cv2.COLORMAP_VIRIDIS) -> np.ndarray:
    """Apply colormap to grayscale image for visualization."""
    gray_uint8 = (np.clip(gray, 0, 1) * 255).astype(np.uint8)
    colored = cv2.applyColorMap(gray_uint8, colormap)
    return cv2.cvtColor(colored, cv2.COLOR_BGR2RGB).astype(np.float32) / 255.0


def create_overlay(
    rgb: np.ndarray, mask: np.ndarray, color: tuple = (1, 0, 0), alpha: float = 0.5
) -> np.ndarray:
    """Create overlay of mask on RGB image."""
    overlay = rgb.copy()
    mask_3ch = np.stack([mask] * 3, axis=-1)
    color_overlay = np.zeros_like(rgb)
    color_overlay[:, :] = color
    overlay = overlay * (1 - mask_3ch * alpha) + color_overlay * mask_3ch * alpha
    return np.clip(overlay, 0, 1).astype(np.float32)


def run_demo(image_path: str | None = None, output_dir: str = "shadow_demo_output"):
    """Run the shadow pipeline demo and save visualizations."""

    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    # Load or create image
    if image_path and Path(image_path).exists():
        print(f"Loading image: {image_path}")
        img_bgr = cv2.imread(image_path)
        rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB).astype(np.float32) / 255.0
    else:
        print("Creating synthetic shadow test image...")
        rgb = create_synthetic_shadow_image(512)

    h, w = rgb.shape[:2]
    print(f"Image size: {w}x{h}")

    # Save original
    print("\n[Stage 01] Input Image")
    cv2.imwrite(
        str(output_path / "01_input.png"),
        cv2.cvtColor((rgb * 255).astype(np.uint8), cv2.COLOR_RGB2BGR),
    )

    # Stage 02: Illumination Invariant
    print("[Stage 02] Computing illumination invariant...")
    illum = illumination_invariant_v(rgb)
    illum_vis = apply_colormap(illum, cv2.COLORMAP_INFERNO)
    cv2.imwrite(
        str(output_path / "02_illumination.png"),
        cv2.cvtColor((illum_vis * 255).astype(np.uint8), cv2.COLOR_RGB2BGR),
    )
    cv2.imwrite(str(output_path / "02_illumination_gray.png"), (illum * 255).astype(np.uint8))

    # Stage 03: Classical Shadow Candidates
    print("[Stage 03] Computing classical shadow candidates...")
    candidates = classical_shadow_candidates(illum)
    candidates_vis = apply_colormap(candidates, cv2.COLORMAP_HOT)
    cv2.imwrite(
        str(output_path / "03_classical_candidates.png"),
        cv2.cvtColor((candidates_vis * 255).astype(np.uint8), cv2.COLOR_RGB2BGR),
    )

    # Overlay on original
    overlay_classical = create_overlay(rgb, candidates, color=(0, 1, 1), alpha=0.4)
    cv2.imwrite(
        str(output_path / "03_classical_overlay.png"),
        cv2.cvtColor((overlay_classical * 255).astype(np.uint8), cv2.COLOR_RGB2BGR),
    )

    # Stage 04: ML Shadow Detection
    print("[Stage 04] Running ML shadow detection...")
    ml_shadow = run_shadow_model(rgb)
    ml_vis = apply_colormap(ml_shadow, cv2.COLORMAP_MAGMA)
    cv2.imwrite(
        str(output_path / "04_ml_shadow.png"),
        cv2.cvtColor((ml_vis * 255).astype(np.uint8), cv2.COLOR_RGB2BGR),
    )

    # Overlay on original
    overlay_ml = create_overlay(rgb, ml_shadow, color=(1, 0, 1), alpha=0.4)
    cv2.imwrite(
        str(output_path / "04_ml_overlay.png"),
        cv2.cvtColor((overlay_ml * 255).astype(np.uint8), cv2.COLOR_RGB2BGR),
    )

    # Stage 06: Depth Estimation
    print("[Stage 06] Estimating depth...")
    depth = run_midas_depth(rgb)
    depth_vis = apply_colormap(depth, cv2.COLORMAP_PLASMA)
    cv2.imwrite(
        str(output_path / "06_depth.png"),
        cv2.cvtColor((depth_vis * 255).astype(np.uint8), cv2.COLOR_RGB2BGR),
    )

    # Normals
    print("[Stage 06] Computing surface normals...")
    normals, normals_vis = depth_to_normals(depth)
    cv2.imwrite(
        str(output_path / "06_normals.png"),
        cv2.cvtColor((normals_vis * 255).astype(np.uint8), cv2.COLOR_RGB2BGR),
    )

    # Combined comparison grid
    print("\nCreating comparison grid...")

    # Create 2x3 grid
    grid_h, grid_w = h, w
    grid = np.zeros((grid_h * 2, grid_w * 3, 3), dtype=np.float32)

    # Row 1: Input, Illumination, Classical
    grid[0:grid_h, 0:grid_w] = rgb
    grid[0:grid_h, grid_w : grid_w * 2] = illum_vis
    grid[0:grid_h, grid_w * 2 : grid_w * 3] = candidates_vis

    # Row 2: ML Shadow, Depth, Normals
    grid[grid_h : grid_h * 2, 0:grid_w] = ml_vis
    grid[grid_h : grid_h * 2, grid_w : grid_w * 2] = depth_vis
    grid[grid_h : grid_h * 2, grid_w * 2 : grid_w * 3] = normals_vis

    cv2.imwrite(
        str(output_path / "00_comparison_grid.png"),
        cv2.cvtColor((grid * 255).astype(np.uint8), cv2.COLOR_RGB2BGR),
    )

    print(f"\n{'=' * 50}")
    print(f"Output saved to: {output_path.absolute()}")
    print(f"{'=' * 50}")
    print("Files generated:")
    print("  00_comparison_grid.png  - Side-by-side comparison")
    print("  01_input.png            - Original input image")
    print("  02_illumination.png     - Stage 02: Brightness map")
    print("  02_illumination_gray.png- Stage 02: Grayscale version")
    print("  03_classical_candidates.png - Stage 03: Classical detection")
    print("  03_classical_overlay.png    - Stage 03: Overlay on input")
    print("  04_ml_shadow.png        - Stage 04: ML shadow probability")
    print("  04_ml_overlay.png       - Stage 04: Overlay on input")
    print("  06_depth.png            - Stage 06: Depth map")
    print("  06_normals.png          - Stage 06: Surface normals")


if __name__ == "__main__":
    image_path = sys.argv[1] if len(sys.argv) > 1 else None
    run_demo(image_path)
