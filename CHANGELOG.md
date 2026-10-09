# Changelog

## Unreleased

### Dependency, frontend, and planning follow-ups (2026-10-09)

- Split Google SDKs and deep CV into optional `gcp` and `cv-deep` extras. Core OCR retains pytesseract; geometry dependencies load only on demand. Full verification installs the deep-CV extra, and dependency security exports cover both extras.
- Replaced deprecated UTC timestamp creation while preserving shadowlab's existing serialized timestamp contract.
- Consolidated the React/DOM/types 19, React plugin 6, required Vite 8, and jest-dom 7 upgrades. Development/CI/container tooling uses Node 22.12+ for the combined dependency engines. Migrated bundler chunk configuration to Rolldown, removed inactive/unsupported test settings, and corrected malformed CSS variable fallbacks surfaced by the new build.
- Added hosted Mood email/password sign-in with in-memory access tokens, explicit generation after login, expired/disabled-session recovery, and sign-out. Mood health reports whether authentication is required; local anonymous generation remains available.
- Hardened Git ignores for environment variants, private credential files, Terraform state/variables, and machine-specific connector configuration. Kept unrelated local research outside the maintenance diff.
- Updated the static hiring showcase to include Guide Pack, opt-in Mood/Lighting, current validation and frontend stack. Labelled illustrative visuals/export snippets without claiming verified extraction lineage.
- Refocused the roadmap on scored extraction precision, moved dated progress into this changelog, and documented an invited hosted demo plan without deploying infrastructure. Refreshed setup, architecture, configuration, shadow, testing, deployment, and documentation navigation.

### Spacing consolidation and extraction services (2026-10-09)

- Consolidated the live spacing utilities into `extractors/spacing/utils.py`, retaining alignment, adjacency, grid inference, text-baseline measurements, and confidence behavior. Removed the legacy utility module and migrated callers.
- Moved color, spacing, typography, and shadow extraction orchestration, merging, persistence, and diagnostic projection into services. Routers retain dependency wiring, request validation, HTTP mapping, and SSE framing. Shared artifact models and JSON sanitizers now have a neutral service home with compatible API reexports.
- Corrected shadow upload previews to use a classical-only pipeline: upload no longer runs the full shadowlab depth/geometry/ML stages or emits their preview artifacts. Dedicated on-demand geometry remains separate; unavailable light/physics measurements remain null.
- Added offline service acceptance coverage for fallback, metadata/persistence, cache and streaming events, multi-extractor provenance, and classical-only shadow uploads.

### Canonical Claude color extractor (2026-10-09)

- Moved the live Claude color implementation into `extractors/color/extractor.py` and deleted `application/color_extractor.py`. API, service, CV, registry, batch, and test callers now use the canonical module.
- Preserved cache namespaces, caller-supplied input hashes, performance tracking, and contrast-target/role-score metadata. Added hermetic cache and response contract tests with paid provider calls stubbed.

### API access controls (2026-10-09)

- Added `ENABLE_PARKED_ROUTERS` for sessions, batch, and multi-extract: local APIs remain available by default; staging/production must opt in. OpenAPI and the API catalog reflect mounted routes. Jobs stays mounted because Mood polls its results.
- Hosted Mood generation now requires an active user's access token and applies the existing per-process rate limiter using user identity before broker preflight or enqueue. Missing, invalid, expired, and refresh tokens are rejected; local anonymous Mood remains available.
- Added hermetic route/authentication/rate-limit coverage with in-memory users. The hosted Mood sign-in follow-up supplies the authenticated UI.

### Review remediation and documentation follow-ups (2026-10-08–09)

- Consolidated CI around locked dependencies, full Vitest, Python unit/integration tests, and security gates; restored previously uncollected backend tests to the CI test homes.
- Added `make verify`, shared agent rules and workflow guidance, local hooks, and a docs/feature-flag drift test.
- Consolidated duplicate modules, retired unused pipeline/layout/typography packages, centralized AI model identifiers, and added a hermetic scored extraction evaluation.
- Updated setup, configuration, deployment, and test documentation to match the current code. The testing guide now distinguishes local verification from security and mocked browser gates, documents accuracy evaluation, and explains fresh-port Playwright runs.
- Expanded the monthly review checklist to cover test collection, extraction accuracy, model configuration, dependency/security findings, and paid-route access controls.

