---
name: playwright-ui-report
description: Generate or refresh Copy That Playwright HTML reports and UI summary reports, including overview screenshots, layout metrics, extraction-flow screenshot bundles, and timing + random UI image capture. Use when asked to run `pnpm ui:report`, capture Overview layout screenshots/metrics, or provide Playwright HTML report artifacts.
---

# Playwright UI Report

## Overview

Run the Copy That UI report workflow that produces the Playwright HTML report plus the UI summary with screenshots, layout metrics, timing, a random UI image capture, and the extraction-flow screenshot bundle. Provide a short status summary and point to the artifacts.

## Workflow

1. Confirm repo root contains `package.json` with the `ui:report` script.
2. Run `pnpm ui:report` (includes overview layout metrics + extraction-flow screenshots + random UI image capture + local change scope).
   - For pre-PR reporting against `origin/main`, run `pnpm ui:report:pr` (or set `UI_REPORT_BASE_REF`).
3. If the dev server cannot bind to `127.0.0.1:5173`, rerun with `PLAYWRIGHT_PORT=<open-port>` (example: `PLAYWRIGHT_PORT=5174 pnpm ui:report`).
4. Verify artifacts exist:
   - `frontend/playwright-report/index.html`
   - `frontend/test-results/ui-report/ui-summary.md`
   - `frontend/test-results/ui-report/layout-metrics.json`
   - `frontend/test-results/ui-report/screenshots/overview-1280.png`
   - `frontend/test-results/ui-report/screenshots/overview-360.png`
   - `frontend/test-results/ui-report/screenshots/overview-480.png`
   - `frontend/test-results/playwright/results.json`
   - `frontend/test-results/ui-report/random-ui/<timestamped-image>`
   - `playwright-tests/<YYYY-MM-DD-HH-MM-SS>/extraction-flow-exposes-token-data-points-and-captures-screens-*.png`
5. Summarize results in the response: test pass/fail, start/end timing, default viewport, key layout metrics, local/unpushed change scope, any missing artifacts, the random UI image picked, and the location of the extraction-flow bundle.

## Output Notes

- Do not open browsers or GUI apps; provide the report paths.
- If users want new viewports or different overview screenshots, update the list in `frontend/tests/playwright/overview_mobile_layout.spec.ts`.
- If users want different extraction-flow screenshots, update the capture list in `frontend/tests/playwright/token-data-points.spec.ts`.
- To override the random UI image directory, set `UI_REPORT_IMAGE_DIR=/path/to/images`.
- To target a different PR base, set `UI_REPORT_BASE_REF=<remote/branch>` or run `UI_REPORT_MODE=pr`.
