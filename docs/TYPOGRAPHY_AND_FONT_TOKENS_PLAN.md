# Typography & Font Tokens Implementation Plan

**Status:** Ready to Implement
**Priority:** HIGH (core design system component)
**Estimated Duration:** 3-4 days
**Pattern:** Follow proven color/spacing/shadow architecture

---

## Overview

This plan implements typography and font token extraction following the established vertical slice pattern:
- **Option A: Typography Tokens** - Extract fonts, sizes, line heights, and text properties from images
- **Option B: Font Family & Font Size Tokens** - Support tokens for typography system

---

## Part A: Typography Tokens Implementation

### Architecture Pattern

```
Image Upload
    ↓
┌─────────────────────────────────────────┐
│ AI Extractor (Claude 4.5 Vision)        │
│ • Analyze fonts in design system        │
│ • Extract font family references        │
│ • Identify font sizes and weights       │
│ • Detect line heights, letter spacing   │
│ • Analyze text colors & opacity         │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│ CV Extractor (OCR + Font Detection)     │
│ • pytesseract for text detection        │
│ • PIL ImageDraw for font analysis       │
│ • Fallback when AI fails                │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│ TypographyToken (Database)              │
│ • Store extracted properties            │
│ • Link to project & extraction_job      │
│ • Confidence scoring                    │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│ Service Layer (db_typography_to_repo)   │
│ • Convert DB → TokenRepository          │
│ • Build relationships to color/fonts    │
│ • Aggregation/deduplication             │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│ REST API Endpoints                      │
│ • POST /api/v1/typography/extract       │
│ • GET /api/v1/typography/projects/{id}  │
│ • GET /api/v1/typography/{id}           │
│ • PUT /api/v1/typography/{id}           │
│ • DELETE /api/v1/typography/{id}        │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│ W3C Export                              │
│ • Integrated in design_tokens.py        │
│ • Merged with colors/spacing/shadows    │
└─────────────────────────────────────────┘
```

---

## Implementation Steps

### Step 1: Database Model (2 hours)

**File:** `src/copy_that/domain/models.py`

Add `TypographyToken` model:

```python
class TypographyToken(Base):
    __tablename__ = "typography_tokens"

    # Standard fields
    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"))
    extraction_job_id: Mapped[int | None] = mapped_column(ForeignKey("extraction_jobs.id"))

    # Typography-specific fields
    font_family: Mapped[str] = mapped_column(String(128))  # e.g., "Inter", "Roboto"
    font_weight: Mapped[int] = mapped_column(Integer, default=400)  # 100-900
    font_size: Mapped[int] = mapped_column(Integer)  # in pixels
    line_height: Mapped[float] = mapped_column(Float)  # 1.0-2.5 multiplier
    letter_spacing: Mapped[float | None] = mapped_column(Float)  # in em units
    text_transform: Mapped[str | None] = mapped_column(String(20))  # uppercase, lowercase, capitalize

    # Design properties
    name: Mapped[str | None] = mapped_column(String(128))  # e.g., "Heading 1", "Body"
    semantic_role: Mapped[str | None] = mapped_column(String(50))  # heading, body, caption, etc.
    category: Mapped[str | None] = mapped_column(String(50))  # display, text, label, etc.

    # Quality metrics
    confidence: Mapped[float] = mapped_column(Float, default=0.8)  # 0.0-1.0
    extraction_metadata: Mapped[dict] = mapped_column(JSON)  # {source, model, tokens_used}

    # Usage tracking
    usage: Mapped[list[dict]] = mapped_column(JSON, default=[])  # where used in design

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="typography_tokens")
    extraction_job: Mapped["ExtractionJob | None"] = relationship("ExtractionJob")
```

**Create migration:**
```bash
alembic revision --autogenerate -m "add_typography_tokens"
alembic upgrade head
```

---

### Step 2: AI Typography Extractor (4 hours)

**File:** `src/copy_that/application/ai_typography_extractor.py`

