#!/usr/bin/env python3
"""
Enhanced Shadow Pipeline Processing Script

Processes all test images with upgraded models:
- ZoeDepth for depth estimation (instead of MiDaS)
- Omnidata for surface normals (instead of depth-derived)
- BDRAR for shadow detection (instead of BDRAR-style classical)
- IntrinsicNet for intrinsic decomposition (instead of MSR)

Outputs to: test_images/processedImageShadows_enhanced/
Also generates comparison images vs original processing.

Run: uv run python scripts/process_enhanced_shadows.py [--device cuda]
"""

import argparse
import sys
from pathlib import Path

import cv2
import numpy as np

# Add project to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from copy_that.shadowlab import (
    # New enhanced models
    estimate_depth,
    estimate_normals,
    run_bdrar,
    decompose_intrinsic_intrinsicnet,
    # Original pipeline functions
    illumination_invariant_v,
    classical_shadow_candidates,
    run_shadow_model,
)


def apply_colormap(gray: np.ndarray, colormap: int = cv2.COLORMAP_VIRIDIS) -> np.ndarray:
    """Apply colormap to grayscale image for visualization."""
    gray_uint8 = (np.clip(gray, 0, 1) * 255).astype(np.uint8)
    colored = cv2.applyColorMap(gray_uint8, colormap)
    return cv2.cvtColor(colored, cv2.COLOR_BGR2RGB).astype(np.float32) / 255.0


def save_image(img: np.ndarray, path: Path, is_rgb: bool = True):
    """Save image, handling RGB/BGR conversion."""
    img_uint8 = (np.clip(img, 0, 1) * 255).astype(np.uint8)
    if is_rgb and img.ndim == 3:
        img_uint8 = cv2.cvtColor(img_uint8, cv2.COLOR_RGB2BGR)
    cv2.imwrite(str(path), img_uint8)


def create_comparison_grid(images: list[np.ndarray], titles: list[str], cols: int = 3) -> np.ndarray:
    """Create a comparison grid of images with labels."""
    n = len(images)
    rows = (n + cols - 1) // cols

    # Ensure all images are same size (use first image size)
    h, w = images[0].shape[:2]

    # Resize all images to match
    resized = []
    for img in images:
        if img.ndim == 2:
            img = np.stack([img] * 3, axis=-1)
        if img.shape[:2] != (h, w):
            img = cv2.resize(img, (w, h))
        resized.append(img)

    # Create grid with padding for labels
    label_h = 30
    cell_h = h + label_h
    grid = np.ones((rows * cell_h, cols * w, 3), dtype=np.float32) * 0.2  # Dark background

    for i, (img, title) in enumerate(zip(resized, titles)):
        row = i // cols
        col = i % cols
        y = row * cell_h + label_h
        x = col * w
        grid[y:y+h, x:x+w] = img

        # Add title (simple approach - just lighter region)
        # In practice, you'd use PIL or cv2.putText

    return grid


