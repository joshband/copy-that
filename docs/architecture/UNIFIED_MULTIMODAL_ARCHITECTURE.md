# Copy That: Unified Multimodal Architecture

**Document Version:** 1.0
**Date:** 2025-12-09
**Status:** Production Architecture Specification
**Purpose:** Single source of truth for platform architecture

---

## Executive Summary

**Copy That is a multimodal design token extraction platform** that uses tokens as a universal creative intermediate representation (IR). The platform extracts design tokens from any input modality (images, audio, video, text) and generates output for any target system (UI frameworks, audio plugins, MIDI, animations).

**Current State:** Production-ready visual token extraction (color, spacing, typography, shadows) with working token graph, 17 tests passing, and interactive demo UI.

**Key Architecture Decision:** Features organized by **modality** (visual, audio, video) not by token type (color, spacing). This enables scaling from 4 token types (current) to 100+ token types (future) without architectural changes.

---

## Core Architecture Principles

### 1. Tokens as Universal Creative IR

Similar to LLVM IR for compilers or MIDI for music:
- **Input adapters** transform modality-specific data → W3C Design Tokens
- **Token platform** manages relationships, dependencies, and validation
- **Output generators** transform tokens → platform-specific code/data

**Key Benefit:** Loose coupling enables any input → any output without n×m integrations.

### 2. Modality-First Organization

```
features/
├── visual-extraction/      ✅ Modality = Visual (images)
│   ├── color/             │  Token types within modality
│   ├── spacing/           │
│   ├── typography/        │
│   └── shadow/            │
├── audio-extraction/       🆕 Modality = Audio (future)
│   ├── pitch/
│   ├── rhythm/
│   └── timbre/
└── video-extraction/       🆕 Modality = Video (future)
    ├── motion/
    ├── transition/
    └── keyframe/
```

**Why this matters:** Adding typography extraction doesn't create a new feature - it's a new token type within existing visual-extraction feature.

### 3. Graph-First Data Model

All tokens stored as **directed graph** with relationships:
- **Aliases:** `{color.primary}` → references another token
- **Composition:** Shadows reference colors, typography references fonts
- **Hierarchies:** Spacing scales reference base units
- **Cross-modal:** Future audio-visual synesthetic mappings

**Implementation:** `tokenGraphStore.ts` + `useTokenGraph()` hook (11 methods, 17 tests passing)

### 4. Adapter Pattern for Multimodal Rendering

Generic components (TokenCard, TokenTable) use **Visual Adapters** to render token-specific UI:

```typescript
interface TokenVisualAdapter<T> {
  category: TokenCategory
  renderSwatch: (token: T) => ReactNode
  renderMetadata: (token: T) => ReactNode
  getDetailTabs: (token: T) => TabDefinition[]
}

// Generic component uses adapter
<TokenCard token={colorToken} adapter={ColorVisualAdapter} />
```

**Key Benefit:** Adding audio tokens requires creating `AudioVisualAdapter` - zero changes to shared components.

---

## System Architecture

```
┌────────────────────────────────────────────────────────────┐
│                   INPUT ADAPTERS (Modular)                  │
│                  Any Modality → Tokens                      │
├────────────────────────────────────────────────────────────┤
│  Image (current) │ Audio (future) │ Video (future)         │
│  - SAM segmentation  - Pitch analysis   - Motion tracking  │
│  - K-means color     - Rhythm detect    - Scene segment    │
│  - Claude Vision     - Timbre extract   - Temporal tokens  │
└────────────────────────────────────────────────────────────┘
                              ↓
┌────────────────────────────────────────────────────────────┐
│                   TOKEN PLATFORM (Core)                     │
│              Universal Token Representation                 │
├────────────────────────────────────────────────────────────┤
│  • W3C Design Tokens (Standard Base)                       │
│  • Token Graph (Relationships & Dependencies)              │
│  • Multi-Modal Extensions ($extensions)                    │
│  • Cross-Modal Mappings (synesthesia)                      │
│  • Validation & Type Safety (Pydantic → Zod)              │
└────────────────────────────────────────────────────────────┘
                              ↓
┌────────────────────────────────────────────────────────────┐
│                OUTPUT GENERATORS (Modular)                  │
│                 Tokens → Any Output                         │
├────────────────────────────────────────────────────────────┤
│  UI (current)    │ Audio Plugins   │ MIDI/Music            │
│  - React         │ - JUCE/VST      │ - Synesthesia         │
│  - Flutter       │ - AudioKit      │ - Brand sonification │
│  - SwiftUI       │ - AAX           │ - Procedural music    │
└────────────────────────────────────────────────────────────┘
```

---

## Directory Structure (Target State)

