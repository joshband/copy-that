# Phase 4 Week 1: Color Token Vertical Slice

**Date:** 2025-11-19 | **Status:** In Progress (Days 1-4 Complete) | **Target:** Complete by End of Week

This is your detailed implementation guide for Week 1 of Phase 4: building color token extraction end-to-end.

---

## 📊 Why Color-First?

**Option A: Color-First (Vertical Slice)** ← CHOSEN ✅
- Implement ONE token type completely (extractor → schema → adapter → database → frontend → generator)
- Validate entire architecture in 1 week
- Low risk: only 1 type to refactor if needed
- ADHD-friendly: achievable milestones

**Option B: All-Tokens-Together (Horizontal Layers)**
- Implement schemas for ALL 9 token types
- Implement adapters for ALL types
- Implement database for ALL types
- Then integrate frontend
- **Problem:** 5+ weeks before knowing if architecture works

**Decision:** Color-First. Build ONE token type perfectly, then copy pattern for remaining tokens.

---

## ✅ Current Status

### Days 1-4: COMPLETE ✅

| Day | Focus | Status | Files Created |
|-----|-------|--------|---|
| **1** | Color core schema + code generation | ✅ Complete | 3 files |
| **2** | Adapter layer + 100% tests | ✅ Complete | 2 files |
| **3** | Database migration | ✅ Complete | 1 migration |
| **4** | AI extractor (Claude Structured Outputs) | ✅ Complete | 3 files |

**What's Done:**
- ✅ Color schema (core, API, generated code)
- ✅ ColorTokenAdapter with bidirectional conversion
- ✅ color_tokens database table
- ✅ AIColorExtractor using Claude Structured Outputs
- ✅ 41 backend tests passing (100%)
- ✅ Type-safe end-to-end (Pydantic → Zod)

### Day 5: FRONTEND INTEGRATION (NOW)

Time: 3-4 hours | Deliverable: Frontend displays extracted colors

---

## 📋 Day 5: Frontend Integration

### Morning: Query Colors from API

**File:** `src/copy_that/interfaces/api/routes/extraction.py` (CREATE)

```python
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from copy_that.domain.models import ColorToken, ExtractionJob
from copy_that.infrastructure.database import get_db

router = APIRouter(prefix="/api/v1", tags=["extraction"])

@router.get("/jobs/{job_id}/colors")
async def get_job_colors(job_id: int, db: AsyncSession = Depends(get_db)):
    """Get all color tokens from an extraction job"""
    result = await db.execute(
        select(ColorToken).where(ColorToken.extraction_job_id == job_id)
    )
    colors = result.scalars().all()
    return {
        "job_id": job_id,
        "colors": [
            {
                "hex": c.hex,
                "confidence": c.confidence,
                "semantic_name": c.semantic_name,
                "id": c.id
            }
            for c in colors
        ]
    }

@router.post("/jobs/{job_id}/extract-colors")
async def extract_colors(job_id: int, db: AsyncSession = Depends(get_db)):
    """Trigger color extraction for a job"""
    # TODO: Call AIColorExtractor here
    pass
```

**Test it:**
```bash
# Create a test job first
curl -X POST http://localhost:8000/api/v1/jobs \
  -H "Content-Type: application/json" \
  -d '{"project_id": 1, "source_url": "image.jpg", "extraction_type": "color"}'

# Get colors (should be empty initially)
curl http://localhost:8000/api/v1/jobs/1/colors
```

### Afternoon: Build Frontend Components

**File:** `frontend/src/components/ColorTokenCard.tsx`

```typescript
import React from 'react';

interface ColorToken {
  id: number;
  hex: string;
  confidence: number;
  semantic_name?: string;
}

export function ColorTokenCard({ token }: { token: ColorToken }) {
  const percentConfidence = Math.round(token.confidence * 100);

  return (
    <div className="color-token-card">
      <div className="color-swatch" style={{ backgroundColor: token.hex }} />

      <div className="token-info">
        <div className="token-hex">{token.hex}</div>
        {token.semantic_name && (
          <div className="token-name">{token.semantic_name}</div>
        )}
        <div className={`token-confidence ${getConfidenceClass(token.confidence)}`}>
          {percentConfidence}% confident
        </div>
      </div>
    </div>
  );
}

function getConfidenceClass(confidence: number): string {
  if (confidence >= 0.9) return 'high';
  if (confidence >= 0.75) return 'medium';
  return 'low';
}
```

**File:** `frontend/src/components/ColorTokenList.tsx`

