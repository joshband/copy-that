#!/usr/bin/env python3
"""
Enhanced Shadow Pipeline v2 Processing

Processes images with upgraded models:
- ZoeDepth for metric depth (replaces MiDaS)
- Omnidata for direct surface normals
- BDRAR for shadow detection
- IntrinsicNet for intrinsic decomposition

Creates 3-way comparison: Original → Previous → Enhanced

Output: test_images/processedImageShadows_v2/
"""

import argparse
import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from copy_that.shadowlab import (
    # Core pipeline
    illumination_invariant_v,
    classical_shadow_candidates,
    run_shadow_model,
    run_intrinsic,
    # Enhanced models
    estimate_depth,
    estimate_normals,
    run_bdrar,
)


def apply_colormap(gray: np.ndarray, colormap: int = cv2.COLORMAP_VIRIDIS) -> np.ndarray:
    """Apply colormap to grayscale image."""
    gray_uint8 = (np.clip(gray, 0, 1) * 255).astype(np.uint8)
    colored = cv2.applyColorMap(gray_uint8, colormap)
    return cv2.cvtColor(colored, cv2.COLOR_BGR2RGB).astype(np.float32) / 255.0


def save_image(img: np.ndarray, path: Path, is_rgb: bool = True):
    """Save image with proper color handling."""
    if img.dtype != np.uint8:
        img = (np.clip(img, 0, 1) * 255).astype(np.uint8)
    if is_rgb and img.ndim == 3 and img.shape[2] == 3:
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    cv2.imwrite(str(path), img)


def load_image(path: Path) -> tuple[np.ndarray, np.ndarray]:
    """Load image, return (rgb_float, bgr_uint8)."""
    bgr = cv2.imread(str(path))
    if bgr is None:
        raise ValueError(f"Could not load: {path}")
    rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB).astype(np.float32) / 255.0
    return rgb, bgr


def create_3way_comparison(
    original: np.ndarray,
    prev_path: Path,
    new_outputs: dict,
    output_path: Path,
):
    """
    Create 3-way comparison grid: Original → Previous → Enhanced.

    Shows key outputs side by side for visual comparison.
    """
    h, w = original.shape[:2]

    # Load previous outputs if they exist
    prev_shadow = None
    prev_depth = None
    prev_shading = None

    if prev_path.exists():
        for name, var in [
            ("04c_full_shadow_hq.png", "shadow"),
            ("06_depth.png", "depth"),
            ("05b_shading.png", "shading"),
        ]:
            p = prev_path / name
            if p.exists():
                img = cv2.imread(str(p))
                if img is not None:
                    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB).astype(np.float32) / 255.0
                    img = cv2.resize(img, (w, h))
                    if var == "shadow":
                        prev_shadow = img
                    elif var == "depth":
                        prev_depth = img
                    elif var == "shading":
                        prev_shading = img

    # Create comparison grid (3 rows x 4 cols)
    # Row 1: Original, Prev Shadow, New Shadow, Diff
    # Row 2: Prev Depth, New Depth, Prev Shading, New Shading
    # Row 3: Prev Normals, New Normals, Labels

    cell_h, cell_w = h, w
    grid = np.ones((cell_h * 2, cell_w * 4, 3), dtype=np.float32) * 0.1

    def place(img, row, col):
        if img is None:
            return
        if img.ndim == 2:
            img = np.stack([img] * 3, axis=-1)
        img = cv2.resize(img, (cell_w, cell_h))
        y = row * cell_h
        x = col * cell_w
        grid[y:y+cell_h, x:x+cell_w] = img

    # Row 0: Original, Prev Shadow, New Shadow, New BDRAR
    place(original, 0, 0)
    place(prev_shadow, 0, 1)
    place(new_outputs.get("shadow_vis"), 0, 2)
    place(new_outputs.get("bdrar_vis"), 0, 3)

    # Row 1: Prev Depth, New Depth, Prev Shading, New Shading
    place(prev_depth, 1, 0)
    place(new_outputs.get("depth_vis"), 1, 1)
    place(prev_shading, 1, 2)
    place(new_outputs.get("shading_vis"), 1, 3)

    save_image(grid, output_path)


