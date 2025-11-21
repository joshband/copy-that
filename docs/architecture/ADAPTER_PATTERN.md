# Adapter Pattern: Schema Transformation

**Version:** 1.0 | **Date:** 2025-11-19 | **Status:** Guide

This document explains the Adapter pattern used to transform tokens between different schema layers in Copy That.

---

## 🎯 The Problem

When tokens flow through Copy That, they need to be transformed multiple times:

```
Extractor Output (Raw)
    ↓
    Core Schema (Ground truth)
    ↓
    API Schema (Public interface)
    ↓
    Database Schema (Persistence)
    ↓
    Frontend Schema (UI needs)
```

Each transformation needs to:
- ✅ Validate data
- ✅ Add metadata
- ✅ Remove sensitive fields
- ✅ Transform field names
- ✅ Maintain type safety

**Without adapters:** Data transformation scattered throughout codebase, hard to maintain, error-prone.

**With adapters:** Centralized, testable, bidirectional transformations.

---

## 💡 The Solution: Adapter Pattern

### Three-Layer Schema

```python
# Layer 1: CORE SCHEMA (Ground Truth)
class CoreColorToken(BaseModel):
    """Minimal, validated color token from extractor"""
    hex: str        # Required: hex color code
    confidence: float  # Required: 0-1 confidence score
    token_type: Literal['color']  # Type identifier

# Layer 2: API SCHEMA (Public Interface)
class APIColorToken(BaseModel):
    """Rich, metadata-enhanced token for API responses"""
    hex: str
    confidence: float
    token_type: Literal['color']
    semantic_name: Optional[str] = None  # Added: human-readable name
    created_at: datetime  # Added: timestamp
    metadata: Dict[str, Any] = {}  # Added: extra data

# Layer 3: DATABASE SCHEMA (Persistence)
class ColorToken(SQLModel, table=True):
    """Mapped to color_tokens table in database"""
    __tablename__ = "color_tokens"

    id: Optional[int] = Field(default=None, primary_key=True)
    extraction_job_id: int = Field(foreign_key="extraction_jobs.id")
    hex: str
    confidence: float
    semantic_name: Optional[str] = None
    metadata: Optional[dict] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

### Adapter: Bidirectional Transformation

```python
from datetime import datetime
from typing import Dict, Any, Optional

class ColorTokenAdapter:
    """Transform colors between schema layers"""

    def to_api_schema(self, core: CoreColorToken) -> APIColorToken:
        """
        Transform Core → API

        Adds:
        - semantic_name: Human-readable color name
        - created_at: Timestamp
        - metadata: Extra color analysis
        """
        return APIColorToken(
            hex=core.hex,
            confidence=core.confidence,
            token_type=core.token_type,
            semantic_name=self._generate_semantic_name(core.hex),
            created_at=datetime.utcnow(),
            metadata={
                'hue': self._extract_hue(core.hex),
                'temperature': self._analyze_temperature(core.hex),
                'saturation': self._analyze_saturation(core.hex)
            }
        )

    def from_api_schema(self, api: APIColorToken) -> CoreColorToken:
        """
        Transform API → Core (reverse)

        Strips metadata and extra fields, returns just essentials
        """
        return CoreColorToken(
            hex=api.hex,
            confidence=api.confidence,
            token_type=api.token_type
        )

    def to_database_schema(
        self,
        api: APIColorToken,
        extraction_job_id: int
    ) -> Dict[str, Any]:
        """
        Transform API → Database

        Prepares fields for SQLAlchemy ORM
        """
        return {
            'extraction_job_id': extraction_job_id,
            'hex': api.hex,
            'confidence': api.confidence,
            'semantic_name': api.semantic_name,
            'metadata': api.metadata
        }

    def from_database_schema(self, db_token: ColorToken) -> APIColorToken:
        """
        Transform Database → API (for queries)

        Reconstructs API schema from database row
        """
        return APIColorToken(
            hex=db_token.hex,
            confidence=db_token.confidence,
            token_type='color',
            semantic_name=db_token.semantic_name,
            created_at=db_token.created_at,
            metadata=db_token.metadata or {}
        )

    # Helper methods
    @staticmethod
    def _generate_semantic_name(hex_color: str) -> str:
        """Generate human-readable color name"""
        # Could use ColorAide or custom naming
        return f"color-{hex_color.lower()}"

    @staticmethod
    def _extract_hue(hex_color: str) -> str:
        """Analyze hue category"""
        # Red, Orange, Yellow, Green, Blue, Purple, etc.
        return "orange"  # Simplified

    @staticmethod
    def _analyze_temperature(hex_color: str) -> str:
        """Analyze color temperature"""
        # Warm, cool, neutral
        return "warm"  # Simplified

    @staticmethod
    def _analyze_saturation(hex_color: str) -> str:
        """Analyze saturation level"""
        # Muted, moderate, vibrant
        return "vibrant"  # Simplified
