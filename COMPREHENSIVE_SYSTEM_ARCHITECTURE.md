# Comprehensive System Architecture - Copy That

**Purpose:** Define how all components, layers, and systems fit together while preserving all existing work
**Version:** 2025-12-10
**Status:** Vision + Implementation plan (no breaking changes)

---

## Executive Summary

Copy That is a **Generative UI System** with 5 distinct layers:

```
┌─────────────────────────────────────────────────────────────┐
│ Layer 5: PRESENTATION (React UI)                            │
│ └─ Reusable component library (ui/)                         │
│ └─ Feature-specific pages (Playground, Inspector, etc.)    │
└─────────────────────────────────────────────────────────────┘
                            ↕
┌─────────────────────────────────────────────────────────────┐
│ Layer 4: STATE MANAGEMENT (Zustand stores)                  │
│ └─ tokenGraphStore (token data)                             │
│ └─ extractionStore (progress, stage tracking)               │
│ └─ uiStore (sidebar, filters, selections)                   │
└─────────────────────────────────────────────────────────────┘
                            ↕
┌─────────────────────────────────────────────────────────────┐
│ Layer 3: HTTP API (FastAPI + OpenAPI)                       │
│ └─ Color endpoints (extract, batch, etc.)                   │
│ └─ Spacing endpoints                                        │
│ └─ Typography endpoints                                     │
│ └─ Shadow endpoints                                         │
│ └─ Streaming endpoints (SSE)                                │
└─────────────────────────────────────────────────────────────┘
                            ↕
┌─────────────────────────────────────────────────────────────┐
│ Layer 2: BUSINESS LOGIC (Services + Extractors)             │
│ ├─ ColorExtractor (K-means + ColorAide)                     │
│ ├─ OpenAIColorExtractor (Claude Sonnet 4.5)                 │
│ ├─ SpacingExtractor (SAM + grid detection)                  │
│ ├─ TypographyExtractor (CLIP + font detection)              │
│ ├─ ShadowExtractor (shadow analysis)                        │
│ └─ TokenService (orchestration)                             │
└─────────────────────────────────────────────────────────────┘
                            ↕
┌─────────────────────────────────────────────────────────────┐
│ Layer 1: DATA & DOMAIN (Pydantic models, TokenGraph)        │
│ ├─ Token (generic token data model)                         │
│ ├─ TokenGraph (relationships, aliases, composition)         │
│ ├─ TokenRepository (persistence)                            │
│ └─ W3C Design Tokens schema                                 │
└─────────────────────────────────────────────────────────────┘
```

---

## Layer-by-Layer Breakdown

### Layer 1: Domain (Data Models)

**Location:** `src/copy_that/domain/`

**What it contains:**
- `Token` - Generic token data class (hex color, spacing value, font name, etc.)
- `TokenType` - Enum: COLOR, SPACING, TYPOGRAPHY, SHADOW
- `TokenGraph` - In-memory graph of tokens + relationships
- `TokenRepository` - Persistence interface (in-memory or database)
- `TokenRelation` - Relationship metadata (ALIAS_OF, COMPOSES, OVERRIDES, etc.)

**Key principle:** This layer is STABLE and imported by everything above it. NO business logic.

**Example Token structure:**
```python
@dataclass
class Token:
    id: str                              # unique identifier
    name: str                            # "primary-blue"
    type: TokenType                      # TokenType.COLOR
    value: str                           # "#2563eb" or "16px" or "Roboto"
    metadata: Dict[str, Any]             # extracted_at, confidence, source, etc.
    relationships: List[TokenRelation]   # aliases, compositions, etc.
```

**Status:** ✅ Exists, stable, ready

---

### Layer 2: Business Logic (Extractors & Services)

**Location:** `src/copy_that/application/` + `src/copy_that/services/`

#### 2A: Extractors (Modular, Zero-Coupling)

**What they do:** Take image/data → Return list of Token

**Current extractors (ALL WORKING):**
1. **ColorExtractor** (`color_extractor.py`) ✅
   - K-means clustering
   - ColorAide analysis (harmony, temperature, saturation)
   - Palette diversity scoring
   - Accent color selection
   - 95% complete, production-ready