def process_image_enhanced(
    image_path: Path,
    output_dir: Path,
    device: str = "cpu",
    generate_comparison: bool = True,
) -> dict:
    """
    Process a single image with enhanced models.

    Args:
        image_path: Path to input image
        output_dir: Directory for outputs
        device: Compute device ("cuda", "mps", "cpu")
        generate_comparison: Whether to generate comparison grid

    Returns:
        Dictionary with processing results
    """
    print(f"\n{'='*60}")
    print(f"Processing: {image_path.name}")
    print(f"{'='*60}")

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load image
    img_bgr = cv2.imread(str(image_path))
    if img_bgr is None:
        print(f"  ERROR: Could not load {image_path}")
        return {}

    rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB).astype(np.float32) / 255.0
    h, w = rgb.shape[:2]
    print(f"  Image size: {w}x{h}")

    results = {"image_path": str(image_path), "size": (w, h)}

    # Save original
    print("  [01] Saving original...")
    save_image(rgb, output_dir / "00_original.png")

    # Stage 02: Illumination (same as before)
    print("  [02] Computing illumination invariant...")
    illum = illumination_invariant_v(rgb)
    illum_vis = apply_colormap(illum, cv2.COLORMAP_INFERNO)
    save_image(illum_vis, output_dir / "02_illumination.png")

    # Stage 03: Classical (same as before)
    print("  [03] Computing classical shadow candidates...")
    classical = classical_shadow_candidates(illum)
    save_image(classical, output_dir / "03_classical.png", is_rgb=False)

    # Stage 04a: BDRAR Shadow Detection (NEW)
    print("  [04a] Running BDRAR shadow detection...")
    try:
        bdrar_shadow = run_bdrar(rgb, device=device)
        bdrar_vis = apply_colormap(bdrar_shadow, cv2.COLORMAP_MAGMA)
        save_image(bdrar_vis, output_dir / "04a_bdrar_shadow.png")
        results["bdrar_available"] = True
    except Exception as e:
        print(f"       BDRAR failed: {e}, using fallback")
        bdrar_shadow = run_shadow_model(rgb, high_quality=False)
        bdrar_vis = apply_colormap(bdrar_shadow, cv2.COLORMAP_MAGMA)
        save_image(bdrar_vis, output_dir / "04a_bdrar_shadow.png")
        results["bdrar_available"] = False

    # Stage 04b: Original ML Shadow (for comparison)
    print("  [04b] Running original ML shadow detection...")
    ml_shadow = run_shadow_model(rgb, high_quality=True)
    ml_vis = apply_colormap(ml_shadow, cv2.COLORMAP_MAGMA)
    save_image(ml_vis, output_dir / "04b_original_shadow.png")

    # Stage 05a: IntrinsicNet Decomposition (NEW)
    print("  [05] Running IntrinsicNet decomposition...")
    try:
        intrinsic = decompose_intrinsic_intrinsicnet(img_bgr, device=device)
        reflectance = intrinsic["reflectance"]
        shading = intrinsic["shading"]
        method = intrinsic.get("method", "unknown")
        print(f"       Method used: {method}")

        # Convert BGR reflectance to RGB for saving
        if reflectance.shape[-1] == 3:
            reflectance_rgb = cv2.cvtColor(
                (reflectance * 255).astype(np.uint8),
                cv2.COLOR_BGR2RGB
            ).astype(np.float32) / 255.0
        else:
            reflectance_rgb = reflectance

        save_image(reflectance_rgb, output_dir / "05a_reflectance.png")
        shading_vis = apply_colormap(shading, cv2.COLORMAP_VIRIDIS)
        save_image(shading_vis, output_dir / "05b_shading.png")
        results["intrinsic_method"] = method
    except Exception as e:
        print(f"       IntrinsicNet failed: {e}")
        results["intrinsic_method"] = "failed"

    # Stage 06a: ZoeDepth (NEW)
    print("  [06a] Running ZoeDepth estimation...")
    try:
        depth_zoe = estimate_depth(img_bgr, device=device, model_name="zoedepth")
        depth_zoe_vis = apply_colormap(depth_zoe, cv2.COLORMAP_PLASMA)
        save_image(depth_zoe_vis, output_dir / "06a_depth_zoedepth.png")
        results["zoedepth_available"] = True
    except Exception as e:
        print(f"       ZoeDepth failed: {e}, using fallback")
        depth_zoe = estimate_depth(img_bgr, device=device, model_name="midas")
        depth_zoe_vis = apply_colormap(depth_zoe, cv2.COLORMAP_PLASMA)
        save_image(depth_zoe_vis, output_dir / "06a_depth_zoedepth.png")
        results["zoedepth_available"] = False

    # Stage 06b: Omnidata Normals (NEW)
    print("  [06b] Running Omnidata normals estimation...")
    try:
        normals = estimate_normals(img_bgr, device=device, model_name="omnidata")
        # Normals visualization: map [-1,1] to [0,1]
        normals_vis = (normals + 1) / 2
        normals_vis = np.clip(normals_vis, 0, 1)
        save_image(normals_vis, output_dir / "06b_normals_omnidata.png")
        results["omnidata_available"] = True
    except Exception as e:
        print(f"       Omnidata failed: {e}, using depth-derived")
        # Fallback to depth-derived normals
        from copy_that.shadowlab.pipeline import depth_to_normals
        _, normals_vis = depth_to_normals(depth_zoe)
        save_image(normals_vis, output_dir / "06b_normals_omnidata.png")
        results["omnidata_available"] = False

    # Create comparison grid
    if generate_comparison:
        print("  [Grid] Creating comparison grid...")

        # Ensure all visualizations are 3-channel
        classical_vis = apply_colormap(classical, cv2.COLORMAP_HOT)

        grid_images = [
            rgb,
            illum_vis,
            classical_vis,
            bdrar_vis,
            shading_vis if 'shading' in dir() else np.zeros_like(rgb),
            depth_zoe_vis,
        ]

        # Create 2x3 grid manually
        grid_h, grid_w = h, w
        grid = np.zeros((grid_h * 2, grid_w * 3, 3), dtype=np.float32)

        # Row 1: Original, Illumination, Classical
        grid[0:grid_h, 0:grid_w] = rgb
        grid[0:grid_h, grid_w:grid_w*2] = illum_vis
        grid[0:grid_h, grid_w*2:grid_w*3] = classical_vis

        # Row 2: BDRAR Shadow, Shading, Depth
        grid[grid_h:grid_h*2, 0:grid_w] = bdrar_vis
        if 'shading_vis' in dir():
            grid[grid_h:grid_h*2, grid_w:grid_w*2] = shading_vis
        grid[grid_h:grid_h*2, grid_w*2:grid_w*3] = depth_zoe_vis

        save_image(grid, output_dir / "comparison_grid.png")

    # Create old vs new comparison if original exists
    old_dir = image_path.parent / "processedImageShadows" / image_path.stem
    if old_dir.exists() and generate_comparison:
        print("  [Comparison] Creating old vs new comparison...")
        create_old_vs_new_comparison(old_dir, output_dir, image_path.stem)

    print(f"  Done! Output saved to: {output_dir}")
    return results


