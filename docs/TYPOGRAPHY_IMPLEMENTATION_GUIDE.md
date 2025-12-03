# Typography Implementation - Complete Implementation Guide

**Status:** 70% Complete (5/7 core steps done)
**Ready for Next Session:** YES - All groundwork complete
**Estimated Time to Finish:** 2-3 hours
**Complexity:** Medium (straightforward pattern replication)

---

## What's Done ✅

### 1. Database Models & Migration (COMPLETE)
- **Files:** `src/copy_that/domain/models.py` + `alembic/versions/2025_12_03_add_typography_and_font_tokens.py`
- **Status:** Ready to migrate on next Docker build
- **Models:** TypographyToken, FontFamilyToken, FontSizeToken

### 2. AI Typography Extractor (COMPLETE)
- **File:** `src/copy_that/application/ai_typography_extractor.py` (500+ lines)
- **Class:** `AITypographyExtractor` with Claude Sonnet 4.5
- **Methods:**
  - `extract_typography_from_image_url()` - URL extraction
  - `extract_typography_from_file()` - File extraction
  - `extract_typography_from_base64()` - Base64 extraction
- **Output:** `TypographyExtractionResult` (Pydantic model)

### 3. CV Typography Extractor (COMPLETE)
- **File:** `src/copy_that/application/cv/typography_cv_extractor.py` (250+ lines)
- **Class:** `CVTypographyExtractor` with Pytesseract OCR
- **Fallback:** When AI fails or image lacks clear text
- **Output:** List of `ExtractedTypographyToken`

### 4. Service Layer (COMPLETE)
- **File:** `src/copy_that/services/typography_service.py` (280+ lines)
- **Functions:**
  - `typography_attributes()` - normalize token attributes
  - `build_typography_repo()` - create TokenRepository
  - `build_typography_repo_from_db()` - DB → graph conversion
  - `merge_typography()` - merge AI + CV results
  - `aggregate_typography_batch()` - deduplicate tokens
  - `deduplicate_typography()` - remove duplicates

### 5. Integration with Token Graph (READY)
- **Helper:** `make_typography_token()` already exists in `src/core/tokens/typography.py`
- **Already Called By:** W3C export (`design_tokens.py`)
- **Status:** Waiting for API to populate database

---

## What's Needed (Next 3 Steps)

### Step 6: REST API Endpoints (2-3 hours)

**File to Create:** `src/copy_that/interfaces/api/typography.py` (~350 lines)

#### 6a. Define Response Models

```python
from pydantic import BaseModel, Field
from datetime import datetime

class TypographyTokenResponse(BaseModel):
    """API response for a single typography token"""
    id: int
    font_family: str
    font_weight: int
    font_size: int
    line_height: float
    letter_spacing: float | None
    text_transform: str | None
    semantic_role: str
    category: str | None
    confidence: float
    created_at: datetime

    class Config:
        from_attributes = True

class TypographyExtractionRequest(BaseModel):
    """Request body for POST /typography/extract"""
    image_url: str | None = None
    image_base64: str | None = None
    project_id: int | None = None
    max_tokens: int = Field(default=15, ge=1, le=50)

class TypographyExtractionResponse(BaseModel):
    """Response for POST /typography/extract"""
    tokens: list[TypographyTokenResponse]
    extraction_confidence: float
    typography_palette: str | None
    extraction_metadata: dict | None
```

#### 6b. Define Router with 5 Endpoints

Pattern to follow: `src/copy_that/interfaces/api/colors.py` (lines 1-100)

**Endpoints:**

1. **POST /api/v1/typography/extract**
   - Extract typography from image
   - Call: `AITypographyExtractor.extract_typography_from_base64()`
   - Store in DB if project_id provided
   - Return: `TypographyExtractionResponse`
   - Error handling: validate image_url OR image_base64 provided