```python
from anthropic import Anthropic
from pydantic import BaseModel, Field
from copy_that.domain.models import TypographyToken

class ExtractedTypographyToken(BaseModel):
    font_family: str = Field(description="Font family name (e.g., Inter, Roboto)")
    font_weight: int = Field(ge=100, le=900, description="Font weight 100-900")
    font_size: int = Field(ge=8, le=120, description="Font size in pixels")
    line_height: float = Field(ge=0.8, le=3.0, description="Line height multiplier")
    letter_spacing: float | None = Field(default=None, description="Letter spacing in em")
    text_transform: str | None = Field(default=None, description="Text transform")
    semantic_role: str = Field(description="Role: heading, body, caption, label")
    category: str | None = Field(default=None, description="Category: display, text, label")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence 0-1")

class TypographyExtractionResult(BaseModel):
    tokens: list[ExtractedTypographyToken]
    confidence: float
    metadata: dict

class AITypographyExtractor:
    def __init__(self, model: str = "claude-sonnet-4.5"):
        self.client = Anthropic()
        self.model = model

    async def extract(self, image_url: str | None, image_base64: str | None) -> TypographyExtractionResult:
        """Extract typography tokens from image using Claude vision."""

        # Build image content block
        if image_base64:
            image_content = {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": "image/png",
                    "data": image_base64,
                },
            }
        elif image_url:
            image_content = {
                "type": "image",
                "source": {
                    "type": "url",
                    "url": image_url,
                },
            }
        else:
            raise ValueError("Either image_base64 or image_url must be provided")

        # Use Anthropic Structured Outputs
        response = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            messages=[
                {
                    "role": "user",
                    "content": [
                        image_content,
                        {
                            "type": "text",
                            "text": """Analyze this design/screenshot and extract all typography tokens.

For each distinct typography style you find, extract:
1. Font family name (e.g., "Inter", "Roboto", "Georgia")
2. Font weight (100-900)
3. Font size in pixels (approximate if needed)
4. Line height (as multiplier, e.g., 1.5)
5. Letter spacing (if visible, in em units)
6. Text transform (uppercase/lowercase/capitalize if applied)
7. Semantic role (heading, body, caption, label, etc.)
8. Category (display, text, label, etc.)
9. Confidence 0-1 (how certain you are)

Return results as JSON."""
                        }
                    ],
                }
            ],
            betas=["interop-2024-12-01"],
        )

        # Parse response (simplified - actual implementation uses Structured Outputs)
        # For now, use JSON parsing from the response
        result = TypographyExtractionResult(
            tokens=[],
            confidence=0.85,
            metadata={
                "model": self.model,
                "extraction_source": "claude_sonnet_4.5",
            }
        )
        return result
```

---

### Step 3: CV Typography Extractor (3 hours)

**File:** `src/copy_that/application/cv/typography_cv_extractor.py`

```python
import pytesseract
from PIL import Image, ImageDraw
import io
from copy_that.application.ai_typography_extractor import ExtractedTypographyToken

class CVTypographyExtractor:
    """Computer vision-based typography extraction using OCR."""

    async def extract(self, image_data: bytes) -> list[ExtractedTypographyToken]:
        """Extract typography using OCR and image analysis."""

        try:
            # Load image
            image = Image.open(io.BytesIO(image_data))

            # Use pytesseract for text detection
            data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)

            tokens = []

            # Group text by position/size to identify typography
            font_sizes = {}
            for i, text in enumerate(data['text']):
                if text.strip():
                    height = data['height'][i]
                    # Group by approximate height (font size proxy)
                    size_key = round(height / 5) * 5
                    if size_key not in font_sizes:
                        font_sizes[size_key] = []
                    font_sizes[size_key].append({
                        'text': text,
                        'x': data['left'][i],
                        'y': data['top'][i],
                        'width': data['width'][i],
                        'height': data['height'][i],
                        'confidence': data['conf'][i] / 100.0
                    })

            # Create typography tokens from grouped text
            for size, text_items in font_sizes.items():
                if text_items and len(text_items) > 0:
                    avg_confidence = sum(t['confidence'] for t in text_items) / len(text_items)

                    # Infer semantic role from position and size
                    semantic_role = self._infer_role(size, text_items)

                    token = ExtractedTypographyToken(
                        font_family="System",  # Would need font detection library for actual font
                        font_weight=400,
                        font_size=max(size, 12),
                        line_height=1.5,
                        letter_spacing=None,
                        text_transform=None,
                        semantic_role=semantic_role,
                        category="text",
                        confidence=min(avg_confidence, 0.8),
                    )
                    tokens.append(token)

            return tokens

        except Exception as e:
            return []  # Fallback

    def _infer_role(self, size: int, text_items: list[dict]) -> str:
        """Infer typography role from size and position."""
        if size > 32:
            return "heading"
        elif size > 20:
            return "subheading"
        elif size < 12:
            return "caption"
        else:
            return "body"
```

