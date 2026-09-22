# Design Guide Pack

**Date:** 2026-09-22  
**Companion to:** [W3C_CONFORMANCE.md](W3C_CONFORMANCE.md)  
**Artifacts:** `guide.pack.json` + self-contained `guide.html`

## Purpose

A **Design Guide Pack** is a product-layer brand guide built on top of the
official DTCG token graph. It does **not** invent new Format `$type`s. Brand
roles, materials, and component slots are:

- references to token ids, and/or
- namespaced `$extensions` (`com.copythat.*`) on those tokens.

## Taxonomy

| Layer | Contents | DTCG relationship |
|-------|----------|-------------------|
| **Brand identity** | Name, voice (1–2 sentences), palette roles, typography voices, material *labels* | Roles map to token ids; materials are labels only |
| **Foundations** | Colors, spacing/dimension, type, shadows, gradients, shape/opacity, motion | Direct refs into exported `$type` sections |
| **Components** | Catalog entries (button, card, …) with slots | Slot → token id; `source: illustrative` unless from extract |
| **Application** | CSS vars, React theme, a11y notes | Implementation guidance; not tokens |

## Schema (`GuidePack`)

Pydantic models in [`src/copy_that/guide_pack/`](../../src/copy_that/guide_pack/):

- `meta` — version, project id, `token_snapshot_hash`, type coverage, source counts  
- `brand` — name, voice, palette/typography role maps, materials  
- `foundations` — lists of token ids by family  
- `components[]` / `applications[]` — structured slots + notes  
- `exports` — links to w3c / css / react / tailwind / guide-html  

Built from `_build_export_repo` + optional overview metrics heuristics.

## HTTP

- `GET /api/v1/design-tokens/export/guide-pack` → JSON  
- `GET /api/v1/design-tokens/export/guide-html` → self-contained HTML  

## Honesty

The pack’s `meta.source_counts` and `meta.type_coverage` mirror the capability
map ([`dtcg_capability.py`](../../src/copy_that/extractors/dtcg_capability.py)):
**live extract** vs **derive** vs **synth/preset**. Motion types stay on the
cue/preset path — no fake extractors.

## Non-goals

- New DTCG `$type`s for widgets / materials / mood  
- PDF / Figma / Flutter generators  
- Strict Color Module migration  

Mood board is product-gated separately (Overview Labs); Guide Pack does not embed mood imagery.  
