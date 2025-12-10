# Color Pipeline Architecture Analysis & Refactoring Plan

**Status:** Ready for refactoring
**Database Schema:** ✅ Complete (all 48+ fields present)
**API Endpoints:** ✅ 8 routes working
**Blocker:** ⚠️ Legacy code dependency in `/src/core/tokens/`
**Priority:** High - Unblock cleanup and enable new features

---

## Executive Summary

The color pipeline is **functionally complete** but **architecturally fragmented**:

- ✅ Fast K-means extractor working
- ✅ AI fallback (Claude/OpenAI) implemented
- ✅ Database schema comprehensive
- ✅ API endpoints operational
- ⚠️ Still depends on `/src/core/tokens/` legacy code
- ❌ Monolithic API layer (803 LOC)
- ❌ Missing error recovery, retry logic, job tracking
- ❌ Services layer underutilized

**Key Finding:** The API imports and uses these legacy functions:
- `make_color_token()` - Token creation
- `make_color_ramp()` - Ramp generation
- `tokens_to_w3c()` - W3C export
- `TokenRepository` - Repository pattern

These **cannot be deleted** without migration first.

---

## Current Color Pipeline Architecture

### API Routes (8 endpoints)
```
POST /api/v1/colors/extract              → Single image extraction
POST /api/v1/colors/extract-streaming    → Streaming extraction with progress
POST /api/v1/colors/batch-extract        → Multiple images
GET  /api/v1/colors/{color_id}           → Retrieve color token
PUT  /api/v1/colors/{color_id}           → Update color token
DELETE /api/v1/colors/{color_id}         → Delete color token
POST /api/v1/colors/harmonize            → Harmony analysis
GET  /api/v1/colors/export/w3c           → W3C design tokens export
```

### Extraction Pipeline (3 strategies)
1. **Fast K-means** (`color_extractor.py` - 634 LOC)
   - Initial clustering
   - ~200ms per image
   - Fallback: AI extraction

2. **AI Extraction** (`openai_color_extractor.py` - 301 LOC)
   - Claude/OpenAI structured outputs
   - Design intent classification
   - Semantic naming

3. **CV Extraction** (`cv_color_cv_extractor.py`)
   - Computer vision fallback
   - Specialized use cases

### Supporting Modules
- `color_utils.py` (1,458 LOC) - Conversions
- `semantic_color_naming.py` (555 LOC) - Naming
- `color_clustering.py` (241 LOC) - Algorithms
- `color_spaces_advanced.py` (347 LOC) - Oklab, Oklch, Delta-E

### Services Layer
- `colors_service.py` - Business logic (extractor selection, post-processing, serialization)

### Database
- `ColorToken` model - 48+ fields, comprehensive color metadata
- ✅ All fields now present in SQLite schema

---

## Issues Identified

### 1. Legacy Code Blocking Cleanup ⚠️ CRITICAL

**Problem:** API still uses `/src/core/tokens/` functions

**Current Imports in `colors.py`:**
```python
from core.tokens.adapters.w3c import tokens_to_w3c
from core.tokens.color import make_color_ramp, make_color_token, ramp_to_dict
from core.tokens.model import Token
from core.tokens.repository import InMemoryTokenRepository, TokenRepository
```

**Usage:** 6 different locations in API file
- Line 75: `make_color_token()`
- Line 86: `make_color_ramp()`
- Lines 96, 482: `InMemoryTokenRepository()`
- Lines 106, 626: `tokens_to_w3c()`
- Line 533: `ramp_to_dict()`

**Cannot Delete `/src/core/` Without:**
- Moving token classes to modern location
- Creating W3C adapter in modern structure
- Updating all import statements
- Testing W3C export functionality

### 2. Monolithic API Endpoint

**Problem:** `colors.py` (803 LOC) handles too many concerns

**Current Responsibilities:**
- Input validation (base64, image size, rate limiting)
- Extraction orchestration
- Database CRUD
- W3C export
- Ramp generation
- Harmony analysis

