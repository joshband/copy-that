# How to Add Features

**Version:** 1.0 | **Date:** 2025-11-19 | **Status:** Complete

Step-by-step guide for adding new features to Copy That, from planning to deployment.

---

## 🎯 Feature Development Workflow

```
1. PLAN        Define what you're building
2. DESIGN      Architecture and schema
3. IMPLEMENT   Write code following patterns
4. TEST        Achieve 80%+ coverage
5. REVIEW      Get feedback via PR
6. DEPLOY      Ship to staging/production
```

---

## Step 1: PLAN - Define the Feature

### Example: "Add Opacity Token Extraction"

Create a feature document (or issue) with:

```markdown
## Feature: Opacity Token Extraction

### Problem
Users can't extract opacity/transparency values from designs

### Solution
Add OpacityExtractor to detect transparency scales

### Success Criteria
- Extract 3-5 opacity levels per image
- Confidence scores ≥ 0.75
- Integrate with existing token flow

### Effort Estimate
- Backend: 2 days
- Frontend: 1 day
- Testing: 1 day
Total: 4 days

### Dependencies
- Requires ColorExtractor (already done)
- Needs Opacity schema (to be created)
```

### Questions to Answer

1. **What problem does this solve?** (user need)
2. **How will it integrate?** (existing systems)
3. **What's the success criteria?** (measurable)
4. **What's the effort?** (realistic estimate)
5. **What are dependencies?** (blockers?)

---

## Step 2: DESIGN - Architecture

### 1. Choose Pattern

Copy That has established patterns. Use them:

**For new Token Type:** Follow color-first vertical slice pattern
- Day 1: Schema (Core, API, Generated code)
- Day 2: Adapter layer + tests
- Day 3: Database table + migration
- Day 4: Extractor + AI integration
- Day 5: Frontend + E2E tests

**For new Extractor:** Follow BaseExtractor pattern
- Inherit from `BaseTokenExtractor`
- Implement `extract()`, `validate()`
- Add comprehensive tests

**For new Generator:** Follow BasePlugin pattern
- Inherit from `BasePlugin`
- Implement `execute()`
- Register with `PluginRegistry`

### 2. Create Schema

**File:** `src/copy_that/domain/schemas/opacity.py`

```python
from pydantic import BaseModel, Field

class CoreOpacityToken(BaseModel):
    """Core opacity token (ground truth)"""
    value: float = Field(ge=0, le=1, description="Opacity 0-1")
    confidence: float = Field(ge=0, le=1)
    token_type: Literal['opacity']

class APIOpacityToken(BaseModel):
    """API opacity token (enriched)"""
    value: float
    confidence: float
    token_type: Literal['opacity']
    semantic_name: Optional[str] = None
    created_at: datetime
```

### 3. Database Schema

**File:** `alembic/versions/xxx_add_opacity_tokens.py`

```python
def upgrade():
    op.create_table(
        'opacity_tokens',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('extraction_job_id', sa.Integer(), nullable=False),
        sa.Column('value', sa.Float(), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=False),
        sa.Column('semantic_name', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['extraction_job_id'], ['extraction_jobs.id']),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade():
    op.drop_table('opacity_tokens')
```

---

## Step 3: IMPLEMENT - Write Code

### 1. Create Extractor

**File:** `src/copy_that/extractors/opacity_extractor.py`

```python
from copy_that.extractors.base import BaseTokenExtractor

class OpacityExtractor(BaseTokenExtractor):
    """Extract opacity/transparency scales from image"""

    def extract(self, image_bytes: bytes) -> List[Dict]:
        """Extract opacity tokens"""
        # Your extraction logic here
        # Detect transparent regions, measure opacity values
        # Return list of dicts with 'value' and 'confidence'
        pass

    def validate(self, tokens: List[Dict]) -> bool:
        """Validate extracted tokens"""
        # Check all required fields present
        # Check values in valid range
        pass
```

### 2. Create Adapter

**File:** `src/copy_that/adapters/opacity_adapter.py`

```python
from copy_that.adapters.base import BaseTokenAdapter
from copy_that.domain.schemas.opacity import CoreOpacityToken, APIOpacityToken

class OpacityTokenAdapter(BaseTokenAdapter):
    """Transform opacity tokens between layers"""

    def to_api_schema(self, core: CoreOpacityToken) -> APIOpacityToken:
        """Core → API (add metadata)"""
        semantic_name = self._generate_semantic_name(core.value)
        return APIOpacityToken(
            value=core.value,
            confidence=core.confidence,
            token_type=core.token_type,
            semantic_name=semantic_name,
            created_at=datetime.utcnow()
        )

    def _generate_semantic_name(self, value: float) -> str:
        """Generate semantic name for opacity level"""
        if value < 0.25:
            return "subtle"
        elif value < 0.5:
            return "light"
        elif value < 0.75:
            return "medium"
        else:
            return "strong"
```

