# DECISIONS.md
# Architectural & Product Decision Records

This document records **high‑impact, non‑trivial decisions** made in Copy That.
The goal is to preserve *context, rationale, and tradeoffs* so decisions are not
re‑litigated later.

---

## ADR‑001: Multi‑Extractor Orchestration
**Status:** Accepted
**Context:** Design screenshots contain overlapping signals (color, spacing,
typography, shadow) that are best extracted using different techniques.
**Decision:** Use parallel, multi‑extractor orchestration instead of a monolithic
pipeline.
**Consequences:**
- Faster wall‑clock extraction
- More complex orchestration logic
- Requires standardized metadata and merging strategies

---

## ADR‑002: Token‑Agnostic Frontend via Adapters
**Status:** Accepted
**Context:** Token types evolve, but UI components should remain reusable.
**Decision:** Introduce adapter interfaces so frontend components are token‑agnostic.
**Consequences:**
- Reduced UI duplication
- Slight upfront abstraction cost
- Easier addition of new token types

---

## ADR‑003: Cloud Run + Neon Architecture
**Status:** Accepted
**Context:** Need low‑ops, scalable infra without managing servers.
**Decision:** Deploy on GCP Cloud Run with Neon Postgres.
**Consequences:**
- Automatic scaling
- Requires explicit connection + migration discipline
- Cold‑start considerations

---

## ADR‑004: Token Graph as Canonical Representation
**Status:** Accepted
**Context:** Tokens require explicit relationships (aliasing, composition, multiples-of,
containment) and must be exported to multiple formats (W3C, CSS, React) without
losing structure or provenance.
**Decision:** Keep a graph-based token repository as the canonical representation;
all exporters and generators derive outputs from this graph via adapters.
**Consequences:**
- Consistent relationship handling across token types
- Requires adapters for each export format and UI consumption
- Enables resolver generation and cross-token validation

---