```

---

## 🔄 Using the Adapter

### In Extraction Pipeline

```python
from copy_that.adapters.color_adapter import ColorTokenAdapter
from copy_that.domain.schemas import CoreColorToken, APIColorToken

async def extract_colors(image_bytes: bytes) -> List[APIColorToken]:
    """
    Extract colors and transform through adapter

    Process:
    1. Extract → Core schema
    2. Adapt → API schema (enrichment)
    3. Store → Database schema
    4. Return → API schema
    """

    # 1. Extract (returns Core schema)
    extractor = AIColorExtractor()
    core_tokens = extractor.extract(image_bytes)

    # 2. Adapt to API (add metadata, semantic names)
    adapter = ColorTokenAdapter()
    api_tokens = [adapter.to_api_schema(ct) for ct in core_tokens]

    # 3. Store in database
    for api_token in api_tokens:
        db_data = adapter.to_database_schema(api_token, job_id=1)
        db_token = ColorToken(**db_data)
        session.add(db_token)
    session.commit()

    # 4. Return API schema to client
    return api_tokens
```

### In Query Endpoint

```python
@router.get("/api/v1/jobs/{job_id}/colors")
async def get_job_colors(
    job_id: int,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Query colors from database"""

    # Query database
    result = await db.execute(
        select(ColorToken).where(ColorToken.extraction_job_id == job_id)
    )
    db_tokens = result.scalars().all()

    # Transform using adapter
    adapter = ColorTokenAdapter()
    api_tokens = [
        adapter.from_database_schema(db_token)
        for db_token in db_tokens
    ]

    return {
        "job_id": job_id,
        "colors": [t.model_dump() for t in api_tokens]
    }
```

---

## 🧪 Testing Adapters

### Unit Tests

```python
import pytest
from datetime import datetime
from copy_that.adapters.color_adapter import ColorTokenAdapter
from copy_that.domain.schemas import CoreColorToken, APIColorToken

class TestColorTokenAdapter:
    @pytest.fixture
    def adapter(self):
        return ColorTokenAdapter()

    @pytest.fixture
    def core_token(self):
        return CoreColorToken(
            hex='#FF6B35',
            confidence=0.95,
            token_type='color'
        )

    def test_to_api_schema(self, adapter, core_token):
        """Test Core → API transformation"""
        api_token = adapter.to_api_schema(core_token)

        # Verify all fields
        assert api_token.hex == '#FF6B35'
        assert api_token.confidence == 0.95
        assert api_token.token_type == 'color'

        # Verify added fields
        assert api_token.semantic_name is not None
        assert isinstance(api_token.created_at, datetime)
        assert isinstance(api_token.metadata, dict)

    def test_from_api_schema(self, adapter):
        """Test API → Core transformation"""
        api_token = APIColorToken(
            hex='#FF6B35',
            confidence=0.95,
            token_type='color',
            semantic_name='vibrant-orange',
            created_at=datetime.utcnow()
        )

        core_token = adapter.from_api_schema(api_token)

        # Verify stripping of extra fields
        assert core_token.hex == '#FF6B35'
        assert core_token.confidence == 0.95
        assert core_token.token_type == 'color'
        assert not hasattr(core_token, 'semantic_name')

    def test_bidirectional_transformation(self, adapter, core_token):
        """Test roundtrip: Core → API → Core"""
        api_token = adapter.to_api_schema(core_token)
        restored_core = adapter.from_api_schema(api_token)

        # Core fields preserved
        assert restored_core.hex == core_token.hex
        assert restored_core.confidence == core_token.confidence
        assert restored_core.token_type == core_token.token_type

    def test_to_database_schema(self, adapter, core_token):
        """Test API → Database transformation"""
        api_token = adapter.to_api_schema(core_token)
        db_dict = adapter.to_database_schema(api_token, extraction_job_id=1)

        # Verify database field format
        assert db_dict['extraction_job_id'] == 1
        assert db_dict['hex'] == '#FF6B35'
        assert db_dict['confidence'] == 0.95
        assert isinstance(db_dict['metadata'], dict)
```

---

## 🎯 Adapter Pattern Benefits

### 1. **Loose Coupling**
```
Extractor doesn't know about API
API doesn't know about Database
Frontend doesn't know about Core
↓
Change one layer without affecting others
```

### 2. **Type Safety**
```python
# Each transformation is type-checked
core: CoreColorToken
api: APIColorToken = adapter.to_api_schema(core)  # ✅ Type-safe
db: Dict = adapter.to_database_schema(api, job_id=1)  # ✅ Type-safe
```

### 3. **Enrichment at Each Layer**
```
Core Layer:      hex, confidence (minimal)
    ↓ (adapter adds)
API Layer:       + semantic_name, created_at, metadata
    ↓ (adapter transforms)
Database Layer:  hex, confidence, semantic_name, metadata
```

### 4. **Testing**
```python
# Can test transformations independently
test_core_to_api()
test_api_to_database()
test_roundtrip()

# Don't need full system running to test transformations
```

### 5. **Version Negotiation**
```python
# Future: Support multiple schema versions
class ColorTokenAdapterV2:
    def to_api_schema_v2(self, core: CoreColorToken) -> APIColorTokenV2:
        # New fields, new transformations
        pass

# API can serve both v1 and v2 based on client request
```

---

## 📋 Adapter Checklist

When creating a new adapter:

- [ ] Create **Core Schema** (minimal, validated)
- [ ] Create **API Schema** (enriched, public)
- [ ] Create **Database Schema** (persistence)
- [ ] Implement **to_api_schema()** (Core → API)
- [ ] Implement **from_api_schema()** (API → Core)
- [ ] Implement **to_database_schema()** (API → Database)
- [ ] Implement **from_database_schema()** (Database → API)
- [ ] Add **validation tests**
- [ ] Add **roundtrip tests**
- [ ] Document **transformation logic**

---

## 🔀 Comparison: With vs Without Adapter

### Without Adapter (❌ Hard to Maintain)
```python
@router.post("/api/v1/extract/color")
async def extract_color(file: UploadFile):
    # Raw extraction
    image = await file.read()
    colors = extract_colors_raw(image)

    # Scattered transformation logic
    api_colors = []
    for color in colors:
        # Transform in-line
        api_colors.append({
            'hex': color['hex'],
            'confidence': color['confidence'],
            'semantic_name': generate_name(color['hex']),
            'created_at': datetime.utcnow(),
            'metadata': {
                'temperature': analyze_temp(color['hex']),
                # ... more logic ...
            }
        })

    # Store in database
    for api_color in api_colors:
        # Scattered database logic
        db.add(ColorToken(
            hex=api_color['hex'],
            confidence=api_color['confidence'],
            semantic_name=api_color['semantic_name'],
            metadata=api_color['metadata']
        ))

    return api_colors

# Similar transformation logic repeated everywhere:
# - GET /colors
# - POST /colors
# - PATCH /colors
# - Websocket updates
# - Batch exports
# - etc.
```

### With Adapter (✅ Clean & Maintainable)
```python
@router.post("/api/v1/extract/color")
async def extract_color(file: UploadFile):
    # Extract → Core
    image = await file.read()
    core_colors = AIColorExtractor().extract(image)

    # Transform via adapter
    adapter = ColorTokenAdapter()
    api_colors = [adapter.to_api_schema(c) for c in core_colors]

    # Store via adapter
    for api_color in api_colors:
        db_data = adapter.to_database_schema(api_color, job_id=1)
        db.add(ColorToken(**db_data))

    return api_colors

# Same adapter used everywhere
# GET /colors: adapter.from_database_schema()
# PATCH /colors: adapter.to_api_schema() + adapter.to_database_schema()
# Exports: adapter patterns reused
```

---

## 🚀 Scaling with Multiple Token Types

The adapter pattern scales beautifully:

```python
# Repeat for each token type
class SpacingTokenAdapter:
    def to_api_schema(self, core: CoreSpacingToken) -> APISpacingToken:
        # Spacing-specific enrichment
        pass

class TypographyTokenAdapter:
    def to_api_schema(self, core: CoreTypographyToken) -> APITypographyToken:
        # Typography-specific enrichment
        pass

# All follow same pattern
```

---

## 📚 Related Documentation

- **extractor_patterns.md** - How extractors work
- **token_system.md** - Token types and structure
- **plugin_architecture.md** - Plugin system overview

---

**Version:** 1.0 | **Last Updated:** 2025-11-19 | **Status:** Complete