### 3. Register Plugin

**File:** `src/copy_that/interfaces/api/main.py`

```python
from copy_that.extractors.opacity_extractor import OpacityExtractor
from copy_that.infrastructure.plugins.registry import PluginRegistry

# At startup
PluginRegistry.register_extractor('opacity', OpacityExtractor())
```

### 4. Add API Endpoint

**File:** `src/copy_that/interfaces/api/routes/extraction.py`

```python
from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()

@router.post("/api/v1/extract/opacity")
async def extract_opacity(
    file: UploadFile = File(...),
    project_id: int = Query(...),
    db: AsyncSession = Depends(get_db)
):
    """Extract opacity tokens from image"""
    # Read image
    image_bytes = await file.read()

    # Get extractor from registry
    extractor = PluginRegistry.get_extractor('opacity')

    # Extract
    core_tokens = extractor.extract(image_bytes)

    # Adapt and store
    adapter = OpacityTokenAdapter()
    api_tokens = [adapter.to_api_schema(ct) for ct in core_tokens]

    # Store in database
    for api_token in api_tokens:
        db_token = OpacityToken(**adapter.to_database_schema(api_token, project_id))
        db.add(db_token)
    await db.commit()

    return {"opacity_tokens": [t.model_dump() for t in api_tokens]}
```

---

## Step 4: TEST - Achieve Coverage

### 1. Unit Tests

**File:** `tests/unit/test_opacity_extractor.py`

```python
import pytest
from copy_that.extractors.opacity_extractor import OpacityExtractor

class TestOpacityExtractor:
    @pytest.fixture
    def extractor(self):
        return OpacityExtractor()

    def test_extract_opacity_tokens(self, extractor, sample_transparent_image):
        """Test extraction"""
        tokens = extractor.extract(sample_transparent_image)

        assert len(tokens) > 0
        for token in tokens:
            assert 'value' in token
            assert 'confidence' in token
            assert 0 <= token['value'] <= 1

    def test_validate_tokens(self, extractor):
        """Test validation"""
        valid = [{'value': 0.5, 'confidence': 0.9}]
        assert extractor.validate(valid)

        invalid = [{'value': 1.5, 'confidence': 0.9}]  # Out of range
        assert not extractor.validate(invalid)
```

### 2. Integration Tests

**File:** `tests/integration/test_opacity_extraction_flow.py`

```python
@pytest.mark.asyncio
async def test_opacity_extraction_end_to_end(db_session):
    """Test full extraction pipeline"""
    # Create test image
    image_bytes = create_test_transparent_image()

    # Extract
    extractor = OpacityExtractor()
    core_tokens = extractor.extract(image_bytes)

    # Adapt
    adapter = OpacityTokenAdapter()
    api_tokens = [adapter.to_api_schema(ct) for ct in core_tokens]

    # Store
    for api_token in api_tokens:
        db_token = OpacityToken(**adapter.to_database_schema(api_token, job_id=1))
        db_session.add(db_token)
    await db_session.commit()

    # Query
    result = await db_session.execute(
        select(OpacityToken).where(OpacityToken.job_id == 1)
    )
    stored = result.scalars().all()

    assert len(stored) > 0
    assert all(0 <= t.value <= 1 for t in stored)
```

### 3. API Tests

```python
@pytest.mark.asyncio
async def test_extract_opacity_endpoint():
    """Test POST /api/v1/extract/opacity"""
    image_bytes = create_test_transparent_image()

    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/extract/opacity",
            files={"file": ("test.png", image_bytes)},
            params={"project_id": 1}
        )

        assert response.status_code == 200
        data = response.json()
        assert "opacity_tokens" in data
        assert len(data["opacity_tokens"]) > 0
```

### 4. Run Tests

```bash
# Run all tests
pytest

# Check coverage
pytest --cov=src/copy_that --cov-report=html

# Target: 80%+ coverage
```

---

## Step 5: REVIEW - Get Feedback

### 1. Create Pull Request

