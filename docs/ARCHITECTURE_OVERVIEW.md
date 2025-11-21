# Copy That: Architecture Overview

**Version**: v0.1.0 | **Date**: 2025-11-19 | **Status**: Phase 4 Week 1 (Color Token Extraction)

This document provides a **complete, accurate overview** of Copy That's current architecture, design patterns, and implementation status.

---

## 🎯 What is Copy That?

Copy That is a **universal token extraction and generation platform** that converts design information from any source into structured design tokens, enabling multi-platform code generation.

**Current State (v0.1.0)**:
- AI-powered color token extraction from images (Claude Sonnet 4.5)
- Type-safe end-to-end data flow (Pydantic → Zod)
- Rest API with 70+ historical extractors
- Multi-platform token generators (17+ platforms)

**Long-Term Vision**:
- Extract ALL design tokens from images (colors, spacing, typography, shadows, etc.)
- Generate complete design systems from images
- Support multi-modal input (video, audio, text, sketches)
- Enable creative transformations (image→music, audio→UI, etc.)

---

## 🏗️ Core Architecture

### High-Level Overview

```
┌─────────────────────────────────────────────────────────┐
│              COPY THAT PLATFORM                         │
│   (Design Information → Tokens → Code Generation)       │
└─────────────────────────────────────────────────────────┘
                          ↓
        ┌─────────────────┴──────────────────┐
        ↓                                    ↓
┌──────────────────────┐          ┌──────────────────────┐
│  BACKEND (FastAPI)   │          │  FRONTEND (React)    │
│  Source of Truth     │ ←API→    │  Dev/Demo UI         │
│                      │          │                      │
│ • Token Extraction   │          │ • Upload interface   │
│ • Token Platform     │          │ • Token explorer     │
│ • Code Generation    │          │ • Results display    │
│ • GraphQL/REST API   │          │ • Documentation      │
└──────────────────────┘          └──────────────────────┘
         ↓
    ┌────────┐
    ↓        ↓
  OUTPUTS   CONSUMERS
  • React   • Design tools
  • Flutter • IDEs
  • CSS     • CI/CD
  • JSON    • Custom
  • YAML    • Extensions
```

---

## 🔄 Token Extraction Pipeline

### Current: Phase 4 Color Token Extraction

```
Image Upload
    ↓
┌─────────────────────────────────────────┐
│ Input Validation & Storage              │
│ • Save to temporary storage             │
│ • Validate format & size                │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│ AI Color Extraction (Claude Sonnet 4.5) │
│ • Structured Outputs for type safety    │
│ • Extract color palette from image      │
│ • Confidence scoring                    │
│ • Cost: ~$0.01-0.02 per image          │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│ Adapter Transformation                  │
│ • Core Schema → API Schema              │
│ • Bidirectional conversion              │
│ • Enrichment (semantic names, etc.)     │
│ • Type validation                       │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│ Database Storage (Neon PostgreSQL)      │
│ • Persist color_tokens table            │
│ • Link to extraction_jobs               │
│ • Metadata & audit trail                │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│ REST API Query                          │
│ • GET /api/v1/jobs/{id}/colors          │
│ • List, filter, export colors           │
│ • Type-safe responses (Zod)             │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│ Frontend Display                        │
│ • React components                      │
│ • Color swatches + metadata             │
│ • Confidence visualization              │
│ • Export options                        │
└─────────────────────────────────────────┘
    ↓
Results
```

---

## 📊 Data Architecture

### Schema Organization

```
schemas/
├── core/                    # W3C-based core schemas
│   └── color-token-v1.json  # Color token schema
│
├── api/                     # API response schemas
│   └── color-token-api.json
│
└── generated/               # Code-generated models
    ├── core_color.py        # Pydantic model
    └── color.zod.ts         # Zod schema
```

### Database Schema

