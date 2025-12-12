# Phase 2.5 Handoff: Multi-Extractor Orchestrators & API Integration

**Date:** 2025-12-10 (End of Phase 2.4)
**Token Usage:** 90% (180K of 200K) - SESSION CLEAR RECOMMENDED
**Commit:** 87a86d6 (Phase 2.3-2.4 Complete)

---

## What Was Accomplished (Phase 2.3-2.4)

### Phase 2.3: E2E Testing ✅
- **12/12 E2E tests passing** - Multi-extractor color pipeline validated
- Delta-E deduplication verified (removes 20-30% duplicates)
- Error handling & graceful degradation tested
- Performance: 1.2-1.5x parallel speedup confirmed

### Phase 2.4: Adapter Pattern Extension ✅
Unified extraction architecture across ALL token types:

```
bytes → Adapter (implements protocol) → ExtractionResult
         (wraps extractor)              (tokens + metadata)
```

**5 Adapters Created:**
- **Color:** AIColorExtractorAdapter, KMeansExtractorAdapter, CVColorExtractorAdapter
- **Spacing:** CVSpacingExtractorAdapter
- **Typography:** AITypographyExtractorAdapter
- **Shadow:** AIShadowExtractorAdapter, CVShadowExtractorAdapter

**Test Coverage:**
- Spacing tests: 44 lines
- Typography tests: 30 lines
- Shadow tests: 40 lines
- Color E2E: 320 lines

---

## What Phase 2.5 Must Build

### 1. Multi-Extractor Orchestrators (3 files)

Each follows the **ColorExtractionOrchestrator** pattern:

```python
# src/copy_that/extractors/spacing/orchestrator.py
class SpacingExtractionOrchestrator:
    def __init__(self, ai_adapter, cv_adapter):
        self.ai_adapter = ai_adapter
        self.cv_adapter = cv_adapter

    async def orchestrate(self, image_bytes, use_ai=True):
        # Parallel extraction
        # Deduplication (Delta-E for spacing equivalence)
        # Return ExtractionResult with combined tokens

# src/copy_that/extractors/typography/orchestrator.py
class TypographyExtractionOrchestrator:
    # Similar pattern

# src/copy_that/extractors/shadow/orchestrator.py
class ShadowExtractionOrchestrator:
    # Similar pattern
```

**File Locations:**
- `src/copy_that/extractors/spacing/orchestrator.py`
- `src/copy_that/extractors/typography/orchestrator.py`
- `src/copy_that/extractors/shadow/orchestrator.py`

**Key Methods:**
- `__init__(self, adapters_dict)` - Initialize with list of adapters
- `async orchestrate(image_bytes, parallel=True)` - Run extraction
- `_deduplicate_tokens(tokens)` - Remove near-duplicates
- `async _store_in_database(tokens, project_id)` - Persist results

### 2. API Endpoints (3 new routes in backend/app/api/)

Create new endpoint modules for each token type:

```python
# backend/app/api/endpoints/spacing.py
@router.post("/spacing/extract")
async def extract_spacing(
    project_id: str,
    file: UploadFile,
    use_ai: bool = True,
):
    bytes_data = await file.read()
    result = await spacing_orchestrator.orchestrate(bytes_data, use_ai)
    return result.to_api_schema()

# backend/app/api/endpoints/typography.py
@router.post("/typography/extract")
# Similar structure

# backend/app/api/endpoints/shadow.py
@router.post("/shadow/extract")
# Similar structure
```

**File Locations:**
- `backend/app/api/endpoints/spacing.py`
- `backend/app/api/endpoints/typography.py`
- `backend/app/api/endpoints/shadow.py`

**Integration Points:**
- Import in `backend/app/api/__init__.py`
- Add to FastAPI `app.include_router(router, prefix="/api")`
- Mirror color endpoints: `GET /:type/:job_id`, `GET /:type/project/:project_id`

### 3. E2E Test Suite (1 comprehensive file)

```python
# backend/tests/test_e2e_extraction_all_types.py
class TestSpacingExtractionE2E:
    async def test_spacing_multi_adapter_extraction
    async def test_spacing_deduplication
    async def test_spacing_error_handling

class TestTypographyExtractionE2E:
    async def test_typography_multi_adapter_extraction
    async def test_typography_deduplication

class TestShadowExtractionE2E:
    async def test_shadow_multi_adapter_extraction
    async def test_shadow_deduplication
```

**Coverage Goal:** 40+ tests across all 3 types

---

## Architecture Reference

### Base Protocols (Already Built)
- `src/copy_that/extractors/spacing/base.py` - SpacingExtractorProtocol
- `src/copy_that/extractors/typography/base.py` - TypographyExtractorProtocol
- `src/copy_that/extractors/shadow/base.py` - ShadowExtractorProtocol

### Adapters (Already Built)
All follow: `adapter_class.extract(image_bytes) → ExtractionResult`

**Spacing Adapters:**
- `CVSpacingExtractorAdapter` - Computer vision (SAM-based)

**Typography Adapters:**
- `AITypographyExtractorAdapter` - Claude-based extraction

**Shadow Adapters:**
- `AIShadowExtractorAdapter` - Claude Structured Outputs
- `CVShadowExtractorAdapter` - Computer vision

### Database Tables (Use existing pattern)
Reference: `backend/models/color_tokens.py`