```
src/
├── features/                           # Feature-based modules
│   ├── visual-extraction/              # Visual modality (current)
│   │   ├── components/
│   │   │   ├── color/                  # 12 color components
│   │   │   │   ├── ColorPalette/
│   │   │   │   ├── ColorDetails/
│   │   │   │   ├── ColorGraph/
│   │   │   │   ├── HarmonyVisualizer/
│   │   │   │   └── color-science/      # 7 educational components
│   │   │   ├── spacing/                # 8 spacing components
│   │   │   │   ├── SpacingRuler/
│   │   │   │   ├── SpacingScale/
│   │   │   │   ├── SpacingPreview/
│   │   │   │   └── SpacingTable/
│   │   │   ├── typography/             # 5 typography components
│   │   │   │   ├── TypographyCards/
│   │   │   │   ├── TypographyDetails/
│   │   │   │   ├── FontShowcase/
│   │   │   │   └── FontSizeScale/
│   │   │   └── shadow/                 # 2 shadow components
│   │   │       ├── ShadowInspector/
│   │   │       └── ShadowTokenList/
│   │   ├── adapters/                   # Visual rendering adapters
│   │   │   ├── ColorVisualAdapter.ts
│   │   │   ├── SpacingVisualAdapter.ts
│   │   │   ├── TypographyVisualAdapter.ts
│   │   │   └── ShadowVisualAdapter.ts
│   │   ├── hooks/
│   │   │   ├── useColorExtraction.ts
│   │   │   ├── useColorHarmony.ts
│   │   │   └── useAccessibility.ts
│   │   ├── types/
│   │   │   └── visual.ts
│   │   └── index.ts                    # Public API
│   │
│   ├── audio-extraction/               # Audio modality (Phase 5)
│   │   ├── components/audio/
│   │   ├── adapters/AudioVisualAdapter.ts
│   │   └── index.ts
│   │
│   ├── video-extraction/               # Video modality (Phase 6)
│   │   ├── components/motion/
│   │   ├── adapters/MotionVisualAdapter.ts
│   │   └── index.ts
│   │
│   └── image-upload/                   # Infrastructure feature
│       ├── components/ImageUploader/
│       ├── hooks/useImageUpload.ts
│       └── index.ts
│
├── shared/                             # Shared across features
│   ├── components/                     # Generic reusable UI
│   │   ├── TokenCard/                  # Generic token card (uses adapters)
│   │   ├── TokenTable/                 # Generic table view
│   │   ├── TokenGraph/                 # Generic graph visualization
│   │   ├── TokenGraphPanel/            # Tree structure view
│   │   ├── RelationsTable/             # Relationship viewer
│   │   ├── TokenInspectorSidebar/      # Generic metadata panel
│   │   └── TokenPlaygroundDrawer/      # Generic drawer
│   ├── hooks/
│   │   ├── useTokenGraph.ts            # ✅ Graph query API (11 methods)
│   │   ├── useApi.ts
│   │   └── useDebounce.ts
│   ├── adapters/
│   │   └── TokenVisualAdapter.ts       # Adapter interface definition
│   ├── types/
│   │   └── common.ts
│   └── utils/
│       └── helpers.ts
│
├── components/                         # App-level infrastructure
│   ├── MetricsOverview/                # System-wide metrics
│   ├── SessionCreator/                 # Project management
│   ├── LibraryCurator/                 # Token library management
│   └── ExportDownloader/               # Multi-token export
│
├── store/                              # State management
│   ├── tokenGraphStore.ts              # ✅ Graph store (multimodal-ready)
│   └── tokenStore.ts                   # ⚠️ Legacy (deprecate)
│
└── api/                                # API layer
    ├── client.ts
    └── endpoints/
```

---

## Token Graph Data Model (Production Implementation)

### Token Node Types

All tokens extend `UiTokenBase<T>`:

```typescript
interface UiTokenBase<T> {
  id: string              // Unique node identifier
  category: TokenCategory // Node type: 'color' | 'spacing' | 'shadow' | 'typography' | 'layout'
  raw: T                  // W3C token data
}
```

### Edge Types (Relationships)

| Edge Type | From → To | Example | Field |
|-----------|-----------|---------|-------|
| **Alias** | Color → Color | `color.button` → `color.primary` | `aliasTargetId` |
| **Base Multiplier** | Spacing → Spacing | `spacing.md` → `spacing.base` × 2 | `baseId`, `multiplier` |
| **Color Reference** | Shadow → Color | `shadow.card` → `color.shadow` | `referencedColorIds[]` |
| **Typography Refs** | Typography → Color/Font | `typography.body` → multiple | `referencedColorId`, `fontFamilyTokenId`, `fontSizeTokenId` |

### Graph Query API (useTokenGraph Hook)