```
Database: copy_that (Neon PostgreSQL)

┌─────────────────────────────────────┐
│ extraction_jobs                     │
├─────────────────────────────────────┤
│ id (PK)                             │
│ project_id (FK)                     │
│ extraction_type (color, spacing...) │
│ source_url                          │
│ status (pending, complete, failed)  │
│ created_at, updated_at              │
└─────────────────────────────────────┘
            ↓
┌─────────────────────────────────────┐
│ color_tokens                        │
├─────────────────────────────────────┤
│ id (PK)                             │
│ extraction_job_id (FK)              │
│ hex (color value)                   │
│ confidence (0.0-1.0)                │
│ semantic_name                       │
│ metadata (JSONB)                    │
│ created_at, updated_at              │
└─────────────────────────────────────┘
```

---

## 🛠️ Implementation Patterns

### 1. Adapter Pattern (Domain ↔ API)

**Purpose**: Separate domain models from API contracts

**Pattern**:
```python
# Core domain model (source of truth)
class ColorTokenCore(BaseModel):
    hex: str
    confidence: float
    token_type: str = "color"

# API model (what clients see)
class ColorTokenAPI(BaseModel):
    hex: str
    confidence: float
    semantic_name: Optional[str]

# Adapter (handles transformation)
class ColorTokenAdapter:
    @staticmethod
    def to_api(core: ColorTokenCore) -> ColorTokenAPI:
        return ColorTokenAPI(
            hex=core.hex,
            confidence=core.confidence,
            semantic_name=generate_semantic_name(core.hex)
        )

    @staticmethod
    def from_api(api: ColorTokenAPI) -> ColorTokenCore:
        return ColorTokenCore(
            hex=api.hex,
            confidence=api.confidence
        )
```

**Benefits**:
- ✅ Domain models stay pure (no API concerns)
- ✅ API can evolve independently
- ✅ Easy to add enrichment (semantic names, etc.)
- ✅ Bidirectional conversion when needed

**Files**:
- `backend/schemas/adapters/color_token_adapter.py` (71 LOC, 100% tested)

### 2. Type Safety: End-to-End

**Backend**: Pydantic v2
```python
from pydantic import BaseModel, Field

class ColorTokenCore(BaseModel):
    hex: str = Field(..., pattern=r"^#[0-9A-F]{6}$")
    confidence: float = Field(..., ge=0.0, le=1.0)
    token_type: Literal["color"] = "color"
```

**API**: Zod (TypeScript)
```typescript
import { z } from "zod";

const ColorTokenSchema = z.object({
    hex: z.string().regex(/^#[0-9A-F]{6}$/),
    confidence: z.number().min(0).max(1),
    semantic_name: z.string().optional()
});

type ColorToken = z.infer<typeof ColorTokenSchema>;
```

**Benefits**:
- ✅ Server validates rigorously (Pydantic)
- ✅ Client validates gracefully (Zod safeParse)
- ✅ Single source of truth (JSON schema)
- ✅ Code generation (datamodel-codegen)

### 3. Vertical Slice Architecture

**Why Color First?**

Instead of implementing all token types horizontally (schemas → adapters → database → frontend all at once), Copy That validates the pattern vertically with ONE token type:

```
Color Token Vertical Slice:
  ↓
Schema + code generation
  ↓
Adapter + bidirectional conversion
  ↓
Database table
  ↓
AI Extractor
  ↓
API endpoints
  ↓
Frontend components
  ↓
VALIDATED! Now replicate for other tokens...
```

**Benefits**:
- ✅ Discover architectural issues early (1 week vs 5+ weeks)
- ✅ Prove pattern before scaling
- ✅ Quick feedback loops
- ✅ Psychologically rewarding milestones

**Current Status**:
- ✅ Color vertical slice 80% complete
- ✅ Pattern validated end-to-end
- ✅ Ready to replicate for spacing, shadow, typography, border+opacity

---

## 🎯 Module Organization

### Backend (FastAPI + Python)

