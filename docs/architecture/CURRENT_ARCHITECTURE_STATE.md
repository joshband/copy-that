# Copy That — Current Architecture State

**Version:** 2.0  
**Last Updated:** 2026-10-08  
**Status:** Primary architecture SoT (inventory)  
**Planning SoT:** [MVP_EXPANSION_ROADMAP.md](../planning/MVP_EXPANSION_ROADMAP.md)  
**W3C / DTCG SoT:** [W3C_CONFORMANCE.md](../domain/W3C_CONFORMANCE.md)  
**Guide Pack:** [DESIGN_GUIDE_PACK.md](../domain/DESIGN_GUIDE_PACK.md)  
**Docs nav:** [DOCUMENTATION_INDEX.md](../../DOCUMENTATION_INDEX.md)

---

## Product contract

**Screenshot → design tokens → W3C + CSS / Guide Pack export**, with a light overview narrative. Mood board and lighting are **opt-in tabs** (never run during extract); geometry is **API-only** and runs on demand from the Lighting tab. Flag values: [`featureFlags.ts`](../../frontend/src/config/featureFlags.ts) (SoT — docs do not copy them).

Visible nav tabs are computed by `visibleAppTabs()` in [`featureFlags.ts`](../../frontend/src/config/featureFlags.ts): the four token families plus overview, shape, and export are always on; Mood, Lighting, Relations, and Raw are flag-gated.

---

## Stack (live)

| Layer | Choice |
|-------|--------|
| Backend | Python 3.12+, FastAPI, Pydantic v2, SQLAlchemy 2, Alembic (`alembic/versions/`) |
| Frontend | React + TypeScript, Vite (`frontend/`), Zustand, TanStack Query |
| DB | PostgreSQL (local Docker / Neon) |
| AI | Anthropic Claude (structured extract); optional OpenAI; mood board local LM Studio. Model IDs: [`infrastructure/ai_models.py`](../../src/copy_that/infrastructure/ai_models.py) only |
| CV | OpenCV + family extractors under `src/copy_that/extractors/` (`cv`, `cv_helpers`) |
| Jobs | Celery + Redis (mood board / async jobs) |
| Deploy | Docker; GCP Cloud Run scripts + Terraform under `deploy/` (root `terraform/` holds only a deprecation note) |

**Rough size (2026-09):** ~65k LOC Python under `src/copy_that/`, ~36k LOC TS/TSX under `frontend/src/`.

---

## Backend layout

```
src/copy_that/
  interfaces/api/     # FastAPI routers (app_factory mounts MVP + parked)
  extractors/         # Canonical extraction + DTCG helpers (new extractor code goes here)
  application/        # Legacy extractors / use cases being drained into extractors/ — no new modules
  services/           # colors, spacing, typography, shadow, layout, mood_board, …
  core_tokens/        # Token model, graph, W3C adapters
  design_tokens/      # 2025.10 schemas + resolver
  guide_pack/         # Design Guide Pack builder / schema / HTML
  shadowlab/          # Deep / classical shadow pipeline
  domain/             # Domain types (incl. w3c_design_tokens)
  generators/         # CSS / React (ThemeProvider) / Tailwind theme.extend plugins
  infrastructure/     # config, ai_models, celery, DB, security
```

### Extractors (canonical home: `extractors/`)

| Family | Status | Notes |
|--------|--------|-------|
| color | LIVE | AI + CV |
| spacing | LIVE | CV + AI; dimension companions derived |
| typography | LIVE | Extract + fontFamily/fontWeight atoms |
| shadow | LIVE | Classical shadowlab default; deep models opt-in |
| gradient | LIVE | CV band/stops (+ optional palette confirm) |
| border / strokeStyle | DERIVE | CV/heuristic (Phase 3) |
| opacity / number | DERIVE | From shadows + UI alpha |
| duration / cubicBezier / transition | DERIVE | UI-kit / style-cue (Phase 5); presets below threshold |
| geometry | Parked | P4 gates — see [P4_GEOMETRY_GATES.md](../planning/P4_GEOMETRY_GATES.md) |