---

### Step 4: Service Layer (2 hours)

**File:** `src/copy_that/services/typography_service.py`

```python
from sqlalchemy.ext.asyncio import AsyncSession
from copy_that.domain.models import TypographyToken
from core.tokens.repository import TokenRepository, InMemoryTokenRepository
from core.tokens.model import Token, TokenType

def typography_attributes(token: TypographyToken | dict) -> dict:
    """Normalize typography attributes."""
    if isinstance(token, dict):
        return token
    return {
        "font_family": token.font_family,
        "font_weight": token.font_weight,
        "font_size": token.font_size,
        "line_height": token.line_height,
        "letter_spacing": token.letter_spacing,
        "text_transform": token.text_transform,
        "semantic_role": token.semantic_role,
    }

def build_typography_repo_from_db(
    tokens: list[TypographyToken],
    namespace: str = "token/typography/export/all"
) -> TokenRepository:
    """Convert DB typography tokens to TokenRepository."""
    repo = InMemoryTokenRepository()

    for token in tokens:
        core_token = Token(
            id=f"{namespace}/{token.semantic_role or 'typography'}/{token.font_size}",
            type=TokenType.TYPOGRAPHY,
            value={
                "fontFamily": token.font_family,
                "fontWeight": token.font_weight,
                "fontSize": token.font_size,
                "lineHeight": token.line_height,
                "letterSpacing": token.letter_spacing,
            },
            attributes=typography_attributes(token),
        )
        repo.upsert_token(core_token)

    return repo

def aggregate_typography_batch(
    tokens: list[TypographyToken],
) -> list[TypographyToken]:
    """Deduplicate similar typography tokens."""
    # Group by font_family + font_weight + font_size
    groups = {}
    for token in tokens:
        key = (token.font_family, token.font_weight, token.font_size)
        if key not in groups:
            groups[key] = []
        groups[key].append(token)

    # Select highest confidence from each group
    result = []
    for group in groups.values():
        best = max(group, key=lambda t: t.confidence)
        result.append(best)

    return result
```

---

### Step 5: REST API Endpoints (4 hours)

**File:** `src/copy_that/interfaces/api/typography.py`

