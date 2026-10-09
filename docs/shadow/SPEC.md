# Shadow pipeline — mapping

**Last Updated:** 2026-10-09

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

## Upload path

`POST /api/v1/shadows/extract` delegates to `services/shadow_extraction_service.py`.
Its diagnostic previews use `extractors/shadow/upload_pipeline.py`: classical masks,
overlay, and token features only. Upload does not run ML, depth, or geometry stages
and does not emit their preview artifacts. Unknown light/physics measurements stay null.
Geometry remains a separate on-demand operation from Lighting.

## Full shadowlab stage → code (explicit experiments)

| Spec stage | Implementation |
|------------|----------------|
| Input / preprocess | OpenCV load/normalize in shadow extract path |
| Illumination / classical candidates | classical CV in shadowlab stages |
| ML shadow mask | `shadowlab/deep_shadow_detector.py` (BDRAR → SegFormer → classical) via `stage_04_ml_mask` / `stage_03_ml_shadow` |
| Intrinsic decomposition | IntrinsicNet/CGIntrinsics in `shadowlab/stages.py` + MSR fallback |
| Depth / normals | `shadowlab/depth_and_normals.py` (ZoeDepth/MiDaS/Omnidata; CPU gradients fallback) |
| Fusion → tokens | shadow extractor → W3C/CSS via design-tokens export |

Deep stages belong to explicit experiments and dedicated geometry operations, not
upload extraction. Their availability is controlled in code; setting an experimental
GPU flag must not enable them on the upload path.

---

## Out of scope here

Long Midjourney-oriented narrative, per-stage artifact schemas, and UI Process View storyboards → archive SPEC only.