**11 Methods, 17 Tests Passing:**

```typescript
const graph = useTokenGraph()

// Node access
graph.getNode('color.primary')               // Get single token
graph.getNodes('color')                      // Get all colors
graph.getAllNodes()                          // Get all tokens

// Edge traversal
graph.getAliases('color.primary')            // Find tokens aliasing this
graph.getDependencies('shadow.card')         // What this token depends on
graph.getDependents('color.primary')         // What depends on this token

// Reference resolution
graph.resolveAlias('color.button')           // Follow alias chain
graph.resolveReferences(token)               // Resolve {refs} to values

// Graph analysis
graph.getRootTokens()                        // Tokens with no dependencies
graph.getLeafTokens()                        // Tokens with no dependents

// Utilities
graph.hasToken('color.primary')              // Check existence
graph.getTokensByIds(['color.primary', ...]) // Batch fetch
```

---

## Visual Adapter Pattern (Critical Innovation)

### Problem Statement

Generic components need to render token-specific UI without domain knowledge:
- TokenCard must show color swatches, spacing rulers, audio waveforms, etc.
- Can't hardcode every token type (doesn't scale to 100+ types)
- Adding new token type shouldn't require changes to shared components

### Solution: Pluggable Visual Adapters

```typescript
// Adapter interface (shared/adapters/TokenVisualAdapter.ts)
interface TokenVisualAdapter<T> {
  category: TokenCategory
  renderSwatch: (token: T) => ReactNode
  renderMetadata: (token: T) => ReactNode
  getDetailTabs: (token: T) => TabDefinition[]
}

// Color adapter (visual-extraction/adapters/ColorVisualAdapter.ts)
const ColorVisualAdapter: TokenVisualAdapter<UiColorToken> = {
  category: 'color',
  renderSwatch: (token) => {
    const hex = extractHex(token.raw)
    return <div style={{ backgroundColor: hex }} className="w-8 h-8 rounded" />
  },
  renderMetadata: (token) => (
    <div>
      <p>Hex: {extractHex(token.raw)}</p>
      <p>Harmony: {token.raw.harmony}</p>
    </div>
  ),
  getDetailTabs: (token) => [
    { name: 'Harmony', component: HarmonyTab },
    { name: 'Accessibility', component: AccessibilityTab }
  ]
}

// Generic component uses adapter (shared/components/TokenCard.tsx)
function TokenCard({ token, adapter }: { token: TokenNode, adapter: TokenVisualAdapter }) {
  return (
    <div className="token-card">
      {adapter.renderSwatch(token)}     {/* Adapter renders token-specific UI */}
      {adapter.renderMetadata(token)}
    </div>
  )
}

// Usage in app
<TokenCard token={colorToken} adapter={ColorVisualAdapter} />
```

### Adapter Registry Pattern

```typescript
// Adapter registry (shared/adapters/registry.ts)
const ADAPTER_REGISTRY: Record<TokenCategory, TokenVisualAdapter<any>> = {
  color: ColorVisualAdapter,
  spacing: SpacingVisualAdapter,
  typography: TypographyVisualAdapter,
  shadow: ShadowVisualAdapter,
}

// Auto-select adapter
function TokenCard({ token }: { token: TokenNode }) {
  const adapter = ADAPTER_REGISTRY[token.category]
  return (
    <div className="token-card">
      {adapter.renderSwatch(token)}
    </div>
  )
}
```

### Benefits

✅ **Zero domain knowledge** - TokenCard knows nothing about colors, spacing, etc.
✅ **Scales to 100+ token types** - Add adapter, no changes to shared components
✅ **Clear separation** - Adapters live in domain features (visual/, audio/, video/)
✅ **Testable** - Mock adapters for component tests
✅ **Multimodal-ready** - Audio/video adapters follow same pattern

---

## Component Migration Matrix (44 Components)

### Layer 1: Token-Agnostic → `shared/components/` (8 components)

| Component | Current | Target | Action |
|-----------|---------|--------|--------|
| TokenCard.tsx | components/ | shared/components/TokenCard/ | Refactor to use adapters |
| TokenGraphPanel.tsx | components/ | shared/components/TokenGraphPanel/ | Move as-is (already generic) |
| TokenGrid.tsx | components/ | shared/components/TokenGrid/ | Move as-is |
| TokenToolbar.tsx | components/ | shared/components/TokenToolbar/ | Move as-is |
| RelationsTable.tsx | components/ | shared/components/RelationsTable/ | Move as-is |
| RelationsDebugPanel.tsx | components/ | shared/components/RelationsDebugPanel/ | Move as-is |
| TokenInspectorSidebar.tsx | components/ | shared/components/TokenInspectorSidebar/ | Move as-is |
| TokenPlaygroundDrawer.tsx | components/ | shared/components/TokenPlaygroundDrawer/ | Move as-is |

