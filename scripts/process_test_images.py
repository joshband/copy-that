#!/usr/bin/env python3
"""
Process test images through the shadow pipeline.

Usage:
    uv run python scripts/process_test_images.py                    # Process all in test_images/
    uv run python scripts/process_test_images.py path/to/image.jpg  # Process specific image
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from copy_that.shadowlab import run_shadow_pipeline


def process_image(image_path: Path, output_base: Path) -> dict:
    """Process a single image through the shadow pipeline."""
    output_dir = output_base / image_path.stem
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n{'=' * 60}")
    print(f"Processing: {image_path.name}")
    print(f"Output: {output_dir}")
    print("=" * 60)

    try:
        results = run_shadow_pipeline(
            image_path=str(image_path),
            output_dir=output_dir,
            verbose=True,
        )

        # Print summary
        tokens = results.get("shadow_token_set", {}).get("shadow_tokens", {})
        print("\n--- Shadow Tokens ---")
        print(f"  Coverage: {tokens.get('coverage', 0):.1%}")
        print(f"  Mean strength: {tokens.get('mean_strength', 0):.1%}")
        print(f"  Edge softness: {tokens.get('edge_softness_mean', 0):.2f}")

        light = tokens.get("key_light_direction", {})
        print(
            f"  Light direction: {light.get('azimuth_deg', 0):.0f}° az, {light.get('elevation_deg', 0):.0f}° el"
        )
        print(f"  Physics consistency: {tokens.get('physics_consistency', 0):.1%}")

        duration = results.get("total_duration_ms", 0)
        print(f"\n  Total time: {duration:.0f}ms")

        return results

    except Exception as e:
        print(f"ERROR: {e}")
        return {"error": str(e)}


def main():
    # Determine input
    if len(sys.argv) > 1:
        # Process specific image
        image_path = Path(sys.argv[1])
        if not image_path.exists():
            print(f"Error: {image_path} not found")
            sys.exit(1)
        images = [image_path]
    else:
        # Process all images in test_images/
        test_dir = Path(__file__).parent.parent / "test_images"
        extensions = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff", ".tif"}
        images = [f for f in test_dir.iterdir() if f.suffix.lower() in extensions]

        if not images:
            print(f"No images found in {test_dir}")
            print("Drop some images there and run again!")
            sys.exit(0)

    # Output directory
    output_base = Path(__file__).parent.parent / "test_images_output"
    output_base.mkdir(exist_ok=True)

    print(f"Found {len(images)} image(s) to process")
    print(f"Output directory: {output_base}")

    # Process each image
    results = {}
    for image_path in sorted(images):
        results[image_path.name] = process_image(image_path, output_base)

    # Summary
    print(f"\n{'=' * 60}")
    print("SUMMARY")
    print("=" * 60)
    for name, result in results.items():
        if "error" in result:
            print(f"  {name}: ERROR - {result['error']}")
        else:
            tokens = result.get("shadow_token_set", {}).get("shadow_tokens", {})
            coverage = tokens.get("coverage", 0)
            print(f"  {name}: {coverage:.1%} shadow coverage")

    print(f"\nResults saved to: {output_base}")


if __name__ == "__main__":
    main()
