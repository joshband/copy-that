# Testing Guide

**Last Updated:** 2026-10-09

Canonical commands for backend (Makefile) and frontend (`pnpm`). Do not treat old pass-count snapshots as SoT — run the suites.

---

## Quick reference

```bash
# Required local validation
make check          # mypy + ruff lint/format + tsc + eslint
make verify         # check + full Vitest + pytest unit/integration

# Backend
make test-quick     # smoke (few minutes)
make test           # fuller suite
make coverage       # HTML → htmlcov/index.html
make test-watch     # pytest watch / TDD

# Frontend (root scripts → frontend/)
pnpm test:all       # full Vitest suite, single run (used by make verify and CI)
pnpm test:split     # phased unit → components → integration
pnpm test:coverage
pnpm type-check

# E2E (Playwright — frontend/tests/playwright/)
pnpm test:e2e
PLAYWRIGHT_PORT=5199 pnpm test:e2e:mvp   # mocked MVP smoke pack on a fresh port
```

CI memory tip for Vitest:

```bash
NODE_OPTIONS="--max-old-space-size=4096" pnpm test:split
```

---

## What lives where

| Layer | Location | Runner |
|-------|----------|--------|
| Python unit | `tests/unit/` | pytest via Make |
| Python integration | `tests/integration/` | pytest via Make |
| Frontend unit | `frontend/src/**/__tests__` | Vitest via `pnpm test*` |
| JS E2E | `frontend/tests/playwright/` | `pnpm test:e2e*` |

CI collects Python tests only from `tests/unit/` and `tests/integration/`. Add backend
tests there so CI runs them. Browser tests live only in `frontend/tests/playwright/`;
the former Python UI suites were retired. Do **not** add new Playwright specs under
deprecated trees (`frontend/playwright/`, `tests/playwright/`).

---

## Recommended loops

| Goal | Commands |
|------|----------|
| While coding | IDE + `make test-watch` or focused `pnpm test <path>` |
| Before finishing a change / commit | `make verify` |
| Before merge / release | `make verify` · mocked MVP Playwright on a fresh port |
| Coverage | `make coverage` · `pnpm test:coverage` |

`make ci-local` is an alias for `make verify`. `make verify` covers lint, format,
type checks, full Vitest, and Python unit/integration tests. The CI security job
(secret scanning, dependency audits, Bandit) and Playwright are separate gates;
a local verification pass does not establish their results.

Agent conventions: [AGENTS.md](../../AGENTS.md).

---

## Optional dependency coverage

`make install` installs development tools and `cv-deep` for the full geometry test
suite. A core-only environment should also be checked independently: installed
optional packages can hide accidental eager imports. Core startup does not prove
live geometry/model behavior. Google SDK integrations use the separate `gcp` extra.
See [setup](../setup/start_here.md#optional-runtime-dependencies).

## Markers & focus (backend)

```bash
.venv/bin/pytest tests/unit -q -m "not slow"
.venv/bin/pytest tests/integration -q -m "not slow"
```

Prefer Make targets over inventing one-off flags unless debugging.

---

## Extraction accuracy

The hermetic [accuracy evaluation](../../tests/unit/regression/test_extraction_accuracy.py)
renders synthetic screenshots with known palettes and spacing. It scores color
recall and precision using perceptual color distance, and checks recovery of the
spacing system. Thresholds live in the test, not this guide.

```bash
.venv/bin/pytest tests/unit/regression/test_extraction_accuracy.py -q -s --no-cov
```

Use the printed scores to investigate regressions before changing thresholds.
Synthetic CV results do not establish live AI extraction quality; live dogfood
requires a separate explicit action and evidence packet.

## Playwright server isolation

Local Playwright reuses an existing server at its configured URL. Choose an unused
port to avoid testing stale code; change this example port if it is already occupied.
Unset `BASE_URL` when you want `PLAYWRIGHT_PORT` to determine the target URL.

```bash
env -u BASE_URL PLAYWRIGHT_PORT=5199 pnpm test:e2e:mvp
```

The MVP pack mocks API responses. It verifies browser interactions and rendering,
not live extraction, provider availability, or paid generation.

---

## Evidence / screenshots

Optional Playwright evidence capture: `pnpm test:e2e:evidence`. Dogfood packs under `docs/evidence/` are retained until ~2026-12-20 per their READMEs.