def process_image_v2(
    image_path: Path,
    output_dir: Path,
    prev_dir: Path | None = None,
    device: str = "cpu",
) -> dict:
    """
    Process single image with enhanced v2 pipeline.
    """
    print(f"\n{'='*60}")
    print(f"Processing: {image_path.name}")
    print(f"{'='*60}")

    output_dir.mkdir(parents=True, exist_ok=True)

    # Load image
    rgb, bgr = load_image(image_path)
    h, w = rgb.shape[:2]
    print(f"  Size: {w}x{h}")

    outputs = {}

    # Save original
    save_image(rgb, output_dir / "00_original.png")

    # Stage 02: Illumination (same as before)
    print("  [02] Illumination invariant...")
    illum = illumination_invariant_v(rgb)
    illum_vis = apply_colormap(illum, cv2.COLORMAP_INFERNO)
    save_image(illum_vis, output_dir / "02_illumination.png")

    # Stage 03: Classical
    print("  [03] Classical shadow candidates...")
    classical = classical_shadow_candidates(illum)
    classical_vis = apply_colormap(classical, cv2.COLORMAP_HOT)
    save_image(classical_vis, output_dir / "03_classical.png")

    # Stage 04a: BDRAR Shadow (NEW)
    print("  [04a] BDRAR shadow detection...")
    try:
        bdrar_shadow = run_bdrar(rgb, device=device)
        bdrar_vis = apply_colormap(bdrar_shadow, cv2.COLORMAP_MAGMA)
        save_image(bdrar_vis, output_dir / "04a_bdrar.png")
        outputs["bdrar_vis"] = bdrar_vis
        print("       ✓ BDRAR OK")
    except Exception as e:
        print(f"       ✗ BDRAR failed: {e}")
        bdrar_shadow = None

    # Stage 04b: ML Shadow (comparison)
    print("  [04b] ML shadow detection...")
    ml_shadow = run_shadow_model(rgb)
    ml_vis = apply_colormap(ml_shadow, cv2.COLORMAP_MAGMA)
    save_image(ml_vis, output_dir / "04b_ml_shadow.png")
    outputs["shadow_vis"] = ml_vis

    # Stage 05: Intrinsic decomposition
    print("  [05] Intrinsic decomposition...")
    try:
        reflectance, shading = run_intrinsic(rgb)
        save_image(reflectance, output_dir / "05a_reflectance.png")
        shading_vis = apply_colormap(shading, cv2.COLORMAP_VIRIDIS)
        save_image(shading_vis, output_dir / "05b_shading.png")
        outputs["shading_vis"] = shading_vis
        print("       ✓ Intrinsic OK")
    except Exception as e:
        print(f"       ✗ Intrinsic failed: {e}")

    # Stage 06a: ZoeDepth (NEW)
    print("  [06a] ZoeDepth estimation...")
    try:
        depth = estimate_depth(bgr, device=device, model_name="zoedepth")
        depth_vis = apply_colormap(depth, cv2.COLORMAP_PLASMA)
        save_image(depth_vis, output_dir / "06a_depth_zoedepth.png")
        outputs["depth_vis"] = depth_vis
        print("       ✓ ZoeDepth OK")
    except Exception as e:
        print(f"       ✗ ZoeDepth failed: {e}, trying MiDaS...")
        try:
            depth = estimate_depth(bgr, device=device, model_name="midas")
            depth_vis = apply_colormap(depth, cv2.COLORMAP_PLASMA)
            save_image(depth_vis, output_dir / "06a_depth_midas.png")
            outputs["depth_vis"] = depth_vis
        except Exception as e2:
            print(f"       ✗ MiDaS also failed: {e2}")
            depth = None

    # Stage 06b: Omnidata Normals (NEW)
    print("  [06b] Omnidata normals...")
    try:
        normals = estimate_normals(bgr, device=device, model_name="omnidata")
        normals_vis = (normals + 1) / 2  # Map [-1,1] to [0,1]
        normals_vis = np.clip(normals_vis, 0, 1)
        save_image(normals_vis, output_dir / "06b_normals_omnidata.png")
        outputs["normals_vis"] = normals_vis
        print("       ✓ Omnidata OK")
    except Exception as e:
        print(f"       ✗ Omnidata failed: {e}, using depth-derived...")
        if depth is not None:
            from copy_that.shadowlab import depth_to_normals
            _, normals_vis = depth_to_normals(depth)
            save_image(normals_vis, output_dir / "06b_normals_derived.png")
            outputs["normals_vis"] = normals_vis

    # Create comparison grid
    print("  [Grid] Creating comparison grid...")
    grid_images = [
        rgb,
        illum_vis,
        classical_vis,
        outputs.get("bdrar_vis", ml_vis),
        outputs.get("shading_vis", np.zeros_like(rgb)),
        outputs.get("depth_vis", np.zeros_like(rgb)),
    ]

    # 2x3 grid
    grid = np.zeros((h * 2, w * 3, 3), dtype=np.float32)
    grid[0:h, 0:w] = rgb
    grid[0:h, w:w*2] = illum_vis
    grid[0:h, w*2:w*3] = classical_vis
    grid[h:h*2, 0:w] = outputs.get("bdrar_vis", ml_vis)
    grid[h:h*2, w:w*2] = outputs.get("shading_vis", np.zeros_like(rgb))
    grid[h:h*2, w*2:w*3] = outputs.get("depth_vis", np.zeros_like(rgb))
    save_image(grid, output_dir / "comparison_grid.png")

    # Create 3-way comparison if previous exists
    if prev_dir and prev_dir.exists():
        print("  [3-Way] Creating prev vs new comparison...")
        create_3way_comparison(rgb, prev_dir, outputs, output_dir / "comparison_prev_vs_new.png")

    print(f"  ✓ Done: {output_dir}")
    return outputs


def main():
    parser = argparse.ArgumentParser(description="Enhanced shadow pipeline v2")
    parser.add_argument("--device", default="cpu", help="cuda, mps, or cpu")
    parser.add_argument("--image", help="Process single image")
    parser.add_argument("--limit", type=int, help="Limit number of images")
    args = parser.parse_args()

    base = Path(__file__).parent.parent
    test_images = base / "test_images"
    output_base = test_images / "processedImageShadows_v2"
    prev_base = test_images / "processedImageShadows"

    # Get images
    if args.image:
        images = [Path(args.image)]
    else:
        images = sorted(test_images.glob("IMG_*.jpeg"))
        if args.limit:
            images = images[:args.limit]

    print(f"\n{'='*60}")
    print("SHADOW PIPELINE v2 - ENHANCED PROCESSING")
    print(f"{'='*60}")
    print(f"Device: {args.device}")
    print(f"Images: {len(images)}")
    print(f"Output: {output_base}")
    print(f"{'='*60}")

    for img_path in images:
        out_dir = output_base / img_path.stem
        prev_dir = prev_base / img_path.stem
        process_image_v2(img_path, out_dir, prev_dir, args.device)

    print(f"\n{'='*60}")
    print("PROCESSING COMPLETE")
    print(f"Output: {output_base}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
