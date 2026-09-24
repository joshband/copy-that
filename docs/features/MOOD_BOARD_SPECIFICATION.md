# Mood Board Generation (Mood tab)

**Last Updated:** 2026-09-22

## Status

- **Product:** First-class **Mood** AppShell tab (not Overview Labs). Opt-in generate; not on extract → Overview → export spine until the user opens Mood.
- **UI:** `featureFlags.showMoodBoard` defaults **`true`** — Mood appears in nav. Generation still requires an explicit Generate click. Kill switch: set `false` to hide the tab. Lighting flags remain off.
- **Composition (imagery on):** Per board visual stack — **Materials & finishes → UI elements → Source (upload preview) → Typography & grid**. Each AI slot is a design board, not a redraw of the photo. Themes-only keeps an optional material/typography themes focus.
- **Cost model:** Themes-first by default (fast). Imagery is opt-in (**2 variants × 3 AI images**). **Cloud Flux** (OpenAI-compatible via `MOOD_BOARD_FLUX_BASE_URL`) preferred for speed; DALL·E fallback; local mflux dogfood; **token collage** last resort. Policy router: `balanced` | `fast` | `cheap` | `private` | `quality`.
- **API:** `POST /api/v1/mood-board/generate` → **202** `{ job_id, status, queue, stream_url }`. Optional body: `policy`, `allow_cloud`, `max_latency_ms`, `image_slots` (`[{focus_type}]`). Default imagery plan from FE: `material`, `ui`, `typography` with `focus_type: "mixed"`. Poll `/api/v1/jobs/{job_id}` (or SSE `/stream`). Requires Celery. Health: `GET /api/v1/mood-board/health` (backends + recommended_policy).
- **Mood tab UI:** Cost banner + provider hint → optional routing when imagery on → Generate → job poll → variants with ordered slots + per-tile selection footnotes on AI images. The source photo is shown in the source slot, read into the design brief, and sent to Fal as a style reference for the material collage, component system, and type poster. Helpers: `frontend/src/api/moodBoard.ts`, `frontend/src/api/jobs.ts`.
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
3. API (`uvicorn` on `:8000`), Vite, LM Studio `:1234`, Fal Flux shim `:8766` (or mflux) when including imagery.
4. Extract a palette → open **Mood** tab → Generate themes (or check Include imagery). Prefer cloud image path for speed when keys are set; local mflux for dogfood.
5. To hide the Mood tab: set `showMoodBoard: false` in `frontend/src/config/featureFlags.ts`.

**Verified (2026-09-21):** API enqueue → Celery solo → LM Studio `google/gemma-2-9b` + mflux schnell (1 variant × 1 image, Midjourney palette) → `completed` in ~130s with `rendering_images` progress + `data:image/png;base64,…`. Prefer `google/gemma-2-9b` for theme JSON (`google/gemma-4-e4b` can stall on long structured prompts).

---

## Composition slots

| Order | Slot | Source |
|------|------|--------|
| 1 | Materials & finishes | AI design board (`focus_type: material`) |
| 2 | UI elements | AI design board (`focus_type: ui`) |
| 3 | Source | Session upload (`imageBase64`). Shown in the stack, and sent as a style reference (not an image-to-image copy) so the material collage, component system, and type poster keep its finish and palette |
| 4 | Typography & grid | AI design board (`focus_type: typography`) |

Generated images are stamped with `role` / `focus_type` so the FE can order the grid.

---

## Providers

| Concern | Preferred | Fallbacks |
|---------|-----------|-----------|
| Themes | Anthropic (`ANTHROPIC_API_KEY`) | OpenAI-compatible chat via `MOOD_BOARD_TEXT_BASE_URL` (LM Studio) |
| Images | **flux_fast** — `MOOD_BOARD_FLUX_BASE_URL` (Fal/Replicate OpenAI-compat) or non-local `MOOD_BOARD_IMAGE_BASE_URL` | **dalle** (`OPENAI_API_KEY`) → **local_mflux** (localhost IMAGE_BASE_URL) → **token_collage** (SVG, always) |

### Image routing policies

| Policy | Behavior |
|--------|----------|
| `balanced` (default) | Rank Q/S/C/A; prefer cloud Flux when available |
| `fast` | Latency-weighted |
| `cheap` | Cost-weighted; collage rises |
| `quality` | Quality-weighted |
| `private` | Never cloud; local → collage only |

