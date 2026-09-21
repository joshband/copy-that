# Shadow pipeline — mapping

**Last Updated:** 2026-09-21

Short implementation map. Full historical narrative (stages, schemas, viz architecture) lives in the archive:

`~/Documents/copy-that-archive/shadow-history/SPEC.md`

---

## Live operators

| Need | Doc / path |
|------|------------|
| Run locally | [GETTING_STARTED.md](./GETTING_STARTED.md) |
| Regen visuals | [VISUAL_GUIDE.md](./VISUAL_GUIDE.md) |
| Code | `src/copy_that/shadowlab/` · API `POST /api/v1/shadows/extract` |

---

## Stage → code (current)

| Spec stage | Implementation |
|------------|----------------|
| Input / preprocess | OpenCV load/normalize in shadow extract path |
| Illumination / classical candidates | classical CV in shadowlab stages |
| ML shadow mask | `shadowlab/deep_shadow_detector.py` (BDRAR → SegFormer → classical) via `stage_04_ml_mask` / `stage_03_ml_shadow` |
| Intrinsic decomposition | IntrinsicNet/CGIntrinsics in `shadowlab/stages.py` + MSR fallback |
| Depth / normals | `shadowlab/depth_and_normals.py` (ZoeDepth/MiDaS/Omnidata; CPU gradients fallback) |
| Fusion → tokens | shadow extractor → W3C/CSS via design-tokens export |

Deep models are **optional**; classical path always works. `ENABLE_GPU=1` enables SegFormer/SAM/geometry when available.

---

## Out of scope here

Long Midjourney-oriented narrative, per-stage artifact schemas, and UI Process View storyboards → archive SPEC only.