### Layer 2: Visual-Specific → `features/visual-extraction/components/` (27 components)

#### Color (12 components)
| Component | Target |
|-----------|--------|
| ColorTokenDisplay.tsx | visual-extraction/components/color/ColorDisplay/ |
| ColorGraphPanel.tsx | visual-extraction/components/color/ColorGraph/ |
| ColorsTable.tsx | visual-extraction/components/color/ColorTable/ |
| ColorPrimaryPreview.tsx | visual-extraction/components/color/ColorPreview/ |
| ColorPaletteSelector.tsx | visual-extraction/components/color/ColorPalette/ |
| CompactColorGrid.tsx | visual-extraction/components/color/ColorGrid/ |
| HarmonyVisualizer.tsx | visual-extraction/components/color/HarmonyVisualizer/ |
| EducationalColorDisplay.tsx | visual-extraction/components/color/EducationalDisplay/ |
| ColorNarrative.tsx | visual-extraction/components/color/ColorNarrative/ |
| color-detail-panel/ (5 tabs) | visual-extraction/components/color/ColorDetailPanel/ |
| color-science/ (7 components) | visual-extraction/components/color/color-science/ |
| OverviewNarrative.tsx | visual-extraction/components/color/OverviewNarrative/ |

#### Spacing (8 components)
| Component | Target |
|-----------|--------|
| SpacingScalePanel.tsx | visual-extraction/components/spacing/SpacingScale/ |
| SpacingTable.tsx | visual-extraction/components/spacing/SpacingTable/ |
| SpacingGraphList.tsx | visual-extraction/components/spacing/SpacingGraph/ |
| SpacingRuler.tsx | visual-extraction/components/spacing/SpacingRuler/ |
| SpacingGapDemo.tsx | visual-extraction/components/spacing/SpacingDemo/ |
| SpacingDetailCard.tsx | visual-extraction/components/spacing/SpacingDetails/ |
| SpacingResponsivePreview.tsx | visual-extraction/components/spacing/SpacingPreview/ |
| spacing-showcase/ (6 components) | visual-extraction/components/spacing/SpacingShowcase/ |

#### Typography (5 components)
| Component | Target |
|-----------|--------|
| TypographyInspector.tsx | visual-extraction/components/typography/TypographyInspector/ |
| TypographyDetailCard.tsx | visual-extraction/components/typography/TypographyDetails/ |
| TypographyCards.tsx | visual-extraction/components/typography/TypographyCards/ |
| FontFamilyShowcase.tsx | visual-extraction/components/typography/FontShowcase/ |
| FontSizeScale.tsx | visual-extraction/components/typography/FontSizeScale/ |

#### Shadow (2 components)
| Component | Target |
|-----------|--------|
| ShadowInspector.tsx | visual-extraction/components/shadow/ShadowInspector/ |
| shadows/ (8 files) | visual-extraction/components/shadow/ |

### Layer 3: App Infrastructure → Keep in `components/` (6 components)

| Component | Keep At | Reason |
|-----------|---------|--------|
| MetricsOverview.tsx | components/ | System-wide metrics |
| SessionCreator.tsx | components/ | Project management |
| SessionWorkflow.tsx | components/ | Multi-step workflow |
| LibraryCurator.tsx | components/ | Token library management |
| ExportDownloader.tsx | components/ | Multi-token export |
| image-uploader/ (7 files) | features/image-upload/ | Infrastructure feature |

### Layer 4: Educational → Evaluate (6 components)

| Component | Decision |
|-----------|----------|
| LearningSidebar.tsx | Move to features/education/ OR deprecate |
| PlaygroundSidebar.tsx | Move to features/education/ OR deprecate |
| AdvancedColorScienceDemo.tsx | Already in color-science/ (keep) |
| AccessibilityVisualizer.tsx | Already in color components (keep) |
| BatchImageUploader.tsx | Deprecate (unused) |
| CostDashboard.tsx | Deprecate (unused) |

---

## Key Conflicts Resolved

### Conflict #1: Feature Naming ✅ RESOLVED

**Earlier approach (❌ Wrong):**
```
features/color-extraction/      # Color is NOT a modality
features/spacing-analysis/      # Spacing is NOT a modality
features/typography-extraction/ # Typography is NOT a modality
```

**Correct approach (✅ Right):**
```
features/visual-extraction/     # Visual IS a modality
  ├── color/                   # Token types within modality
  ├── spacing/
  ├── typography/
  └── shadow/
```

**Why?** Color, spacing, typography, shadows are all **visual domain** concepts extracted from images. The modality is "visual" (vs "audio" or "video"). This scales to 100+ token types without creating 100+ features.

