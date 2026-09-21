# Evidence — dual-CV third cut + shadow quality (2026-09-20)

**Proof question:** Did we move high-traffic CV helpers under extractors, ship classical CSS shadows by default (dark-blob still opt-in), and leave lighting flags off — with measurable pass/fail evidence?

**Kind:** QA / validation evidence (local API + offline unit + mocked Playwright). No secrets.

## Manifest

| Asset | Proves |
|-------|--------|
| `hero/app-home.png` | Shipped product home surface (Vite @ 5173) |
| `details/upload-surface.png` | Upload / first-viewport composition |
| `supporting/synthetic-card-shadow.png` | Synthetic card used for classical shadow live call |
| `logs/shadow-extract-gradient.json` | Live `POST /api/v1/shadows/extract` → `cv_classical_css`, 3 tokens, opacity_from_shadows |
| `logs/shadow-extract-live.json` | Flat `sample.png` → honest `cv_classical_empty` (no invented elevation) |
| `logs/classical-offline.json` | Offline extractor path (~442 ms, 3 CSS tokens) |
| `logs/unit-tests.txt` | Focused pytest (helpers + shadow) — 11 passed |
| `logs/vitest-focused.txt` | TokenSourceChip + featureFlags.policy — 6 passed |
| `logs/type-check.txt` | `pnpm type-check` clean |
| `logs/playwright-mvp.txt` | `pnpm test:e2e:mvp` — 3 passed (smoke + overview-shape-polish) |

## Metrics (live)

| Call | Latency | Result |
|------|---------|--------|
| Shadows extract (synthetic card) | ~4676 ms | 200 · 3 tokens · conf ≈ 0.50 · `cv_classical_css` |
| Shadows extract (flat sample.png) | ~7311 ms | 200 · 0 tokens · `cv_classical_empty` |
| Classical offline (same card) | ~442 ms | 3 tokens · opacity token emitted |
| Playwright MVP pack | ~9.3 s | 3/3 passed |
| Focused pytest | ~7 s | 11 passed |

## Constraints held

- `ENABLE_DARK_BLOB_SHADOW_CV` default off
- `showLightingTab` / `showLightingAnalyzer` / `showMoodBoard` remain `false`
- No merge of PR #168 / mood board / P5

## Retention

Keep until **~2026-12-20** (~90 days from evidence date 2026-09-20), then move to `~/Documents/copy-that-archive/`.