Per-tile soft fail advances the chain; circuit breaker opens after consecutive failures. Each image carries `selection: { provider, policy, scores, fallback_from? }`. `models_used.routing_policy` records the run policy.

Env: `MOOD_BOARD_ROUTING_POLICY` (default `balanced`).

**Focus types:** themes-only `material` | `typography`; imagery composition uses `mixed` themes + per-slot `image_slots`.

### Cloud Flux (Mood tab speed path)

**Recommended (local Fal shim):** Fal’s native API is not OpenAI-shaped. Run the
in-repo shim so Copy That’s OpenAI `images.generate` client works:

```bash
# 1. Create a key at https://fal.ai/dashboard/keys
export FAL_KEY=…   # also put in .env (do not commit)

# 2. Start shim (port 8766 — mflux local shim uses 8765)
python scripts/mood_board_fal_openai_shim.py

# 3. .env for Copy That API / Celery:
MOOD_BOARD_FLUX_BASE_URL=http://127.0.0.1:8766/v1
MOOD_BOARD_FLUX_API_KEY=local
MOOD_BOARD_FLUX_MODEL=flux-schnell
MOOD_BOARD_ROUTING_POLICY=balanced
FAL_KEY=…          # required by the shim process
```

4. Restart API + `make celery-mood-board`. Confirm health lists `flux_fast`:

```bash
curl -s http://127.0.0.1:8000/api/v1/mood-board/health | jq '.backends'
# expect id "flux_fast", available true
```

5. Smoke the shim alone:

```bash
curl -s http://127.0.0.1:8766/health
curl -s http://127.0.0.1:8766/v1/images/generations \
  -H 'Content-Type: application/json' \
  -d '{"model":"flux-schnell","prompt":"brushed aluminum knob, soft light","n":1,"size":"512x512"}'
```

**Alternatives:** any OpenAI-compat `…/v1` that implements `images.generate`
(Together, LiteLLM→Fal, falProxy, Baseten, Vercel AI Gateway). Set
`MOOD_BOARD_FLUX_BASE_URL` to that host’s `/v1` and put the Bearer key in
`MOOD_BOARD_FLUX_API_KEY` (or `FAL_KEY` / `REPLICATE_API_TOKEN` as fallbacks).

Until `MOOD_BOARD_FLUX_BASE_URL` is set, health omits `flux_fast` and the
router uses DALL·E / local mflux / token collage. Local mflux remains dogfood
via localhost `MOOD_BOARD_IMAGE_BASE_URL` — not the product default.
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

Robotic check (no UI): `make mood-verify` → `tmp/mood_board_verify/report.json`.

Health: `GET /api/v1/mood-board/health`. Themes-only API: `"include_images": false`.  
Footnotes: A1111 shim `scripts/mood_board_a1111_openai_shim.py`; mock backend `MOOD_BOARD_LOCAL_IMAGE_BACKEND=mock`.

Env index: [ENVIRONMENT_VARIABLES.md](../configuration/ENVIRONMENT_VARIABLES.md) · [`.env.example`](../../.env.example).

---

## Request sketch

Themes-only:

```json
{
  "colors": [{ "hex": "#2171B5", "name": "Blue" }],
  "focus_type": "material",
  "num_variants": 2,
  "include_images": false,
  "num_images_per_variant": 1
}
```

Imagery composition:

```json
{
  "colors": [{ "hex": "#2171B5", "name": "Blue" }],
  "focus_type": "mixed",
  "num_variants": 2,
  "include_images": true,
  "num_images_per_variant": 3,
  "image_slots": [
    { "focus_type": "material" },
    { "focus_type": "material" },
    { "focus_type": "typography" }
  ]
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
| Mood tab UI | `frontend/src/components/overview-narrative/MoodBoard.tsx` |
| Tab mount | `frontend/src/features/explorer/TokenExplorer.tsx` (`mood`) |
| FE job poll | `frontend/src/api/jobs.ts` + `frontend/src/api/moodBoard.ts` |

Cloud image path preferred for speed; local mflux for dogfood. Full multi-provider router is out of scope — health endpoint + env defaults are enough for the Mood tab.