### Conflict #2: Component Categorization ✅ RESOLVED

**Rule:** Components belong in 1 of 4 layers:

1. **Token-agnostic** (shared/components/) - Works for any token type via adapters
2. **Visual-specific** (visual-extraction/components/) - Renders visual tokens
3. **App infrastructure** (components/) - System-level concerns
4. **Educational** (features/education/ or deprecate) - Learning/demo content

**44 Components Mapped:**
- 8 token-agnostic → shared/
- 27 visual-specific → visual-extraction/
- 6 app infrastructure → components/
- 3 educational → features/education/ or deprecate

### Conflict #3: Abstraction Pattern ✅ RESOLVED

**Adapter Pattern Implementation:**
1. Define `TokenVisualAdapter<T>` interface in `shared/adapters/`
2. Create concrete adapters in `visual-extraction/adapters/` (ColorVisualAdapter, etc.)
3. Refactor shared components (TokenCard, TokenTable) to use adapters
4. Register adapters in `ADAPTER_REGISTRY`
5. Components auto-select adapter based on `token.category`

**Migration Order:**
- Phase 1: Create adapter interface + ColorVisualAdapter
- Phase 2: Refactor TokenCard to use adapters
- Phase 3: Create remaining visual adapters (Spacing, Typography, Shadow)
- Phase 4: Prove pattern with mock audio adapter

---

## Implementation Roadmap (4 Phases, 4 Weeks)

### Phase 1: Foundation (Week 1) - Adapter Pattern + Shared Components

**Goal:** Extract token-agnostic components and create adapter system

**Day 1-2: Adapter Interface (6 hours)**
- [ ] Create `shared/adapters/TokenVisualAdapter.ts` interface
- [ ] Create `shared/adapters/registry.ts` adapter registry
- [ ] Document adapter pattern with examples
- [ ] Write adapter interface tests

**Day 3-4: First Adapter Implementation (8 hours)**
- [ ] Create `visual-extraction/adapters/ColorVisualAdapter.ts`
- [ ] Implement renderSwatch, renderMetadata, getDetailTabs
- [ ] Test adapter with existing color components
- [ ] Register in ADAPTER_REGISTRY

**Day 5: Refactor TokenCard (6 hours)**
- [ ] Copy TokenCard to `shared/components/TokenCard/`
- [ ] Refactor to use adapter pattern (remove hardcoded color logic)
- [ ] Update tests to use mock adapters
- [ ] Verify color tokens still render correctly

**Success Criteria:**
- ✅ TokenCard renders colors via ColorVisualAdapter
- ✅ All 17 existing tests passing
- ✅ Zero TypeScript errors
- ✅ App functionality unchanged

---

### Phase 2: Visual Consolidation (Week 2) - Move Components

**Goal:** Consolidate all visual components under `features/visual-extraction/`

**Day 1: Create Directory Structure (2 hours)**
- [ ] Create `features/visual-extraction/components/{color,spacing,typography,shadow}/`
- [ ] Create `features/visual-extraction/adapters/`
- [ ] Create `features/visual-extraction/hooks/`
- [ ] Create barrel exports (index.ts)

**Day 2-3: Move Color Components (12 hours)**
- [ ] Move 12 color components to visual-extraction/components/color/
- [ ] Update imports in App.tsx
- [ ] Test after each component
- [ ] Run full test suite

**Day 4: Move Spacing Components (6 hours)**
- [ ] Move 8 spacing components to visual-extraction/components/spacing/
- [ ] Update imports
- [ ] Test

**Day 5: Move Typography + Shadow (4 hours)**
- [ ] Move 5 typography components to visual-extraction/components/typography/
- [ ] Move 2 shadow components to visual-extraction/components/shadow/
- [ ] Update imports
- [ ] Final test run

**Success Criteria:**
- ✅ All visual components in features/visual-extraction/
- ✅ Zero components in components/ root (except infrastructure)
- ✅ All tests passing
- ✅ App works identically

---

### Phase 3: Adapter Extraction (Week 3) - Complete Adapter System

**Goal:** Extract domain logic into adapters for all visual token types

**Day 1-2: Create Remaining Adapters (10 hours)**
- [ ] Create SpacingVisualAdapter
- [ ] Create TypographyVisualAdapter
- [ ] Create ShadowVisualAdapter
- [ ] Register all adapters in registry

**Day 3-4: Refactor Shared Components (10 hours)**
- [ ] Move 7 remaining generic components to shared/
- [ ] Refactor TokenTable to use adapters
- [ ] Refactor TokenGraph to use adapters
- [ ] Update all adapter usage sites

**Day 5: Testing & Documentation (4 hours)**
- [ ] Write adapter tests (all 4 adapters)
- [ ] Update component documentation
- [ ] Create adapter developer guide
- [ ] Run full integration tests