2. **OpenAIColorExtractor** (`openai_color_extractor.py`) ✅
   - Claude Sonnet 4.5 structured output
   - Semantic naming
   - State variants generation
   - 100% working, recently fixed Pydantic config

3. **SpacingExtractor** (exists, needs frontend integration)
   - SAM-based segmentation
   - Grid detection
   - Gap clustering
   - Alignment analysis

4. **TypographyExtractor** (exists)
   - Font family detection
   - Size/weight/line-height analysis
   - Pairing recommendations

5. **ShadowExtractor** (exists)
   - Shadow detection
   - Elevation mapping
   - CSS shadow generation

**Key architecture:**
- Each extractor is independent (no cross-imports)
- Registered in a registry at import time
- Services call extractors via registry, not direct import
- Can add new extractor = 1 new module + 1 registration line

**Status:** ✅ Color 95%, Others 70-80%

#### 2B: Services (Orchestration)

**Location:** `src/copy_that/services/`

**What they do:** Coordinate extractors, manage TokenGraph, handle async workflows

**Current services:**
1. **TokenService** - Core service for token operations
2. **ExtractionService** - Coordinates multi-stage extraction (CV → ML → AI)
3. **ExportService** - Coordinates token → code generation

**Status:** ✅ Partially implemented, ready to complete

---

### Layer 3: HTTP API (FastAPI)

**Location:** `src/copy_that/interfaces/api/`

**Endpoint categories:**

**A) Extraction Endpoints** (existing)
- `POST /api/v1/colors/extract` - Single image color extraction
- `POST /api/v1/colors/extract-streaming` - Stream colors as they're found
- `POST /api/v1/colors/batch` - Multiple images
- `/api/v1/spacing/extract` - Spacing tokens
- `/api/v1/typography/extract` - Typography tokens
- `/api/v1/shadows/extract` - Shadow tokens

**B) Token Management Endpoints** (existing)
- `GET /api/v1/projects/{id}/colors` - List project colors
- `GET /api/v1/colors/{id}` - Get specific color token
- `PUT /api/v1/colors/{id}` - Update token metadata
- `DELETE /api/v1/colors/{id}` - Delete token

**C) Streaming Endpoints** (new for pipeline)
- `GET /api/v1/extract/{id}/stream` - SSE stream of extraction progress
- `GET /api/v1/projects/{id}/tokens/stream` - SSE stream of token updates

**Status:** ✅ Core endpoints exist, streaming partially implemented

---

### Layer 4: State Management (Zustand)

**Location:** `frontend/src/store/`

**What it contains:**

#### Store 1: `tokenGraphStore.ts`
```typescript
interface TokenGraphStore {
  // Data
  tokens: {
    colors: ColorToken[]
    spacing: SpacingToken[]
    typography: TypographyToken[]
    shadows: ShadowToken[]
  }

  // Operations
  addToken: (token) => void
  updateToken: (id, updates) => void
  deleteToken: (id) => void
  selectToken: (id) => void
  clearTokens: () => void

  // Relationships
  addRelationship: (source, target, type) => void
  resolveAlias: (tokenId) => Token
}
```

#### Store 2: `extractionStore.ts` (new)
```typescript
interface ExtractionStore {
  // Progress tracking
  isExtracting: boolean
  currentStage: 'color' | 'spacing' | 'typography' | 'shadow' | null
  progress: {
    color: { extracted: number, target: number }
    spacing: { extracted: number, target: number }
    typography: { extracted: number, target: number }
    shadow: { extracted: number, target: number }
  }

  // Operations
  startExtraction: () => void
  updateStage: (stage) => void
  addExtractedToken: (type, token) => void
  completeExtraction: () => void
}
```

#### Store 3: `uiStore.ts` (new)
```typescript
interface UIStore {
  // UI state
  selectedTokenId: string | null
  filteredTokenType: TokenType | 'all'
  sidebarOpen: boolean
  inspectorOpen: boolean

  // Operations
  selectToken: (id) => void
  setFilter: (type) => void
  toggleSidebar: () => void
  toggleInspector: () => void
}
```

**Status:** ✅ `tokenGraphStore` exists, others need to be created (low effort)

---

### Layer 5: Presentation (React Components)

**Location:** `frontend/src/`

This layer has **two sub-sections:**

#### 5A: Reusable Component Library (`frontend/src/components/ui/`)

