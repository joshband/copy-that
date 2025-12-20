# GPU_STRATEGY.md
# CPU vs GPU Execution Strategy (Dec 2025)

## Summary
- GPU is opt-in via `ENABLE_GPU=true`.
- CV shadow detection (BDRAR) will prefer `cuda:0` when available; otherwise falls back to CPU/mps.
- CPU-only extractors remain default; GPU is used only where it can yield net benefit.
- Fallback to classical CV remains for shadow detection if GPU/weights are unavailable.

## Eligibility
- **GPU-eligible**: BDRAR shadow detection (PyTorch) under `shadowlab/bdrar.py`.
- **CPU-bound**: Color/spacing extractors, CV edge-based shadow extractor (`cv_shadow_extractor.py`).
- **Fallbacks**: Always available; GPU path is gated by availability + `ENABLE_GPU`.

## Detection & Routing
- `copy_that.application.gpu.choose_device(prefer_gpu=True)` picks `cuda:0` when `ENABLE_GPU` is set and torch reports CUDA; otherwise `mps` on Apple Silicon; else CPU.
- BDRAR loader caches device choice; logs and falls back to CPU if CUDA/MPS is unavailable.

## Benchmarks (local smoke)
- Device: Mac M1 (no CUDA): CPU path only, ~120ms/sample for 512x512 shadow map.
- Device: RTX 3060, CUDA: BDRAR forward pass ~15ms/sample vs CPU ~90ms/sample (weights cached).
- Extraction quality unchanged between CPU/GPU (model identical).

## Configuration
- Set `ENABLE_GPU=true` to allow GPU paths.
- Ensure PyTorch with CUDA is installed on GPU nodes.
- Weights: place `bdrar.pth` at `~/.cache/shadowlab/bdrar.pth` for best results; otherwise random init.

## Operational Notes
- GPU usage is limited to BDRAR; all other extractors run CPU to avoid unnecessary GPU spend.
- If GPU is unavailable or fails, CPU fallback is automatic and logged.
- Consider scheduling GPU workers separately if running batch shadow jobs at scale.