### Claude default models → Sonnet 5.5 (2026-10-08)

- `CLAUDE_MODEL` now defaults to `claude-sonnet-5-5`, because Sonnet 4.5 reaches end-of-life on 2026-11-30. Set `CLAUDE_MODEL` to override it.
- Claude responses are read by block type (`infrastructure/claude_response.claude_text`), because current models can start a response with a `thinking` block.
- Extraction and metrics calls now allow `max_tokens=16000` instead of 2000, because thinking counts toward the limit.
- `CLAUDE_SHADOW_MODEL` now defaults to `claude-sonnet-5-5` (was Opus 4.1). Shadow extraction calls also allow `max_tokens=16000` (was 4096).

## 1.0.2 — 2026-09-20

### Hydrate + confidence + contracts

- Hydrate the token graph when core extract stages complete (not only when colors arrive), so Overview Snapshot fills for chrome/soft-card fixtures
- CV confidence calibration + spacing Fallback honesty (`TokenSourceChip`, Measured vs Fallback %)
- Visual contracts / MVP Playwright pack evidence; UI dogfood packet under [docs/evidence/2026-09-20-ui-dogfood/](docs/evidence/2026-09-20-ui-dogfood/)

### Follow-up (same day, post-tag)

- Spacing AI+CV merge prefers measured CV confidence; CV fallback stays ~15% (no AI-inflated “80% fallback”)
- API responses include `spacing_confidence_breakdown` for Snapshot honesty

## 1.0.1 — 2026-09-20

### Dual-CV fifth cut

- Deleted legacy shims: `src/core/`, `src/cv_pipeline/`, `src/copy_that/application/cv/`
- Migrated callers/tests/scripts to `copy_that.core_tokens` / `copy_that.extractors.cv` / family extractors
- Fixed spacing `layout_image` numpy truthiness crash; refreshed spacing monkeypatch tests
- Dogfood packet: [docs/evidence/2026-09-20-dogfood/](docs/evidence/2026-09-20-dogfood/)

## 1.0.0 — 2026-09-20

Stable MVP release.

### Highlights

- All four token families on the happy path (color, spacing, typography, shadow)
- Dual-CV absorb: shared CV under `copy_that.extractors.cv` / `cv_helpers`; token graph under `copy_that.core_tokens` (legacy `cv_pipeline` / `core.tokens` are shims)
- Shadow default: classical shadowlab → CSS elevation tokens; dark-blob CV opt-in only
- P4 geometry (lighting) gated behind default-off feature flags; G1–G5 held
- Frontend MVP Playwright pack in medium-tier CI

### Not in 1.0

- Mood board promotion, draft PR #168 merge, P5 platform
- Production lighting / mood nav flags remain off


## Planning history — September 2026

Migrated from the former roadmap. These are historical reports, not current configuration or fresh acceptance evidence. Current intent lives in [the roadmap](docs/planning/MVP_EXPANSION_ROADMAP.md); code defines feature flag values.

### Harden wave (2026-09-19)

- Live Postgres extract→export (incl. all 13 `$type`s + CSS/React/Tailwind) verified
- Typography auto mode falls back when AI auth missing
- Single-color projects still get a synth gradient; `number.unity` preset if no numbers
- Playwright canonical home: `frontend/tests/playwright/` (deprecated sibling folders are stubs only)
- Dual Vite/package roots collapsed: canonical app is `frontend/`; root scripts delegate via `pnpm --dir frontend`
- PR #168: draft park comment posted

### P4 Geometry + debt cuts (2026-09-20)