**Purpose:** Shared, generic components used everywhere

**What exists (to be refactored):**
- Panels, Cards, Badges, Chips
- Tabs (3 different implementations to unify)
- Grids, Sidebars, Containers
- Button, Input, Label components

**What to organize:**
```
frontend/src/components/ui/
├── tabs/
│   ├── Tabs.tsx              (generic container)
│   ├── TabList.tsx           (tab buttons)
│   ├── TabButton.tsx         (individual button)
│   ├── TabPanel.tsx          (content pane)
│   └── useTabState.ts        (state hook)
│
├── panel/
│   ├── Panel.tsx             (generic wrapper)
│   ├── PanelHeader.tsx
│   ├── PanelBody.tsx
│   └── PanelTabs.tsx         (panel with tabs integrated)
│
├── card/
│   ├── Card.tsx
│   ├── CardHeader.tsx
│   ├── CardBody.tsx
│   ├── CardFooter.tsx
│   └── TokenCard.tsx         (token-specific)
│
├── badge/
│   ├── Badge.tsx
│   └── Badge.variants.ts     (status, role, temperature, etc.)
│
├── grid/
│   ├── Grid.tsx
│   └── GridItem.tsx
│
├── sidebar/
│   ├── Sidebar.tsx
│   ├── SidebarSection.tsx
│   └── useSidebarState.ts
│
└── common/
    ├── Button.tsx
    ├── Input.tsx
    ├── Label.tsx
    └── Separator.tsx
```

**Status:** ✅ Components exist scattered, need to be organized (2-3 hour refactor)

#### 5B: Feature Pages & Specific Components

**Playground** (`frontend/src/pages/Playground/`)
- Upload image
- View extraction progress
- Token inspector with tabs
- Export options

**Token Inspector** (new, using library components)
- Left panel: token list + filters
- Right panel: selected token detail view with tabs

**Feature-Specific Components** (keep as-is, use library components)
- ColorDetailPanel
- ShadowAnalysisPanel
- SpacingScalePanel
- TypographyPreview

**Status:** ✅ Mostly exists, need to integrate streaming

---

## Integration Points (How Data Flows)

### Extraction Flow

```
1. User uploads image → Playground.tsx
2. POST /api/v1/extract/stream
3. Backend extracts colors (K-means) → Stream to frontend
4. Frontend receives SSE → Add to tokenGraphStore
5. tokenGraphStore update triggers TokenCard re-render
6. User sees colors appearing in real-time in TokenGrid
7. Backend continues with spacing/typography/shadows (async, streaming)
8. Each token type streams to its own store section
9. User can click token → TokenInspector shows tabs for that token
10. Click "Export" → Generate React component using selected tokens
```

### Component Layer Integration

```
Playground (container)
├─ UploadArea (UI component)
├─ ExtractionProgressBar (UI component)
└─ TokenExplorer (feature component)
   ├─ Sidebar (UI component)
   │  └─ TokenGrid (UI component)
   │     └─ TokenCard[] (UI component)
   └─ Main (container)
      └─ TokenInspectorPanel (feature component)
         └─ PanelTabs (UI component)
            ├─ OverviewTab
            ├─ DataTab
            ├─ MetricsTab
            └─ ExportTab
```

---

## Preservation Checklist (What We Keep)

### Backend - KEEP ALL
- ✅ ColorExtractor (color_extractor.py)
- ✅ OpenAIColorExtractor (openai_color_extractor.py)
- ✅ SpacingExtractor
- ✅ TypographyExtractor
- ✅ ShadowExtractor
- ✅ All API endpoints
- ✅ All database tables
- ✅ All migrations

### Frontend - KEEP ALL
- ✅ 67 existing components
- ✅ 4 visual adapters (Color, Spacing, Typography, Shadow)
- ✅ tokenGraphStore (Zustand)
- ✅ All CSS and styling
- ✅ All pages and routes

### What Changes
- ❌ Component folder organization (move to ui/ but same files)
- ❌ Duplicate tab implementations (consolidate to 1 generic)
- ❌ Add missing UI components (new, no removal)

---

## Implementation Strategy (Non-Breaking)