```python
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from copy_that.application.ai_typography_extractor import AITypographyExtractor, TypographyExtractionResult
from copy_that.domain.models import TypographyToken, Project, ExtractionJob
from copy_that.infrastructure.database import get_db
from copy_that.services.typography_service import build_typography_repo_from_db, aggregate_typography_batch
from core.tokens.adapters.w3c import tokens_to_w3c

router = APIRouter(
    prefix="/api/v1/typography",
    tags=["typography"],
    responses={404: {"description": "Not found"}},
)

class TypographyTokenResponse(BaseModel):
    id: int
    font_family: str
    font_weight: int
    font_size: int
    line_height: float
    letter_spacing: float | None
    text_transform: str | None
    semantic_role: str | None
    confidence: float
    created_at: datetime

class TypographyExtractionRequest(BaseModel):
    image_url: str | None = None
    image_base64: str | None = None
    project_id: int | None = None
    max_tokens: int = 15

class TypographyExtractionResponse(BaseModel):
    tokens: list[TypographyTokenResponse]
    extraction_confidence: float
    extraction_metadata: dict
    w3c_export: dict | None = None

@router.post("/extract", response_model=TypographyExtractionResponse)
async def extract_typography(
    request: TypographyExtractionRequest,
    db: AsyncSession = Depends(get_db),
):
    """Extract typography tokens from image."""

    if not request.image_url and not request.image_base64:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either image_url or image_base64 required"
        )

    # Validate project if provided
    if request.project_id:
        project = await db.get(Project, request.project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project {request.project_id} not found"
            )

    # Extract using AI
    extractor = AITypographyExtractor()
    extraction_result = await extractor.extract(request.image_url, request.image_base64)

    # Store in database if project_id provided
    if request.project_id:
        job = ExtractionJob(project_id=request.project_id)
        db.add(job)
        await db.flush()

        for extracted_token in extraction_result.tokens:
            token = TypographyToken(
                project_id=request.project_id,
                extraction_job_id=job.id,
                font_family=extracted_token.font_family,
                font_weight=extracted_token.font_weight,
                font_size=extracted_token.font_size,
                line_height=extracted_token.line_height,
                letter_spacing=extracted_token.letter_spacing,
                text_transform=extracted_token.text_transform,
                semantic_role=extracted_token.semantic_role,
                category=extracted_token.category,
                confidence=extracted_token.confidence,
                extraction_metadata=extraction_result.metadata,
            )
            db.add(token)

        await db.commit()

    # Format response
    tokens = [
        TypographyTokenResponse(
            id=i,
            font_family=t.font_family,
            font_weight=t.font_weight,
            font_size=t.font_size,
            line_height=t.line_height,
            letter_spacing=t.letter_spacing,
            text_transform=t.text_transform,
            semantic_role=t.semantic_role,
            confidence=t.confidence,
            created_at=datetime.utcnow(),
        )
        for i, t in enumerate(extraction_result.tokens)
    ]

    return TypographyExtractionResponse(
        tokens=tokens,
        extraction_confidence=extraction_result.confidence,
        extraction_metadata=extraction_result.metadata,
    )

@router.get("/projects/{project_id}/typography")
async def list_project_typography(
    project_id: int,
    db: AsyncSession = Depends(get_db),
):
    """List all typography tokens for a project."""

    project = await db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    query = select(TypographyToken).where(TypographyToken.project_id == project_id)
    result = await db.execute(query)
    tokens = list(result.scalars().all())

    return {
        "project_id": project_id,
        "tokens": tokens,
        "total": len(tokens),
    }

@router.get("/{token_id}")
async def get_typography(token_id: int, db: AsyncSession = Depends(get_db)):
    """Get a single typography token."""
    token = await db.get(TypographyToken, token_id)
    if not token:
        raise HTTPException(status_code=404, detail="Typography token not found")
    return token

@router.put("/{token_id}")
async def update_typography(
    token_id: int,
    updates: dict,
    db: AsyncSession = Depends(get_db),
):
    """Update typography token."""
    token = await db.get(TypographyToken, token_id)
    if not token:
        raise HTTPException(status_code=404, detail="Not found")

    for key, value in updates.items():
        if hasattr(token, key):
            setattr(token, key, value)

    await db.commit()
    return token

@router.delete("/{token_id}")
async def delete_typography(token_id: int, db: AsyncSession = Depends(get_db)):
    """Delete typography token."""
    token = await db.get(TypographyToken, token_id)
    if not token:
        raise HTTPException(status_code=404, detail="Not found")

    await db.delete(token)
    await db.commit()
    return {"status": "deleted"}
```

**Register in main.py:**
```python
from copy_that.interfaces.api import typography
app.include_router(typography.router)
```

---

### Step 6: Comprehensive Tests (4 hours)

**File:** `tests/unit/api/test_typography_api.py`

Structure: 30+ tests following the color/spacing/shadow pattern

```python
import pytest
from httpx import AsyncClient
from copy_that.application.ai_typography_extractor import (
    ExtractedTypographyToken,
    TypographyExtractionResult,
)

class TestTypographyExtraction:
    # Test extract from base64
    # Test extract from URL
    # Test with project persistence
    # Test no image error
    # Test invalid project
    # Test response schema
    # Test confidence range
    # ... 25+ more tests

class TestTypographyCRUD:
    # Test list typography tokens
    # Test get single token
    # Test update token
    # Test delete token
    # ... 15+ more tests

class TestTypographyAggregation:
    # Test deduplication
    # Test preserve unique tokens
    # ... 5+ more tests
```

---

## Part B: Font Family & Font Size Tokens Implementation

### Step 1: Database Models (1 hour)

**File:** `src/copy_that/domain/models.py`