```typescript
import React, { useEffect, useState } from 'react';
import { ColorTokenCard } from './ColorTokenCard';

interface ColorToken {
  id: number;
  hex: string;
  confidence: number;
  semantic_name?: string;
}

export function ColorTokenList({ jobId }: { jobId: number }) {
  const [colors, setColors] = useState<ColorToken[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchColors() {
      try {
        const response = await fetch(`/api/v1/jobs/${jobId}/colors`);
        if (!response.ok) throw new Error('Failed to fetch colors');

        const data = await response.json();
        setColors(data.colors);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error');
      } finally {
        setLoading(false);
      }
    }

    fetchColors();
  }, [jobId]);

  if (loading) return <div className="loading">Loading colors...</div>;
  if (error) return <div className="error">Error: {error}</div>;
  if (colors.length === 0) return <div className="empty">No colors extracted</div>;

  return (
    <div className="color-token-list">
      <h2>Extracted Colors ({colors.length})</h2>
      <div className="token-grid">
        {colors.map(color => (
          <ColorTokenCard key={color.id} token={color} />
        ))}
      </div>
    </div>
  );
}
```

**File:** `frontend/src/pages/ExtractColors.tsx`

```typescript
import React, { useState } from 'react';
import { ColorTokenList } from '../components/ColorTokenList';

export function ExtractColors() {
  const [jobId, setJobId] = useState<number | null>(null);
  const [uploading, setUploading] = useState(false);

  async function handleImageUpload(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    try {
      // 1. Create extraction job
      const jobResponse = await fetch('/api/v1/jobs', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          project_id: 1, // TODO: Get from context
          source_url: file.name,
          extraction_type: 'color'
        })
      });

      if (!jobResponse.ok) throw new Error('Failed to create job');
      const jobData = await jobResponse.json();
      const newJobId = jobData.id;

      // 2. Trigger extraction
      await fetch(`/api/v1/jobs/${newJobId}/extract-colors`, {
        method: 'POST'
      });

      setJobId(newJobId);
    } catch (err) {
      console.error('Upload failed:', err);
    } finally {
      setUploading(false);
    }
  }

  return (
    <div className="extract-colors-page">
      <h1>Extract Color Tokens</h1>

      <div className="upload-section">
        <input
          type="file"
          accept="image/*"
          onChange={handleImageUpload}
          disabled={uploading}
        />
        {uploading && <p>Uploading...</p>}
      </div>

      {jobId && <ColorTokenList jobId={jobId} />}
    </div>
  );
}
```

### End of Day 5: Test End-to-End

```bash
# 1. Start backend
uvicorn src.copy_that.interfaces.api.main:app --reload

# 2. Start frontend (in another terminal)
cd frontend
npm run dev

# 3. Navigate to http://localhost:5173/extract
# 4. Upload an image
# 5. See colors extracted and displayed!
```

---

## 🧪 Testing

### Backend Tests (Should Already Pass)

```bash
# Run all color tests
pytest tests/ -k color -v

# Expected: 41 passing
```

### New Integration Tests

**File:** `tests/integration/test_color_extraction_flow.py`

```python
import pytest
from httpx import AsyncClient
from copy_that.interfaces.api.main import app
from copy_that.infrastructure.database import AsyncSessionLocal

@pytest.mark.asyncio
async def test_color_extraction_end_to_end():
    """Test complete flow: upload → extract → query → display"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # 1. Create extraction job
        job_response = await client.post(
            "/api/v1/jobs",
            json={
                "project_id": 1,
                "source_url": "test.jpg",
                "extraction_type": "color"
            }
        )
        assert job_response.status_code == 200
        job_id = job_response.json()["id"]

        # 2. Extract colors
        extract_response = await client.post(f"/api/v1/jobs/{job_id}/extract-colors")
        assert extract_response.status_code == 200

        # 3. Query colors
        colors_response = await client.get(f"/api/v1/jobs/{job_id}/colors")
        assert colors_response.status_code == 200

        data = colors_response.json()
        assert "colors" in data
        assert len(data["colors"]) > 0

        # 4. Verify color structure
        color = data["colors"][0]
        assert "hex" in color
        assert "confidence" in color
        assert 0 <= color["confidence"] <= 1
```

---

## 📊 Success Criteria (End of Week 1)

**At end of Day 5, you should have:**

1. ✅ Color schema (core + API) - **DONE**
2. ✅ ColorTokenAdapter with tests - **DONE**
3. ✅ Database table with migration - **DONE**
4. ✅ AI extractor with Claude Structured Outputs - **DONE**
5. ⏳ **Frontend displays extracted colors** - IN PROGRESS
6. ⏳ **End-to-end tests passing** - IN PROGRESS
7. ⏳ **Feature deployed to staging** - PENDING

