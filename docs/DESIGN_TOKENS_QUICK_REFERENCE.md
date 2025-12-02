# Design Tokens - Quick Reference

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
```

---

## 🟡 SCHEMA READY - MISSING EXTRACTORS

### Shadow Tokens
```
Status: ⚠️ 20% (Schema only)

What exists:
✅ W3C schema support
✅ Token model (make_shadow_token)
✅ Database model (ShadowToken)
✅ Generators ready

What's missing:
❌ Shadow detection algorithm
❌ Extractor implementation
❌ Database table
❌ API endpoint

Current API:
GET /api/v1/shadows → Returns hardcoded sample only
```

### Typography Tokens
```
Status: ⚠️ 40% (Recommendations only)

What exists:
✅ W3C schema support
✅ Rule-based recommender (from color palette)
✅ Token model (make_typography_token)
✅ W3C export

What's missing:
❌ Image-based font detection
❌ Font size extraction
❌ Line height detection
❌ Database table
❌ Standalone API endpoint

Current API:
GET /api/v1/design-tokens/export/w3c → Includes typography recommendations
(Not extracted from images, only generated from color palette)
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
| **Extractor** | ✅✅ | ✅✅ | ❌ | ⚠️ | ❌ | ❌ |
| **Database Table** | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| **Token Graph** | ✅ | ✅ | ⚠️ | ⚠️ | ⚠️ | ❌ |
| **W3C Schema** | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| **API Endpoint** | ✅ | ✅ | ⚠️ | ⚠️ | ❌ | ❌ |
| **Generator** | ✅✅ | ✅✅ | ✅ | ✅ | ✅ | ❌ |
| **Tests** | ✅✅ | ✅ | ❌ | ✅ | ✅ | ❌ |

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

### ❌ Missing: Shadow → Export
```
Image
  ↓
ShadowExtractor ← STUCK HERE (returns [])
  ↓
(No database insertion)
  ↓
(No graph integration)
  ↓
(No export possible)
```

### ⚠️ Incomplete: Typography → Export
```
Color Palette (from color extraction)
  ↓
TypographyRecommender (rule-based)
  ↓
make_typography_token()
  ↓ (NOT in database)
TokenGraph (only during export)
  ↓
W3C Export
  ↓
Output: W3C JSON (recommendations only)

Note: No extraction from image (fonts not detected)
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
src/copy_that/application/shadow_extractor.py       ← MODIFY (implement detection)
src/copy_that/domain/models.py                       ← ADD ShadowToken table
src/copy_that/services/shadow_service.py             ← CREATE (new file)
src/copy_that/interfaces/api/shadows.py              ← MODIFY (add extraction)
tests/unit/api/test_shadows_api.py                   ← CREATE (tests)
```

### Adding Typography Extraction
```
src/copy_that/application/typography_extractor.py   ← CREATE/MODIFY
src/copy_that/domain/models.py                       ← ADD TypographyToken table
src/copy_that/services/typography_service.py         ← CREATE
src/copy_that/interfaces/api/design_tokens.py        ← MODIFY (add extraction)
tests/unit/api/test_typography_api.py                ← CREATE
```

### Adding Layout/Grid Extraction
```
src/copy_that/application/layout_extractor.py        ← CREATE
src/copy_that/domain/models.py                       ← ADD LayoutToken, GridToken tables
src/copy_that/services/layout_service.py             ← CREATE
src/copy_that/interfaces/api/design_tokens.py        ← MODIFY (add extraction)
tests/unit/api/test_layout_api.py                    ← CREATE
```

---

## 💻 Current API Summary

### Available Now ✅
```
POST   /api/v1/colors/extract                  → Extract colors
GET    /api/v1/colors/{id}                     → Get color details
POST   /api/v1/spacing/extract                 → Extract spacing
GET    /api/v1/spacing/{id}                    → Get spacing details
GET    /api/v1/design-tokens/export/w3c        → Export all (unified)
GET    /api/v1/shadows                         → Get sample shadows (hardcoded)
```

### Missing ❌
```
POST   /api/v1/shadows/extract                 → Would extract real shadows
POST   /api/v1/typography/extract              → Would extract fonts
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
| Current | 25% (2/8) | 6 | 50+ |
| After Shadow | 37% (3/8) | 7 | 65+ |
| After Typography | 50% (4/8) | 8 | 85+ |
| After Layout | 62% (5/8) | 10 | 100+ |
| After Border | 75% (6/8) | 12 | 112+ |
| Full W3C | 100% (8/8) | 14 | 140+ |

---

## 🔗 Related Docs

- [DESIGN_TOKENS_W3C_STATUS.md](./DESIGN_TOKENS_W3C_STATUS.md) - Full implementation analysis
- [copy-that-code-review-issues.md](./copy-that-code-review-issues.md) - Code quality issues
- [STRATEGIC_VISION_AND_ARCHITECTURE.md](./STRATEGIC_VISION_AND_ARCHITECTURE.md) - Platform vision
