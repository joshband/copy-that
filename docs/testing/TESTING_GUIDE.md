# Testing Guide

**Last Updated:** 2026-09-21

Canonical commands for backend (Makefile) and frontend (`pnpm`). Do not treat old pass-count snapshots as SoT — run the suites.

---

## Quick reference

```bash
# Backend
make check          # mypy + ruff + pnpm type-check
make test-quick     # smoke (few minutes)
make test           # fuller suite
make coverage       # HTML → htmlcov/index.html
make test-watch     # pytest watch / TDD

# Frontend (root scripts → frontend/)
pnpm test           # Vitest run
pnpm test:split     # phased unit → components → integration
pnpm test:coverage
pnpm type-check

# E2E (Playwright — frontend/tests/playwright/)
pnpm test:e2e
pnpm test:e2e:mvp   # MVP smoke pack
```

CI memory tip for Vitest:

```bash
NODE_OPTIONS="--max-old-space-size=4096" pnpm test:split
```

---

## What lives where

| Layer | Location | Runner |
|-------|----------|--------|
| Python unit / integration | `tests/` | `pytest` via Make |
| Frontend unit | `frontend/src/**/__tests__` | Vitest via `pnpm test*` |
| JS E2E | `frontend/tests/playwright/` | `pnpm test:e2e*` |
| Python UI E2E | `tests/ui/` | separate; use only when needed |

Do **not** add new Playwright specs under deprecated trees (`frontend/playwright/`, `tests/playwright/`).

---

## Recommended loops

| Goal | Commands |
|------|----------|
| While coding | IDE + `make test-watch` or focused `pnpm test <path>` |
| Before commit | `make check` · `make test-quick` · `pnpm test` |
| Before merge / release | `make ci-local` (if available) · `pnpm test:e2e:mvp` |
| Coverage | `make coverage` · `pnpm test:coverage` |

Agent conventions: [../guides/AGENTS.md](../guides/AGENTS.md).

---

## Markers & focus (backend)

```bash
pytest tests/unit -q -m "not slow"
pytest tests/ -m "integration and not slow"
```

Prefer Make targets over inventing one-off flags unless debugging.

---

## Evidence / screenshots

Optional Playwright evidence capture: `pnpm test:e2e:evidence`. Dogfood packs under `docs/evidence/` are retained until ~2026-12-20 per their READMEs.