def create_old_vs_new_comparison(old_dir: Path, new_dir: Path, image_name: str):
    """Create side-by-side comparison of old vs new processing."""

    # Key outputs to compare
    comparisons = [
        ("06_depth.png", "06a_depth_zoedepth.png", "depth"),
        ("05b_shading.png", "05b_shading.png", "shading"),
        ("04c_full_shadow_hq.png", "04a_bdrar_shadow.png", "shadow"),
    ]

    for old_name, new_name, label in comparisons:
        old_path = old_dir / old_name
        new_path = new_dir / new_name

        if not old_path.exists() or not new_path.exists():
            continue

        old_img = cv2.imread(str(old_path))
        new_img = cv2.imread(str(new_path))

        if old_img is None or new_img is None:
            continue

        # Resize to match
        h, w = old_img.shape[:2]
        new_img = cv2.resize(new_img, (w, h))

        # Create side-by-side
        comparison = np.hstack([old_img, new_img])

        cv2.imwrite(str(new_dir / f"compare_{label}_old_vs_new.png"), comparison)


def main():
    parser = argparse.ArgumentParser(description="Process images with enhanced shadow pipeline")
    parser.add_argument("--device", default="cpu", help="Compute device (cuda, mps, cpu)")
    parser.add_argument("--image", help="Process single image instead of all")
    parser.add_argument("--no-comparison", action="store_true", help="Skip comparison grid generation")
    args = parser.parse_args()

    # Paths
    test_images_dir = Path(__file__).parent.parent / "test_images"
    output_base = test_images_dir / "processedImageShadows_enhanced"

    # Get images to process
    if args.image:
        images = [Path(args.image)]
    else:
        # All Midjourney images
        images = sorted(test_images_dir.glob("IMG_*.jpeg"))

    print(f"\n{'='*60}")
    print("ENHANCED SHADOW PIPELINE PROCESSING")
    print(f"{'='*60}")
    print(f"Device: {args.device}")
    print(f"Output: {output_base}")
    print(f"Images: {len(images)}")
    print(f"{'='*60}")

    # Process each image
    all_results = []
    for image_path in images:
        output_dir = output_base / image_path.stem
        result = process_image_enhanced(
            image_path,
            output_dir,
            device=args.device,
            generate_comparison=not args.no_comparison,
        )
        all_results.append(result)

    # Summary
    print(f"\n{'='*60}")
    print("PROCESSING COMPLETE")
    print(f"{'='*60}")
    print(f"Total images processed: {len(all_results)}")
    print(f"Output directory: {output_base}")

    # Model availability summary
    bdrar_count = sum(1 for r in all_results if r.get("bdrar_available", False))
    zoedepth_count = sum(1 for r in all_results if r.get("zoedepth_available", False))
    omnidata_count = sum(1 for r in all_results if r.get("omnidata_available", False))

    print(f"\nModel availability:")
    print(f"  BDRAR: {bdrar_count}/{len(all_results)}")
    print(f"  ZoeDepth: {zoedepth_count}/{len(all_results)}")
    print(f"  Omnidata: {omnidata_count}/{len(all_results)}")


if __name__ == "__main__":
    main()