### Phase 1: Library Infrastructure (2-3 hours)
```
GOAL: Organize components into library structure WITHOUT changing them

TASKS:
1. Create frontend/src/components/ui/ directory
2. Move existing generic components (no code changes):
   - Badges → ui/badge/
   - Cards → ui/card/
   - Grid → ui/grid/
   - Sidebar → ui/sidebar/
   - etc.
3. Update imports in existing code
4. Test: No functionality changes, all tests pass ✅
```

### Phase 2: Tabs Abstraction (1-2 hours)
```
GOAL: Consolidate 3 tab implementations into 1 generic <Tabs> component

TASKS:
1. Create ui/tabs/Tabs.tsx (generic, composable)
2. Refactor ColorDetailPanel to use <Tabs>
3. Refactor ShadowAnalysisPanel to use <Tabs>
4. Keep SpacingScalePanel tabs as-is (optional refactor)
5. Test: All panels work identically ✅
```

### Phase 3: Panel System (2-3 hours)
```
GOAL: Create generic <PanelTabs> for token detail views

TASKS:
1. Create ui/panel/PanelTabs.tsx
2. Create TokenInspectorPanel using <PanelTabs>
3. Dynamically render tabs based on token type
4. Integration with tokenGraphStore
5. Test: Click token → Detail panel shows right tabs ✅
```

### Phase 4: Streaming Integration (3-4 hours)
```
GOAL: Connect SSE streaming to UI

TASKS:
1. Add extractionStore (Zustand)
2. Create useTokenExtraction hook
3. Connect Playground to API streaming
4. Update TokenCard to subscribe to store
5. Test: Upload image → tokens appear in real-time ✅
```

### Phase 5: Export & Polish (2-3 hours)
```
GOAL: Add token export functionality

TASKS:
1. Create exporters for W3C tokens, CSS, React
2. Add "Export" button to TokenInspector
3. Add download functionality
4. Add copy-to-clipboard
5. Test: Export generates valid code ✅
```

---

## File Organization After Refactor

```
frontend/src/
├── pages/
│   ├── Playground.tsx         ← Main feature page
│   ├── Documentation.tsx
│   └── ...
│
├── components/
│   ├── ui/                    ← REUSABLE LIBRARY
│   │   ├── tabs/
│   │   │   ├── Tabs.tsx
│   │   │   ├── TabList.tsx
│   │   │   ├── TabButton.tsx
│   │   │   └── TabPanel.tsx
│   │   │
│   │   ├── panel/
│   │   │   ├── Panel.tsx
│   │   │   ├── PanelHeader.tsx
│   │   │   ├── PanelBody.tsx
│   │   │   └── PanelTabs.tsx
│   │   │
│   │   ├── card/
│   │   │   ├── Card.tsx
│   │   │   ├── CardHeader.tsx
│   │   │   ├── CardBody.tsx
│   │   │   ├── CardFooter.tsx
│   │   │   └── TokenCard.tsx
│   │   │
│   │   ├── badge/
│   │   │   ├── Badge.tsx
│   │   │   └── Badge.variants.ts
│   │   │
│   │   ├── grid/
│   │   ├── sidebar/
│   │   └── common/
│   │
│   ├── features/               ← FEATURE-SPECIFIC
│   │   ├── token-explorer/
│   │   │   ├── TokenExplorer.tsx
│   │   │   ├── TokenList.tsx
│   │   │   └── TokenFilters.tsx
│   │   │
│   │   ├── token-inspector/
│   │   │   ├── TokenInspectorPanel.tsx
│   │   │   ├── tabs/
│   │   │   │   ├── OverviewTab.tsx
│   │   │   │   ├── DataTab.tsx
│   │   │   │   ├── MetricsTab.tsx
│   │   │   │   └── ExportTab.tsx
│   │   │   └── hooks/
│   │   │       └── useTokenData.ts
│   │   │
│   │   ├── color/              ← EXISTING, KEEP
│   │   ├── spacing/            ← EXISTING, KEEP
│   │   ├── typography/         ← EXISTING, KEEP
│   │   └── shadow/             ← EXISTING, KEEP
│   │
│   └── legacy/                 ← OLD, GRADUALLY REFACTOR
│       ├── image-uploader/
│       ├── diagnostics-panel/
│       └── ...
│
├── store/
│   ├── tokenGraphStore.ts      ← EXISTING
│   ├── extractionStore.ts      ← NEW
│   └── uiStore.ts              ← NEW
│
└── hooks/
    ├── useTokenExtraction.ts   ← NEW
    ├── useTabNavigation.ts     ← NEW
    └── ...
```