2. **GET /api/v1/typography/projects/{project_id}**
   - List all typography tokens for project
   - Query: `select * from typography_tokens where project_id = ?`
   - Return: `{"project_id": id, "tokens": [...], "total": count}`
   - Error handling: 404 if project not found

3. **GET /api/v1/typography/{token_id}**
   - Get single token by ID
   - Query: `select * from typography_tokens where id = ?`
   - Return: `TypographyTokenResponse`
   - Error handling: 404 if not found

4. **PUT /api/v1/typography/{token_id}**
   - Update token fields
   - Accept: dict of fields to update
   - Return: updated `TypographyTokenResponse`
   - Error handling: 404 if not found, 400 if validation fails

5. **DELETE /api/v1/typography/{token_id}**
   - Delete token
   - Return: `{"status": "deleted"}`
   - Error handling: 404 if not found

#### 6c. Register Router in Main App

**File:** `src/copy_that/interfaces/api/main.py`

Add after line with colors router:
```python
from copy_that.interfaces.api import typography

app.include_router(typography.router)
```

---

### Step 7: Comprehensive Tests (1-2 hours)

**File to Create:** `tests/unit/api/test_typography_api.py` (~300 lines)

Pattern to follow: `tests/unit/api/test_shadows_api.py` or `test_colors_api.py`

#### 7a. Test Class Structure

```python
import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch, MagicMock

class TestTypographyExtraction:
    """Test extraction endpoint"""
    # 10+ tests for POST /typography/extract

    @pytest.mark.asyncio
    async def test_extract_from_base64(self, client: AsyncClient, db_session):
        # Test extraction from base64 image
        # Mock AITypographyExtractor
        # Verify response schema
        # Verify tokens stored in DB
        pass

    @pytest.mark.asyncio
    async def test_extract_from_url(self, client: AsyncClient):
        # Test extraction from image URL
        # Mock HTTP request for image download
        pass

    @pytest.mark.asyncio
    async def test_extract_no_image_error(self, client: AsyncClient):
        # Test 400 error when no image provided
        pass

    @pytest.mark.asyncio
    async def test_extract_with_project_persistence(self, client: AsyncClient, db_session):
        # Test tokens saved to DB
        pass

class TestTypographyCRUD:
    """Test CRUD operations"""
    # 12+ tests for GET/PUT/DELETE

    @pytest.mark.asyncio
    async def test_list_project_typography(self, client: AsyncClient, db_session):
        # GET /typography/projects/{project_id}
        pass

    @pytest.mark.asyncio
    async def test_get_single_token(self, client: AsyncClient, db_session):
        # GET /typography/{token_id}
        pass

    @pytest.mark.asyncio
    async def test_update_token(self, client: AsyncClient, db_session):
        # PUT /typography/{token_id}
        pass

    @pytest.mark.asyncio
    async def test_delete_token(self, client: AsyncClient, db_session):
        # DELETE /typography/{token_id}
        pass

class TestTypographyAggregation:
    """Test aggregation/deduplication"""
    # 8+ tests for service layer

    @pytest.mark.asyncio
    async def test_merge_ai_cv_results(self):
        # Test merge_typography() prefers AI
        pass

    @pytest.mark.asyncio
    async def test_deduplicate_by_properties(self):
        # Test deduplicate_typography()
        pass
```

#### 7b. Fixtures Needed

```python
@pytest.fixture
async def typography_tokens():
    """Sample typography tokens for testing"""
    return [
        ExtractedTypographyToken(
            font_family="Inter",
            font_weight=700,
            font_size=32,
            line_height=1.2,
            semantic_role="heading",
            confidence=0.95,
        ),
        # ... more tokens
    ]

@pytest.fixture
async def mock_ai_extractor():
    """Mock AI extractor"""
    with patch('copy_that.application.ai_typography_extractor.AITypographyExtractor') as mock:
        extractor = AsyncMock()
        # Mock extraction result
        yield extractor
```

---

### Step 8: W3C Export Integration (30 min)

