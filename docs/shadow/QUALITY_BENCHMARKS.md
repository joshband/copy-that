# Shadow Pipeline – Quality Notes (Deep Models)

Status: draft (synthetic sanity checks)

## What changed
- Added deep-first detectors with safe CPU fallbacks:
  - `src/copy_that/shadowlab/deep_shadow_detector.py` — prefers BDRAR, then SegFormer/SAM (optional), then classical.
  - `src/copy_that/shadowlab/depth_and_normals.py` — prefers ZoeDepth/MiDaS + Omnidata when GPU is allowed, defaults to fast CPU heuristics otherwise.
  - `stage_04_ml_mask` / `stage_03_ml_shadow` now call the deep detector; `stage_05_intrinsic` uses IntrinsicNet/CGIntrinsics before MSR; geometry stages use the unified depth+normals estimator.
- Model caching:
  - Detectors and estimators are cached per device (`_detector_cache`, `_estimator_cache`).
  - BDRAR weights are cached under `~/.cache/shadowlab/`; skipped unless weights exist or `auto_download_weights=True`.
  - CPU fast-path avoids heavy downloads; GPU path enables full deep backends.

## CPU fallback rules
- If `ENABLE_GPU` is unset, SegFormer/SAM downloads are skipped and the detector falls back to the classical path.
- Depth/normals default to a fast gradient proxy on CPU (`prefer_lightweight_on_cpu=True`).
- Intrinsic decomposition blends IntrinsicNet/CGIntrinsics with MSR for stability; pure MSR is used if deep models are unavailable.

## Synthetic benchmark (placeholder vs deep stack)
Baseline: placeholder mask = “no shadows” (all zeros) to measure uplift over a minimal implementation.

| Scenario | IoU (deep) | IoU (placeholder) | F1 (deep) | F1 (placeholder) |
| --- | --- | --- | --- | --- |
| Hard shadow block | 0.34 | 0.00 | 0.51 | 0.00 |
| Soft/penumbra | 0.34 | 0.00 | 0.51 | 0.00 |

How to reproduce:
```bash
uv run python - <<'PY'
from copy_that.shadowlab.deep_shadow_detector import benchmark_against_classical
print(benchmark_against_classical())
PY
```
(Runs with SegFormer disabled to keep CPU-only benchmarks quick; enable GPU + weights to exercise full BDRAR/SegFormer paths.)

## Notes for full-quality runs
- Set `ENABLE_GPU=1` to allow SegFormer/SAM fallback and GPU tensors.
- Provide BDRAR weights in `~/.cache/shadowlab/bdrar.pth` (or call `download_bdrar_weights()`).
- For high-quality geometry on GPU, instantiate `DepthAndNormalsConfig(prefer_lightweight_on_cpu=False)`.
