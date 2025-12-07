#!/usr/bin/env python3
"""
Batch reprocess Midjourney images with upgraded shadow pipeline models.

Processes all images with:
1. OLD PIPELINE: Placeholder models (for comparison)
2. NEW PIPELINE: Upgraded models (BDRAR, ZoeDepth, IntrinsicNet, Omnidata)

Generates comparison outputs showing improvements.

Usage:
    python scripts/batch_reprocess_shadows.py \
        --input-dir /path/to/images \
        --output-dir /path/to/results \
        --device cuda \
        --skip-old  # Optional: only process with new models
"""

import argparse
import json
import logging
import time
from pathlib import Path
from typing import Optional

import cv2
import numpy as np

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


class BatchShadowProcessor:
    """Process multiple images with shadow pipeline (old vs new models)."""

    def __init__(
        self,
        input_dir: Path,
        output_dir: Path,
        device: str = "cpu",
        skip_old: bool = False,
        skip_new: bool = False,
    ):
        """
        Initialize batch processor.

        Args:
            input_dir: Directory containing source images
            output_dir: Where to save results
            device: "cuda" or "cpu"
            skip_old: Skip processing with old (placeholder) models
            skip_new: Skip processing with new (upgraded) models
        """
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.device = device
        self.skip_old = skip_old
        self.skip_new = skip_new

        # Create output structure
        self.output_old = self.output_dir / "old_pipeline"
        self.output_new = self.output_dir / "new_pipeline"
        self.output_comparison = self.output_dir / "comparison"

        self.output_old.mkdir(parents=True, exist_ok=True)
        self.output_new.mkdir(parents=True, exist_ok=True)
        self.output_comparison.mkdir(parents=True, exist_ok=True)

        # Model cache for efficient reuse
        self.upgraded_models = None

        logger.info(f"Initialized batch processor")
        logger.info(f"  Input: {self.input_dir}")
        logger.info(f"  Output: {self.output_dir}")
        logger.info(f"  Device: {device}")

    def process_all(self) -> dict:
        """
        Process all images in input directory.

        Returns:
            Summary statistics
        """
        image_files = self._find_images()
        logger.info(f"Found {len(image_files)} images")

        if not image_files:
            logger.warning("No images found!")
            return {"error": "No images found"}

        results = {
            "total_images": len(image_files),
            "processed_old": 0,
            "processed_new": 0,
            "failed": 0,
            "timings": {},
            "output_paths": {
                "old": str(self.output_old),
                "new": str(self.output_new),
                "comparison": str(self.output_comparison),
            },
        }

        for i, image_path in enumerate(image_files, 1):
            logger.info(f"\n[{i}/{len(image_files)}] Processing: {image_path.name}")

            try:
                timings = self.process_image(image_path)
                results["timings"][image_path.name] = timings

                if not self.skip_old:
                    results["processed_old"] += 1
                if not self.skip_new:
                    results["processed_new"] += 1

            except Exception as e:
                logger.error(f"Failed to process {image_path.name}: {e}")
                results["failed"] += 1

        # Save summary
        summary_path = self.output_dir / "batch_summary.json"
        with open(summary_path, "w") as f:
            json.dump(results, f, indent=2)
        logger.info(f"\nSummary saved to: {summary_path}")

        return results

    def process_image(self, image_path: Path) -> dict:
        """
        Process single image with both pipelines.

        Returns:
            Timing information
        """
        timings = {}

        # Process with OLD pipeline (placeholders)
        if not self.skip_old:
            logger.info("  -> OLD pipeline (placeholder models)...")
            start = time.time()
            try:
                self._process_with_old_pipeline(image_path)
                timings["old_ms"] = 1000 * (time.time() - start)
                logger.info(f"     Old pipeline: {timings['old_ms']:.0f}ms")
            except Exception as e:
                logger.error(f"     Old pipeline failed: {e}")

        # Process with NEW pipeline (upgraded models)
        if not self.skip_new:
            logger.info("  -> NEW pipeline (upgraded models)...")
            start = time.time()
            try:
                self._process_with_new_pipeline(image_path)
                timings["new_ms"] = 1000 * (time.time() - start)
                logger.info(f"     New pipeline: {timings['new_ms']:.0f}ms")
            except Exception as e:
                logger.error(f"     New pipeline failed: {e}")

        # Generate comparison
        logger.info("  -> Generating comparison...")
        try:
            self._generate_comparison(image_path)
        except Exception as e:
            logger.error(f"     Comparison failed: {e}")

        return timings

    def _process_with_old_pipeline(self, image_path: Path) -> None:
        """Process image with old (placeholder) models."""
        from copy_that.shadowlab import ShadowPipelineOrchestrator

        output_subdir = self.output_old / image_path.stem
        output_subdir.mkdir(parents=True, exist_ok=True)

        orchestrator = ShadowPipelineOrchestrator(
            image_path=str(image_path),
            output_dir=output_subdir,
            verbose=False,
        )

        results = orchestrator.run()

        # Save results
        results_file = output_subdir / "shadow_results.json"
        with open(results_file, "w") as f:
            # Convert numpy arrays and other non-serializable types
            json.dump(self._serialize_results(results), f, indent=2)

        logger.debug(f"     Saved to: {output_subdir}")

    def _process_with_new_pipeline(self, image_path: Path) -> None:
        """Process image with new (upgraded) models."""
        from copy_that.shadowlab import ShadowPipelineOrchestrator
        from copy_that.shadowlab.pipeline import (
            estimate_normals_upgraded,
            run_intrinsic_upgraded,
            run_midas_depth_upgraded,
            run_shadow_model_upgraded,
        )
        from copy_that.shadowlab.upgraded_models import get_upgraded_models

        output_subdir = self.output_new / image_path.stem
        output_subdir.mkdir(parents=True, exist_ok=True)

        # Load upgraded models once
        if self.upgraded_models is None:
            logger.info("     Loading upgraded models (this may take a moment)...")
            self.upgraded_models = get_upgraded_models(device=self.device)

        # Load image
        from copy_that.shadowlab import load_rgb

        rgb_image = load_rgb(str(image_path))

        # Run upgraded models
        logger.debug("     Running BDRAR shadow detection...")
        shadow_mask = run_shadow_model_upgraded(
            rgb_image, device=self.device, use_cached_model=self.upgraded_models
        )

        logger.debug("     Running ZoeDepth depth estimation...")
        depth = run_midas_depth_upgraded(
            rgb_image, device=self.device, use_cached_model=self.upgraded_models
        )

        logger.debug("     Running IntrinsicNet decomposition...")
        reflectance, shading = run_intrinsic_upgraded(
            rgb_image, device=self.device, use_cached_model=self.upgraded_models
        )

        logger.debug("     Running Omnidata normal estimation...")
        normals = estimate_normals_upgraded(
            rgb_image, device=self.device, use_cached_model=self.upgraded_models
        )

        # Save visualizations
        self._save_upgraded_outputs(
            output_subdir, rgb_image, shadow_mask, depth, reflectance, shading, normals
        )

        logger.debug(f"     Saved to: {output_subdir}")

    def _save_upgraded_outputs(
        self,
        output_dir: Path,
        rgb_image: np.ndarray,
        shadow_mask: np.ndarray,
        depth: np.ndarray,
        reflectance: np.ndarray,
        shading: np.ndarray,
        normals: np.ndarray,
    ) -> None:
        """Save upgraded model outputs as visualizations."""
        # Shadow mask heatmap
        shadow_vis = cv2.applyColorMap(
            (shadow_mask * 255).astype(np.uint8), cv2.COLORMAP_JET
        )
        cv2.imwrite(str(output_dir / "shadow_mask_bdrar.png"), shadow_vis)

        # Depth map heatmap
        depth_vis = cv2.applyColorMap(
            (depth * 255).astype(np.uint8), cv2.COLORMAP_VIRIDIS
        )
        cv2.imwrite(str(output_dir / "depth_zoedepth.png"), depth_vis)

        # Reflectance
        reflectance_bgr = (reflectance[:, :, [2, 1, 0]] * 255).astype(np.uint8)
        cv2.imwrite(str(output_dir / "reflectance_intrinsicnet.png"), reflectance_bgr)

        # Shading
        shading_vis = cv2.applyColorMap(
            (shading * 255).astype(np.uint8), cv2.COLORMAP_GRAY
        )
        cv2.imwrite(str(output_dir / "shading_intrinsicnet.png"), shading_vis)

        # Normals (convert from [-1, 1] to RGB)
        normals_vis = ((normals + 1) / 2 * 255).astype(np.uint8)
        normals_vis_bgr = cv2.cvtColor(normals_vis, cv2.COLOR_RGB2BGR)
        cv2.imwrite(str(output_dir / "normals_omnidata.png"), normals_vis_bgr)

        # Save metadata
        metadata = {
            "models": {
                "shadow": "BDRAR",
                "depth": "ZoeDepth",
                "intrinsic": "IntrinsicNet",
                "normals": "Omnidata",
            },
            "shapes": {
                "shadow_mask": shadow_mask.shape,
                "depth": depth.shape,
                "reflectance": reflectance.shape,
                "shading": shading.shape,
                "normals": normals.shape,
            },
        }

        with open(output_dir / "metadata.json", "w") as f:
            json.dump(metadata, f, indent=2)

    def _generate_comparison(self, image_path: Path) -> None:
        """Generate side-by-side comparison visualizations."""
        comparison_dir = self.output_comparison / image_path.stem
        comparison_dir.mkdir(parents=True, exist_ok=True)

        # Create a comparison summary image
        # This is a placeholder - in reality, you'd create multi-panel visualizations
        summary_file = comparison_dir / "comparison_summary.txt"
        with open(summary_file, "w") as f:
            f.write(f"Comparison for: {image_path.name}\n")
            f.write(f"\nOld results location: {self.output_old / image_path.stem}\n")
            f.write(f"New results location: {self.output_new / image_path.stem}\n")

    def _find_images(self) -> list[Path]:
        """Find all image files in input directory."""
        extensions = {".jpg", ".jpeg", ".png", ".tiff", ".bmp"}
        images = [
            p
            for p in self.input_dir.rglob("*")
            if p.suffix.lower() in extensions and p.is_file()
        ]
        return sorted(images)

    def _serialize_results(self, obj) -> dict:
        """Convert non-serializable types in results for JSON."""
        if isinstance(obj, dict):
            return {k: self._serialize_results(v) for k, v in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return [self._serialize_results(v) for v in obj]
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, (np.integer, np.floating)):
            return float(obj)
        elif isinstance(obj, Path):
            return str(obj)
        else:
            return obj