Capability map: `src/copy_that/extractors/dtcg_capability.py`.

### Key services

- `type_coverage_service` — export-complete synth for all 13 official `$type`s  
- `motion_service` — duration / easing presets & cues  
- `mood_board_generator` — P4 Mood tab; Claude or LM Studio + image router  
- `layout_service` — shape / border / radius persistence  
- Family services: colors, spacing, typography, shadow, projects, sessions  

### API surface (high level)

**MVP path:** auth, projects, colors, spacing, typography, shadows, gradients, design-tokens (W3C/CSS/React/Tailwind/Guide Pack export).  
**Opt-in tabs:** mood-board (+ jobs for polling/SSE), lighting (+ on-demand geometry). **Parked (mounted, no default UI):** sessions, batch, multi-extract, snapshots, metrics, admin (see `app_factory.py` + `featureFlags.ts`).

**Multi-extract:** `interfaces/api/multi_extract.py` is **mounted** in `app_factory` under demos/ops (alt SSE path). Prefer per-family MVP routes or the UI for the happy path — not the primary product surface.

---

## Frontend layout

```
frontend/src/
  components/           # App shell, upload, overview, export, …
  features/visual-extraction/adapters/  # Color/Spacing/Typography/Shadow visual adapters
  shared/adapters/      # TokenVisualAdapter registry
  config/featureFlags.ts
  config/tokenTypeRegistry.tsx
  store/                # tokenGraphStore, etc.
  design/tokens.css     # Live UI tokens (light monochromatic + slate accent)
```

**Adapter pattern:** generic explorer components call `TokenVisualAdapter`; family adapters register for color / spacing / typography / shadow.

**Canonical commands:** root `pnpm dev` / `pnpm build` / `pnpm type-check` / `pnpm test` → `pnpm --dir frontend …`; `pnpm test:e2e` runs Playwright with `frontend/playwright.config.ts`. E2E home: `frontend/tests/playwright/` (the only one). Full gate: `make verify`.

---

## Mood board (P4 Mood tab)

- Flag: `showMoodBoard` — dedicated **Mood** nav tab; generation needs an explicit click; kill switch `false`  
- Spec: [MOOD_BOARD_SPECIFICATION.md](../features/MOOD_BOARD_SPECIFICATION.md)  
- **Local default images:** mflux 4-bit schnell Hub mirror `dhairyashil/FLUX.1-schnell-mflux-4bit` via `scripts/mood_board_local_image_server.py`  
- Themes: LM Studio (OpenAI-compatible) or Anthropic; themes-first UI default  
- Z-Image-Turbo: **opt-in only** (not default)

---

## Dual-CV note

Canonical CV lives under `copy_that.extractors.cv` / `cv_helpers` and `copy_that.core_tokens`. Prefer the extractors package for new work.

`src/copy_that/` is the only Python package; the legacy top-level `core` / `cv_pipeline` / `pipeline` / `layout` / `typography` packages are gone (history: [CHANGELOG.md](../../CHANGELOG.md) and git log).

---

## Shadow outputs

Pipeline PNGs under `test_images/processedImageShadows*` are **gitignored**. Regenerate locally — see [shadow/GETTING_STARTED.md](../shadow/GETTING_STARTED.md) and [test_images/README.md](../../test_images/README.md).

---

## Related docs

| Doc | Role |
|-----|------|
| [MVP_EXPANSION_ROADMAP.md](../planning/MVP_EXPANSION_ROADMAP.md) | Scheduling P0–P5 |
| [W3C_CONFORMANCE.md](../domain/W3C_CONFORMANCE.md) | DTCG Compat+ |
| [MOOD_BOARD_SPECIFICATION.md](../features/MOOD_BOARD_SPECIFICATION.md) | Mood tab |
| [P4_GEOMETRY_GATES.md](../planning/P4_GEOMETRY_GATES.md) | Geometry promotion gates |

Historical architecture / vision docs: `~/Documents/copy-that-archive/architecture-history/`.
