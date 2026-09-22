# P4 Geometry — go / no-go gates

**Status:** G1–G5 met (G3/G5 held as policy); G2 unit-verified (2026-09-21); production nav stays **default-off**  
**Parent:** [MVP_EXPANSION_ROADMAP.md](./MVP_EXPANSION_ROADMAP.md)  
**Nav policy:** Keep `showLightingTab` / `showLightingAnalyzer` **`false`** on the production path. Mood board may be `showMoodBoard=true` only as Overview Labs (collapsed; see [MOOD_BOARD_SPECIFICATION.md](../features/MOOD_BOARD_SPECIFICATION.md)).

Geometry is the **first** parked P4 feature to promote (foundation for lighting). Mood board is Labs-unparked (themes-first, cost-aware). Lighting analyze consumes real geometry extract when `use_geometry=true`; lighting UI surfaces `geometry_used` / `geometry_meta` / depth+normals previews when flags are on locally.

---

## Exit criteria (all required)

| # | Gate | Pass when |
|---|------|-----------|
| G1 | **Consumer** | Shadow quality **or** lighting tab uses geometry extract output (depth/normals meta or overlays), not a stand-in |
| G2 | **MPS / CPU story** | Documented and verified: Apple Silicon MPS depth + depth-gradient normals; CUDA optional for Marigold; CPU profiles force CPU (`cpu_fast` / `cpu_accurate`) |
| G3 | **Default App nav OFF** | `featureFlags.showLightingTab` / `showLightingAnalyzer` remain `false`; mood board is Labs-only (not a nav tab); geometry stays API-only or behind an explicit future flag |
| G4 | **Cost / latency budget** | Product note accepted: first extract cold-loads Depth Anything weights; budget target ≤ ~5s warm CPU `cpu_fast` on a typical screenshot, ≤ ~2s warm MPS/CUDA when available; document failure mode (503 on missing deps) |
| G5 | **Non-goals respected** | No lighting default-on; no full multimodal; no merge of draft PR #168 extras. Mood board Labs unpark is separate (cost-aware, not nav). |

**Go:** G1–G5 met → lighting/geometry may be exercised behind flags; still prefer default-off in production.  
**No-go:** Any gate missing → keep geometry mounted for API/tests only; do not feature in README happy path or default App nav.

### Gate progress (2026-09-21)

| Gate | Status | Notes |
|------|--------|-------|
| G1 | **Pass** | API: `POST /lighting/analyze` → shared `extract_depth_and_normals`; response includes `geometry_used`, `geometry_meta`, optional `geometry_images` (`depth_png` / `normals_png`). UI: `LightingGeometryEvidence` in `LightingAnalyzer` when `showLightingAnalyzer` is true (defaults stay false). |
| G2 | **Pass (unit-verified)** | Profile resolve covered for CPU force, AUTO→CPU, AUTO/MPS→`gpu_full` + `gpu_non_cuda_depth_only`, CUDA AUTO→`gpu_full`, `gpu_full` without accelerator → `cpu_fast`. Live warm MPS timing remains optional (see § below). |
| G3 | **Pass (held)** | Defaults remain `false` by production flag policy (below) |
| G4 | **Pass (accepted)** | Product acceptance recorded below; geometry `503` on missing deps covered by unit test; geometry stays **off** upload happy path |
| G5 | **Pass (held)** | Mood board / #168 / multimodal not promoted |

---

## Explicit non-goals (this slice)

- Mood board / DALL·E / Celery promotion
- Full multimodal platform
- Enabling default App lighting/geometry tabs
- Merging draft PR #168
- Replacing the four-token MVP spine
- Putting geometry/lighting on the upload → four-extractor happy path

---

## Current API surface (parked, mounted)

### Geometry

Router: `src/copy_that/interfaces/api/geometry.py`  
Mounted in `app_factory.py` (P4 comment). Prefix: `/api/v1/geometry`.

| Method | Path | Purpose |
|--------|------|---------|
| `POST` | `/api/v1/geometry/extract` | Depth + normals from image |

**Request (JSON):**

