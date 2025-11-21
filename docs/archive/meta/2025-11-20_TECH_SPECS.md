# Copy That: Technical Specification

**Version:** 1.0
**Date:** 2025-11-21
**Scope:** MVP Implementation
**Audience:** Developers, Architects

---

## 📋 Table of Contents

1. [System Architecture](#system-architecture)
2. [Technology Decisions (With Trade-offs)](#technology-decisions)
3. [Data Model](#data-model)
4. [API Design](#api-design)
5. [Frontend Architecture](#frontend-architecture)
6. [Implementation Order](#implementation-order)

---

## 🏗️ System Architecture

### High-Level Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     USER BROWSER                             │
│                                                               │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │  React App (Vite)                                       │ │
│  │  • TokenGrid (display tokens)                           │ │
│  │  • TokenToolbar (filter/sort)                           │ │
│  │  • TokenInspectorSidebar (details)                      │ │
│  │  • TokenPlaygroundDrawer (editor)                       │ │
│  │  • ImageUploader (drag-drop)                            │ │
│  │                                                          │ │
│  │  Zustand Store                                          │ │
│  │  • tokens: ColorToken[]                                 │ │
│  │  • selectedTokenId, editingToken, filters, etc.        │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            ↑
                      (JSON over HTTP)
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    BACKEND (FastAPI)                         │
│                                                               │
│  POST /api/v1/colors/extract                                │
│    • Input: image (base64 or URL)                           │
│    • Process: Claude Sonnet + K-means clustering            │
│    • Output: ColorToken[] with confidence + semantic names  │
│                                                               │
│  POST /api/v1/colors/update (Future)                        │
│    • Input: token changes                                    │
│    • Process: Validate, persist                             │
│    • Output: Updated token                                   │
│                                                               │
│  DELETE /api/v1/colors/:id (Future)                         │
│  POST /api/v1/colors/duplicate (Future)                     │
│  POST /api/v1/export/css (Future)                           │
│                                                               │
│  Pydantic Schemas + Validation                              │
│  ColorExtractor + AIColorExtractor + ColorTokenAdapter      │
│  Database Layer (SQLModel + Neon PostgreSQL)                │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

```
1. USER UPLOADS IMAGE
   Browser → POST /api/v1/colors/extract

2. BACKEND EXTRACTS
   FastAPI receives image
   → AI extraction (Claude Sonnet 4.5 Structured Outputs)
   → Color detection (K-means, semantic naming)
   → Validation (Pydantic ColorToken schema)
   → Return ColorToken[]

3. FRONTEND DISPLAYS
   Browser receives JSON
   → Zustand store setTokens()
   → React re-renders TokenGrid
   → Show colors + metadata

4. USER EDITS
   Click token → Inspector shows details
   Click edit → Playground opens
   Edit name/color → Store updates (local)

5. USER EXPORTS
   Click export → POST /api/v1/export/css
   Download CSS variables file
```

---

## 🎯 Technology Decisions (With Trade-offs Analyzed)

### Frontend Framework: React + Vite + TypeScript

**Decision:** React + Vite + TypeScript (keep what we have)

**Alternatives Considered:**
| Alternative | Pros | Cons | Score |
|-------------|------|------|-------|
| **React + Vite** | Fast dev, great DX, wide ecosystem | Larger bundle | ✅ CHOSEN |
| Vue 3 + Vite | Simpler syntax, smaller bundle | Smaller community, less hiring pool | 6/10 |
| Svelte | Truly reactive, smallest bundle | Tiny ecosystem, hard to hire | 5/10 |
| Next.js | SSR, full stack in one | Overkill for MVP, slower dev | 4/10 |

**Why React:**
- ✅ Existing codebase (don't rewrite)
- ✅ Large hiring pool (easier to scale team)
- ✅ Ecosystem maturity (UI libraries, testing tools, etc.)
- ✅ Fast dev cycle with Vite
- ✅ Works great for single-page apps

**Trade-off Accepted:** Larger bundle (180KB gzip) vs simplicity

---

### State Management: Zustand

**Decision:** Zustand (already implemented and tested)

**Alternatives Considered:**
| Alternative | Pros | Cons | Score |
|-------------|------|------|-------|
| **Zustand** | Simple, 27 tests passing, no boilerplate | Smaller ecosystem than Redux | ✅ CHOSEN |
| Redux | Industry standard, devtools, time-travel | Boilerplate, learning curve, slow | 6/10 |
| Jotai | Atomic state, lightweight | Less mature than Redux/Zustand | 7/10 |
| TanStack Query | Great for server state | Overkill for token list | 5/10 |
| Context API | Zero dependencies, built-in | Prop drilling, re-render performance | 3/10 |

**Why Zustand:**
- ✅ Already built and tested (27 passing tests)
- ✅ Type-safe with TypeScript
- ✅ Minimal boilerplate
- ✅ Perfect for this scale (single store)
- ✅ Easy to add persistence later

**Trade-off Accepted:** Smaller community vs simplicity & speed

---

### Backend Framework: FastAPI + Python

**Decision:** FastAPI + Python (existing, proven)

**Alternatives Considered:**
| Alternative | Pros | Cons | Score |
|-------------|------|------|-------|
| **FastAPI** | Type-safe, async, great for AI, fast dev | Python ecosystem fragmentation | ✅ CHOSEN |
| Node.js/Express | JavaScript everywhere, fast | Poor type safety, async chaos | 6/10 |
| Go | Fast, simple, production ready | Verbose, learning curve | 7/10 |
| Rust | Speed, safety, performance | Steep learning curve, slow dev | 5/10 |

**Why FastAPI:**
- ✅ Already built color extraction service
- ✅ Perfect for AI/ML (Pydantic, NumPy, etc.)
- ✅ Type-safe end-to-end
- ✅ Async-first (good for I/O)
- ✅ Auto-generated OpenAPI docs

**Trade-off Accepted:** Python ecosystem vs perfect for this use case

---

### Color Science: ColorAide Library

**Decision:** ColorAide for perceptual color operations

**Alternatives Considered:**
| Alternative | Pros | Cons | Score |
|-------------|------|------|-------|
| **ColorAide** | Comprehensive, perceptually accurate, Oklch/OkLab | Heavier library | ✅ CHOSEN |
| colorsys (stdlib) | Zero deps, built-in | Limited (only HSV), inaccurate | 2/10 |
| skimage.color | Scientific, accurate | Large dependency (scikit-image), heavy | 6/10 |
| PIL colors | Lightweight, ubiquitous | Limited features, not perceptual | 4/10 |

**Why ColorAide:**
- ✅ CIEDE2000 color distance (accurate duplication detection)
- ✅ Oklch color space (40% better uniformity than HSL)
- ✅ Semantic color naming (warm/cool/vibrant/muted)
- ✅ Perceptually uniform scales
- ✅ Comprehensive (everything we need in one library)

**Trade-off Accepted:** 1.2MB dependency vs comprehensive color science

---

### Database: Neon PostgreSQL (Optional for MVP)

**Decision:** Neon PostgreSQL for persistence (optional, can skip for MVP)

**Alternatives Considered:**
| Alternative | Pros | Cons | Score |
|-------------|------|------|-------|
| **Neon PostgreSQL** | Serverless, branching, PITR, affordable | Vendor lock-in | ✅ CHOSEN |
| LocalStorage only | Zero backend, instant | Limited storage (5MB), no sharing | 4/10 |
| Firebase/Firestore | Real-time, serverless, easy auth | Expensive, vendor lock-in | 6/10 |
| MongoDB Atlas | Flexible schema, serverless | Not relational, overkill | 5/10 |
| Self-hosted PostgreSQL | Full control, unlimited | Ops burden, scaling pain | 3/10 |

**Why Neon:**
- ✅ Already set up and working
- ✅ Serverless (no ops)
- ✅ Affordable ($0.3/compute-hour, $0.25/storage-GB)
- ✅ Developer-friendly (branching, PITR)
- ✅ Excellent DX

**Trade-off Accepted:** Vendor lock-in vs simplicity

**MVP Simplification:** Can skip database entirely for MVP, add in Phase 2

---

### API Design: REST with Structured Outputs

**Decision:** REST API with Claude Structured Outputs

**Alternatives Considered:**
| Alternative | Pros | Cons | Score |
|-------------|------|------|-------|
| **REST + Structured Outputs** | Simple, predictable, type-safe | No real-time updates | ✅ CHOSEN |
| GraphQL | Flexible, queryable | Complex, overkill for this API | 4/10 |
| WebSocket streaming | Real-time, progressive | Complex state sync, harder to test | 6/10 |
| Server-Sent Events (SSE) | Real-time, simpler than WS | Still need REST for fallback | 6/10 |

**Why REST:**
- ✅ Extraction is one-shot (<10s), no need for streaming
- ✅ Simple for client to understand
- ✅ Easy to debug (curl, Postman, browser DevTools)
- ✅ Scales well to multi-image later (just loop the call)

**Trade-off Accepted:** No real-time updates vs simplicity

---

## 📊 Data Model

### ColorToken Schema

```typescript
interface ColorToken {
  id: string | number;
  hex: string;                    // #RRGGBB
  rgb: string;                    // rgb(r, g, b)
  name: string;                   // "Primary Blue"
  confidence: number;             // 0-1 (0.95 = 95% confident)

  // Optional (from extraction metadata)
  semantic_name?: string;         // "warm", "cool", "vibrant", "muted"
  harmony?: string;               // "monochromatic", "complementary", etc.
  hue?: number;                   // 0-360
  saturation?: number;            // 0-100
  lightness?: number;             // 0-100
  temperature?: string;           // "warm" | "neutral" | "cool"

  // Extraction metadata
  extraction_metadata?: {
    source: "ai" | "cv" | "manual";
    model?: string;               // "claude-sonnet-4.5"
    algorithm?: string;           // "k-means"
    created_at?: string;          // ISO 8601
  };

  // Future
  project_id?: string;            // For persistence
  created_at?: string;
  updated_at?: string;
}
```

### Why This Schema

- ✅ **Minimal**: Only essential fields for MVP
- ✅ **Extensible**: Optional fields for metadata
- ✅ **Future-proof**: project_id for multi-image merging
- ✅ **Type-safe**: Full TypeScript coverage

---

## 🔌 API Design

### Endpoints (MVP)

#### POST /api/v1/colors/extract
Extract colors from image

**Request:**
```typescript
{
  image: string;           // base64 or URL
  max_colors?: number;     // default 20, range 5-50
  project_id?: string;     // optional
}
```

**Response:**
```typescript
{
  tokens: ColorToken[];
  extraction_time_ms: number;
  confidence_average: number;
}
```

**Status Codes:**
- 200: Success
- 400: Invalid input (bad image format, too large)
- 500: Extraction failed

**Error Response:**
```typescript
{
  error: "Image too large",
  max_size_mb: 10,
  provided_size_mb: 15
}
```

### Endpoints (Future - Phase 2)

```
POST /api/v1/colors/update      - Edit token
DELETE /api/v1/colors/:id        - Delete token
POST /api/v1/colors/duplicate    - Duplicate token
POST /api/v1/export/css          - Export CSS variables
POST /api/v1/export/tailwind     - Export Tailwind config
POST /api/v1/export/json         - Export W3C tokens
```

---

## 🎨 Frontend Architecture

### Component Hierarchy

```
App (composition root)
├── Header
│   └── ImageUploader
├── Main (flex container)
│   ├── TokenPlaygroundDrawer (left, collapsible)
│   ├── TokenGrid area (center, flex: 1)
│   │   ├── TokenToolbar (filtering/sorting)
│   │   └── TokenGrid (multi-view grid/list/table)
│   │       └── TokenCard[] (individual tokens)
│   └── TokenInspectorSidebar (right, collapsible)
```

### State Management (Zustand Store)

```typescript
interface TokenState {
  // Data
  tokens: ColorToken[];
  projectId: string;

  // Selection & Editing
  selectedTokenId: string | null;
  editingToken: Partial<ColorToken> | null;
  playgroundToken: Partial<ColorToken> | null;

  // Filters & Display
  filters: Record<string, string>;
  sortBy: "hue" | "name" | "confidence" | "temperature" | "saturation";
  viewMode: "grid" | "list" | "table";
  sidebarOpen: boolean;
  playgroundOpen: boolean;

  // Actions (20+ methods)
  setTokens: (tokens: ColorToken[]) => void;
  selectToken: (id: string | null) => void;
  startEditing: (token: ColorToken) => void;
  saveEdit: () => Promise<void>;
  deleteToken: (id: string) => Promise<void>;
  // ... more
}
```

### Data Flow

```
ImageUploader
  ↓
POST /api/v1/colors/extract
  ↓
receive ColorToken[]
  ↓
useTokenStore.setTokens(tokens)
  ↓
Zustand store updates
  ↓
TokenGrid subscribes to tokens
TokenToolbar subscribes to filters/sortBy
TokenInspectorSidebar subscribes to selectedTokenId
  ↓
Components re-render with new data
```

---

## 📦 Implementation Order

### Phase 1: MVP (Week 1-2)

**Week 1:**
- [ ] Day 1: API endpoint POST /api/v1/colors/extract
- [ ] Day 2: Wire frontend to API (ImageUploader → extract)
- [ ] Day 3: Fix any API response schema issues
- [ ] Day 4: Add error handling (400, 500 responses)
- [ ] Day 5: Test end-to-end (upload → display)

**Week 2:**
- [ ] Day 6: Wire edit/delete/duplicate to API
- [ ] Day 7: Add loading states + error messages
- [ ] Day 8: UI polish + responsive mobile test
- [ ] Day 9: Integration testing
- [ ] Day 10: Performance optimization + deployment

### Phase 2: Token Persistence (Week 3)
- [ ] Save tokens to database
- [ ] Add project-based grouping
- [ ] Implement undo/redo

### Phase 3: Multi-Image Merging (Week 4)
- [ ] Upload multiple images
- [ ] Merge logic (ΔE < 10 deduplication)
- [ ] Weighted averaging

### Phase 4: More Tokens (Week 5)
- [ ] Typography extractor
- [ ] Spacing extractor
- [ ] Shadow extractor

---

## 🔒 Validation & Error Handling

### Input Validation

**Image Upload:**
```python
- Format: JPG, PNG, WebP, SVG only
- Size: ≤ 10MB
- Dimensions: 100x100 to 10000x10000 px
```

**Color Token:**
```python
- hex: Valid hex color (#RRGGBB)
- confidence: 0.0 ≤ x ≤ 1.0
- name: Non-empty string, < 100 chars
```

### Error Handling Strategy

**Graceful Degradation:**
```
If extraction partially fails:
  ✅ Return successful tokens (don't fail entire request)
  ⚠️ Include warning in response
  ⚠️ Log error for debugging
```

**User-Friendly Errors:**
```
✗ "Image too large (15MB, max 10MB)"
✗ "Invalid image format (expected PNG, got GIF)"
✗ "Extraction failed - try another image"
✓ "Extracted 12 colors (3 similar, merged to 9)"
```

---

## 📈 Performance Targets

| Metric | Target | How to Measure |
|--------|--------|----------------|
| Page load | < 2s | Lighthouse |
| Image upload (5MB) | < 5s | Network tab |
| Color extraction | < 10s | API response time |
| Token display | < 1s | React DevTools Profiler |
| Filter/sort | < 100ms | User interaction latency |

---

## 🧪 Testing Strategy

**Backend:**
```
- Unit tests: Schema validation, color algorithms
- Integration tests: API endpoints, database
- Target: 80% coverage
```

**Frontend:**
```
- Unit tests: Store actions (already have 27)
- Component tests: TokenCard, TokenGrid, etc.
- E2E tests: Upload → extract → edit → export
- Target: 60% coverage (store 100%, UI 60%)
```

---

## 🚀 Deployment

**Development:**
```bash
Frontend: pnpm dev
Backend: uvicorn main:app --reload
```

**Production (Optional):**
```
Frontend: Vercel or Netlify (static site)
Backend: Google Cloud Run (serverless)
Database: Neon PostgreSQL
```

---

## 📋 Implementation Checklist

- [ ] Phase 1 Week 1: API endpoints working
- [ ] Phase 1 Week 2: Frontend wired to API
- [ ] Phase 1 Week 3: Error handling + polish
- [ ] Phase 1 Week 4: Testing + deployment
- [ ] Phase 2: Persistence
- [ ] Phase 3: Multi-image merging
- [ ] Phase 4: More token types

---

**Status:** ✅ READY FOR IMPLEMENTATION

This tech spec removes ambiguity and provides clear guidance for building Copy That MVP.

Next: Implementation roadmap with day-by-day tasks.