```
src/copy_that/
├── domain/
│   ├── models/          # SQLModel (database models)
│   │   └── color_token.py
│   └── schemas/         # Domain schemas (core logic)
│       └── color_token_schema.py
│
├── infrastructure/
│   ├── database.py      # Connection, migrations
│   └── storage/         # File/image storage
│
├── ai/
│   ├── extractors/      # AI-powered extractors
│   │   └── color_extractor.py (AIColorExtractor)
│   └── orchestrators/   # Orchestrate extract → adapt → store
│       └── color_extraction_orchestrator.py
│
├── schemas/
│   ├── core/            # JSON schemas (W3C)
│   │   └── color-token-v1.json
│   ├── adapters/        # Domain → API adapters
│   │   └── color_token_adapter.py
│   └── generated/       # Code-generated models
│       ├── core_color.py (Pydantic)
│       └── color.zod.ts (Zod)
│
├── interfaces/
│   ├── api/
│   │   ├── main.py      # FastAPI app
│   │   ├── routes/      # API endpoints
│   │   │   └── extraction.py
│   │   └── dependencies.py
│   └── cli/             # CLI interface
│
└── tests/
    ├── test_color_schema_validation.py (20 tests)
    ├── schemas/
    │   └── test_core_color.py (21 tests)
    └── integration/
        └── test_color_extraction_flow.py
```

### Frontend (React + TypeScript)

```
frontend/src/
├── components/
│   ├── ColorTokenCard.tsx       # Display single color
│   ├── ColorTokenList.tsx       # List of colors
│   └── ExtractionUpload.tsx     # Upload interface
│
├── hooks/
│   └── useProgressiveExtraction.ts  # Extraction state
│
├── pages/
│   └── ExtractColors.tsx        # Full page
│
├── types/
│   └── generated/
│       ├── color.zod.ts         # Zod schemas
│       └── __tests__/
│           └── color.zod.test.ts
│
└── api/
    └── client.ts                # API client
```

---

## 📈 Technology Stack Rationale

### Backend: FastAPI + Python

**Why?**
- ✅ Modern async Python framework (fast, modern syntax)
- ✅ Pydantic v2 integration (type validation + serialization)
- ✅ OpenAPI/Swagger automatic documentation
- ✅ Great for AI/ML workflows (Claude API integration)
- ✅ Scalable (async everything)

**Tech Choices**:
- **Database**: PostgreSQL (Neon) → type-safe, JSONB support
- **ORM**: SQLModel → bridges SQLAlchemy + Pydantic
- **Migrations**: Alembic → version control for schema
- **AI**: Claude Sonnet 4.5 → structured outputs for type safety

### Frontend: React + Vite

**Why?**
- ✅ Fastest iteration cycle (Vite dev server)
- ✅ Rich visualization ecosystem (D3, Cytoscape for graphs)
- ✅ Easy migration to Next.js later if SEO needed
- ✅ Current focus: dev/demo UI (not public-facing)

**Tech Choices**:
- **Build**: Vite → sub-second HMR
- **Type Safety**: TypeScript + Zod → graceful validation
- **State**: React hooks + fetch API (minimal dependencies)

### Data: W3C Design Tokens

