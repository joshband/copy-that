#!/usr/bin/env python3
"""
Test shadow detection methods on images.

Creates synthetic test images and processes them through different methods,
saving results to test_images/processedImageShadows/
"""

import sys
from pathlib import Path

import cv2
import numpy as np

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from copy_that.shadowlab.pipeline import (
    load_rgb,
    illumination_invariant_v,
    classical_shadow_candidates,
    run_shadow_model,
    run_intrinsic,
    run_midas_depth,
    _enhanced_classical_shadow,
    _multi_scale_shadow_features,
)


def create_synthetic_shadow_image(name: str = "synthetic_shadow") -> tuple[np.ndarray, Path]:
    """Create a synthetic image with clear shadow regions."""
    h, w = 256, 256
    img = np.ones((h, w, 3), dtype=np.float32) * 0.8  # Light background

    # Add a "floor" gradient
    for y in range(h):
        img[y, :, :] *= 0.7 + 0.3 * (y / h)

    # Add shadow region (bottom right quadrant, darker)
    img[h//2:, w//2:, :] *= 0.4

    # Add penumbra (soft edge)
    for i in range(20):
        alpha = i / 20.0
        img[h//2 - i:h//2 - i + 1, w//2:, :] *= (0.4 + 0.6 * (1 - alpha))
        img[h//2:, w//2 - i:w//2 - i + 1, :] *= (0.4 + 0.6 * (1 - alpha))

    # Add some color variation
    img[:, :, 0] *= 0.95  # Slightly less red
    img[:, :, 2] *= 1.05  # Slightly more blue in shadows

    img = np.clip(img, 0, 1)

    # Save to test_images
    output_path = Path(__file__).parent.parent / "test_images" / f"{name}.png"
    cv2.imwrite(str(output_path), (img[:, :, ::-1] * 255).astype(np.uint8))

    return img, output_path


def create_gradient_shadow_image(name: str = "gradient_shadow") -> tuple[np.ndarray, Path]:
    """Create image with soft gradient shadow."""
    h, w = 256, 256
    img = np.ones((h, w, 3), dtype=np.float32) * 0.85

    # Create radial gradient shadow from top-left light source
    for y in range(h):
        for x in range(w):
            dist = np.sqrt((x / w) ** 2 + (y / h) ** 2)
            shadow = 0.3 + 0.7 * (1 - min(dist, 1.0))
            img[y, x, :] *= shadow

    img = np.clip(img, 0, 1)

    output_path = Path(__file__).parent.parent / "test_images" / f"{name}.png"
    cv2.imwrite(str(output_path), (img[:, :, ::-1] * 255).astype(np.uint8))

    return img, output_path


def save_result(img: np.ndarray, name: str, output_dir: Path):
    """Save a result image."""
    if img.ndim == 2:
        # Grayscale
        cv2.imwrite(str(output_dir / f"{name}.png"), (img * 255).astype(np.uint8))
    else:
        # RGB
        cv2.imwrite(str(output_dir / f"{name}.png"), (img[:, :, ::-1] * 255).astype(np.uint8))


def process_image(rgb: np.ndarray, image_name: str, output_dir: Path):
    """Process an image through all shadow methods."""
    print(f"\n{'='*60}")
    print(f"Processing: {image_name}")
    print("=" * 60)

    # Create output subdirectory for this image
    img_output = output_dir / image_name
    img_output.mkdir(parents=True, exist_ok=True)

    # Save original
    save_result(rgb, "00_original", img_output)

    # Stage 02: Illumination invariant
    print("  [Stage 02] Illumination invariant...")
    illum = illumination_invariant_v(rgb)
    save_result(illum, "02_illumination", img_output)

    # Stage 03: Classical candidates
    print("  [Stage 03] Classical candidates...")
    classical = classical_shadow_candidates(illum)
    save_result(classical, "03_classical", img_output)

    # Stage 04a: BDRAR-style features (no SAM)
    print("  [Stage 04a] BDRAR-style multi-scale features...")
    bdrar_features = _multi_scale_shadow_features(rgb)
    save_result(bdrar_features, "04a_bdrar_features", img_output)

    # Stage 04b: Enhanced classical (BDRAR + refinement)
    print("  [Stage 04b] Enhanced classical (BDRAR-style)...")
    enhanced = _enhanced_classical_shadow(rgb)
    save_result(enhanced, "04b_enhanced_classical", img_output)

    # Stage 04c: Full shadow model (with SAM if available)
    print("  [Stage 04c] Full shadow model (high_quality=True)...")
    try:
        full_shadow = run_shadow_model(rgb, high_quality=True)
        save_result(full_shadow, "04c_full_shadow_hq", img_output)
    except Exception as e:
        print(f"    Warning: {e}")
        full_shadow = enhanced
        save_result(full_shadow, "04c_full_shadow_hq_fallback", img_output)

    # Stage 04d: Fast shadow model (no SAM)
    print("  [Stage 04d] Fast shadow model (high_quality=False)...")
    fast_shadow = run_shadow_model(rgb, high_quality=False)
    save_result(fast_shadow, "04d_fast_shadow", img_output)

    # Stage 05: Intrinsic decomposition
    print("  [Stage 05] Intrinsic decomposition (MSR)...")
    reflectance, shading = run_intrinsic(rgb)
    save_result(reflectance, "05a_reflectance", img_output)
    save_result(shading, "05b_shading", img_output)

    # Stage 06: Depth estimation
    print("  [Stage 06] Depth estimation (MiDaS)...")
    try:
        depth = run_midas_depth(rgb)
        save_result(depth, "06_depth", img_output)
    except Exception as e:
        print(f"    Warning: {e}")

    # Create comparison grid
    print("  Creating comparison grid...")
    create_comparison_grid(rgb, illum, classical, enhanced, full_shadow, shading, img_output)

    print(f"  Results saved to: {img_output}")


def create_comparison_grid(rgb, illum, classical, enhanced, full_shadow, shading, output_dir):
    """Create a 2x3 comparison grid."""
    h, w = rgb.shape[:2]

    # Resize all to same size and convert to RGB
    def to_rgb(img):
        if img.ndim == 2:
            return np.stack([img, img, img], axis=-1)
        return img

    grid = np.zeros((h * 2, w * 3, 3), dtype=np.float32)

    # Row 1: Original, Illumination, Classical
    grid[0:h, 0:w] = rgb
    grid[0:h, w:2*w] = to_rgb(illum)
    grid[0:h, 2*w:3*w] = to_rgb(classical)

    # Row 2: Enhanced, Full Shadow, Shading
    grid[h:2*h, 0:w] = to_rgb(enhanced)
    grid[h:2*h, w:2*w] = to_rgb(full_shadow)
    grid[h:2*h, 2*w:3*w] = to_rgb(shading)

    # Add labels
    grid_uint8 = (grid * 255).astype(np.uint8)
    labels = ["Original", "Illumination", "Classical", "Enhanced", "Full Shadow", "Shading"]
    positions = [(10, 20), (w + 10, 20), (2*w + 10, 20), (10, h + 20), (w + 10, h + 20), (2*w + 10, h + 20)]

    for label, pos in zip(labels, positions):
        cv2.putText(grid_uint8, label, pos, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

    cv2.imwrite(str(output_dir / "comparison_grid.png"), grid_uint8[:, :, ::-1])


def main():
    output_dir = Path(__file__).parent.parent / "test_images" / "processedImageShadows"
    output_dir.mkdir(parents=True, exist_ok=True)

    print("Shadow Pipeline Method Comparison")
    print("=" * 60)

    # Create synthetic test images
    print("\nCreating synthetic test images...")
    img1, path1 = create_synthetic_shadow_image("synthetic_hard_shadow")
    img2, path2 = create_gradient_shadow_image("synthetic_soft_shadow")

    # Process synthetic images
    process_image(img1, "synthetic_hard_shadow", output_dir)
    process_image(img2, "synthetic_soft_shadow", output_dir)

    # Process any user-provided images in test_images/
    test_images_dir = Path(__file__).parent.parent / "test_images"
    extensions = {".jpg", ".jpeg", ".png", ".webp"}
    user_images = [
        f for f in test_images_dir.iterdir()
        if f.suffix.lower() in extensions
        and f.stem not in ["synthetic_hard_shadow", "synthetic_soft_shadow"]
        and not f.name.startswith(".")
    ]

    for img_path in user_images:
        try:
            rgb = load_rgb(str(img_path))
            process_image(rgb, img_path.stem, output_dir)
        except Exception as e:
            print(f"Error processing {img_path}: {e}")

    print("\n" + "=" * 60)
    print("COMPLETE")
    print("=" * 60)
    print(f"Results saved to: {output_dir}")
    print("\nOutput structure:")
    print("  processedImageShadows/")
    print("  ├── {image_name}/")
    print("  │   ├── 00_original.png")
    print("  │   ├── 02_illumination.png")
    print("  │   ├── 03_classical.png")
    print("  │   ├── 04a_bdrar_features.png")
    print("  │   ├── 04b_enhanced_classical.png")
    print("  │   ├── 04c_full_shadow_hq.png")
    print("  │   ├── 04d_fast_shadow.png")
    print("  │   ├── 05a_reflectance.png")
    print("  │   ├── 05b_shading.png")
    print("  │   ├── 06_depth.png")
    print("  │   └── comparison_grid.png")


if __name__ == "__main__":
    main()