**Success Criteria:**
- ✅ All 4 visual adapters implemented
- ✅ Generic components have zero domain knowledge
- ✅ All rendering delegated to adapters
- ✅ Easy to add new adapters

---

### Phase 4: Multimodal POC (Week 4) - Prove Architecture

**Goal:** Validate architecture supports non-visual tokens (audio)

**Day 1-2: Audio Token Schema (8 hours)**
- [ ] Define W3CAudioToken TypeScript interface
- [ ] Create UiAudioToken graph node type
- [ ] Add 'audio' to TokenCategory union
- [ ] Update tokenGraphStore to handle audio tokens

**Day 3: Audio Visual Adapter (4 hours)**
- [ ] Create AudioVisualAdapter implementation
- [ ] Implement renderSwatch (waveform placeholder)
- [ ] Implement renderMetadata (BPM, key, duration)
- [ ] Register in ADAPTER_REGISTRY

**Day 4: Mock Data & Integration (6 hours)**
- [ ] Create mock audio tokens (5-10 tokens)
- [ ] Add to tokenGraphStore
- [ ] Verify TokenCard renders audio tokens
- [ ] Verify TokenGraph includes audio nodes

**Day 5: Documentation & Demo (4 hours)**
- [ ] Document multimodal architecture
- [ ] Create demo video showing audio tokens
- [ ] Update roadmap for Phase 5 (real audio extraction)
- [ ] Celebrate architecture validation 🎉

**Success Criteria:**
- ✅ Audio tokens visible in Token Graph Explorer
- ✅ No changes to shared components required
- ✅ Architecture validated for multimodal future
- ✅ Clear path forward for real audio extraction

---

## Technology Stack

### Frontend (Current - Production)
- **Framework:** React 18 + Vite + TypeScript
- **State:** Zustand (tokenGraphStore)
- **UI:** Custom components (Token Page Template system)
- **Visualization:** D3.js (planned), Cytoscape (planned)
- **Testing:** Vitest, React Testing Library (17 tests passing)

### Backend (Current - Production)
- **Framework:** FastAPI + Python 3.12+
- **Type Safety:** Pydantic v2 (server) → Zod (client)
- **AI/ML:** Claude Sonnet 4.5, OpenCV, SAM
- **Database:** PostgreSQL via SQLModel
- **Color Science:** ColorAide, NumPy, Scikit-learn

### Token Schema (Current - Production)
- **Format:** W3C Design Tokens Community Group
- **Validation:** JSON Schema + Pydantic + Zod
- **Features:** Token references, hierarchies, extensions

### Future Additions (Phase 5-6)
- **Audio:** librosa, essentia, aubio (audio analysis)
- **Video:** OpenCV, PyAV, FFmpeg (video processing)
- **MIDI:** mido, music21 (music generation)
- **Animation:** Lottie, GSAP (motion export)

---

## Success Metrics

### Current State (Baseline)
- ✅ 17 tests passing (tokenGraphStore + useTokenGraph)
- ✅ 44 components (disorganized)
- ✅ 4 token types (color, spacing, typography, shadow)
- ✅ 11 graph query methods working
- ✅ Interactive demo with 24 tokens

### Phase 1 Goals (Week 1)
- ✅ Adapter pattern implemented
- ✅ ColorVisualAdapter working
- ✅ TokenCard refactored
- ✅ All 17 tests passing
- ✅ Zero TypeScript errors

### Phase 2 Goals (Week 2)
- ✅ All visual components in features/visual-extraction/
- ✅ Clean directory structure
- ✅ All tests passing
- ✅ App functionality unchanged

### Phase 3 Goals (Week 3)
- ✅ All 4 visual adapters implemented
- ✅ Generic components domain-agnostic
- ✅ All tests passing
- ✅ Adapter developer guide complete

### Phase 4 Goals (Week 4)
- ✅ Audio token POC working
- ✅ Architecture validated for multimodal
- ✅ Zero changes to shared components
- ✅ Clear roadmap for Phase 5+

### Ultimate Vision (6-12 Months)
- 🎯 10+ modalities (visual, audio, video, text, 3D, AR/VR)
- 🎯 100+ token types across all modalities
- 🎯 20+ output generators (UI, audio plugins, MIDI, animations)
- 🎯 Cross-modal creativity (image → music, audio → UI)
- 🎯 Full multimodal design system generation

---

## Developer Quick Start

### Working with Token Graph

