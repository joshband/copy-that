# Copy That — MVP & Expansion Roadmap

**Status:** Active (source of truth for planning)  
**Date:** 2026-09-18  
**Supersedes:** Competing phase numbers in CURRENT_ARCHITECTURE_STATE, STRATEGIC_VISION, IMPLEMENTATION_ROADMAP, root SESSION_* docs  
**Related (archived):** Nov 2025 PRD/roadmap + Phase 0 superpowers plan/spec → `~/Documents/copy-that-archive/planning-history/`

---

## Product contract (one sentence)

**Screenshot → reliable design tokens (starting with the four extractors we have) → W3C + CSS export → light overview narrative — with a clean seam to add more W3C token families later, and lighting / geometry / mood board parked.**

---

## Principles

1. **Finish the spine before growing the platform.** No new extractors or generative features until Phase 1 exit criteria pass.
2. **W3C Design Tokens is the interchange format.** New families plug into the same graph → export path.
3. **Park ≠ delete.** Lighting, geometry, mood board, sessions/jobs stay in the repo but off the default App path until a later phase promotes them.
4. **One phase numbering.** Ignore “Phase 2.5 / Phase 4 / Phase 7” in older docs for scheduling; use **P0–P5** below.
5. **Historical context.** Original Nov 2025 PRD was color-only MVP. Code already runs four families; this roadmap re-centers on that reality without claiming multimodal/platform completion.

---

## Phase map

| Phase | Name | Goal | Exit when |
|-------|------|------|-----------|
| **P0** | Freeze & slim | One happy path; remove distraction | App/API surface matches keep list; docs point here |
| **P1** | MVP harden | Tokens + export + overview are trustworthy | Smoke E2E green; W3C+CSS export used by UI; `pnpm type-check` pass |
| **P2** | W3C family expansion | Add remaining token families on the same seam | Each family: extract → persist → graph → export → tab |
| **P3** | Generator depth | More useful outputs without new modalities | Tailwind/React export quality bar met |
| **P4** | Parked intelligence | Promote lighting / geometry / mood board deliberately | Each has product owner criteria + cost model |
| **P5** | Platform (optional) | Sessions, batch, plugins, multimodal | Only after P1–P3 stable |

```
P0 Freeze ──► P1 MVP harden ──► P2 W3C families ──► P3 Generators
                                      │
                                      └──► P4 Parked (lighting / geometry / mood)
                                      └──► P5 Platform (sessions / batch / multimodal)
```

---

## P0 — Freeze & slim (now)

**Scope of work**