**Validation:**
- Upload image → Extract colors → See on frontend ✓
- All tests passing (backend + integration) ✓
- Confidence scores visible ✓
- Semantic names displayed ✓

---

## 🚀 Week 1 Deployment

### Pre-Deployment Checklist

- [ ] All tests passing (`pytest tests/ -v`)
- [ ] Frontend typecheck passes (`pnpm typecheck`)
- [ ] No console errors in frontend
- [ ] Database migrations applied
- [ ] API endpoints responding
- [ ] Frontend components rendering

### Deploy to Staging

```bash
# 1. Commit changes
git add .
git commit -m "feat: Color token extraction end-to-end (Phase 4 Week 1)"

# 2. Push to staging branch
git push origin feature/phase-4-color-tokens

# 3. Monitor CI/CD pipeline
# 4. Verify on staging environment
```

### Smoke Test

```bash
# 1. Load staging URL
# 2. Upload test image
# 3. Verify colors extracted
# 4. Check confidence scores
# 5. Test export to CSS/JSON
```

---

## 🎯 Week 2: Copy Pattern for Spacing Tokens

Once Week 1 is validated, Week 2 becomes easier:

1. **Copy color schema** → spacing schema
2. **Copy ColorTokenAdapter** → SpacingTokenAdapter
3. **Copy color_tokens table** → spacing_tokens table
4. **Copy AI extractor logic** → spacing extractor
5. **Copy frontend components** → reuse structure

**Time estimate:** 2-3 days (much faster!)

---

## 🔮 Weeks 3-5: Additional Tokens

| Week | Token | Duration | Notes |
|------|-------|----------|-------|
| **3** | Shadow | 1-2 days | Simpler pattern (Z-axis elevation) |
| **4** | Typography | 2 days | More complex (font stack, families) |
| **5** | Border + Opacity | 1-2 days | Simple scaling patterns |

By end of Week 5, all 5 core token types will be production-ready.

---

## 📝 Implementation Notes

### ColorTokenAdapter Pattern

This adapter pattern will be repeated for ALL token types:

```python
# Abstract base (create once)
class BaseTokenAdapter:
    def to_api_schema(self, core: CoreToken) -> APIToken:
        raise NotImplementedError

# Specific implementation (repeat for each token type)
class ColorTokenAdapter(BaseTokenAdapter):
    def to_api_schema(self, core: CoreColorToken) -> APIColorToken:
        # Transform core → API with enrichment
        pass
```

### Database Table Pattern

Same pattern for all token types:

```python
class ColorToken(Base):
    __tablename__ = "color_tokens"

    id: int (PK)
    extraction_job_id: int (FK)
    [token-specific fields]
    confidence: float
    semantic_name: str
    metadata: JSONB
    created_at: datetime
```

### Frontend Component Pattern

Reusable structure for all token types:

```typescript
// Generic
<TokenCard token={token} />
<TokenList jobId={jobId} type="color" />

// Rendered for each type
<ColorTokenList />
<SpacingTokenList />
<TypographyTokenList />
```

---

## 🐛 Troubleshooting

### Database Errors

```bash
# Check current migration version
alembic current

# See migration history
alembic history

# Rollback and retry
alembic downgrade -1
alembic upgrade head
```

### API Endpoint Issues

```bash
# Test endpoint directly
curl http://localhost:8000/api/v1/jobs/1/colors

# Check FastAPI docs
open http://localhost:8000/docs
```

### Frontend Type Errors

```bash
# Run typecheck
pnpm typecheck

# Fix issues in TypeScript files
```

---

## 📚 Related Documentation

- **token_system.md** - Complete token reference
- **setup/database_setup.md** - Database configuration and migrations
- **setup/start_here.md** - Quick start and overview

---

## ✨ What You're Building

By end of Week 1, you'll have:

```
Image Upload
    ↓
AI Analysis (Claude Structured Outputs)
    ↓
Type-Safe Extraction (Pydantic)
    ↓
Adapter Transformation (ColorTokenAdapter)
    ↓
Database Storage (Neon PostgreSQL)
    ↓
API Query (/api/v1/jobs/{id}/colors)
    ↓
Frontend Display (React Components)
    ↓
Export Options (CSS, JSON, etc.)
```

**Result:** Complete end-to-end color extraction pipeline! 🎉

---

**Week:** 1 of Phase 4 | **Status:** Days 1-4 Complete, Day 5 In Progress | **Target:** Complete by 2025-11-23
