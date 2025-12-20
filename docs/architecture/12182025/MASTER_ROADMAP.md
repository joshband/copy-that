# MASTER_ROADMAP.md
# Copy That – Master Roadmap & Navigation

This document is the canonical index and sequencing guide for all roadmap and completion artifacts.
It explains *what is done*, *what is next*, and *why the order matters*.

---

## Completed Work (Ground Truth)

These documents describe work that is **verified in code, tests, and migrations**.

- **COMPLETED.md** – Initial completed feature set
- **COMPLETED_02.md** – Extended completed work from docs
- **COMPLETED_03.md** – Architecture consolidation & pipeline maturity
- **COMPLETED_04.md** – Verified completed platform & CI work

> Rule: Items only belong in COMPLETED if they are observable in the codebase or CI.

---

## Active & Planned Roadmaps

### ROADMAP_05 – Architecture & Refactor Foundation
**Focus:** correctness, maintainability, velocity

Key themes:
- Enforced domain boundaries
- Standardized extractor orchestration
- Token schema normalization
- Frontend/backend contract hardening
- Test pyramid rationalization

This roadmap is a **prerequisite** for nearly everything that follows.

---

### ROADMAP_06 – CI/CD, Security & Operations
**Focus:** risk reduction, reliability, security posture

Key themes:
- Single-source-of-truth CI
- Mandatory staging migrations
- Cloud Run authentication
- Workload Identity standardization
- Neon preview DB decision

This roadmap hardens delivery so future work is safe.

---

### ROADMAP_07 – Product & Platform Expansion
**Focus:** new capabilities and scale

Key themes:
- Token graph & dependency analysis
- Generator plugin ecosystem
- Generative UI pipeline
- SaaS & multi-tenancy hardening

This roadmap should only be pursued once ROADMAP_05 and 06 are largely complete.

---

## Recommended Execution Order

1. **ROADMAP_05** – Fix structure before adding power
2. **ROADMAP_06** – Make delivery safe and predictable
3. **ROADMAP_07** – Expand into a true platform

Skipping this order will increase rework and operational risk.

---

## How to Use These Docs

- Use **ROADMAP_05–07** to generate GitHub issues
- Use **COMPLETED_xx** as historical record and audit trail
- Update MASTER_ROADMAP.md whenever a roadmap is completed

---

## Governance Rules

- No new major features without ROADMAP_05 alignment
- No production deploys without ROADMAP_06 controls
- No platform promises without ROADMAP_07 capacity planning

---

## Status Tracking (Recommended)

Add a simple status badge to each roadmap:
- ⏳ Planned
- 🚧 In Progress
- ✅ Complete

---

## Next Documents

Planned future additions:
- **ROADMAP_08.md** – Performance, cost, ML inference optimization
- **ROADMAP_09.md** – Ecosystem, marketplace, and integrations
