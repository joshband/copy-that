# Changelog

## 1.0.2 — 2026-09-20

### Hydrate + confidence + contracts

- Hydrate the token graph when core extract stages complete (not only when colors arrive), so Overview Snapshot fills for chrome/soft-card fixtures
- CV confidence calibration + spacing Fallback honesty (`TokenSourceChip`, Measured vs Fallback %)
- Visual contracts / MVP Playwright pack evidence; UI dogfood packet under [docs/evidence/2026-09-20-ui-dogfood/](docs/evidence/2026-09-20-ui-dogfood/)

### Follow-up (same day, post-tag)

- Spacing AI+CV merge prefers measured CV confidence; CV fallback stays ~15% (no AI-inflated “80% fallback”)
- API responses include `spacing_confidence_breakdown` for Snapshot honesty

## 1.0.1 — 2026-09-20

### Dual-CV fifth cut

- Deleted legacy shims: `src/core/`, `src/cv_pipeline/`, `src/copy_that/application/cv/`
- Migrated callers/tests/scripts to `copy_that.core_tokens` / `copy_that.extractors.cv` / family extractors
- Fixed spacing `layout_image` numpy truthiness crash; refreshed spacing monkeypatch tests
- Dogfood packet: [docs/evidence/2026-09-20-dogfood/](docs/evidence/2026-09-20-dogfood/)

## 1.0.0 — 2026-09-20

Stable MVP release.

### Highlights

- All four token families on the happy path (color, spacing, typography, shadow)
- Dual-CV absorb: shared CV under `copy_that.extractors.cv` / `cv_helpers`; token graph under `copy_that.core_tokens` (legacy `cv_pipeline` / `core.tokens` are shims)
- Shadow default: classical shadowlab → CSS elevation tokens; dark-blob CV opt-in only
- P4 geometry (lighting) gated behind default-off feature flags; G1–G5 held
- Frontend MVP Playwright pack in medium-tier CI

### Not in 1.0

- Mood board promotion, draft PR #168 merge, P5 platform
- Production lighting / mood nav flags remain off