```typescript
import { useTokenGraph } from '@/shared/hooks/useTokenGraph'

function MyComponent() {
  const graph = useTokenGraph()

  // Get tokens by category
  const colors = graph.getNodes('color')

  // Find relationships
  const primaryColor = graph.getNode('color.primary')
  const aliases = graph.getAliases('color.primary')
  const dependents = graph.getDependents('color.primary')

  // Resolve references
  const resolved = graph.resolveAlias('color.button')

  return (
    <div>
      {colors.map(color => {
        const usedBy = graph.getDependents(color.id)
        return (
          <TokenCard
            key={color.id}
            token={color}
            usedBy={usedBy}
          />
        )
      })}
    </div>
  )
}
```

### Creating a Visual Adapter

```typescript
// 1. Define adapter (visual-extraction/adapters/MyAdapter.ts)
export const MyTokenVisualAdapter: TokenVisualAdapter<UiMyToken> = {
  category: 'mytoken',
  renderSwatch: (token) => <MyTokenSwatch token={token} />,
  renderMetadata: (token) => <MyTokenMetadata token={token} />,
  getDetailTabs: (token) => [
    { name: 'Details', component: MyDetailsTab },
    { name: 'Analysis', component: MyAnalysisTab }
  ]
}

// 2. Register (shared/adapters/registry.ts)
const ADAPTER_REGISTRY = {
  // ... existing
  mytoken: MyTokenVisualAdapter
}

// 3. Use in components (automatic via registry)
<TokenCard token={myToken} />  // Auto-selects MyTokenVisualAdapter
```

### Adding a New Feature

```bash
# 1. Create feature directory
mkdir -p src/features/my-feature/components/token-type
mkdir -p src/features/my-feature/adapters
mkdir -p src/features/my-feature/hooks

# 2. Create adapter
touch src/features/my-feature/adapters/MyTokenVisualAdapter.ts

# 3. Create components
touch src/features/my-feature/components/token-type/MyTokenDisplay.tsx

# 4. Export from feature
echo "export * from './components/token-type/MyTokenDisplay'" > src/features/my-feature/index.ts
echo "export { MyTokenVisualAdapter } from './adapters/MyTokenVisualAdapter'" >> src/features/my-feature/index.ts

# 5. Register adapter
# Add to shared/adapters/registry.ts
```

---

## Related Documentation

### Architecture (Must Read)
- **This Document** - Single source of truth
- `STRATEGIC_VISION_AND_ARCHITECTURE.md` - Original vision (context)
- `MODULAR_TOKEN_PLATFORM_VISION.md` - Multimodal theory (context)
- `TOKEN_GRAPH_DATA_MODEL_2025_12_09.md` - Graph implementation details

### Analysis Documents (Reference)
- `COMPONENT_MODULARITY_ANALYSIS_2025_12_09.md` - Component breakdown
- `PLAN_AGENT_MULTIMODAL_ARCHITECTURE_2025_12_09.md` - Adapter pattern design
- `FRONTEND_COMPONENT_USAGE_MAP.md` - Component usage analysis

### Implementation Guides (Coming Soon)
- `ADAPTER_PATTERN_GUIDE.md` - How to create adapters
- `FEATURE_CREATION_GUIDE.md` - How to add features
- `GRAPH_QUERY_COOKBOOK.md` - useTokenGraph examples

---

## FAQ

### Q: Why "visual-extraction" not "color-extraction"?

**A:** Color is a token type within the visual modality (images). Grouping by modality (visual, audio, video) scales better than grouping by token type (color, spacing, typography, etc.). Visual modality contains 30+ token types; creating 30+ features would be chaos.

### Q: Why adapter pattern instead of inheritance?

**A:** Adapters enable composition over inheritance. Generic components delegate rendering to adapters without coupling. Adding new token types requires zero changes to shared components. Adapters live in domain features, maintaining clear boundaries.

### Q: Why is tokenGraphStore separate from tokenStore?

**A:** `tokenGraphStore` is the new graph-based model (multimodal-ready). `tokenStore` is legacy flat arrays (deprecate after migration). Graph model enables relationship queries (aliases, dependencies, dependents) that flat arrays can't support.

### Q: Can I still use legacy tokenStore?

**A:** Yes, but migrate to `useTokenGraph()` hook ASAP. `tokenGraphStore` provides backward-compatible `legacyColors()`, `legacySpacing()` methods during transition. Plan to deprecate `tokenStore` by Phase 3.

### Q: How do I add audio tokens?

**A:** Phase 4 proves architecture with mock audio tokens. Phase 5 (real audio extraction) requires:
1. Define `W3CAudioToken` schema
2. Create `UiAudioToken` graph node type
3. Add audio extraction backend (librosa)
4. Create `AudioVisualAdapter` for rendering
5. Register adapter - done!

### Q: What's the largest change in this refactor?

**A:** Moving from flat component structure (45 root components) to feature-based modules (3 features with clear boundaries). Requires updating ~100 imports but zero logic changes. All tests should pass throughout migration.