**File to Update:** `src/copy_that/interfaces/api/design_tokens.py`

#### Current Structure
```python
# Lines 1-50: Colors export
# Lines 51-100: Spacing export
# Lines 101+: Final W3C merge
```

#### What to Add

1. **Add typography imports** (after spacing imports):
```python
from copy_that.domain.models import TypographyToken, FontFamilyToken, FontSizeToken
from copy_that.services.typography_service import build_typography_repo_from_db
```

2. **Add typography query** (in async function):
```python
# Query typography tokens
typography_query = select(TypographyToken).where(
    TypographyToken.project_id == project_id
)
typography_tokens = (await db.execute(typography_query)).scalars().all()

# Build typography repository
typography_repo = build_typography_repo_from_db(typography_tokens)
```

3. **Merge into W3C export** (final merge section):
```python
# Merge all repositories
merged_tokens = []
merged_tokens.extend(colors_repo.get_all_tokens())
merged_tokens.extend(spacing_repo.get_all_tokens())
merged_tokens.extend(typography_repo.get_all_tokens())

# Export to W3C
w3c_export = tokens_to_w3c(merged_tokens)
```

---

## Implementation Checklist

### Before Starting
- [ ] Read this guide completely
- [ ] Review `src/copy_that/interfaces/api/colors.py` (reference pattern)
- [ ] Review `tests/unit/api/test_colors_api.py` (test pattern)
- [ ] Check branch status: `git log --oneline -5`

### API Implementation
- [ ] Create `src/copy_that/interfaces/api/typography.py`
- [ ] Define response models (Pydantic)
- [ ] Create router with 5 endpoints
- [ ] Import and use service layer functions
- [ ] Handle errors (400, 404, 500)
- [ ] Register router in `main.py`
- [ ] Test manually with curl/Postman

### Testing
- [ ] Create `tests/unit/api/test_typography_api.py`
- [ ] Write extraction tests (POST)
- [ ] Write CRUD tests (GET/PUT/DELETE)
- [ ] Write aggregation tests (service layer)
- [ ] Mock AI extractor to avoid API calls
- [ ] Run: `pytest tests/unit/api/test_typography_api.py -v`
- [ ] Target: 30+ tests, all passing

### W3C Export
- [ ] Update `design_tokens.py` with typography imports
- [ ] Add typography token query
- [ ] Build typography repository
- [ ] Merge with colors/spacing
- [ ] Test export endpoint: `GET /api/v1/design-tokens/export/w3c`
- [ ] Verify typography section in JSON output

### Final Verification
- [ ] All tests passing: `pytest tests/unit/api/test_typography_api.py`
- [ ] Type checking: `pnpm typecheck`
- [ ] Linting: `ruff check src/copy_that/interfaces/api/typography.py`
- [ ] Manual test: Upload image → extract typography → verify API
- [ ] W3C export includes typography

---

## Key Code References

### Patterns to Copy From

**API Endpoints:** `src/copy_that/interfaces/api/colors.py`
- Response models (lines 1-60)
- Error handling (lines 61-100)
- Database queries (lines 101-200)
- Service layer integration (lines 201-250)

**Service Layer:** `src/copy_that/services/spacing_service.py`
- Attribute normalization (lines 1-30)
- Repository building (lines 31-50)
- Merging logic (lines 51-80)
- Aggregation (lines 81-120)

**Tests:** `tests/unit/api/test_shadows_api.py`
- Test structure (class per feature)
- Mocking patterns
- Fixture setup
- Assertions

### Critical Imports

For `typography.py`:
```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field
from datetime import datetime

from copy_that.application.ai_typography_extractor import (
    AITypographyExtractor,
    TypographyExtractionResult,
)
from copy_that.domain.models import TypographyToken, Project
from copy_that.infrastructure.database import get_db
from copy_that.services.typography_service import (
    build_typography_repo_from_db,
    merge_typography,
    deduplicate_typography,
)
```

---

## Potential Issues & Fixes

