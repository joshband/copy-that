# Architecture Parity Check – Copy That vs. Strategic Vision vs. Copy-This-Archive
_Date: 2025-11-24 (updated)_

## Scope
- **Current app (Copy That)**: repo `copy-that` (advanced color/spacing demo, CV-first + AI refinement, project save/load with image + spacing metadata).
- **Target**: `docs/architecture/STRATEGIC_VISION_AND_ARCHITECTURE.md` (multi-token, governed, observable pipeline + exports).
- **Archive**: `copy-this-archive` (CV-first, richer token coverage and extractors; weaker architecture/governance).

---

## Parity Checklist (Current vs Target vs Archive)
- Token coverage
  - [x] Color (CV+AI, saves to DB)
  - [x] Spacing (CV+AI, returned; persistence as metadata only)
  - [ ] Typography
  - [ ] Shadows / radius / borders / animation
  - [ ] Cross-token variants/density (only in code, not wired)
- Pipeline orchestration
  - [~] Orchestrator code present; front-end simulates stages; CV-first, AI-second for color/spacing
  - [ ] Real multi-token orchestrated runs with per-run state/metrics
  - [ ] Streaming SSE by token type (partial: synchronous CV+AI merge)
- Persistence & snapshots
  - [x] Projects table; color tokens persisted; image + spacing tokens stored in description JSON
  - [ ] Spacing/typography DB tables; versioned snapshots; rollback
  - [ ] Project “snapshot” entity to store all token types atomically
- Project/Session UX
  - [x] Project create/load/save (disabled until tokens exist)
  - [ ] Session dashboard, run history, ownership enforcement
  - [ ] Batch/multi-image runs
- Validation
  - [~] WCAG/harmony for color; semantic names
  - [ ] Validation for spacing/typography/shadows; design rulesets
- Generation/Exports
  - [ ] W3C/CSS/React/Tailwind/Figma/diff UI (generators exist but not exposed)
- Auth/Governance
  - [ ] AuthN/Z, ACL, audit, rate limits (owner_id column only)
- Observability
  - [ ] Per-run metrics/logs dashboards; current /metrics only
- UI demos
  - [x] Advanced color/spacing page; light theme
  - [ ] Unified homepage + demos for typography/shadow/animation
- Fail-safety
  - [x] CV fallback for color/spacing; AI errors degrade gracefully
  - [ ] Token-level retry/backoff across all types

Legend: [x] done, [~] partial, [ ] missing.

---

## Comparison Table (Deeper)
| Area | Current (Copy That) | Target (Strategic Vision) | Archive (copy-this-archive) | Gaps / Actions |
| --- | --- | --- | --- | --- |
| Token Types | Color (CV+AI), Spacing (CV+AI, no DB table), no typography/shadow | Full set: color, spacing, typography, shadow, radius, animation, states | Color, spacing, typography CV/AI pipelines present | Add DB + endpoints for spacing/typography/shadow; port archive extractors; single token schema with per-type adapters |
| Ingestion | Single-image upload (base64/URL); no batch | Multi-modal (img/video/audio/doc), batch | Image upload + some batch hooks | Add batch ingest and modal detection; reuse archive batch planner |
| Preprocess | Minimal; implicit in UI | Robust CV/ML preprocess per modality | CV preprocess (opencv/pillow) available | Port archive preprocess modules; expose per-token preprocess configs |
| Extract (fast path) | CV color (Pillow+coloraide), CV spacing (OpenCV gaps); AI refinement via OpenAI | CV-first for all types; AI refinement optional/streaming | CV-first implemented for color/spacing/typography | Port CV typography/shadow; add token-type registry; stream CV immediately |
| Extract (AI path) | OpenAI vision; merges CV+AI; spacing AI via OpenAI | AI enrichment per type; tiered models | Claude/OpenAI; prompt-rich; tiered | Keep OpenAI default; add prompt+JSON per token; tiered models; streaming SSE |
| Aggregation/Provenance | Basic dedup for color; no provenance graph | Cross-token dedup, provenance, lineage | Provenance light | Add provenance map per token id; merge policies (cv→ai→user) |
| Validation | WCAG/harmony for color | Design/accessibility rules across all tokens | Minimal | Extend validators per type; quality scoring |
| Generation/Exports | Generators in code (CSS/React/Tailwind/W3C) not surfaced in UI | Full export suite + diffing | Some style guide generation | Add export UI; token diffing; Figma export hook |
| Persistence | Projects table; colors stored; spacing tokens in JSON; project image stored | Token library, versioned snapshots, rollback | Projects + colors | Add spacing/typography tables; snapshot table; rollback/versioning |
| Sessions/Runs | Not exposed; manual project ID | Session dashboard, run history, ownership | Simple runs | Build session service; per-run telemetry; ownership enforcement |
| Auth/Gov | owner_id column only | AuthN/Z, ACL, audit, rate limits | None | Implement auth; tenant scoping; quotas |
| Observability | /metrics only | Per-run metrics/logs dashboards | Minimal | Instrument pipeline; store run metrics; UI dashboard |
| UI | Advanced color/spacing page; Save disabled until tokens; load restores image/spacing metadata | Unified Copy That home; demos for all tokens | Simple color demo | Make `/` the unified page; add typography/shadow demos; SSE-driven updates |
| Failover | CV fallback if AI fails | Graceful 0-many tokens; retries | Some fallbacks | Add retries/backoff per type; snapshot commit even on partials |

