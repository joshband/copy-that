# Design Tokens - Quick Reference

## W3C 2025.10 Schema Scaffolding

- Schemas live at `src/copy_that/design_tokens/schemas/2025_10/`:
  - `format.schema.json` (full token document)
  - `color.schema.json` (color section / tokens)
  - `resolver.schema.json` (resolver documents)
- Format rules: tokens require `$type` + `$value`; groups may declare `$type` for children.
- Format schema enumerates currently supported `$type` values (expand as new types ship).
- Resolver helper: `src/copy_that/design_tokens/resolver.py`.
- Resolver rules: `version`, `sources`, `contexts`, `resolutionOrder` are required.
- `$extensions` reserved for confidence + provenance; algorithm details stay out of `$value`.
- Validation tests cover format/color/resolver; optional API guard remains planned.
- Streaming artifact E2E check: `frontend/tests/playwright/streaming-artifacts.spec.ts`.

## 🟢 READY TO USE (Production)

### Color Tokens
```
Status: ✅ COMPLETE (100%)

What works:
- Extract colors from images (AI + CV)
- Database persistence
- W3C export
- CSS variables
- React components
- 40+ tests passing

Try it:
POST /api/v1/colors/extract
  → Get: ExtractedColorToken with confidence scores
  → Export as W3C, CSS, React
```

### Spacing Tokens
```
Status: ✅ COMPLETE (100%)

What works:
- Extract spacing/padding from images (AI + CV)
- Grid alignment detection
- W3C export
- CSS variables
- React components
- 11 API tests + comprehensive coverage

Try it:
POST /api/v1/spacing/extract
  → Get: SpacingToken with grid metadata
  → Export as W3C, CSS, React

Note:
- Directional spacing exports as per-side `dimension` tokens (e.g., `/top`, `/inline`).
```

---

## 🟡 IN PROGRESS / BETA

### Shadow Tokens
```
Status: 🔄 Beta (extraction + persistence live, tuning ongoing)

What exists:
✅ W3C schema + domain entity (ShadowLayer/make_shadow_token)
✅ Alembic migration + ORM model (infrastructure/persistence/models.py#ShadowToken)
✅ Repository (infrastructure/persistence/repositories/shadow_tokens.py)
✅ Extractors: CV + AI (application/cv_shadow_extractor.py, application/ai_shadow_extractor.py)
✅ FastAPI router (/api/v1/shadows: extract + CRUD)
✅ W3C export path via design_tokens export

What's pending:
🔄 Broader test coverage (only smoke/API checks today)
🔄 Deduplication/quality tuning for noisy inputs

Current API:
POST /api/v1/shadows/extract → Extract + optionally persist
GET  /api/v1/shadows/projects/{id} → List for project
GET  /api/v1/shadows/{id} → Detail
PUT  /api/v1/shadows/{id} → Update metadata
DELETE /api/v1/shadows/{id} → Delete
```

### Typography Tokens
```
Status: 🔄 Beta (AI-first extraction with CV fallback; DB + CRUD live)

What exists:
✅ W3C schema + domain entity
✅ Alembic migration + ORM model (infrastructure/persistence/models.py#TypographyToken)
✅ Repository (infrastructure/persistence/repositories/typography_tokens.py)
✅ Extractors: AI + CV fallback (application/ai_typography_extractor.py, application/cv/typography_cv_extractor.py)
✅ FastAPI router (/api/v1/typography: extract + CRUD + export)
✅ W3C export (flattened) via design_tokens + typography export endpoints

What's pending:
🔄 More robust CV/AI fusion + ranking
🔄 Wider test coverage and readability scoring validation

Current API:
POST /api/v1/typography/extract → Extract + persist
POST /api/v1/typography/batch → Multi-image extraction
GET  /api/v1/typography/projects/{id} → List for project
GET  /api/v1/typography/{id} → Detail
PUT  /api/v1/typography/{id} → Update
DELETE /api/v1/typography/{id} → Delete
GET  /api/v1/typography/export/w3c → Export typography only
```

### Layout/Grid Tokens
```
Status: ⚠️ 30% (Schema only)

What exists:
✅ W3C schema support
✅ Token model (make_layout_token, make_grid_token)
✅ Generators ready

What's missing:
❌ Grid detection algorithm
❌ Column/gutter detection
❌ Extractor implementation
❌ Database tables
❌ API endpoints

Current API:
(No endpoints)
```