**Result:** Hard to test, hard to maintain, hard to extend

### 3. Architectural Layers Not Fully Separated

**Current Flow:**
```
API → Extractor → Database → API Response
```

**Should Be:**
```
API → Service Layer → Extractor/Database/Cache → API Response
```

**Gap:** Services layer exists but is underutilized

### 4. Missing Critical Features

#### Error Handling
- ❌ No retry logic
- ❌ No fallback extraction strategy on failure
- ❌ No partial batch operation support
- ❌ No extraction job tracking

#### Batch Operations
- ❌ No batch status tracking
- ❌ No webhook support
- ❌ No async job queue

#### Color Curation
- ❌ No color refinement endpoints
- ❌ No palette curation
- ❌ No theme generation

---

## Refactoring Plan

### Phase 1: Migrate Legacy Code (Session 1 - 2 hours)

**Objective:** Move `/src/core/tokens/` code into modern architecture without deleting legacy

**Create:** `src/copy_that/application/color/`
```
color/
├── __init__.py
├── extractor.py                (existing code)
├── ai_extractor.py            (existing code)
├── cv_extractor.py            (existing code)
├── semantic_naming.py         (existing code)
├── clustering.py              (existing code)
├── color_spaces.py            (existing code)
├── utils.py                   (existing code)
├── token_factory.py           (NEW - migrate from core)
├── w3c_adapter.py             (NEW - migrate from core)
├── repository.py              (NEW - migrate from core)
├── models.py                  (NEW - migrate from core)
└── __pycache__/
```

**Migrate from `/src/core/tokens/`:**
1. Copy `Token` model → `token_factory.py`
2. Copy `make_color_token()` → `token_factory.py`
3. Copy `make_color_ramp()` → `token_factory.py`
4. Copy `ramp_to_dict()` → `token_factory.py`
5. Copy `TokenRepository` interface → `repository.py`
6. Copy `InMemoryTokenRepository` → `repository.py`
7. Copy W3C adapter → `w3c_adapter.py`

**Update Imports:**
```python
# Before
from core.tokens.color import make_color_token, make_color_ramp

# After
from copy_that.application.color.token_factory import make_color_token, make_color_ramp
```

**Deliverable:** All legacy functions available from modern location, no `/src/core/` imports in API

### Phase 2: Refactor API Layer (Session 2-3 - 4 hours)

**Objective:** Break monolithic `colors.py` into focused, testable components

**Create:** `src/copy_that/interfaces/api/colors/`
```
colors/
├── __init__.py              (route registration)
├── router.py                (route definitions)
├── schemas.py               (Pydantic request/response models)
├── handlers.py              (endpoint handlers)
├── validators.py            (input validation logic)
└── dependencies.py          (FastAPI dependencies)
```

**Extract from current `colors.py`:**
1. **router.py** - Route definitions and registration
2. **schemas.py** - Request/response models (Pydantic)
3. **handlers.py** - Endpoint handler logic
4. **validators.py** - Input validation (base64, image size, etc.)
5. **dependencies.py** - FastAPI dependency injection

**Result:** `colors.py` reduces from 803 → ~100 LOC (just router registration)

### Phase 3: Strengthen Services Layer (Session 3 - 4 hours)

**Objective:** Create proper service classes, move business logic from API

**Create:** `src/copy_that/services/color/`
```
color/
├── __init__.py
├── extraction_service.py       (orchestrate extractors)
├── storage_service.py          (database operations)
├── export_service.py           (W3C, JSON, other formats)
├── ramp_service.py            (color ramp generation)
└── harmonization_service.py    (harmony analysis)
```

**ExtractionService** (new)
```python
class ExtractionService:
    async def extract_colors(
        self,
        image_base64: str,
        project_id: int,
        extractor_preference: str = "fast"
    ) -> ColorExtractionResult:
        # Try fast extractor
        # Fallback to AI if needed
        # Post-process results
        # Return with metadata
```

