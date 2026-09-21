# DEPRECATED — not a Playwright suite

Dated capture artifacts only (full-page PNG dumps for human review). **Canonical E2E:** [`frontend/tests/playwright/`](../frontend/tests/playwright/README.md) via `pnpm test:e2e`.

PNG dumps under this folder are **gitignored** — only this README is tracked.

## How dumps are produced

| Command | Writes here? |
|---------|----------------|
| `pnpm test:e2e:evidence` | Yes — `playwright-tests/<stamp>-mvp-tabs/` (mocked extract + MVP tabs) |
| `PLAYWRIGHT_CAPTURE_EVIDENCE=true` + any spec using `maybeCaptureEvidence` | Yes when gated |
| `token-data-points.spec.ts` | Yes — always (deep live walkthrough) |

Helper: [`frontend/tests/playwright/helpers/evidenceCapture.ts`](../frontend/tests/playwright/helpers/evidenceCapture.ts).

Do **not** auto-promote PNGs into `docs/evidence/` — copy manually when dogfooding. No pixel `toHaveScreenshot` baselines.