---

## 🔴 NOT STARTED

### Border/Border-Radius Tokens
```
Status: ❌ 5% (Enum only)

What exists:
✅ Enum in SpacingToken.spacing_type

What's missing:
❌ TokenType enum entry
❌ Token model
❌ Detection algorithm
❌ Extractor
❌ Database tables
❌ API endpoints
❌ W3C schema mapping
❌ Generators

Start here if adding: Add to TokenType enum
```

---

## 📊 By the Numbers

| Feature | Color | Spacing | Shadow | Typography | Layout | Border |
|---------|-------|---------|--------|------------|--------|--------|
| **Extractor** | ✅✅ | ✅✅ | ✅ (CV+AI) | ✅ (AI+CV) | ⚠️ (derived only) | ❌ |
| **Database Table** | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ |
| **Token Graph** | ✅ | ✅ | ⚠️ (basic) | ⚠️ (basic) | ⚠️ (helpers) | ❌ |
| **W3C Schema** | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| **API Endpoint** | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ |
| **Generator** | ✅✅ | ✅✅ | ✅ | ✅ | ✅ | ❌ |
| **Tests** | ✅✅ | ✅ | ⚠️ (smoke) | ⚠️ (api) | ✅ | ❌ |

---

## 🔄 Data Flow Examples

### ✅ Working: Color → Export
```
Image
  ↓
AIColorExtractor
  ↓ ExtractedColorToken (18 fields)
Database (color_tokens)
  ↓
db_colors_to_repo()
  ↓ TokenRepository
TokenGraph (OKLCH + semantic names)
  ↓
W3C Adapter / Generators
  ↓
Output: W3C JSON | CSS | React | HTML
```

### ✅ Working: Spacing → Export
```
Image
  ↓
AISpacingExtractor + CVSpacingExtractor
  ↓ SpacingToken
Database (spacing_tokens)
  ↓
build_spacing_repo_from_db()
  ↓ TokenRepository
TokenGraph (scales, multiples_of, aliases)
  ↓
W3C Adapter / Generators
  ↓
Output: W3C JSON | CSS | React | HTML
```

### ✅ Working (Beta): Shadow → Export
```
Image
  ↓
CVShadowExtractor + AIShadowExtractor (fallback)
  ↓ ShadowExtractionResult
Database (shadow_tokens)
  ↓
SQLAlchemyShadowTokenRepository.record_extraction()
  ↓ TokenRepository (db_shadows_to_repo)
W3C Adapter / Generators
  ↓
Output: W3C JSON | Combined export
```

### ⚠️ Incomplete (Beta): Typography → Export
```
Image (or palette hint)
  ↓
AITypographyExtractor (+ optional CV fallback)
  ↓ TypographyExtractionResult
Database (typography_tokens)
  ↓
SQLAlchemyTypographyTokenRepository.record_extraction()
  ↓ TokenRepository (build_typography_repo_from_db)
  ↓
W3C Export (flattened)
  ↓
Output: W3C JSON (extracted + recommended tokens)

Note: CV fusion + scoring still evolving
```

---

## 🎯 To Complete Each Token Type

### Shadow (1-2 days)
1. Implement `detect_shadows()` in `shadow_extractor.py`
2. Create `ShadowToken` table migration
3. Add service: `build_shadow_repo_from_db()`
4. Add API: `POST /api/v1/shadows/extract`
5. Wire into extraction job system
6. Add 15 tests

### Typography (2-3 days)
1. Implement `detect_fonts()` + `detect_sizes()` in `typography_extractor.py`
2. Create `TypographyToken` table migration
3. Add service: `build_typography_repo_from_db()`
4. Add API: `POST /api/v1/typography/extract`
5. Migrate from recommendations to extraction
6. Add 20 tests

### Layout/Grid (2-3 days)
1. Implement `detect_grid()` + `detect_columns()` (CV-based)
2. Create `LayoutToken` + `GridToken` table migrations
3. Add services: `build_layout_repo_from_db()`, `build_grid_repo_from_db()`
4. Add APIs: `POST /api/v1/layout/extract`, `POST /api/v1/grid/extract`
5. Add token graph relations (CONTAINS)
6. Add 15 tests