```json
{
  "image_base64": "<data-url or raw base64>",
  "image_media_type": "image/png",
  "profile": "auto"
}
```

**Profiles** (`GeometryProfile`): `auto` | `cpu_fast` | `cpu_accurate` | `gpu_full`

**Response:** `{ "meta": {…}, "images": { "depth_png", "normals_png", … } }`  
`meta` includes `device`, `profile_resolved`, `depth_model`, `normals_source`, `warnings`.

**Errors:** `400` bad image · `503` missing optional deps (transformers / models) · `500` extract failure · rate limit 10/min.

### Lighting (consumer of geometry)

Router: `src/copy_that/interfaces/api/lighting.py` · Prefix: `/api/v1/lighting`.

| Method | Path | Purpose |
|--------|------|---------|
| `POST` | `/api/v1/lighting/analyze` | Shadow/lighting tokens; optional real geometry |

When `use_geometry` is true (default), analysis calls the **same** `extract_depth_and_normals` used by `/geometry/extract`. Optional `geometry_profile` overrides device→profile mapping. Response fields: `geometry_used`, `geometry_meta`, optional `geometry_images` (`depth_png`, `normals_png`). Missing optional deps → analysis continues **without** depth/normals (no stand-in); `geometry_used=false`.

Flag-gated UI (`showLightingAnalyzer`): `LightingAnalyzer` renders `LightingGeometryEvidence` (status + meta + thumbnails).

---

## MPS / CPU behavior (code truth)

From `extractors/geometry/depth_normals.py`:

| Condition | Behavior |
|-----------|----------|
| `ENABLE_GPU` off or no accelerator | `auto` → `cpu_fast`; Depth Anything Small on CPU; normals from depth gradients |
| Apple Silicon MPS + GPU enabled | Depth on MPS; **Marigold skipped** (CUDA-only); normals = depth gradients; warning `gpu_non_cuda_depth_only` / `marigold_requires_cuda_depth_gradient` |
| CUDA + `gpu_full` | Depth Anything Base + Marigold normals when deps present |
| Explicit `cpu_fast` / `cpu_accurate` | Forces CPU even if GPU present |

Deterministic normals path (no HF models): `compute_normals_from_depth` in `normals_from_depth.py`.

### G2 verification (unit + optional live)

**Unit (required for G2 pass; no HF weights):**

```bash
pnpm exec pytest tests/unit/extractors/geometry/test_normals_from_depth.py -q
```

Asserts:

| Case | Expect |
|------|--------|
| `cpu_fast` / `cpu_accurate` with GPU present | device=`cpu`, warning `cpu_profile_forced` |
| `auto` + GPU disabled | `cpu` + `cpu_fast` |
| `auto` / `gpu_full` on MPS (CUDA absent) | device=`mps`, profile=`gpu_full`, warning `gpu_non_cuda_depth_only` |
| `auto` on CUDA | device=`cuda`, profile=`gpu_full`, no warning |
| `gpu_full` without accelerator | falls back to `cpu_fast` + `gpu_unavailable_fallback_cpu_fast` |

Extract-time (not profile-resolve) on MPS: meta also gains `marigold_requires_cuda_depth_gradient` and `normals_source=depth_gradient`. Flag-gated UI surfaces these via `LightingGeometryEvidence` warnings.

**Live Apple Silicon spot-check (optional; weights cached):**

1. `ENABLE_GPU=1` and start API.
2. Call `/geometry/extract` with `"profile":"auto"` on a small PNG.
3. Expect `meta.device == "mps"`, `normals_source == "depth_gradient"`, warnings including `gpu_non_cuda_depth_only` / `marigold_requires_cuda_depth_gradient`.
4. Repeat with `"profile":"cpu_fast"` → `device == "cpu"` and `cpu_profile_forced`.
5. Warm wall clock against G4 targets (≤ ~2s MPS / ≤ ~5s `cpu_fast`) using the curl timing snippet in § G4.

Do **not** treat cold download minutes as a G2 failure.

---

## G4 — Cost / latency (product accepted 2026-09-20)

### Accepted budgets