**StorageService** (new)
```python
class StorageService:
    async def save_colors(
        self,
        colors: list[ExtractedColorToken],
        project_id: int
    ) -> list[ColorToken]:
        # Insert to database
        # Handle deduplication
        # Index for search
```

**ExportService** (new)
```python
class ExportService:
    async def export_w3c(
        self,
        colors: list[ColorToken]
    ) -> dict:
        # Generate W3C tokens
        # Include ramps
        # Return JSON
```

**Result:** Services become reusable across API, CLI, webhooks, jobs

### Phase 4: Add Missing Features (Session 4+ - Progressive)

#### 4.1 Error Recovery & Retry Logic
```python
class ExtractionService:
    async def extract_with_retry(
        self,
        image_base64: str,
        max_retries: int = 3
    ):
        """Try fast → AI → CV with exponential backoff"""
```

#### 4.2 Extraction Job Tracking
```python
class ExtractionJob(Base):
    id: int
    project_id: int
    status: str  # pending, processing, completed, failed
    image_count: int
    completed_count: int
    error_message: str | None
    created_at: datetime
    completed_at: datetime | None
```

#### 4.3 Batch Progress Tracking
```python
@router.post("/batch-extract")
async def batch_extract(request: BatchExtractRequest):
    job = create_extraction_job(len(request.images))
    # Process images
    # Update job progress
    # Return job ID for polling
```

#### 4.4 Color Refinement Endpoints
```python
@router.post("/colors/{color_id}/refine")
async def refine_color(
    color_id: int,
    adjustments: ColorAdjustments  # hue_shift, saturation, lightness
):
    # Apply adjustments
    # Regenerate ramps
    # Update database
```

#### 4.5 Palette Curation
```python
@router.post("/colors/{color_id}/set-role")
async def set_color_role(
    color_id: int,
    role: Literal["primary", "secondary", "accent", "neutral"]
):
    # Update color role
    # Regenerate theme
```

---

## Implementation Priority

### Must Have (Session 1-3, ~10 hours)
1. ✅ Migrate legacy code
2. ✅ Refactor API layer
3. ✅ Strengthen services layer
4. ✅ Test end-to-end

### Should Have (Session 4, ~6 hours)
5. Error recovery & retry logic
6. Extraction job tracking
7. Color refinement endpoints

### Nice to Have (Future sessions)
8. Batch progress tracking
9. Webhook support
10. Palette curation UI

---

## Testing Plan

### Unit Tests (Per Module)
- `test_color_extractor.py` - K-means extraction
- `test_ai_extractor.py` - AI extraction
- `test_token_factory.py` - Token creation
- `test_w3c_adapter.py` - W3C export

### Integration Tests
- `test_extraction_service.py` - End-to-end extraction
- `test_color_api.py` - API endpoints

### E2E Tests
- `test_color_pipeline.e2e.ts` - Frontend to backend

**Current Status:**
- ✅ API endpoints operational
- ✅ Database schema complete
- ⚠️ Need comprehensive error handling tests

---

## Deliverables by Phase

| Phase | Deliverable | Status |
|-------|-------------|--------|
| 1 | Migrated token code | Pending |
| 2 | Refactored API | Pending |
| 3 | Service layer | Pending |
| 4 | Error recovery | Pending |
| Test | Full E2E test coverage | Partial |

---

## Success Criteria

- [ ] Phase 1: `colors.py` only imports from `copy_that.*`
- [ ] Phase 2: API broken into subdirectory with <100 LOC per file
- [ ] Phase 3: Services layer handles all business logic
- [ ] Phase 4: Error recovery with 3+ extraction strategies
- [ ] All tests passing
- [ ] Can delete `/src/core/` and `/src/cv_pipeline/`

---

## Next Steps

1. **Immediate:** Start Phase 1 (legacy code migration)
2. **This session:** Aim for Phase 1-2 completion
3. **Follow-up:** Phase 3-4 in next session

Shall I begin with Phase 1 (migrating legacy code)?
