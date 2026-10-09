"""Classical shadow previews for uploads without ML, depth, or geometry execution."""

from __future__ import annotations

import json
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import cv2
import numpy as np
from PIL import Image

from copy_that.shadowlab.classical import detect_shadows_classical
from copy_that.shadowlab.pipeline import ShadowPipeline, ShadowStageResult
from copy_that.shadowlab.tokens import compute_shadow_features


class ClassicalUploadPipeline:
    """Produce shadowlab-compatible diagnostics from classical image evidence only."""

    def __init__(self, image_path: str, output_dir: Path, verbose: bool = False) -> None:
        self.image_path = image_path
        self.output_dir = output_dir

    def run(self) -> dict[str, Any]:
        started = time.monotonic()
        image_bgr = cv2.imread(self.image_path)
        if image_bgr is None:
            raise ValueError("Unable to decode shadow image")
        classical = detect_shadows_classical(image_bgr)
        soft = classical["shadow_soft"]
        mask = classical["shadow_mask"]
        features = compute_shadow_features(image_bgr, soft, mask)
        rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
        overlay = rgb.copy()
        overlay[mask > 127] = (
            overlay[mask > 127].astype(np.float32) * 0.5 + np.array([128, 0, 128])
        ).astype(np.uint8)
        images = {
            "candidate_mask": mask,
            "final_shadow_mask": soft,
            "shadow_overlay": overlay,
        }
        paths: dict[str, str] = {}
        artifacts_dir = self.output_dir / "artifacts"
        artifacts_dir.mkdir(parents=True, exist_ok=True)
        for name, data in images.items():
            pixels = (
                np.clip(data * 255, 0, 255).astype(np.uint8)
                if np.issubdtype(data.dtype, np.floating)
                else data.astype(np.uint8)
            )
            path = artifacts_dir / f"{name}.png"
            Image.fromarray(pixels).save(path)
            paths[name] = str(path)

        token_set = {
            "image_id": Path(self.image_path).stem,
            "timestamp": datetime.now(UTC).isoformat(),
            "shadow_tokens": {
                "coverage": features.shadow_area_fraction,
                "mean_strength": 1.0 - features.mean_shadow_intensity,
                "edge_softness_mean": features.edge_softness_mean,
                "edge_softness_std": features.edge_softness_std,
                "key_light_direction": None,
                "key_light_softness": None,
                "physics_consistency": None,
                "style_label": None,
                "style_embedding": None,
                "shadow_cluster_stats": [],
            },
        }
        pipeline = ShadowPipeline(self.output_dir)
        duration_ms = (time.monotonic() - started) * 1000
        pipeline.register_stage(
            ShadowStageResult(
                id="shadow_stage_classical_upload",
                name="Classical upload preview",
                description="Classical shadow cues without geometry or ML inference",
                inputs=["rgb_image"],
                outputs=list(images),
                metrics={"coverage": features.shadow_area_fraction},
                artifacts={name: name for name in images},
                duration_ms=duration_ms,
            ),
            [],
        )
        paths["pipeline_results"] = str(pipeline.save_results())
        tokens_path = self.output_dir / "shadow_tokens.json"
        tokens_path.write_text(json.dumps(token_set, indent=2), encoding="utf-8")
        paths["shadow_tokens"] = str(tokens_path)
        return {
            "pipeline_results": pipeline.get_results_summary(),
            "shadow_token_set": token_set,
            "total_duration_ms": duration_ms,
            "artifacts_paths": paths,
            "pipeline_mode": "classical_upload",
        }