### Border (1-2 days)
1. Add `BORDER` + `BORDER_RADIUS` to TokenType enum
2. Implement detection in CV pipeline
3. Create database tables
4. Implement service + API
5. Add 12 tests

---

## 📍 Key Files to Modify

### Adding Shadow Extraction
```
src/copy_that/application/ai_shadow_extractor.py                ← refine AI flow
src/copy_that/application/cv_shadow_extractor.py                ← refine CV flow
src/copy_that/infrastructure/persistence/models.py              ← ShadowToken ORM model
src/copy_that/infrastructure/persistence/repositories/shadow_tokens.py ← Repository wiring
src/copy_that/interfaces/api/shadows.py                          ← API + DI
tests/unit/api/test_shadows_api.py                               ← Coverage
```

### Adding Typography Extraction
```
src/copy_that/application/ai_typography_extractor.py            ← AI extraction
src/copy_that/application/cv/typography_cv_extractor.py         ← CV fallback
src/copy_that/infrastructure/persistence/models.py              ← TypographyToken ORM model
src/copy_that/infrastructure/persistence/repositories/typography_tokens.py ← Repository wiring
src/copy_that/interfaces/api/typography.py                      ← API + DI
tests/unit/api/test_typography_api.py                           ← Coverage
```

### Adding Layout/Grid Extraction
```
src/copy_that/application/cv/grid_cv_extractor.py              ← CV detection (TODO)
src/copy_that/application/presentation/spacing.py              ← Derived layout helpers
src/copy_that/infrastructure/persistence/models.py             ← Layout/Grid ORM models (future)
src/copy_that/infrastructure/persistence/repositories/spacing_tokens.py ← Derived layout export hooks
src/copy_that/interfaces/api/spacing.py                         ← Layout derivation wiring
tests/unit/api/test_layout_api.py                               ← Coverage
```

---

## 💻 Current API Summary

### Available Now ✅
```
POST   /api/v1/colors/extract                  → Extract colors
GET    /api/v1/colors/{id}                     → Get color details
POST   /api/v1/spacing/extract                 → Extract spacing
GET    /api/v1/spacing/{id}                    → Get spacing details
POST   /api/v1/shadows/extract                 → Extract shadows (CV + AI fallback)
GET    /api/v1/shadows/projects/{id}           → List shadows for project
POST   /api/v1/typography/extract              → Extract typography (AI + CV fallback)
POST   /api/v1/typography/batch                → Batch typography extraction
GET    /api/v1/typography/{id}                 → Typography detail
GET    /api/v1/design-tokens/export/w3c        → Export all (unified)
```

### Missing ❌
```
POST   /api/v1/layout/extract                  → Would extract layouts
POST   /api/v1/grid/extract                    → Would extract grids
POST   /api/v1/borders/extract                 → Would extract borders
```

---

## 🚀 Recommended Implementation Order

1. **Shadow** (easiest, high-impact)
   - Reuse CV detection patterns from colors/spacing
   - Dual implementation: CV + AI fallback
   - 2 days

2. **Typography** (medium complexity)
   - Font detection via OCR or LLM
   - Line height inference from spacing
   - 3 days

3. **Layout/Grid** (medium-high complexity)
   - Column detection from spacing patterns
   - Gutter inference from grid alignment
   - 3 days

4. **Border** (lower priority)
   - Stroke detection from CV
   - Radius detection from corners
   - 2 days

---

## 📈 Impact by Completion

| Milestone | Coverage | API Endpoints | Test Count |
|-----------|----------|---------------|-----------|
| Current | ~66% (4/6 types live) | 12+ (color/spacing/shadow/typography) | 70+ |
| After Layout | ~83% (5/6) | 14+ | 90+ |
| After Border | 100% (6/6) | 16+ | 100+ |

---

## 🔗 Related Docs

- [DESIGN_TOKENS_W3C_STATUS.md](./DESIGN_TOKENS_W3C_STATUS.md) - Full implementation analysis
- [copy-that-code-review-issues.md](./copy-that-code-review-issues.md) - Code quality issues
- [STRATEGIC_VISION_AND_ARCHITECTURE.md](./STRATEGIC_VISION_AND_ARCHITECTURE.md) - Platform vision
