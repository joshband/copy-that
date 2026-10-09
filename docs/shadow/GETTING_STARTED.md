# Shadow Extraction - Quick Start

**Last Updated:** 2026-10-09

Run classical shadow extraction in the UI/API. Deep pipeline experiments are a
separate local workflow and require the `cv-deep` extra.

## What you get

- Shadow tokens via `/api/v1/shadows/extract`
- Classical masks/overlay and diagnostic metadata on upload; no depth, geometry, or ML previews
- Optional lighting analysis via `POST /api/v1/lighting/analyze` (opt-in Lighting tab / Overview card; flags in [`featureFlags.ts`](../../frontend/src/config/featureFlags.ts))

## Processed outputs are local-only

Directories such as `test_images/processedImageShadows/`, `processedImageShadows_v2/`, and `processedImageShadows_enhanced/` are **gitignored**. Regenerate:

```bash
# Method comparison → test_images/processedImageShadows/{image}/
uv run python scripts/test_shadow_methods.py

# Full pipeline with tokens → test_images_output/
uv run python scripts/process_test_images.py
# or: uv run python scripts/process_test_images.py test_images/IMG_8405.jpeg
```

See also [test_images/README.md](../../test_images/README.md) and [VISUAL_GUIDE.md](./VISUAL_GUIDE.md).

## 1) Prereqs

- Python env + deps (`make install` / uv)
- Frontend: `pnpm install`
- Fixture: `test_images/IMG_8405.jpeg`

## 2) Separate deep experiments (optional)

Install `uv sync --frozen --extra dev --extra cv-deep` before using the full
shadowlab scripts above. These scripts are not the upload pipeline.

### Weights (BDRAR)

Deep detector looks for `~/.cache/shadowlab/bdrar.pth`.

```bash
mkdir -p ~/.cache/shadowlab
ln -sf /path/to/BDRAR/ckpt/BDRAR/3000.pth ~/.cache/shadowlab/bdrar.pth
```

Or: `python -c "from copy_that.shadowlab.bdrar import download_bdrar_weights; print(download_bdrar_weights())"`

## 3) Run backend + frontend

```bash
# Terminal 1
PYTHONPATH=src .venv/bin/python -m uvicorn src.copy_that.interfaces.api.main:app --reload --port 8000

# Terminal 2
pnpm dev  # http://localhost:5173
```

Upload extraction always uses the classical path. Installing deep dependencies or
configuring GPU support must not turn upload into a geometry/ML request. Lighting
requests geometry explicitly; hardware/profile behavior is documented in
[geometry gates](../planning/P4_GEOMETRY_GATES.md).

## 4) UI / API

1. Open `http://localhost:5173`, upload `test_images/IMG_8405.jpeg`
2. Inspect Shadows tab / network `POST /api/v1/shadows/extract`

```bash
IMAGE_PATH="test_images/IMG_8405.jpeg"
BASE64=$(base64 -i "$IMAGE_PATH" | tr -d '\n')
curl -X POST http://localhost:8000/api/v1/shadows/extract \
  -H "Content-Type: application/json" \
  -d '{"image_base64":"'"$BASE64"'","image_media_type":"image/jpeg"}'
```

## Troubleshooting

- Upload requires no deep model weights or downloads.
- On-demand geometry without its optional dependencies reports unavailable.
- Corrupt `bdrar.pth` (HTML error page) → delete and re-download.

## References

- Spec: [SPEC.md](./SPEC.md)
- Visual guide: [VISUAL_GUIDE.md](./VISUAL_GUIDE.md)
- Architecture: [../architecture/CURRENT_ARCHITECTURE_STATE.md](../architecture/CURRENT_ARCHITECTURE_STATE.md)

Long-form implementation notes / quality benchmarks → `~/Documents/copy-that-archive/shadow-history/`.
