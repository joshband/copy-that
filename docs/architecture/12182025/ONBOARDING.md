# ONBOARDING.md
# Copy That – Developer Onboarding

This guide helps new contributors build a correct mental model quickly.

---

## System Mental Model
1. User uploads an image
2. Image is preprocessed
3. Multiple extractors run in parallel
4. Tokens are merged and normalized
5. Tokens are served to frontend and generators

---

## Core Directories
- `src/` – backend logic
- `frontend/` – React UI
- `docs/` – design and planning docs

---

## Getting Started
```bash
make install
make dev
```

---

## Safe Areas to Change
- UI components
- New extractors
- Generators

## Areas Requiring Caution
- Token schemas
- Orchestrator contracts
- CI workflows

---
