# Dogfood — 2026-09-20 (post shim deletion)

Offline CV extractor pass on available screenshots after dual-CV fifth cut
(`core` / `cv_pipeline` / `application/cv` removed).

## Images

| Image | Notes |
|-------|--------|
| `docs/evidence/2026-09-20-dual-cv-shadow/hero/app-home.png` | App chrome screenshot |
| `docs/evidence/2026-09-20-dual-cv-shadow/details/upload-surface.png` | Upload surface screenshot |
| `docs/evidence/2026-09-20-dual-cv-shadow/supporting/synthetic-card-shadow.png` | Soft card shadow fixture |
| `tests/fixtures/test_image.png` | Colorful synthetic fixture |

Raw JSON: [dogfood-results.json](./dogfood-results.json)

## Results (summary)

Refreshed after classical confidence + prominence calibration:

| Image | Color | Spacing | Shadow | Typography |
|-------|-------|---------|--------|------------|
| app-home | OK (~0.46 prominence-weighted) | OK (base 6, conf ~0.81) | empty (no elevation cues) | OK (15 OCR tokens after junk filter) |
| upload-surface | OK (~0.45) | OK (floored base, conf ~0.78) | empty | OK (16 OCR tokens) |
| synthetic-card | OK (~0.51) | **4pt fallback** (conf 0.15, `fallback=1`) | classical CSS ~0.58 | 0 OCR (no text) |
| test_image | OK (~0.73) | OK (conf ~0.85) | classical CSS ~0.56 | OK (3 tokens) |

## Gaps filed (product / quality)

1. ~~**UI screenshots → no shadow elevation**~~ — **Closed 2026-09-20 follow-up:** classical empty now returns `product_message` / warnings (“No elevation detected”) and the shadows empty UI states that explicitly (not a hard failure). Lighting flags stay default-off.
2. ~~**Spacing `base_unit=1` on upload-surface**~~ — **Closed 2026-09-20 follow-up:** `infer_base_spacing_robust` floors sub-4 measured bases to **4** and caps confidence ≤0.25 (CV extractor also tempers overall extraction confidence).
3. **Spacing fallback on soft-shadow-only cards** — Honest 4pt fallback is correct when no layout components exist; breakdown now marks `fallback=1.0`.
4. **Typography CV is async OCR** — Works offline when deps present; empty on non-text fixtures is fine; low-OCR / tiny boxes filtered before grouping.

## Not gaps

- Color confidence is prominence-weighted (no longer flat 0.6).
- Classical CSS shadows use area/softness/contrast when geometry is off; flat UI stays empty.
- Shim deletion did not break offline extractors.

## Next dogfood (human)

Upload 2–3 real product screenshots through the running app UI and confirm overview chips match the offline notes above.

Optional UI dumps: `pnpm test:e2e:evidence` → `playwright-tests/<stamp>-mvp-tabs/`.

## Retention

Keep until **~2026-12-20** (~90 days from evidence date 2026-09-20), then move to `~/Documents/copy-that-archive/`.