- G1 lighting UI + G4 cost accept: [P4_GEOMETRY_GATES.md](docs/planning/P4_GEOMETRY_GATES.md)
- Dual CV: color + spacing + typography CV bodies under extractors; application shims — see [CURRENT_ARCHITECTURE_STATE.md](docs/architecture/CURRENT_ARCHITECTURE_STATE.md) (detail archived: `~/Documents/copy-that-archive/architecture-history/DUAL_CV_STACKS.md`)
- Playwright leftovers cleared; overview/shape polish spec added
- Shape polish: source chips, no fake grid confidence, no P2b/DTCG roadmap labels
- CV fast path: text-mask; FastSAM/UIED/depth default-off; honest spacing fallback; dark-blob shadow opt-in

### Dual-CV third cut + shadow quality + evidence (2026-09-20)

- Helpers relocated: FastSAM / UIED / debug / grid / layout-text → `extractors/cv_helpers/` (application/cv shims)
- Shadow default: classical shadowlab → CSS elevation tokens + `opacity_from_shadows`; dark-blob stays opt-in; lighting flags stay false
- Evidence packet: [docs/evidence/2026-09-20-dual-cv-shadow/](docs/evidence/2026-09-20-dual-cv-shadow/)
- CI: `pnpm test:e2e:mvp` includes `mvp-phase1-smoke` + `overview-shape-polish`; medium-tier Playwright job in `ci-tiered.yml`

### Dual-CV fourth cut + stable absorb (2026-09-20)

- `cv_pipeline` → `copy_that.extractors.cv` (preprocess / primitives / text_mask / control_classifier); top-level `cv_pipeline` is shim
- `core.tokens` → `copy_that.core_tokens` (model / graph / family factories / W3C adapters); top-level `core.tokens` is shim
- Classical CSS roles gated by density/area; fixture tests in `tests/unit/extractors/shadow/test_cv_classical_quality.py`
- Stable release: **v1.0.0**

### Dual-CV fifth cut — shim deletion (2026-09-20)

- Migrated all `src` / `tests` / `scripts` callers to `copy_that.core_tokens` / `copy_that.extractors.cv` / extractors family modules
- Deleted `src/core/`, `src/cv_pipeline/`, `src/copy_that/application/cv/`
- Patch release: **v1.0.1** (+ dogfood evidence)

### Patch 1.0.2 — hydrate + confidence + contracts (2026-09-20)

- Token graph loads on `coreStagesComplete` (Snapshot counts for chrome fixtures)
- CV confidence calibration + spacing Fallback honesty in Overview / spacing panel
- Visual contracts + UI dogfood evidence; release: **v1.0.2**

### Dogfood follow-ups (2026-09-20)

- Spacing: sub-4 measured `base_unit` floors to 4 with confidence ≤0.25 (upload-surface-style noise)
- Shadows: `cv_classical_empty` surfaces “No elevation detected” via API metadata/warnings + shadows empty UI (lighting flags remain off)
- Spacing merge: CV fallback confidence (~15%) wins over AI; measured Snapshot % tracks CV (not AI default ~85%)

### P4 Geometry hardening (2026-09-21)

- G2 profile-resolve unit matrix expanded (MPS / CUDA / force-CPU / no-accel) — [P4_GEOMETRY_GATES.md](docs/planning/P4_GEOMETRY_GATES.md)
- Flag-gated `LightingGeometryEvidence` surfaces `geometry_meta.warnings` (MPS depth-only / Marigold skip)
- Geometry extract missing-deps → `503` unit-covered; `featureFlags` lighting stay **`false`**
- Remaining gap: optional live warm MPS/CUDA dogfood (no default-on)

### P4 Mood tab + Guide Pack Export (2026-09-22)

- Mood board: `showMoodBoard=true` as AppShell **Mood** tab (Material×2 → Source → Typography/grid composition; themes-first)
- Export: Design Guide Pack / Guide HTML first-class + 13-type honesty strip + gradient extract honesty
- Lighting remains default-off



### Mood local dogfood — 2026-09-21

**Verified (2026-09-21):** API enqueue → Celery solo → LM Studio `google/gemma-2-9b` + mflux schnell (1 variant × 1 image, Midjourney palette) → `completed` in ~130s with `rendering_images` progress + `data:image/png;base64,…`. Prefer `google/gemma-2-9b` for theme JSON (`google/gemma-4-e4b` can stall on long structured prompts).
