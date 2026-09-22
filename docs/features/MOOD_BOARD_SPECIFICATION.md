# Mood Board Generation (unparked P4 — Labs)

**Last Updated:** 2026-09-22

## Status

- **Product:** Unparked behind Overview **Labs** (collapsed by default). Not on the extract → tabs → export happy path.
- **UI:** `featureFlags.showMoodBoard` defaults **`true`** — Overview shows a Labs disclosure; generation still requires an explicit Generate click. Kill switch: set `false`. Lighting flags remain off.
- **Cost model:** Themes-first by default (fast). Imagery is opt-in (2 variants × 1 image). Cloud ~$0.10–0.20 when imagery + Anthropic/OpenAI; local LM Studio + mflux dogfood is free aside from compute.
- **API:** `POST /api/v1/mood-board/generate` → **202** `{ job_id, status, queue, stream_url }`. Poll `/api/v1/jobs/{job_id}` (or SSE `/stream`). Requires Celery. Health: `GET /api/v1/mood-board/health` (provider hints in Labs UI).
- **Overview UI:** Labs → cost banner + provider hint → Generate (themes or imagery) → job poll → variants (themes-only path when images empty / imagery off). Helpers: `frontend/src/api/moodBoard.ts`, `frontend/src/api/jobs.ts`.
- **Client wait:** Themes poll up to 10 min; imagery up to `MOOD_BOARD_POLL_MAX_WAIT_MS` (45 min). Progress shows job message + elapsed time; Cancel aborts the client poll (worker may still finish).
- **Worker limits:** `generate_mood_board_job` soft/hard time limits are 45/50 min for long local mflux runs.

### Local dogfood

1. Start infra: `docker compose up -d redis postgres` (Docker Desktop must be running).
2. Celery mood-board worker — on macOS prefer **solo** pool (prefork often SIGSEGVs with native deps):
   ```bash
   make celery-mood-board
   # equivalent:
   set -a && . ./.env && set +a
   PYTHONPATH=src .venv/bin/celery -A copy_that.infrastructure.celery.app worker \
     --loglevel=info -Q mood-board,celery --pool=solo
   ```
3. API (`uvicorn` on `:8000`), Vite, LM Studio `:1234`, mflux shim `:8765` (only if including imagery).
4. Overview → expand **Labs** → Generate themes (or check Include imagery). Prefer cloud image path for speed when keys are set; local mflux for dogfood.
5. To hide Labs entirely: set `showMoodBoard: false` in `frontend/src/config/featureFlags.ts`.

**Verified (2026-09-21):** API enqueue → Celery solo → LM Studio `google/gemma-2-9b` + mflux schnell (1 variant × 1 image, Midjourney palette) → `completed` in ~130s with `rendering_images` progress + `data:image/png;base64,…`. Prefer `google/gemma-2-9b` for theme JSON (`google/gemma-4-e4b` can stall on long structured prompts).

---

## Providers

| Concern | Cloud default | Local |
|---------|---------------|-------|
| Themes | Anthropic (`ANTHROPIC_API_KEY`) | OpenAI-compatible chat via `MOOD_BOARD_TEXT_BASE_URL` (LM Studio `:1234`) |
| Images | DALL·E 3 (`OPENAI_API_KEY`) | mflux shim `scripts/mood_board_local_image_server.py` via `MOOD_BOARD_IMAGE_BASE_URL` |

`models_used` in the job result records actual model ids; Labs UI surfaces them after a successful run.

**Focus types today:** `material` | `typography` (color/spatial future).

---

## Local stack runbook (Apple Silicon)

**Default image model:** Hub mirror `dhairyashil/FLUX.1-schnell-mflux-4bit` (Z-Image-Turbo is opt-in only; very large).

LM Studio model ids should match `GET http://127.0.0.1:1234/v1/models` (not Hub folder names):

```bash
# Themes — LM Studio Local Server :1234
MOOD_BOARD_TEXT_BASE_URL=http://127.0.0.1:1234/v1
MOOD_BOARD_TEXT_API_KEY=lm-studio
MOOD_BOARD_TEXT_MODEL=google/gemma-2-9b
# Avoid gemma-4-e4b for long theme JSON — it can stall; keep as optional experiment only.

# Images — mflux shim
MOOD_BOARD_LOCAL_IMAGE_MODEL=dhairyashil/FLUX.1-schnell-mflux-4bit
MOOD_BOARD_LOCAL_IMAGE_BASE_MODEL=schnell
MOOD_BOARD_LOCAL_IMAGE_QUANTIZE=4
MOOD_BOARD_LOCAL_IMAGE_STEPS=4
MOOD_BOARD_IMAGE_BASE_URL=http://127.0.0.1:8765/v1
MOOD_BOARD_IMAGE_API_KEY=local
MOOD_BOARD_IMAGE_MODEL=schnell
MOOD_BOARD_IMAGE_SIZE=1024x1024
```

```bash
huggingface-cli login   # or HF_TOKEN=…
uv run --with mflux --with pillow python scripts/mood_board_local_image_server.py
```

Smoke image server:

```bash
curl -s http://127.0.0.1:8765/v1/images/generations \
  -H 'Content-Type: application/json' \
  -d '{"model":"schnell","prompt":"brushed aluminum knob","n":1,"size":"512x512"}' \
  | python -c "import sys,json; d=json.load(sys.stdin); print('ok', len(d['data'][0]['b64_json']))"
```

**Refined pair smoke (Midjourney 4-up siblings):** `IMG_8324.jpeg` + `IMG_8325.jpeg` share one generation. Extract a joint palette → themes (LM Studio) → local images:

```bash
set -a && . ./.env && set +a
# LM Studio Local Server :1234 + image shim :8765 must be up
python scripts/mood_board_smoke_midjourney_pair.py
# themes only:
python scripts/mood_board_smoke_midjourney_pair.py --themes-only
```

Outputs: `tmp/mood_board_smoke_midjourney_pair/result.json` + PNGs.

Health: `GET /api/v1/mood-board/health`. Themes-only API: `"include_images": false`.  
Footnotes: A1111 shim `scripts/mood_board_a1111_openai_shim.py`; mock backend `MOOD_BOARD_LOCAL_IMAGE_BACKEND=mock`.

Env index: [ENVIRONMENT_VARIABLES.md](../configuration/ENVIRONMENT_VARIABLES.md) · [`.env.example`](../../.env.example).

---

## Request sketch

```json
{
  "colors": [{ "hex": "#2171B5", "name": "Blue" }],
  "focus_type": "material",
  "num_variants": 2,
  "include_images": false,
  "num_images_per_variant": 0
}
```

Empty `colors` → **422**. Missing Celery → **503**.

---

## Implementation pointers

| Piece | Location |
|-------|----------|
| API | `src/copy_that/interfaces/api/mood_board.py` |
| Jobs (poll/SSE) | `src/copy_that/interfaces/api/jobs.py` |
| Generator | `src/copy_that/services/mood_board_generator.py` |
| Celery worker | `make celery-mood-board` (solo pool) |
| Local image server | `scripts/mood_board_local_image_server.py` |
| Overview Labs | `frontend/src/components/overview-narrative/OverviewLabs.tsx` |
| Overview UI | `frontend/src/components/overview-narrative/MoodBoard.tsx` |
| FE job poll | `frontend/src/api/jobs.ts` + `frontend/src/api/moodBoard.ts` |

Cloud image path preferred for speed; local mflux for dogfood. Full multi-provider router is out of scope — health endpoint + env defaults are enough for Labs.