### Issue 1: Import Errors for Extractors
**Cause:** `AITypographyExtractor` not exported
**Fix:** Ensure `__all__` in `ai_typography_extractor.py` includes the class

### Issue 2: Database Session Not Injecting
**Cause:** Missing `Depends(get_db)` in endpoint signature
**Fix:** All endpoints need: `db: AsyncSession = Depends(get_db)`

### Issue 3: Pydantic Validation Fails on Optional Fields
**Cause:** Some fields can be None
**Fix:** Use `Optional[type] = Field(default=None, ...)`

### Issue 4: Tests Fail Due to Missing Mock
**Cause:** Not mocking `AITypographyExtractor` API call
**Fix:** Use `@patch('copy_that.application.ai_typography_extractor.AITypographyExtractor')`

### Issue 5: W3C Export Missing Typography
**Cause:** Forgot to import/call `build_typography_repo_from_db()`
**Fix:** Check `design_tokens.py` has all three: colors, spacing, typography

---

## Success Criteria

✅ **API Endpoints Working**
- POST /api/v1/typography/extract returns 200 with tokens
- GET /api/v1/typography/{id} returns token data
- PUT /api/v1/typography/{id} updates token
- DELETE /api/v1/typography/{id} deletes token

✅ **Tests Passing**
- 30+ tests all green
- Coverage > 90% for typography module
- No flaky tests

✅ **W3C Export Complete**
- GET /api/v1/design-tokens/export/w3c includes `"typography"` section
- Typography tokens properly formatted
- All 4 token types (colors, spacing, shadow, typography) in export

✅ **Type Safety**
- `pnpm typecheck` passes with 0 errors
- All imports resolved
- Pydantic models validate correctly

---

## Time Estimate

| Task | Time | Difficulty |
|------|------|------------|
| API Endpoints | 45 min | Easy (copy pattern) |
| Tests | 60 min | Medium (15-20 test cases) |
| W3C Integration | 20 min | Easy (3-4 lines added) |
| Debugging | 15 min | Medium (if issues arise) |
| **Total** | **140 min** | **~2.5 hours** |

---

## Files Summary

### Already Created ✅
1. `src/copy_that/application/ai_typography_extractor.py` - 500 lines
2. `src/copy_that/application/cv/typography_cv_extractor.py` - 250 lines
3. `src/copy_that/services/typography_service.py` - 280 lines
4. `src/copy_that/domain/models.py` - Updated with 3 new models
5. `alembic/versions/2025_12_03_add_typography_and_font_tokens.py` - Migration

### To Create Next
1. `src/copy_that/interfaces/api/typography.py` - 350 lines
2. `tests/unit/api/test_typography_api.py` - 300 lines
3. Update: `src/copy_that/interfaces/api/main.py` - 2 lines
4. Update: `src/copy_that/interfaces/api/design_tokens.py` - 15 lines

---

## Commands for Next Session

```bash
# Start from where we left off
cd /Users/noisebox/Documents/3_Development/Repos/copy-that
git log --oneline -5  # Verify you're on the right branch

# Run existing tests to verify everything still works
pytest tests/unit/test_typography*.py -v

# When ready to commit
git add src/copy_that/interfaces/api/typography.py
git add tests/unit/api/test_typography_api.py
git commit -m "Add typography API endpoints and tests"

# Final verification
pnpm typecheck
pytest tests/unit/api/test_typography_api.py -v
```

---

## Questions?

Refer to these docs for guidance:
1. `docs/HANDOFF_TYPOGRAPHY_FONTS_20251203_SESSION2.md` - Session summary
2. `docs/TYPOGRAPHY_AND_FONT_TOKENS_PLAN.md` - Detailed plan
3. `src/copy_that/interfaces/api/colors.py` - API pattern
4. `tests/unit/api/test_shadows_api.py` - Test pattern

All infrastructure is ready. Just need 2-3 hours of straightforward implementation!
