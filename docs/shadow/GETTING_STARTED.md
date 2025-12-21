# Shadow Extraction - Quick Start

This guide shows how to run the shadow pipeline locally, enable deep models (BDRAR + geometry), and verify results in the UI or API.

## What you get

- Shadow tokens via `/api/v1/shadows/extract`
- Deep pipeline metadata (BDRAR + geometry) via `extraction_metadata.shadowlab`
- Optional lighting analysis via `/api/v1/lighting/analyze`

## 1) Prereqs

- Python env set up and deps installed
- Frontend deps installed (`pnpm install`)
- A test image (try `test_images/IMG_8634.jpeg`)

## 2) Weights (BDRAR)

The deep shadow detector looks for weights at:

- `~/.cache/shadowlab/bdrar.pth`

If you already downloaded BDRAR weights, copy or symlink them:

```bash
mkdir -p ~/.cache/shadowlab
ln -sf /path/to/BDRAR/ckpt/BDRAR/3000.pth ~/.cache/shadowlab/bdrar.pth
```

Optional: you can also use the built-in helper:

```bash
python - <<'PY'
from copy_that.shadowlab.bdrar import download_bdrar_weights
print(download_bdrar_weights())
PY
```

## 3) Run backend + frontend (local)

Deep models are easiest to run outside Docker so they can access your local caches.

Terminal 1 (backend):

```bash
ENABLE_GPU=1 python -m uvicorn src.copy_that.interfaces.api.main:app --reload --port 8000
```

Terminal 2 (frontend):

```bash
pnpm dev  # http://localhost:5173
```

Notes:

- `ENABLE_GPU=1` enables SegFormer/SAM and deep geometry (ZoeDepth/Omnidata). BDRAR can still run on CPU if GPU is off.
- On Apple Silicon, MPS is used when available.

## 4) Use the UI (Chrome)

1. Open `http://localhost:5173`
2. Upload an image (try `test_images/IMG_8634.jpeg`)
3. After extraction, check the **ShadowLab (Deep Pipeline)** section in the Upload panel.

You should see backend strings like:

- Stage 4: `bdrar (cuda|mps|cpu)` or `segformer_*` or `classical_fallback`
- Stage 6: `depth=zoedepth|midas, normals=omnidata|depth_gradient`

If you want raw response details:

- Open Chrome DevTools → Network → `POST /api/v1/shadows/extract`
- Inspect `extraction_metadata.shadowlab.pipeline`

## 5) Use the API (curl)

```bash
curl -X POST http://localhost:8000/api/v1/shadows/extract \
  -H "Content-Type: application/json" \
  -d '{"image_url":"https://example.com/design.png"}'
```

Or with base64:

```bash
IMAGE_PATH="test_images/IMG_8634.jpeg"
BASE64=$(base64 -i "$IMAGE_PATH" | tr -d '\n')
curl -X POST http://localhost:8000/api/v1/shadows/extract \
  -H "Content-Type: application/json" \
  -d '{"image_base64":"'"$BASE64"'","image_media_type":"image/jpeg"}'
```

## 6) Optional: lighting analysis

If you want the higher-level lighting summary panel:

```bash
curl -X POST http://localhost:8000/api/v1/lighting/analyze \
  -H "Content-Type: application/json" \
  -d '{"image_url":"https://example.com/design.png","use_geometry":true,"device":"cuda"}'
```

## Troubleshooting

- If deep models fail to load, you will still get shadows via CV fallback.
- If downloads are slow, keep `ENABLE_GPU=0` and the pipeline will use CPU-safe fallbacks.
- If you see HTML files at `~/.cache/shadowlab/bdrar.pth`, delete and re-download.

## References

- Spec: `docs/shadow/SPEC.md`
- Implementation: `docs/shadow/IMPLEMENTATION.md`
- Pipeline visual guide: `docs/shadow/VISUAL_GUIDE.md`