- Declare this roadmap + design spec as planning SoT; mark vision docs historical.
- Default UI: upload → colors / spacing / typography / shadows → overview narrative → export.
- Hide or unwire from App: lighting tab auto-fetch noise, mood board, relations/raw demos, SessionWorkflow, AdvancedColorScienceDemo, CostDashboard.
- Keep routers mounted optionally behind flags **or** leave mounted but unused by App (prefer flags for clarity).
- Dual package/Vite and Playwright homes: inventory only in P0; collapse in P1 if blocking.
- Draft PR [#168](https://github.com/joshband/copy-that/pull/168): merge only slices that harden extract/export/overview; otherwise leave draft.

**Out of scope:** New extractors, React 19 / ESLint 9, mood board polish, geometry pipeline.

**Deliverables:** Updated INDEX/README claims; App tab set reduced; park list documented in code comments or feature flags.

**Status (2026-09-18):** P0 executed — `featureFlags.ts` parks mood/lighting/relations/raw/demo; AppShell shows MVP tabs only; `app_factory` documents parked routers. Draft PR #168: add park comment via `gh pr comment 168` (agent gh auth blocked).

---

## P1 — MVP harden (foundational MVP)

**Status (2026-09-18):** Complete. Export tab downloads W3C JSON + CSS; CSS emits usable color values; ASGI smoke + Playwright mocked smoke (`mvp-phase1-smoke.spec.ts`); extract failures surface via banners + pipeline stage errors; `pnpm type-check` clean.

**In scope**

| Area | Work |
|------|------|
| Extract | Color streaming + spacing/typography/shadow parallel path reliable; clear errors |
| Persist | Project-scoped tokens for all four families |
| Graph | `tokenGraphStore` + `/design-tokens/export/w3c` is the display source of truth |
| Export | **W3C JSON** and **CSS** downloadable from Export tab (not guidance-only copy) |
| Overview | Client narrative / counts stay; no mood board requirement |
| Quality | `pnpm type-check`; one Playwright smoke: upload fixture → four tabs → export |
| Auth | Minimal (anonymous project or simple JWT) — do not expand admin/cost |

**Explicitly parked in P1**

- Mood board API/UI  
- Lighting analyze / geometry extract  
- Sessions / libraries / curate  
- Jobs / batch / Celery  
- Multi-extract SSE demo  
- Flutter / Figma / Material generator claims  

**Exit criteria**

1. [x] Cold start → extract sample screenshot → see four token families → download W3C + CSS.  
2. [x] Typecheck clean on frontend; critical backend tests for extract+export green.  
3. [x] README describes this MVP only (no “multi-modal platform” as shipped).

---

## P2 — Expand to all W3C token families

**North star families** (from [W3C_CONFORMANCE.md](../domain/W3C_CONFORMANCE.md) + DTCG-shaped types):

| Wave | Families | Notes |
|------|----------|--------|
| **Already in MVP** | `color`, `dimension`/`spacing`, `typography`, `shadow` | Harden schemas toward DTCG `$type` consistency |
| **P2a** | `border` / `borderRadius`, `opacity`, `fontFamily` (if split from typography composites) | Often derivable from layout/CV |
| **P2b** | `gradient`, `transition` / duration / cubicBezier (animation) | Higher ambiguity; confidence UX required |
| **P2c** | Full DTCG 13-type coverage (export-complete, Compat+) | Done — see below |

**P2a status (2026-09-18):** Complete for border/radius + opacity v0.
- CV shape tokens (`corner_radius` / `border_width`) persist in `layout_tokens` on spacing extract **and** streaming spacing extract
- Reloaded via `/design-tokens/export/w3c` + CSS vars; MVP **shape** tab mounts `LayoutTokenPanel`
- Opacity synthesized at export from unique shadow opacities (`$type: "number"`)
- Deferred: dedicated opacity extractor, fontFamily split tab

**Local DB:** `make db-bootstrap` (Docker Postgres + Alembic). SQLite smoke: `make db-bootstrap-sqlite`.

**P2b status (2026-09-18):** Minimal complete (synthesize-at-export).
- Gradients synthesized from color pairs (`$type: gradient`) → W3C + CSS `linear-gradient()`
- Duration + cubicBezier presets emitted when a project has any tokens
- Shown under Shape tab as Motion (P2b); confidence UX / CV gradient detection deferred

**P2c status (2026-09-19):** Export-complete coverage of all 13 DTCG Format 2025.10 `$type`s (A + Compat+).
- Derive/synth at export: `fontFamily`, `fontWeight`, `strokeStyle`, `border`, `transition`, `dimension` companions, line-height `number`, fallback `shadow` when none extracted
- Existing extract/synth paths cover `color`, `typography`, `shadow`, `gradient`, `duration`, `cubicBezier`, opacity-as-`number`
- Compat+: keep hex colors, `spacing` section (often `$type: dimension`), `layout` section; see [W3C_CONFORMANCE.md](../domain/W3C_CONFORMANCE.md)
- Shape tab lists derived DTCG types; CSS/React/Tailwind emit new sections
- Tests: `tests/unit/api/test_w3c_all_types_coverage.py`

**Per-family checklist (repeatable seam)**

1. Schema (Pydantic + Zod) aligned to W3C `$type`  
2. Extractor (AI and/or CV) with confidence  
3. Persist + repository  
4. Include in `/design-tokens/export/w3c`  
5. Explorer tab or section  
6. CSS variable mapping where meaningful  
7. Tests (unit + one integration)

**Do not** invent new UI chrome systems per family — reuse TokenExplorer patterns.

---

## P3 — Generator depth

**Status:** Done (CSS depth + React theme provider + Tailwind depth + Export tab downloads).

- Improve CSS/React exports for families present in graph. ✅  
  - CSS: typography weight/style/line-height/letter-spacing/align; spacing rem companions; multi-layer shadows.  
  - React: deterministic `theme` / `tokens` + `cssVars` + `ThemeProvider` / `useTheme` (`GET /export/react`).  
- Optional: Tailwind theme snippet. ✅ (`GET /export/tailwind`, Export tab download).  
  - Depth (2026-09-21): `boxShadow`, `backgroundImage`, `fontSize`, `opacity`; section-prefix stripped keys (`primary` not `color-primary`).  
- Still no Flutter/Figma until demand is proven.  
- Plugin interface stays thin; prefer quality of two formats over many stubs.

---

## P4 — Promote parked intelligence (gates)

| Feature | Park reason | Promote when |
|---------|-------------|--------------|
| **Overview narrative** | Already in MVP | N/A (keep) |
| **Mood board** | Cost (Claude+DALL·E), Celery, not on extract spine | **Mood tab (2026-09-22):** `showMoodBoard=true` → AppShell **Mood**; themes-first; imagery composition Material×2 → Source → Type/grid; lighting stays off |
| **Lighting** | Separate API; couples to geometry | G1 consumer + flag-gated UI done; **parked default-off** (G3/G4 policy) |
| **Geometry** | Depth/normals side path; not token family | Gates G1–G4 met; API mounted; **off upload happy path** — see [P4_GEOMETRY_GATES.md](./P4_GEOMETRY_GATES.md) |

Focused gates doc: [P4_GEOMETRY_GATES.md](./P4_GEOMETRY_GATES.md).

Until Geometry exit criteria pass: **do not** feature lighting/geometry in README happy path or default App navigation (`showLighting*` stay off). Mood board is a dedicated **Mood** tab (`showMoodBoard=true`).

### P4 Geometry gates (go / no-go)

Start **Geometry only** (foundation for lighting). Mood board lives on its own Mood tab (not Overview Labs).

| Gate | Exit criterion |
|------|----------------|
| **Consumer** | Shadow quality **or** lighting tab consumes geometry extract output (depth/normals), not a stand-in |
| **MPS / CPU** | Apple Silicon MPS vs CPU fallback documented and **unit-verified** (`cpu_fast` / `cpu_accurate` force CPU; MPS depth + depth-gradient normals; Marigold CUDA-only) — see [P4_GEOMETRY_GATES.md](./P4_GEOMETRY_GATES.md) § G2 |
| **Default App nav OFF** | `showLightingTab` / `showLightingAnalyzer` remain `false`; `showMoodBoard` may be `true` for the **Mood** nav tab; geometry remains API-only |
| **Cost / latency** | **Accepted (2026-09-20):** cold load excluded; warm `cpu_fast` ≤ ~5s; warm MPS/CUDA ≤ ~2s; geometry `503` / lighting degrades; **geometry stays off upload happy path** — see [P4_GEOMETRY_GATES.md](./P4_GEOMETRY_GATES.md) § G4 |
| **Non-goals** | No mood board; no full multimodal; draft PR #168 stays unmerged |

**Status (2026-09-21):** G1–G5 held/pass; G2 profile-resolve **unit-verified**; G4 accepted. Production nav flags stay **`false`**. Remaining: optional live warm MPS dogfood; no default-on. See [P4_GEOMETRY_GATES.md](./P4_GEOMETRY_GATES.md).

---

## P5 — Platform (optional, later)

Sessions/libraries, batch/jobs, collaborative editing, multimodal inputs, Figma plugins — only after P1–P3 are stable. Treat [copy-that-phase13-archive](https://github.com/joshband/copy-that-phase13-archive) and [Copy](https://github.com/joshband/Copy) as **sibling products**, not in-tree requirements.

---

## Keep / park / archive (planning)

### Keep on happy path
- Projects, colors (streaming), spacing, typography, shadows, design-tokens W3C (+ CSS in P1)
- Overview narrative
- AppShell + UploadPanel + TokenExplorer (trimmed tabs)
- Design Guide Pack + Guide HTML on Export (DTCG honesty strip)

### Park (code may exist; off default path)
- Mood tab mood board (flag-on; Celery/cost-aware — see [MOOD_BOARD_SPECIFICATION.md](../features/MOOD_BOARD_SPECIFICATION.md))
- `lighting`, `geometry`
- `sessions`, `jobs`, `batch`, `multi_extract`
- AdvancedColorScienceDemo, TokenGraphDemo, CostDashboard, LibraryCurator
- Draft PR #168 extras that are not extract/export/overview

### Archive / historical (docs)
- STRATEGIC_VISION, MULTIMODAL_*, DUAL_CV detail, Phase 0 superpowers, Nov 2025 PRD → `~/Documents/copy-that-archive/` (architecture-history / planning-history)
- Sibling repos: `copy-this-archive`, `copy-that-phase13-archive`, `Copy`
- Missing `~/Documents/copy-that-archive` — recover PRD/history from **git** / GitHub, not that folder

---

## Suggested sequencing (calendar-agnostic)

1. **P0** (days): slim UI + docs SoT  
2. **P1** (1–2 weeks): export UX + smoke E2E + README  
3. **P2a** (1+ weeks): border/opacity family wave  
4. **P2b+** as capacity allows  
5. **P4 Geometry** first (gates + API-only); lighting/mood only after Geometry exit criteria  
6. **P5** platform only after P1–P3 stable (and preferably after deliberate P4)  

---

## Open decisions (track here)

- [x] CSS-only vs CSS+React for P1 export bar (default: **CSS + W3C**; React polish in P3 — done)  
- [x] Feature flags vs hard unmount for parked routers — **keep flags + keep routers mounted** (documented in `app_factory.py` / `featureFlags.ts`, 2026-09-19)  
- [x] Whether P2 uses DTCG composite `typography` only or also atomic font tokens — **both**: composites from extract/recommendation; atomic `fontFamily` / `fontWeight` derived at export (P2c)

### Harden wave (2026-09-19)

- Live Postgres extract→export (incl. all 13 `$type`s + CSS/React/Tailwind) verified  
- Typography auto mode falls back when AI auth missing  
- Single-color projects still get a synth gradient; `number.unity` preset if no numbers  
- Playwright canonical home: `frontend/tests/playwright/` (deprecated sibling folders are stubs only)  
- Dual Vite/package roots collapsed: canonical app is `frontend/`; root scripts delegate via `pnpm --dir frontend`  
- PR #168: draft park comment posted  

### P4 Geometry + debt cuts (2026-09-20)

- G1 lighting UI + G4 cost accept: [P4_GEOMETRY_GATES.md](./P4_GEOMETRY_GATES.md)  
- Dual CV: color + spacing + typography CV bodies under extractors; application shims — see [CURRENT_ARCHITECTURE_STATE.md](../architecture/CURRENT_ARCHITECTURE_STATE.md) (detail archived: `~/Documents/copy-that-archive/architecture-history/DUAL_CV_STACKS.md`)  
- Playwright leftovers cleared; overview/shape polish spec added  
- Shape polish: source chips, no fake grid confidence, no P2b/DTCG roadmap labels  
- CV fast path: text-mask; FastSAM/UIED/depth default-off; honest spacing fallback; dark-blob shadow opt-in  

### Dual-CV third cut + shadow quality + evidence (2026-09-20)

- Helpers relocated: FastSAM / UIED / debug / grid / layout-text → `extractors/cv_helpers/` (application/cv shims)  
- Shadow default: classical shadowlab → CSS elevation tokens + `opacity_from_shadows`; dark-blob stays opt-in; lighting flags stay false  
- Evidence packet: [docs/evidence/2026-09-20-dual-cv-shadow/](../evidence/2026-09-20-dual-cv-shadow/)  
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

- G2 profile-resolve unit matrix expanded (MPS / CUDA / force-CPU / no-accel) — [P4_GEOMETRY_GATES.md](./P4_GEOMETRY_GATES.md)  
- Flag-gated `LightingGeometryEvidence` surfaces `geometry_meta.warnings` (MPS depth-only / Marigold skip)  
- Geometry extract missing-deps → `503` unit-covered; `featureFlags` lighting stay **`false`**  
- Remaining gap: optional live warm MPS/CUDA dogfood (no default-on)

### P4 Mood tab + Guide Pack Export (2026-09-22)

- Mood board: `showMoodBoard=true` as AppShell **Mood** tab (Material×2 → Source → Typography/grid composition; themes-first)  
- Export: Design Guide Pack / Guide HTML first-class + 13-type honesty strip + gradient extract honesty  
- Lighting remains default-off

### Still open / post-stable (do not expand MVP scope here)

- Retire parked `src/pipeline` / `src/layout` / `src/typography` when unused  
- Merge PR #168 leftovers, P5 platform  
- Flipping production `showLighting*` to true  

### Next — P4 Mood dogfood

The image router is done. Style-locked boards exist (Flux Ultra Redux). Lighting, FastSAM, and depth stay default-off. The remaining P4 Mood gap is live dogfood plus board layout and label quality.

1. **Mood board image router** — **done**  
   - Hosted Flux via `MOOD_BOARD_FLUX_BASE_URL`; DALL·E + local mflux + token collage fallbacks.  
   - Policies: balanced/fast/cheap/private/quality; Mood routing select + selection footnotes.  

2. **Draft PR #168** — cherry-picked onto main (2026-09-20) with conflict resolution toward MVP defaults (lighting flags stay false; no FastSAM/depth default-on; stripped playwright-report + PR screenshot dumps). Leave remaining science/geometry polish as optional follow-up.

3. **Lighting / FastSAM / depth** — remain default-off (G3/G5). Geometry G2 unit-verified 2026-09-21; classical shadow path stays the MVP default. Optional: live warm MPS latency spot-check only.

4. **Parked package retire** (`src/pipeline` / `src/layout` / `src/typography`) — **retain** (2026-09-22): still imported by `tests/pipeline`, `tests/layout`, `tests/typography` and `panel_to_tokens`. Delete only after those suites are migrated or dropped.