**Schema**: [W3C Design Tokens Format](https://design-tokens.github.io/community-group/format/) + extensions

**Key Fields**:
```json
{
  "color": {
    "primary": {
      "$value": "#0066CC",
      "$type": "color",
      "$description": "Primary action color",
      "$extensions": {
        "confidence": 0.95,
        "semantic_role": "primary",
        "harmony": "complementary"
      }
    }
  }
}
```

**Benefits**:
- ✅ Industry standard (Figma, Adobe, Sketch all support)
- ✅ Hierarchical nesting
- ✅ Extensible via `$extensions`
- ✅ Tool-agnostic format

---

## 🧪 Quality Assurance

### Test Coverage (Phase 4)

| Module | Tests | Coverage | Status |
|--------|-------|----------|--------|
| Color Schema | 20 | 100% | ✅ |
| ColorTokenAdapter | 21 | 100% | ✅ |
| AIColorExtractor | 14 | 100% | ✅ |
| **Total** | **41** | **100%** | ✅ |

**Target**: 90%+ coverage for Phase 5+

### Testing Strategy

**Unit Tests**:
```python
# Test schema validation
def test_color_token_valid_hex():
    token = ColorTokenCore(hex="#FF6B35", confidence=0.95)
    assert token.hex == "#FF6B35"

# Test adapter
def test_adapter_to_api():
    core = ColorTokenCore(hex="#FF6B35", confidence=0.95)
    api = ColorTokenAdapter.to_api(core)
    assert api.semantic_name == "vibrant-orange"
```

**Integration Tests**:
```python
# Test end-to-end flow
async def test_color_extraction_flow():
    # 1. Extract from image
    # 2. Store in database
    # 3. Query via API
    # 4. Verify structure
```

---

## 🚀 Deployment Architecture

### Current: Cloud Run + Neon

```
User Request
    ↓
┌───────────────────────────────────┐
│ Cloud Run (FastAPI container)     │
│ • Auto-scaling                    │
│ • Per-request pricing             │
│ • ~$5-20/month typical            │
└───────────────────────────────────┘
    ↓
┌───────────────────────────────────┐
│ Neon PostgreSQL (Serverless)      │
│ • Auto-scaling                    │
│ • Pay-per-compute                 │
│ • ~$5-50/month typical            │
└───────────────────────────────────┘
    ↓
┌───────────────────────────────────┐
│ Cloud Storage (Images)            │
│ • Temporary storage               │
│ • Auto-cleanup after 24h          │
└───────────────────────────────────┘
```

**Cost Estimate**: $20-100/month for moderate usage

---

## 🔮 Future Architecture Considerations

### Phase 5+: Multi-Modal Platform

```
Input Adapters          Token Platform         Output Generators
─────────────────       ──────────────         ─────────────────
  Image (v0.1)  ┐         W3C Tokens             React + CSS
  Video         ├────→  Token Graph ────→      Flutter
  Audio         │      (NetworkX)              JSON/YAML
  Text          │      Relationships           Custom
  Sketch        │      Ontologies
  Custom        ┘

Phase 4: Color           Phase 6: Multi-Modal   Phase 9: Generative
Phase 5: Spacing        Phase 7: Educational   Phase 10: Platform
```

### Scaling Considerations

**Current Bottleneck**: AI extraction cost ($0.01-0.02/image)

**Phase 9 Solution**:
- Cache common patterns
- Fine-tune smaller models
- Batch processing
- User-defined extraction rules

---

## 📝 Key Files Reference

### Architecture Files

| File | Purpose | LOC |
|------|---------|-----|
| `backend/schemas/core/color-token-v1.json` | Schema definition | 25 |
| `backend/schemas/adapters/color_token_adapter.py` | Domain→API transform | 71 |
| `backend/domain/models/color_token.py` | Database model | 45 |
| `backend/ai/color_extractor.py` | AI extraction | 180 |
| `backend/tests/test_color_*.py` | Tests | 250+ |

### API Files

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/v1/jobs` | POST | Create extraction job |
| `/api/v1/jobs/{id}/colors` | GET | Query extracted colors |
| `/api/v1/jobs/{id}/extract-colors` | POST | Trigger extraction |
| `/docs` | GET | OpenAPI documentation |

---

## 🤝 Extending the Architecture

### Adding a New Token Type (Phase 5)

1. **Create Schema**: `schemas/core/spacing-token-v1.json`
2. **Generate Models**: `datamodel-codegen --input ... --output ...`
3. **Create Adapter**: `SpacingTokenAdapter` (copy ColorTokenAdapter)
4. **Create Extractor**: `AISpacingExtractor` (copy AIColorExtractor)
5. **Create Database**: Alembic migration for `spacing_tokens` table
6. **Create API Routes**: `/api/v1/jobs/{id}/spacing` endpoints
7. **Create Tests**: 100% coverage like colors

**Estimated Time**: 2-3 days per token type

---

## 🔗 Related Documentation

- **[strategic_vision_and_architecture.md](architecture/strategic_vision_and_architecture.md)** - Strategic decisions
- **[modular_token_platform_vision.md](architecture/modular_token_platform_vision.md)** - Long-term vision
- **[phase_4_color_vertical_slice.md](phase_4_color_vertical_slice.md)** - Current implementation
- **[ROADMAP.md](../ROADMAP.md)** - Phases 5-10 roadmap
- **[implementation_strategy.md](implementation_strategy.md)** - Strategic choices

---

**Status**: ✅ Accurate as of 2025-11-19
**Questions?** Check [docs/documentation.md](documentation.md) for navigation