def main():
    """CLI entrypoint."""
    parser = argparse.ArgumentParser(
        description="Batch reprocess images with upgraded shadow pipeline"
    )
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=Path("/home/user/copy-that/test_images"),
        help="Directory containing source images",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("/home/user/copy-that/test_images_results"),
        help="Output directory for results",
    )
    parser.add_argument(
        "--device",
        choices=["cuda", "cpu"],
        default="cpu",
        help="Compute device",
    )
    parser.add_argument(
        "--skip-old",
        action="store_true",
        help="Skip old pipeline processing",
    )
    parser.add_argument(
        "--skip-new",
        action="store_true",
        help="Skip new pipeline processing",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limit to N images (for testing)",
    )

    args = parser.parse_args()

    # Validate input directory
    if not args.input_dir.exists():
        logger.error(f"Input directory not found: {args.input_dir}")
        logger.info("Create test_images directory and add Midjourney images there.")
        return 1

    # Process
    processor = BatchShadowProcessor(
        input_dir=args.input_dir,
        output_dir=args.output_dir,
        device=args.device,
        skip_old=args.skip_old,
        skip_new=args.skip_new,
    )

    results = processor.process_all()

    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("BATCH PROCESSING COMPLETE")
    logger.info("=" * 60)
    logger.info(f"Total images: {results['total_images']}")
    logger.info(f"Processed with old pipeline: {results['processed_old']}")
    logger.info(f"Processed with new pipeline: {results['processed_new']}")
    logger.info(f"Failed: {results['failed']}")
    logger.info(f"Results saved to: {args.output_dir}")

    return 0


if __name__ == "__main__":
    exit(main())