---

## Architectural Alignment (Guidance)
- **CV-first, AI-second (streaming):** Already for color/spacing; extend to all token types; emit CV tokens immediately, then AI deltas via SSE tagged by token type/id.
- **Canonical token schema + adapters:** Keep one token model with per-type extensions; avoid duplicate fields; provenance shows source (cv/ai/user) and step.
- **Snapshot-first persistence:** Projects own immutable snapshots (all token types + source image + preprocess manifest). Store per-type tables for query; snapshot blob for restore.
- **Registry-driven extractors/generators:** Register CV extractor + AI refiner + generator per token type; orchestrator fans out based on requested token types.
- **Fail-safe:** Allow 0-many tokens; CV fallback; partial commits; retries around AI calls.

---

## Recommended Next Moves (ordered)
1) **Routing/UI:** Make `/` the unified Copy That page; keep `/color` and `/spacing` as focused demos.
2) **Token coverage:** Port archive CV extractors for typography/shadow; add spacing DB table + `/projects/{id}/spacing`; add snapshot entity.
3) **Multi-token extract endpoint:** Accept token_types list; run CV in parallel; stream AI refinements; merge per token id.
4) **Snapshots & persistence:** Add project_snapshots with versioning; move spacing out of description JSON; store source image ref.
5) **Export surface:** Expose generators (CSS/React/Tailwind/W3C/Figma) in UI with diffing.
6) **Validation:** Extend validators per type (spacing, typography, shadow) with scoring.
7) **Observability:** Per-run metrics/logs; UI dashboard; keep graceful partial success.
8) **Auth/Governance:** Add authN/Z, ACL, audit, rate limits; enforce owner_id on projects/snapshots.

---

## Color Implementation Plan (Copy That vs Copy-This-Archive)
**Current (copy-that):** CV+AI (OpenAI) with SSE; rich metadata (WCAG, semantic names, harmony); colors persisted per project; UI saves/loads projects; spacing tokens also fetched on load. Missing batch/multi-image, snapshots/versioning, exports UI, provenance graph, diffing, token-level retry, observability, auth.

**Archive strengths to reuse:** richer CV palette/histogram analysis (coloraide), tiered AI prompts, variation system, style guide generator, schema validator, batch extract/routing planner.

**Plan (phased):**
1) Extractors: port archive CV color extractor (palette + histogram significance); add tiered AI modes; keep OpenAI default; add batch color endpoint.
2) Persistence: add `project_snapshots` (immutable bundles of all colors + source image); versioning/rollback; provenance per token (source cv/ai/user, model, step).
3) Variation/Style guide: port variation system and style guide generator; expose `/exports/style-guide`; UI panel.
4) Exports/Diff: surface generators (CSS/React/Tailwind/W3C/Figma stub); snapshot diff API + UI.
5) Quality/Retry: add quality scores; token-level retry/backoff for AI; CV fallback always.
6) Observability/Auth: per-run metrics/logs; dashboards; enforce ownership/rate limits on color endpoints.
7) UI: wire SSE multi-extract to show color streaming, batch runs, exports/diff, snapshot restore.

Recent changes:
- Added batch color endpoint (`/api/v1/colors/batch`) with optional persistence.
- Added project_snapshots table and snapshot persistence for color+spacing via SSE multi-extract.

---

## Spacing Implementation Plan (Copy That vs Copy-This-Archive)
**Current (copy-that):** CV spacing (OpenCV gaps) + AI refinement (OpenAI); SSE streaming; DB table `spacing_tokens`; project load fetches spacing tokens; saved image retained. Missing typography/shadow, snapshots/versioning, variation system for spacing, exports UI, batch/multi-image, provenance, diffing, observability, auth.

**Archive strengths to reuse:** richer spacing extractors (edge + SAM, enhanced spacing), variation system (compact/standard/spacious), validation rules, style guide outputs, batch extraction, routing planner.

**Plan (phased):**
1) Extractors: port archive enhanced spacing (SAM/edge) as CV fast path; keep OpenAI refinement; add batch spacing endpoint.
2) Persistence: include spacing in `project_snapshots` with versioning/rollback; keep `spacing_tokens` table; provenance fields.
3) Variation/Style guide: port spacing variation system and style guide pieces; expose in exports API/UI.
4) Exports/Diff: include spacing in CSS/Tailwind/W3C exports; snapshot diff API/UI.
5) Quality/Retry: spacing validation (grid compliance, density), quality scores, retry/backoff for AI, CV fallback.
6) Observability/Auth: per-run metrics/logs; dashboards; enforce ownership/rate limits.
7) UI: SSE multi-extract shows spacing streaming; load snapshot restores spacing; batch UI for multi-image spacing.