---

## Next Session Checklist

**Before starting:**
1. ✅ Review this document (you are here)
2. ✅ Review working implementation (`tokenGraphStore.ts`, `useTokenGraph.ts`)
3. ✅ Verify 17 tests passing (`pnpm test`)
4. ✅ Run `pnpm typecheck` (baseline)

**First 3 hours (Phase 1, Day 1-2):**
1. Create `shared/adapters/TokenVisualAdapter.ts` interface (30 min)
2. Create `shared/adapters/registry.ts` adapter registry (30 min)
3. Create `visual-extraction/adapters/ColorVisualAdapter.ts` (1 hour)
4. Write adapter tests (1 hour)

**Expected deliverables:**
- ✅ Adapter interface defined
- ✅ ColorVisualAdapter implemented
- ✅ Tests passing
- ✅ Documentation updated

---

**Document Status:** Production Architecture Specification
**Last Updated:** 2025-12-09
**Next Review:** After Phase 1 completion
**Maintained By:** Architecture Team

---

## Appendix A: Component Migration Checklist

**Phase 1: Shared Components (Week 1)**
- [ ] TokenCard → shared/components/TokenCard/ (refactor for adapters)
- [ ] TokenGraphPanel → shared/components/TokenGraphPanel/
- [ ] TokenGrid → shared/components/TokenGrid/
- [ ] TokenToolbar → shared/components/TokenToolbar/
- [ ] RelationsTable → shared/components/RelationsTable/
- [ ] RelationsDebugPanel → shared/components/RelationsDebugPanel/
- [ ] TokenInspectorSidebar → shared/components/TokenInspectorSidebar/
- [ ] TokenPlaygroundDrawer → shared/components/TokenPlaygroundDrawer/

**Phase 2: Visual Components (Week 2)**
- [ ] 12 color components → visual-extraction/components/color/
- [ ] 8 spacing components → visual-extraction/components/spacing/
- [ ] 5 typography components → visual-extraction/components/typography/
- [ ] 2 shadow components → visual-extraction/components/shadow/

**Phase 3: Adapters (Week 3)**
- [ ] ColorVisualAdapter (already done in Phase 1)
- [ ] SpacingVisualAdapter
- [ ] TypographyVisualAdapter
- [ ] ShadowVisualAdapter

**Phase 4: Validation (Week 4)**
- [ ] AudioVisualAdapter (mock)
- [ ] Audio token POC
- [ ] Architecture validation

---

## Appendix B: Import Path Updates

**Before (flat structure):**
```typescript
import ColorTokenDisplay from './components/ColorTokenDisplay'
import SpacingTable from './components/SpacingTable'
import TokenCard from './components/TokenCard'
```

**After (feature-based):**
```typescript
import { ColorDisplay } from '@/features/visual-extraction/components/color'
import { SpacingTable } from '@/features/visual-extraction/components/spacing'
import { TokenCard } from '@/shared/components/TokenCard'
```

**Batch update command:**
```bash
# Find all imports to update
rg "from.*components/(Color|Spacing|Typography|Shadow)" frontend/src/

# Update imports (manual or with tool)
# Use VSCode/Cursor "Rename Symbol" for safety
```

---

## Appendix C: Key Architectural Decisions (ADRs)

### ADR-001: Feature Organization by Modality (2025-12-09)

**Decision:** Organize features by input modality (visual, audio, video) not by token type (color, spacing).

**Rationale:**
- Token types are implementation details within a modality
- Visual extraction produces 30+ token types - 30+ features would be chaos
- Audio extraction will produce 20+ token types (pitch, rhythm, timbre, etc.)
- Modality-first scales to 100+ token types without architectural changes

**Status:** Accepted

---

### ADR-002: Adapter Pattern for Multimodal Rendering (2025-12-09)

**Decision:** Use Visual Adapter pattern for token-specific rendering in generic components.

**Rationale:**
- Enables composition over inheritance
- Generic components stay simple and testable
- Adding new token types requires zero changes to shared components
- Adapters live in domain features, maintaining clear boundaries
- Proven pattern in multimodal systems (strategy pattern)

**Status:** Accepted

---

### ADR-003: Graph-First Data Model (2025-11-18)

**Decision:** Store all tokens in graph with relationships, not flat arrays.

**Rationale:**
- Design tokens form natural graph (aliases, dependencies, compositions)
- Graph queries enable "where is this used?" functionality
- Cross-modal relationships possible (synesthesia mappings)
- W3C spec supports token references (`{color.primary}`)
- Scales to 1000s of tokens with complex dependencies

**Status:** Accepted (implemented, 17 tests passing)

---

**End of Document**
