"""
Shadow Pipeline Orchestrator.

Coordinates all 8 stages, manages state, and produces final outputs.
"""

import time
from pathlib import Path
from typing import Any

import numpy as np

from .pipeline import ShadowPipeline, ShadowTokenSet
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


class ShadowPipelineOrchestrator:
    """
    Orchestrates the complete 8-stage shadow extraction pipeline.

    Manages:
    - Stage execution and state
    - Artifact passing between stages
    - Error handling and logging
    - Output serialization
    """

    def __init__(
        self,
        image_path: str,
        output_dir: Path | None = None,
        target_size: tuple | None = None,
        verbose: bool = True,
    ):
        """
        Initialize orchestrator.

        Args:
            image_path: Path to input image
            output_dir: Where to save outputs
            target_size: Optional (height, width) for resizing
            verbose: Enable logging
        """
        self.image_path = image_path
        self.output_dir = output_dir or Path("/tmp/shadow_pipeline")
        self.target_size = target_size
        self.verbose = verbose

        self.pipeline = ShadowPipeline(self.output_dir)
        self.execution_log: list[dict[str, Any]] = []
        self.start_time = time.time()

    def log(self, message: str) -> None:
        """Log message if verbose mode enabled."""
        if self.verbose:
            print(f"[ShadowPipeline] {message}")

    def run(self) -> dict[str, Any]:
        """
        Execute complete pipeline.

        Returns:
            Dictionary with all results:
            {
                'pipeline_results': {...},
                'shadow_token_set': {...},
                'execution_log': [...],
                'total_duration_ms': float,
                'artifacts_paths': {...}
            }
        """
        self.log("Starting shadow extraction pipeline...")

        artifacts = {}

        try:
            # ================================================================
            # STAGE 1: Input & Preprocessing
            # ================================================================
            self.log("Stage 1: Input & Preprocessing...")
            start = time.time()

            stage_result, visual_layers, stage_artifacts = stage_01_input(
                self.image_path, self.target_size
            )

            for layer in visual_layers:
                self.pipeline.visual_layers[layer.id] = layer

            artifacts.update(stage_artifacts)
            self.pipeline.register_stage(stage_result, visual_layers)
            self.log(f"  ✓ Completed in {time.time() - start:.2f}s")

            rgb_image = artifacts["rgb_image"]

            # ================================================================
            # STAGE 2: Illumination-Invariant View
            # ================================================================
            self.log("Stage 2: Illumination-Invariant View...")
            start = time.time()

            stage_result, visual_layers, stage_artifacts = stage_02_illumination(rgb_image)

            for layer in visual_layers:
                self.pipeline.visual_layers[layer.id] = layer

            artifacts.update(stage_artifacts)
            self.pipeline.register_stage(stage_result, visual_layers)
            self.log(f"  ✓ Completed in {time.time() - start:.2f}s")

            illumination_map = artifacts["illumination_map"]

            # ================================================================
            # STAGE 3: Classical Shadow Candidates
            # ================================================================
            self.log("Stage 3: Classical Shadow Candidates...")
            start = time.time()

            stage_result, visual_layers, stage_artifacts = stage_03_candidates(illumination_map)

            for layer in visual_layers:
                self.pipeline.visual_layers[layer.id] = layer

            artifacts.update(stage_artifacts)
            self.pipeline.register_stage(stage_result, visual_layers)
            self.log(f"  ✓ Completed in {time.time() - start:.2f}s")

            candidate_mask = artifacts["candidate_mask"]

            # ================================================================
            # STAGE 4: ML Shadow Mask
            # ================================================================
            self.log("Stage 4: ML Shadow Mask...")
            start = time.time()

            stage_result, visual_layers, stage_artifacts = stage_04_ml_mask(rgb_image)

            for layer in visual_layers:
                self.pipeline.visual_layers[layer.id] = layer

            artifacts.update(stage_artifacts)
            self.pipeline.register_stage(stage_result, visual_layers)
            self.log(f"  ✓ Completed in {time.time() - start:.2f}s")

            ml_shadow_mask = artifacts["ml_shadow_mask"]

            # ================================================================
            # STAGE 5: Intrinsic Image Decomposition
            # ================================================================
            self.log("Stage 5: Intrinsic Image Decomposition...")
            start = time.time()

            stage_result, visual_layers, stage_artifacts = stage_05_intrinsic(rgb_image)

            for layer in visual_layers:
                self.pipeline.visual_layers[layer.id] = layer

            artifacts.update(stage_artifacts)
            self.pipeline.register_stage(stage_result, visual_layers)
            self.log(f"  ✓ Completed in {time.time() - start:.2f}s")

            shading_map = artifacts["shading_map"]

            # ================================================================
            # STAGE 6: Depth & Surface Normals
            # ================================================================
            self.log("Stage 6: Depth & Surface Normals...")
            start = time.time()

            stage_result, visual_layers, stage_artifacts = stage_06_geometry(rgb_image)

            for layer in visual_layers:
                self.pipeline.visual_layers[layer.id] = layer

            artifacts.update(stage_artifacts)
            self.pipeline.register_stage(stage_result, visual_layers)
            self.log(f"  ✓ Completed in {time.time() - start:.2f}s")

            normal_map = artifacts["normal_map"]

            # ================================================================
            # STAGE 7: Lighting Fit & Consistency
            # ================================================================
            self.log("Stage 7: Lighting Fit & Consistency...")
            start = time.time()

            stage_result, visual_layers, stage_artifacts = stage_07_lighting(
                normal_map, shading_map
            )

            for layer in visual_layers:
                self.pipeline.visual_layers[layer.id] = layer

            artifacts.update(stage_artifacts)
            self.pipeline.register_stage(stage_result, visual_layers)
            self.log(f"  ✓ Completed in {time.time() - start:.2f}s")

            light_direction = artifacts["light_direction"]
            lighting_error_map = artifacts["lighting_error_map"]

            # ================================================================
            # STAGE 8: Fusion & Token Generation
            # ================================================================
            self.log("Stage 8: Fusion & Token Generation...")
            start = time.time()

            result = stage_08_tokens(
                candidate_mask=candidate_mask,
                ml_shadow_mask=ml_shadow_mask,
                shading_map=shading_map,
                light_direction=light_direction,
                lighting_error_map=lighting_error_map,
                rgb_image=rgb_image,
            )

            stage_result, visual_layers, stage_artifacts, shadow_tokens = result

            for layer in visual_layers:
                self.pipeline.visual_layers[layer.id] = layer

            artifacts.update(stage_artifacts)
            self.pipeline.register_stage(stage_result, visual_layers)
            self.log(f"  ✓ Completed in {time.time() - start:.2f}s")

            # ================================================================
            # Finalization
            # ================================================================
            total_duration = time.time() - self.start_time

            # Create ShadowTokenSet
            token_set = ShadowTokenSet(
                image_id=Path(self.image_path).stem, shadow_tokens=shadow_tokens
            )

            self.log(f"\n✅ Pipeline completed in {total_duration:.2f}s")
            self.log(f"   Shadow coverage: {shadow_tokens.coverage:.1%}")
            self.log(f"   Mean strength: {shadow_tokens.mean_strength:.1%}")
            self.log(f"   Physics consistency: {shadow_tokens.physics_consistency:.1%}")

            # Save artifacts to disk
            self.log("\nSaving artifacts...")
            artifacts_paths = {}

            # Save visual artifacts
            for name in [
                "rgb_image",
                "illumination_map",
                "candidate_mask",
                "ml_shadow_mask",
                "reflectance_map",
                "shading_map",
                "depth_map",
                "normal_map_rgb",
                "final_shadow_mask",
                "shadow_overlay",
            ]:
                if name in artifacts:
                    path = self._save_artifact_image(name, artifacts[name])
                    if path:
                        artifacts_paths[name] = str(path)

            # Save pipeline results
            pipeline_results_path = self.pipeline.save_results("pipeline_results.json")
            artifacts_paths["pipeline_results"] = str(pipeline_results_path)

            # Save token set
            token_set_path = self.output_dir / "shadow_tokens.json"
            with open(token_set_path, "w") as f:
                f.write(token_set.to_json())
            artifacts_paths["shadow_tokens"] = str(token_set_path)

            self.log(f"✓ Artifacts saved to {self.output_dir}")

            # Compile final result
            result = {
                "pipeline_results": self.pipeline.get_results_summary(),
                "shadow_token_set": token_set.to_dict(),
                "execution_log": self.execution_log,
                "total_duration_ms": total_duration * 1000,
                "artifacts_paths": artifacts_paths,
                "output_dir": str(self.output_dir),
            }

            return result

        except Exception as e:
            self.log(f"\n❌ Pipeline failed: {e}")
            raise

    def _save_artifact_image(self, name: str, data: np.ndarray) -> Path | None:
        """
        Save a numpy array as image file.

        Args:
            name: Artifact name
            data: Image data (H, W) or (H, W, 3)

        Returns:
            Path to saved file, or None on error
        """
        try:
            from PIL import Image

            output_dir = self.output_dir / "artifacts"
            output_dir.mkdir(parents=True, exist_ok=True)

            if data.dtype == np.float32 or data.dtype == np.float64:
                # Convert float [0, 1] to uint8 [0, 255]
                data_uint8 = np.clip(data * 255, 0, 255).astype(np.uint8)
            else:
                data_uint8 = data.astype(np.uint8)

            # Determine filename and format
            filename = output_dir / f"{name}.png"

            # Handle grayscale vs RGB
            if data_uint8.ndim == 2:
                # Grayscale
                Image.fromarray(data_uint8, mode="L").save(filename)
            elif data_uint8.ndim == 3 and data_uint8.shape[2] == 3:
                # RGB
                Image.fromarray(data_uint8, mode="RGB").save(filename)
            else:
                return None

            return filename

        except Exception as e:
            self.log(f"Warning: Failed to save artifact {name}: {e}")
            return None

    def get_summary(self) -> str:
        """Get human-readable summary of results."""
        results = self.pipeline.get_results_summary()

        lines = ["=" * 70, "SHADOW EXTRACTION PIPELINE - SUMMARY", "=" * 70, ""]

        # Stages
        lines.append("STAGES EXECUTED:")
        for stage in results["stages"]:
            lines.append(f"  ✓ {stage['name']} ({stage['duration_ms']:.0f}ms)")
            if stage["metrics"]:
                for metric_name, metric_value in list(stage["metrics"].items())[:2]:
                    lines.append(f"      {metric_name}: {metric_value:.3f}")

        lines.append("")
        lines.append(f"Total Pipeline Time: {results['total_duration_ms']:.0f}ms")
        lines.append("")
        lines.append(f"Visual Layers: {len(results['visual_layers'])}")
        lines.append(f"Artifacts Generated: {len(results['artifacts_list'])}")

        return "\n".join(lines)


def run_shadow_pipeline(
    image_path: str,
    output_dir: Path | None = None,
    target_size: tuple | None = None,
    verbose: bool = True,
) -> dict[str, Any]:
    """
    Convenience function to run complete shadow pipeline.

    Args:
        image_path: Path to input image
        output_dir: Where to save outputs
        target_size: Optional (height, width) for resizing
        verbose: Enable logging

    Returns:
        Pipeline results dictionary
    """
    orchestrator = ShadowPipelineOrchestrator(
        image_path=image_path, output_dir=output_dir, target_size=target_size, verbose=verbose
    )

    results = orchestrator.run()

    if verbose:
        print("\n" + orchestrator.get_summary())

    return results
