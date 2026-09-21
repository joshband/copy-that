# Playwright (canonical)

**Canonical home for browser E2E:** this directory (`frontend/tests/playwright`).

Run from repo root:

```bash
pnpm test:e2e
# or
pnpm exec playwright test -c frontend/playwright.config.ts
```

Config: [`frontend/playwright.config.ts`](../playwright.config.ts) (`testDir: 'tests/playwright'`).

MVP smoke pack (`pnpm test:e2e:mvp`):  
`mvp-phase1-smoke` + `overview-shape-polish` + `ui_redundancy` + `tabs_layout` + `visual-contracts`.  
Script sets `PLAYWRIGHT_USE_MOCKS=true` so mocked contracts are not skipped. Assertion-only — no screenshot dumps.

Evidence dumps (optional, local):  
`pnpm test:e2e:evidence` sets `PLAYWRIGHT_CAPTURE_EVIDENCE=true` + mocks and runs `evidence-screens` → full-page PNGs under `playwright-tests/<stamp>/`. Promote to `docs/evidence/` by hand. Helper: [`helpers/evidenceCapture.ts`](./helpers/evidenceCapture.ts).

Medium-tier CI (`ci-tiered.yml` → `frontend-playwright-mvp`) runs the same pack with Chromium.

## Deprecated sibling trees (stubs only — no specs)

| Path | Status |
|------|--------|
| `frontend/playwright/` | Stub README only (orphaned overview/metrics/relations removed 2026-09-20) |
| `tests/playwright/` (repo root) | Stub README only (soft shadow smokes removed; use `shadow-tokens.spec.ts`) |
| `playwright-tests/` | Artifact / dated dumps — not a test suite |

Add new E2E only here. Python UI E2E (`tests/ui/`) is a separate stack.
