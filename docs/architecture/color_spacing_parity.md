Here’s a comprehensive evaluation of color implementation, comparing what we have in copy-that vs. what’s available in copy-this-archive, plus a concrete plan to close the gaps.

Current State – copy-that

- Extractors: CV-first (Pillow+coloraide) + AI (OpenAI) with SSE streaming; merges CV+AI; robust metadata (WCAG, semantic names, harmony, temperature, variants).
- Persistence: Colors persisted to DB per project; project save/load works; SSE path streams color tokens.
- UI: Unified page at / with upload, parallel extract (color+spacing), project save/load; shows tokens (no typography/shadow panels yet).
- Gaps: No batch/multi-image; no token provenance graph; exports not surfaced (CSS/React/Tailwind/W3C, Figma); no diffing; no per-token retry/backoff; no color snapshot versioning; no streaming UI for additional token types.

What copy-this-archive offers (color)

- Rich CV extractors: coloraide quantization, palette analysis, histogram significance.
- AI refiners (Claude/OpenAI), prompt-rich, tiered models.
- Variation system (compact/standard/spacious), style guide generator.
- Schema validator, routing planner, batch extraction.
- Style guide outputs and Tailwind/React/W3C hooks (scattered).

Gaps there: loose typing, duplication, limited governance/observability.

What’s missing in copy-that vs archive
- Batch/multi-image color extraction and aggregation.
- Variation system and style guide generation exposed in API/UI.
- Export/diff surface (CSS/React/Tailwind/W3C/Figma).
- Provenance/lineage and token-level quality scoring.
- Snapshot/versioning for colors (per-project immutable snapshots).
- Observability: per-run timings/metrics/logs for color pipeline.
- Auth/governance: none enforced in UI/API.

Implementation Plan (color)
Extractors
- Port archive’s richer CV color extractor (palette, histogram significance) into copy_that.application.cv.
- Add tiered AI models (fast/rich) and configurable prompts; keep OpenAI as default.
- Add batch endpoint: multi-image color extraction + aggregation.

Persistence/Snapshots
- Add project_snapshots table with immutable blobs (all color tokens + source image + metadata) and versioning/rollback.
- Keep per-token tables for querying; link tokens to snapshots.

Variation/Style Guide
- Port variation system (compact/standard/spacious) and style guide generator; expose via /exports/style-guide and UI panel.

Exports & Diffing
- Surface generators (CSS/React/Tailwind/W3C, Figma stub) via API + UI.
- Add snapshot diff endpoint (old vs new) and UI view.

Provenance/Quality
- Add provenance fields (source cv/ai/user, model, step) per token.
- Add quality scoring (contrast, harmony, semantic name confidence).
- Token-level retry/backoff around AI; keep CV fallback.

Streaming/UI
- Extend SSE to batch and multi-token types; keep CV-first, AI-second updates per token id.
- Show streaming state per token type; allow cancel/retry.

Observability
- Instrument per-run metrics (latency CV/AI, token counts, errors); store logs; dashboard view.

Auth/Governance
Enforce project ownership on color endpoints; add authN/Z, rate limits; audit logs.

Not yet surfaced in the UI or API contracts you use day‑to‑day:

Token types: Typography/shadow/radius/animation aren’t exposed; SSE still streams only color + spacing.
Batch endpoints: Color batch and spacing batch exist, but the UI doesn’t call them.
Snapshots: List/fetch endpoints are live and “Load Latest Snapshot” is wired, but there’s no snapshot list/selector in the UI or restore of other types.
Enhanced CV extractors: Only basic CV color/spacing are live; enriched palette/histogram (color) and SAM/edge spacing are not ported/exposed yet.
Exports/Variation: Generators (CSS/React/Tailwind/W3C/Figma), variation/style-guide, and diffing are not exposed in the UI.
Provenance/quality/observability: Provenance graph, quality scores, per-run metrics/logs, and dashboards aren’t exposed.
Auth/governance: No UI or API enforcement of auth/ownership/rate limits.yes