| Mode | Contract | Product decision |
|------|----------|------------------|
| Cold start | Model download + first load — **minutes**; not interactive | **Accepted.** Exclude from UX SLOs; document “first run may download weights.” |
| Warm `cpu_fast` | ≤ ~**5s** per typical UI screenshot | **Accepted** as the CPU interactive target when weights are already local. |
| Warm MPS / CUDA depth | ≤ ~**2s** when hardware + weights ready | **Accepted** as the accelerator target; not required for shipping flags-off. |
| Missing deps | Geometry extract → **`503`** with clear detail; lighting analyze → continue with `geometry_used=false` (no stand-in) | **Accepted.** Prefer fail-loud on dedicated geometry; degrade on lighting consumer. |

### Happy-path policy (accepted)

| Surface | Geometry / lighting? | Rationale |
|---------|----------------------|-----------|
| Upload → color / spacing / typography / shadow extract | **Never** call geometry or `/lighting/analyze` by default | Keeps MVP extract SLO independent of HF model cold/warm cost |
| README / default App nav | **Off** | Same; see production flag policy |
| `POST /api/v1/geometry/extract` | Opt-in API | Power users / tests / future flag-gated UI |
| `POST /api/v1/lighting/analyze` | Opt-in API; UI only when flags on | Consumer path for G1; still not on upload spine |
| Local flag flip (`featureFlags`) | Dev / demos only | Must not ship as default-on |

**Decision:** Geometry may **not** sit on the upload happy path. Lighting remains a parked, flag-gated adjacent surface even after G1–G4.

### How to spot-check warm latency (optional)

After weights are cached locally:

```bash
# Warm timing for geometry extract (cpu_fast). Expect wall ≤ ~5s on a typical screenshot.
time curl -sS -o /tmp/geo.json -X POST "http://127.0.0.1:8000/api/v1/geometry/extract" \
  -H "Content-Type: application/json" \
  -d "{\"image_base64\":\"$IMAGE_B64\",\"image_media_type\":\"image/png\",\"profile\":\"cpu_fast\"}"
python -c "import json; d=json.load(open('/tmp/geo.json')); print(d.get('meta'))"
```

Cold start is out of budget by design (download + load). Do not treat first-run minutes as a regression against the warm targets.

---

## Production flag policy (post-G4)

**Prefer still default-off.** G4 acceptance does **not** flip production nav.

| Flag | Production default | When to enable |
|------|--------------------|----------------|
| `showLightingAnalyzer` | `false` | Local/dev demos of lighting + geometry evidence |
| `showLightingTab` | `false` | Local/dev explorer Lighting tab |
| `showMoodBoard` | `true` | Overview Labs (collapsed). Kill switch: set `false`. Generation still requires Generate click. |

Rules:

1. Lighting defaults in [`frontend/src/config/featureFlags.ts`](../../frontend/src/config/featureFlags.ts) stay **`false`** on `main`.
2. Mood board Labs is the approved cost-aware unpark; do not add mood board to App nav tabs.
3. Do not advertise lighting/geometry in README happy path while lighting defaults are off.
4. APIs remain mounted for clients/tests; mounting ≠ product promotion.

---

## How to exercise locally (API-only; nav stays off)

1. Start API as usual (`uvicorn` / project compose). Do **not** flip frontend feature flags.
2. Tiny PNG → base64, then:

```bash
# Replace IMAGE_B64 with raw or data-URL base64 of a small PNG
curl -sS -X POST "http://127.0.0.1:8000/api/v1/geometry/extract" \
  -H "Content-Type: application/json" \
  -d "{\"image_base64\":\"$IMAGE_B64\",\"image_media_type\":\"image/png\",\"profile\":\"cpu_fast\"}" \
  | python -c "import sys,json; d=json.load(sys.stdin); print(d['meta']); print(sorted(d['images']))"
```

3. Lighting with real geometry (same extractor):