```bash
# Create feature branch
git checkout -b feature/opacity-extraction

# Make changes, commit
git add .
git commit -m "feat: Add opacity token extraction

- Add OpacityExtractor with transparency detection
- Create OpacityTokenAdapter for schema transformation
- Add opacity_tokens database table
- Implement /api/v1/extract/opacity endpoint
- Add 20+ unit/integration/API tests

Closes #123"

# Push
git push origin feature/opacity-extraction

# Create PR
gh pr create --title "Add opacity token extraction" \
  --body "Implements opacity token extraction for images..."
```

### 2. PR Checklist

- [ ] All tests passing (`pytest`)
- [ ] Type checking passes (`mypy src/`)
- [ ] Linting clean (`ruff check .`)
- [ ] Coverage ≥ 80%
- [ ] Documentation updated
- [ ] No breaking changes

### 3. Address Feedback

Get feedback from team, address comments, iterate.

---

## Step 6: DEPLOY - Ship to Production

### 1. Merge to Main

```bash
# After PR approved
gh pr merge --merge

# Result: feature branch merged, deleted
# Triggers deployment to production
```

### 2. Monitor Deployment

```bash
# Watch CI/CD pipeline
gh run watch

# Check logs if needed
gh run view
```

### 3. Verify in Production

```bash
# Test endpoint
curl https://api.copythis.io/api/v1/extract/opacity \
  -F "file=@image.png" \
  -F "project_id=1"

# Check logs for errors
gcloud run services logs read copy-that-api
```

---

## 🔄 Common Patterns

### Adding Another Token Type (Repeat Pattern)

Once opacity is done, adding Border-Radius follows same pattern:

```
1. Create CoreBorderRadiusToken schema
2. Create APIBorderRadiusToken schema
3. Create BorderRadiusExtractor
4. Create BorderRadiusTokenAdapter
5. Add database migration
6. Register plugin
7. Add API endpoint
8. Add tests
9. PR and merge
```

**Time:** 3-4 days (vs 4 days for opacity because pattern is proven)

### Adding New Generator

Adding Flutter generator follows plugin pattern:

```
1. Create FlutterGeneratorPlugin
2. Implement execute() method
3. Register in PluginRegistry
4. Add unit tests
5. Add /api/v1/export?format=flutter endpoint
```

**Time:** 1-2 days

---

## ⚠️ Common Mistakes

### ❌ Don't: Skip Tests
```python
def new_feature():
    # No tests? Don't do this!
    pass
```

**Why:** No confidence it works, breaks later, hard to maintain.

### ❌ Don't: Break Existing Tests
```python
def existing_function():
    # Changed behavior but didn't update tests
    return "different result"
```

**Why:** CI fails, blocks deployment, breaks other features.

### ❌ Don't: Ignore Patterns
```python
# New extractor that doesn't inherit from BaseExtractor
class MyExtractor:
    def extract_tokens(self):  # Wrong method name
        pass
```

**Why:** Inconsistent codebase, plugin discovery fails, others confused.

### ❌ Don't: Leave TODO Comments
```python
def new_feature():
    # TODO: fix this later
    pass
```

**Why:** Never gets fixed, technical debt grows.

---

## ✅ Best Practices

### ✅ Do: Plan First
Before coding, write down: what, why, success criteria, estimate.

### ✅ Do: Follow Patterns
Use existing patterns: Extractor, Adapter, Plugin, etc.

### ✅ Do: Test as You Go
Write tests WHILE implementing, not after.

### ✅ Do: Commit Frequently
Small, logical commits with clear messages.

### ✅ Do: Document as You Go
Update docs alongside code.

---

## 📚 Reference Docs

- **extractor_patterns.md** - How to build extractors
- **adapter_pattern.md** - Schema transformation
- **plugin_architecture.md** - Plugin system
- **testing/testing_overview.md** - Test strategies
- **api_reference.md** - API endpoints

---

## 📊 Feature Checklist

Before shipping any feature:

- [ ] Code written and committed
- [ ] All tests passing (80%+ coverage)
- [ ] Type checking passes
- [ ] Linting clean
- [ ] Documentation updated
- [ ] Pull request created
- [ ] PR reviewed and approved
- [ ] No merge conflicts
- [ ] CI/CD pipeline passing
- [ ] Deployed to staging
- [ ] Tested in staging
- [ ] Merged to main
- [ ] Deployed to production
- [ ] Verified in production
- [ ] Monitoring setup

---

**Version:** 1.0 | **Last Updated:** 2025-11-19 | **Status:** Complete