```python
# backend/models/spacing_tokens.py
class SpacingToken(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    project_id: int = Field(foreign_key="projects.id")
    value: str  # e.g., "8px", "16px"
    semantic_name: Optional[str]
    category: str  # "margin", "padding", "gap"
    confidence: float
    created_at: datetime

# backend/models/typography_tokens.py
class TypographyToken(SQLModel, table=True):
    # fontFamily, fontSize, fontWeight, lineHeight, letterSpacing
    # Similar structure

# backend/models/shadow_tokens.py
class ShadowToken(SQLModel, table=True):
    # x, y, blur, spread, color, inset
    # Similar structure
```

### Alembic Migrations
Reference: `backend/alembic/versions/xxx_add_color_tokens.py`

Create similar migrations:
- `backend/alembic/versions/xxx_add_spacing_tokens.py`
- `backend/alembic/versions/xxx_add_typography_tokens.py`
- `backend/alembic/versions/xxx_add_shadow_tokens.py`

---

## Execution Plan for Phase 2.5

### Day 1: Spacing Orchestrator & API
- [ ] Create `spacing/orchestrator.py` (180-200 LOC)
- [ ] Create `backend/models/spacing_tokens.py` (120 LOC)
- [ ] Create Alembic migration for spacing_tokens
- [ ] Create `backend/app/api/endpoints/spacing.py` (150 LOC)
- [ ] Create `backend/tests/test_spacing_orchestrator.py` (250 LOC)

### Day 2: Typography Orchestrator & API
- [ ] Create `typography/orchestrator.py` (180-200 LOC)
- [ ] Create `backend/models/typography_tokens.py` (150 LOC)
- [ ] Create Alembic migration for typography_tokens
- [ ] Create `backend/app/api/endpoints/typography.py` (150 LOC)
- [ ] Create `backend/tests/test_typography_orchestrator.py` (250 LOC)

### Day 3: Shadow Orchestrator & API
- [ ] Create `shadow/orchestrator.py` (180-200 LOC)
- [ ] Create `backend/models/shadow_tokens.py` (150 LOC)
- [ ] Create Alembic migration for shadow_tokens
- [ ] Create `backend/app/api/endpoints/shadow.py` (150 LOC)
- [ ] Create `backend/tests/test_shadow_orchestrator.py` (250 LOC)

### Day 4: Comprehensive E2E Tests
- [ ] Run all migration tests
- [ ] Create `backend/tests/test_e2e_extraction_all_types.py` (400+ LOC)
- [ ] Validate parallel extraction performance
- [ ] Validate deduplication logic
- [ ] Document production readiness

---

## Key Files for Reference

### Color Extraction (Reference Implementation)
- `src/copy_that/extractors/color/orchestrator.py` - Model for Phase 2.5
- `backend/models/color_tokens.py` - Database model pattern
- `backend/app/api/endpoints/color.py` - API pattern
- `backend/tests/test_e2e_color_extraction.py` - Test pattern

### Shared Patterns
- `src/copy_that/extractors/core.py` - ExtractionResult, ExtractionMetadata
- `backend/app/core/config.py` - Configuration management
- `backend/app/db.py` - Database session management

---

## Success Criteria

### Phase 2.5 Complete When:
- ✅ 3 orchestrators fully implemented (Spacing, Typography, Shadow)
- ✅ 3 API endpoints deployed and tested
- ✅ 3 database tables with Alembic migrations
- ✅ 40+ E2E tests passing (all token types)
- ✅ Parallel extraction validated (1.2-1.5x speedup)
- ✅ Error handling & graceful degradation working
- ✅ All `pnpm typecheck` tests passing
- ✅ Commit: `feat: Phase 2.5 Complete - Multi-Extractor Production Platform`

---

## Next Session Start

### 1. Clear Session & Start Fresh with Sonnet
```bash
/clear
```

### 2. Start Phase 2.5
"Implement Phase 2.5: Multi-Extractor Orchestrators & API Integration"

### 3. Reference This File
Everything needed is documented above. Use this file as your specification.

---

## Token Budget Summary

- **Started Session:** 50% (100K)
- **Before Phase 2.5:** 90% (180K of 200K)
- **Remaining:** 20K tokens (10%)
- **Action:** Clear session and start Phase 2.5 with fresh Sonnet context

---

## Questions for Next Session

These can guide the Sonnet session when Phase 2.5 begins:

1. **Deduplication Strategy:** What equivalence metric should we use for Spacing, Typography, Shadow tokens? (Similar to Delta-E for Color)
   - Spacing: Euclidean distance between (x, y) coordinates?
   - Typography: Font similarity score + size threshold?
   - Shadow: Combined distance in (x, y, blur, spread) space?

2. **API Response Format:** Should orchestrators return:
   - Grouped by extractor (which adapter found what)?
   - Ranked by confidence?
   - De-duplicated merged results?

3. **Database Schema:** Should we add token comparison/relationship tracking (like the color harmony graph)?

---

## Session Metadata

**Repository:** copy-that (multimodal token extraction platform)
**Phase:** 2.5 of 5 (Multi-Extractor Production Platform)
**Completion:** 2025-12-10
**Next:** Phase 2.5 - Orchestrators & API (Days 1-4)
**Estimated Phase 2.5 Effort:** 4 days (with Sonnet)