```bash
curl -sS -X POST "http://127.0.0.1:8000/api/v1/lighting/analyze" \
  -H "Content-Type: application/json" \
  -d "{\"image_base64\":\"$IMAGE_B64\",\"use_geometry\":true,\"geometry_profile\":\"cpu_fast\"}" \
  | python -c "import sys,json; d=json.load(sys.stdin); print(d.get('geometry_used'), d.get('geometry_meta')); print(sorted((d.get('geometry_images') or {}).keys())); print(d.get('style_key_direction'))"
```

4. Unit path without models:

```bash
pnpm exec pytest tests/unit/extractors/geometry/ tests/unit/interfaces/api/test_geometry.py \
  tests/unit/interfaces/api/test_lighting_geometry.py \
  tests/unit/shadowlab/test_lighting_geometry_wiring.py -q
```

5. Optional visual compare of saved depth/normals grids: `scripts/compare_geometry_outputs.py`.

---

## Flag-gated lighting (local / dev only)

Defaults in `frontend/src/config/featureFlags.ts` stay **`false`**. To exercise UI locally:

1. Temporarily set in that file (do not commit):
   - `showLightingAnalyzer: true` — Overview auto-calls `/lighting/analyze`
   - `showLightingTab: true` — Explorer Lighting tab in nav
2. Mood board Labs may already be `showMoodBoard: true` (collapsed). Leave lighting flags off unless exercising G1 UI.
3. Rebuild / restart the frontend (`pnpm --dir frontend dev` or equivalent).
4. Revert lighting flags to `false` before merging to main.

API path does not need flags: call `/api/v1/lighting/analyze` directly as above.

---

## Thin slice delivered

- Gates written (this doc + roadmap subsection)
- Geometry API surface documented; extract remains available for API/tests
- Lighting analyze wired to shared `extract_depth_and_normals` (G1)
- Lighting response includes optional `geometry_images` PNG previews
- Flag-gated UI: `LightingGeometryEvidence` surfaces used/meta/thumbnails **and** `geometry_meta.warnings` (MPS / Marigold skip codes)
- G2 profile-resolve paths unit-verified (CPU force, MPS depth-only, CUDA gpu_full, no-accel fallback)
- Geometry extract missing-deps → **`503`** unit-covered (G4 failure mode)
- G4 cost/latency budgets **product-accepted**; happy path excludes geometry
- Production flag policy: lighting remain default-off after G4; mood board Labs-unparked separately
- Unit tests: depth-gradient normals + mocked geometry extract + lighting↔geometry wiring + UI evidence component
- Default App lighting flags unchanged (`showLightingTab` / `showLightingAnalyzer` stay `false`); `showMoodBoard` Labs-gated

## Follow-ups / remaining gate gaps

- Still not next: merge #168 extras as product promotion, P5 platform, default-on lighting nav
- Optional live warm MPS/CUDA latency dogfood on a real screenshot (unit path does not load Depth Anything)
- Larger dual-CV absorb (`core.tokens` / `cv_pipeline`) — see architecture SoT dual-CV note in [CURRENT_ARCHITECTURE_STATE.md](../architecture/CURRENT_ARCHITECTURE_STATE.md) (detailed DUAL_CV_STACKS.md archived)
- Env/config mechanism for flags (today: local edit only; do not commit `true`)

## Shadow / geometry verify notes (2026-09-20)

- Upload → shadow extract **does not** call geometry / Depth Anything (G4 still holds).
- Default shadow CV path uses classical shadowlab cues → CSS tokens only (`use_geometry=False`); dark-blob remains `ENABLE_DARK_BLOB_SHADOW_CV` opt-in.
- `/lighting/analyze` may still attach geometry when explicitly called; App nav flags stay false.
- Live evidence for classical shadow + dual-CV helper move: [docs/evidence/2026-09-20-dual-cv-shadow/](../evidence/2026-09-20-dual-cv-shadow/).

## Hardening slice (2026-09-21)

- Expanded `_resolve_device_and_profile` unit matrix (MPS / CUDA / force-CPU / no-accel).
- `LightingGeometryEvidence` shows meta warnings so local flag-on demos make MPS depth-only behavior obvious.
- `POST /geometry/extract` OptionalDependencyError → 503 regression test.
- Defaults in `featureFlags.ts` unchanged (`false`).