---

## Technology Decisions

### Why This Architecture?

| Decision | Why | Trade-off |
|----------|-----|-----------|
| 5-layer architecture | Clear separation of concerns | Learning curve for new devs |
| TokenGraph as central IR | Enables multi-framework generation | Adds complexity for simple use cases |
| Zustand for state | Lightweight, performant, flexible | No time-travel debugging (easy fix) |
| Streaming/SSE | Progressive display, better UX | Server resource usage |
| Modular extractors | Easy to add new token types | Slightly more boilerplate |
| Generic Token type | Works for any token type | Less type safety than specific classes |

### Why NOT X?

| Rejected | Why Not |
|----------|---------|
| Redux | Overkill for this project, Zustand is simpler |
| Context API | Performance issues with frequent updates |
| Server components | Not needed, client-side extraction works great |
| GraphQL | REST + SSE is simpler, sufficient for this use case |
| ORM TypeORM | SQLAlchemy already in use, works fine |
| Class-based tokens | Generic Token + enum is more flexible |

---

## Success Criteria

After implementation, this architecture succeeds if:

✅ **Colors work end-to-end**
- Upload image → Colors extract → Appear in UI → Can be exported

✅ **Spacing works end-to-end**
- Same flow as colors

✅ **Typography works end-to-end**
- Same flow

✅ **Shadows work end-to-end**
- Same flow

✅ **Component library is reusable**
- Can add new token type with NO changes to ui/ components

✅ **All existing tests pass**
- No regressions

✅ **Performance is good**
- Colors appear in <500ms from upload
- UI responds instantly to store changes

---

## Rollout Strategy

### Week 1: Foundation (Non-Breaking)
1. Create ui/ library structure
2. Organize existing components (imports updated)
3. All tests pass

### Week 2: Unification
1. Consolidate tab implementations
2. Create PanelTabs system
3. Create TokenInspector

### Week 3: Integration
1. Connect streaming to UI
2. Test color pipeline end-to-end
3. Test spacing pipeline end-to-end

### Week 4: Polish
1. Add export functionality
2. Performance optimization
3. Documentation

---

## Risk Mitigation

### Risk: Breaking existing components
**Mitigation:** Phase 1 is import-only refactor, all tests pass before moving on

### Risk: Performance degradation with streaming
**Mitigation:** Monitor store update frequency, debounce if needed

### Risk: Token type mismatch (color vs spacing displays)
**Mitigation:** TokenType enum in domain layer ensures consistency

### Risk: Extractors breaking when refactored
**Mitigation:** Registry pattern means services never hardcode extractor imports

---

## Next Steps

1. ✅ Read this document end-to-end
2. ☐ Decide: Start with Phase 1 (library organization)?
3. ☐ If yes: Begin file reorganization
4. ☐ Run tests after each phase
5. ☐ Commit working checkpoints

---

## Questions This Architecture Answers

**Q: Where does color extraction happen?**
A: Layer 2 (ColorExtractor) calls Layer 1 (Token, TokenGraph) to produce tokens, API (Layer 3) serves them, Store (Layer 4) manages them, Components (Layer 5) display them.

**Q: How do I add a new token type (e.g., Border)?**
A: Create BorderExtractor in Layer 2, register in API (Layer 3), consume in UI (Layer 5). No changes to existing code.

**Q: Why does the playground work?**
A: Playground is Layer 5 (presentation) that uses all 4 layers below it.

**Q: What about streaming?**
A: API endpoints (Layer 3) use SSE to stream tokens to frontend, Store (Layer 4) receives them, Components (Layer 5) re-render.

**Q: What's the flow from image → code?**
A: Image → ColorExtractor → Token → TokenGraph → Zustand store → React components → Export generator → Code output

---

## Reference Documents

- `GENERATIVE_UI_ARCHITECTURE.md` - Why this is a generative UI system
- `ARCHITECTURE_CONSOLIDATION.md` - How modules should be organized
- `ARCHITECTURE_QUICK_REFERENCE.md` - Daily reference guide
- `COLOR_PIPELINE_END_TO_END.md` - Color extraction specifics