```python
class FontFamilyToken(Base):
    __tablename__ = "font_family_tokens"

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"))

    name: Mapped[str] = mapped_column(String(128))  # "Inter", "Roboto"
    category: Mapped[str] = mapped_column(String(50))  # "sans-serif", "serif", "mono"
    font_file_url: Mapped[str | None] = mapped_column(String(512))
    fallback_stack: Mapped[list[str]] = mapped_column(JSON)  # ["Helvetica", "Arial", "sans-serif"]

    confidence: Mapped[float] = mapped_column(Float, default=0.9)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class FontSizeToken(Base):
    __tablename__ = "font_size_tokens"

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"))

    size_px: Mapped[int] = mapped_column(Integer)
    size_rem: Mapped[float] = mapped_column(Float)
    semantic_name: Mapped[str | None] = mapped_column(String(50))  # "h1", "h2", "body", etc.

    confidence: Mapped[float] = mapped_column(Float, default=0.9)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
```

---

### Step 2: Font Detection Service (2 hours)

**File:** `src/copy_that/services/font_service.py`

```python
# Font detection and mapping service
# Google Fonts integration
# System font mapping
# Fallback stack generation
```

---

### Step 3: API Endpoints (2 hours)

**File:** `src/copy_that/interfaces/api/fonts.py`

- `POST /api/v1/fonts/families` - Register font family
- `POST /api/v1/fonts/sizes` - Register font size
- `GET /api/v1/fonts/families` - List all fonts
- `GET /api/v1/fonts/sizes` - List all sizes

---

### Step 4: Tests (2 hours)

**File:** `tests/unit/api/test_fonts_api.py`

- Font family CRUD tests
- Font size management tests
- Fallback stack generation tests

---

## W3C Export Integration (1 hour)

Update `src/copy_that/interfaces/api/design_tokens.py`:

```python
# Add typography and font imports
# Query typography tokens
# Build typography repo
# Merge into unified export
# Result: colors + spacing + shadows + typography + fonts in W3C JSON
```

---

## Timeline & Deliverables

### Day 1: Foundation (6 hours)
- ✅ Database models for all 5 entities
- ✅ Alembic migrations
- ✅ AI extractors (typography)
- ✅ CV extractors (typography)

### Day 2: Services & API (8 hours)
- ✅ Service layer for all types
- ✅ REST endpoints (typography + fonts)
- ✅ W3C export integration
- ✅ Route registration

### Day 3: Testing & Polish (6 hours)
- ✅ Comprehensive test suite (40+ tests)
- ✅ Error handling & validation
- ✅ Documentation updates
- ✅ Code review & fixes

### Day 4: Verification (4 hours)
- ✅ Integration tests
- ✅ End-to-end flow testing
- ✅ Performance validation
- ✅ Final commit & merge

---

## Success Criteria

✅ All 40+ tests passing
✅ W3C export includes typography and fonts
✅ API endpoints fully functional
✅ Zero Pydantic validation errors
✅ TypeScript frontend types generated
✅ End-to-end extraction working
✅ Token graph relationships complete

---

## Files to Create/Modify

### New Files
- `src/copy_that/application/ai_typography_extractor.py`
- `src/copy_that/application/cv/typography_cv_extractor.py`
- `src/copy_that/services/typography_service.py`
- `src/copy_that/services/font_service.py`
- `src/copy_that/interfaces/api/typography.py`
- `src/copy_that/interfaces/api/fonts.py`
- `tests/unit/api/test_typography_api.py`
- `tests/unit/api/test_fonts_api.py`
- `alembic/versions/2025_12_03_add_typography_font_tokens.py`

### Modified Files
- `src/copy_that/domain/models.py` - Add 3 new token models
- `src/copy_that/interfaces/api/main.py` - Register new routers
- `src/copy_that/interfaces/api/design_tokens.py` - Add typography/font export
- `src/core/tokens/model.py` - Verify TokenType enum (already complete)

---

## Architecture Notes

This implementation follows the proven pattern established by color, spacing, and shadow tokens:

1. **AI Extractor First** - Claude Sonnet 4.5 with Structured Outputs
2. **CV Fallback** - Pytesseract for OCR + image analysis
3. **Standardized Service Layer** - db_*_to_repo() pattern
4. **REST API** - 5 standard endpoints per type (extract, list, get, update, delete)
5. **Comprehensive Testing** - 30+ tests per token type
6. **W3C Integration** - All tokens exported to unified schema

---

## Ready to Begin?

Proceed with Step 1: Database Models

```bash
cd /Users/noisebox/Documents/3_Development/Repos/copy-that
# Will implement TypographyToken and FontFamily/FontSize models
```
