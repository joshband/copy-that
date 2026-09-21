# UI dogfood — 2026-09-20

Live app pass + promoted mocked evidence dumps after visual-contracts / CV confidence work.

## Inputs (robotic upload)

| File | Notes |
|------|--------|
| [inputs/UI-test01.jpg](./inputs/UI-test01.jpg) | Steampunk / “BEMMENAINT” panel |
| [inputs/UI-test02.jpg](./inputs/UI-test02.jpg) | Starry painterly control surface |
| [inputs/UI-test03.jpg](./inputs/UI-test03.jpg) | Flat navy/red instrument panel |

## Live extracts (`http://127.0.0.1:5173/`)

Artifacts under [live/](./live/) — preview + overview/colors/spacing/typography/shadows/shape per image.  
Notes: [live/ui-test-live-notes.json](./live/ui-test-live-notes.json).

| Image | Snapshot (UI) | Spacing honesty | Shadows |
|-------|---------------|-----------------|---------|
| UI-test01 | 11 colors · 9 spacing · **85%** · 3 typography · 1 shadow | Measured scale · 85% | `shadow-subtle` card |
| UI-test02 | 11 colors · 7 spacing · **85%** · 3 typography · 1 shadow | Measured scale · 85% | `shadow.soft` linked |
| UI-test03 | 11 colors · 5 spacing · **85%** · 3 typography · 1 shadow | Measured scale · 85% | `shadow.soft` linked |

### Graph hydrate recheck (post-fix)

After loading the token graph on `coreStagesComplete` (not `colors.length`), chrome fixtures also populate Snapshot ([live/hydrate-recheck.json](./live/hydrate-recheck.json)):

| Image | Snapshot after hydrate |
|-------|------------------------|
| app-home | 11 colors · 7 spacing · 15 typography · 1 shadow |
| synthetic-card | 4 colors · 6 spacing · **80% fallback** · 3 typography · 1 shadow |
| UI-test01 | 11 colors · 9 spacing · 85% · 3 typography · 1 shadow |

## Offline CV (same inputs)

[offline-cv-ui-tests.json](./offline-cv-ui-tests.json)

| Image | Color conf | Spacing | Shadow classical |
|-------|------------|---------|------------------|
| UI-test01 | ~0.65 (10) | base 4, ~0.93 | 2 layers, ~0.73 |
| UI-test02 | ~0.65 (10) | base 4, ~0.94 | 2 layers, ~0.67 |
| UI-test03 | ~0.63 (8) | base 4, ~0.95 | 2 layers, ~0.77 |

OCR typography stayed empty offline (stylized/gibberish labels); live UI still showed 3 typography stand-ins from graph/AI path.

## Promoted mocked tab dumps

From `pnpm test:e2e:evidence` → [screens/](./screens/).

## UI honesty shipped

- `TokenSourceChip` maps `cv_fallback` / `measured:false` → **Fallback**
- Spacing scale shows Measured vs Fallback + % confidence
- Overview Snapshot appends spacing `%` / `fallback` when present
- **Post-1.0.2 polish:** AI+CV merge prefers measured CV confidence and keeps CV fallback at ~15% (no more “80% fallback” when AI invents a 4pt scale)

## Retention

Keep until **~2026-12-20** (~90 days from evidence date 2026-09-20), then move to `~/Documents/copy-that-archive/`.
