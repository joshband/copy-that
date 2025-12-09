# Plan Agent - Multimodal Architecture Analysis - 2025-12-09

**Agent:** Claude Code Plan Agent
**Task:** Design multimodal token platform architecture
**Status:** ✅ Complete
**Context:** 44 ad-hoc components need proper organization for multimodal tokens

---

## 🎯 Executive Summary

**Key Finding:** Your token graph foundation (`useTokenGraph()` hook and `tokenGraphStore.ts`) is **already multimodal-ready**! The problem is at the component layer - 44 components are organized ad-hoc without clear taxonomy.

**Critical Insight:**
- **Color, Spacing, Typography** are ALL **visual domain tokens**
- They should be grouped as `features/visual-extraction/` (not separate features)
- **8 components are token-agnostic** and should be in `shared/`
- **Visual Adapter Pattern** needed to make generic components work for any token type

---

## 📊 Component Taxonomy (All 44 Components Categorized)

### Layer 1: Token-Agnostic (8 components) → `shared/components/`

| Component | Why Generic | Refactor Needed |
|-----------|-------------|-----------------|
| TokenCard.tsx | Uses registry pattern | ✅ Remove hardcoded color logic |
| TokenGraphPanel.tsx | Visualizes tree structure | ✅ Already generic |
| TokenGrid.tsx | Generic grid layout | ✅ Already generic |
| TokenToolbar.tsx | Generic actions | ✅ Already generic |
| RelationsTable.tsx | Generic relationships | ✅ Already generic |
| RelationsDebugPanel.tsx | Generic debug view | ✅ Already generic |
| TokenInspectorSidebar.tsx | Generic metadata | ✅ Already generic |
| TokenPlaygroundDrawer.tsx | Generic drawer | ✅ Already generic |

**Action:** Move to `src/shared/components/` in Phase 1

---

### Layer 2: Visual-Specific (24 components) → `features/visual-extraction/`

#### Color Components (12)
- ColorTokenDisplay.tsx
- ColorGraphPanel.tsx
- ColorsTable.tsx
- ColorPrimaryPreview.tsx
- ColorPaletteSelector.tsx
- CompactColorGrid.tsx
- HarmonyVisualizer.tsx
- EducationalColorDisplay.tsx
- ColorNarrative.tsx
- color-detail-panel/ (5 tabs)
- color-science/ (7 components)
- OverviewNarrative.tsx

**Action:** Move to `features/visual-extraction/components/color/`

---

#### Spacing Components (8)
- SpacingScalePanel.tsx
- SpacingTable.tsx
- SpacingGraphList.tsx
- SpacingRuler.tsx
- SpacingGapDemo.tsx
- SpacingDetailCard.tsx
- SpacingResponsivePreview.tsx
- spacing-showcase/ (6 components)

**Action:** Move to `features/visual-extraction/components/spacing/`

---

#### Typography Components (4)
- TypographyInspector.tsx
- TypographyDetailCard.tsx
- TypographyCards.tsx
- FontFamilyShowcase.tsx
- FontSizeScale.tsx
- typography-detail-card/ (2 components)

**Action:** Move to `features/visual-extraction/components/typography/`

---

#### Shadow Components (2)
- ShadowInspector.tsx
- shadows/ (8 files)

**Action:** Move to `features/visual-extraction/components/shadow/`

---

### Layer 3: App Infrastructure (6) → Keep in `components/`

- image-uploader/ (7 components) - File upload orchestration
- MetricsOverview.tsx - System-wide metrics
- SessionCreator.tsx - Project management
- SessionWorkflow.tsx - Multi-step workflow
- LibraryCurator.tsx - Token library management
- ExportDownloader.tsx - Multi-token export

**Action:** Keep at root level (app-level concerns)

---

### Layer 4: Educational (6) → Evaluate

- LearningSidebar.tsx
- PlaygroundSidebar.tsx
- AdvancedColorScienceDemo.tsx
- AccessibilityVisualizer.tsx
- BatchImageUploader.tsx
- CostDashboard.tsx

**Action:** Create `features/education/` or deprecate

---

## 🏗️ Visual Adapter Pattern (Critical Innovation)

### The Problem

**Current:** TokenCard hardcodes color-specific logic:
```typescript
{tokenType === 'color' && token.hex && (
  <div style={{ backgroundColor: token.hex }} />
)}
```

**Future:** Need to support audio, video, motion tokens

---

### The Solution: Pluggable Adapters

```typescript
// Adapter interface
interface TokenVisualAdapter<T> {
  category: TokenCategory
  renderSwatch: (token: T) => ReactNode
  renderMetadata: (token: T) => ReactNode
  getDetailTabs: (token: T) => TabDefinition[]
}

// Color adapter
const ColorVisualAdapter: TokenVisualAdapter<UiColorToken> = {
  category: 'color',
  renderSwatch: (token) => {
    const hex = extractHex(token.raw)
    return <div style={{ backgroundColor: hex }} />
  },
  renderMetadata: (token) => (
    <div>Harmony: {token.raw.harmony}</div>
  ),
  getDetailTabs: (token) => [
    { name: 'Harmony', component: HarmonyTab },
    { name: 'Accessibility', component: AccessibilityTab }
  ]
}

// Audio adapter (future)
const AudioVisualAdapter: TokenVisualAdapter<UiAudioToken> = {
  category: 'audio',
  renderSwatch: (token) => <AudioWaveform data={token.raw.waveform} />,
  renderMetadata: (token) => (
    <div>BPM: {token.bpm} | Key: {token.raw.key}</div>
  ),
  getDetailTabs: (token) => [
    { name: 'Waveform', component: WaveformTab },
    { name: 'Spectrum', component: SpectrumTab }
  ]
}
```

**Benefits:**
- ✅ TokenCard becomes truly generic (no domain knowledge)
- ✅ Add new token type = create adapter (no changes to shared components)
- ✅ Adapters live in domain features (visual/, audio/, video/)

---

## 🗺️ Revised Feature Structure

### Current (What We Created Today):
```
features/
├── color-extraction/        ❌ Too granular!
├── spacing-analysis/        ❌ Too granular!
├── typography-extraction/   ❌ Too granular!
└── shadow-analysis/         ❌ Too granular!
```

### Correct (What Plan Agent Recommends):
```
features/
├── visual-extraction/       ✅ All visual tokens together!
│   ├── components/
│   │   ├── color/          # 12 color components
│   │   ├── spacing/        # 8 spacing components
│   │   ├── typography/     # 4 typography components
│   │   └── shadow/         # 2 shadow components
│   ├── adapters/
│   │   ├── ColorVisualAdapter.ts
│   │   ├── SpacingVisualAdapter.ts
│   │   ├── TypographyVisualAdapter.ts
│   │   └── ShadowVisualAdapter.ts
│   ├── hooks/
│   ├── types/
│   └── index.ts
│
├── audio-extraction/        🆕 Future (Phase 5)
│   ├── components/audio/
│   ├── adapters/AudioVisualAdapter.ts
│   └── index.ts
│
└── video-extraction/        🆕 Future (Phase 6)
    ├── components/motion/
    ├── adapters/MotionVisualAdapter.ts
    └── index.ts
```

**Why This is Better:**
- **Domain-driven** (visual vs audio vs video) not token-type-driven
- **Fewer top-level features** (3 instead of 5+)
- **Scales to multimodal** without creating dozens of features

---

## 📐 Critical Files for Implementation

### 1. NEW: `src/shared/adapters/TokenVisualAdapter.ts`
**Purpose:** Define adapter interface
**Priority:** Phase 1, Day 1 (Foundation)
**Impact:** Enables all future multimodal work

### 2. REFACTOR: `src/shared/components/TokenCard.tsx`
**Purpose:** Make truly generic via adapters
**Priority:** Phase 1, Day 2
**Impact:** Most-used component becomes reusable

### 3. NEW: `features/visual-extraction/adapters/ColorVisualAdapter.ts`
**Purpose:** First concrete adapter (template for all future)
**Priority:** Phase 3, Day 2
**Impact:** Proves pattern works

### 4. DOCUMENT: `src/store/tokenGraphStore.ts`
**Purpose:** Explain multimodal extensibility
**Priority:** Phase 1, Day 5
**Impact:** Developer understanding

### 5. UPDATE: `src/App.tsx`
**Purpose:** Use generic components with adapters
**Priority:** Phase 2, Day 5
**Impact:** Main integration point

---

## 🎯 Migration Strategy (4 Phases, 4 Weeks)

### Phase 1: Foundation (Week 1)
**Goal:** Extract token-agnostic components to `shared/`

**Steps:**
1. Create `shared/` directory structure
2. **Copy** (don't move) 8 generic components
3. Create `TokenVisualAdapter` interface
4. Create `ColorVisualAdapter` implementation
5. Refactor `TokenCard` to use adapter registry
6. Test that color tokens still render correctly

**Success Criteria:**
- ✅ `TokenCard` works with adapters
- ✅ All existing tests pass
- ✅ Zero TypeScript errors
- ✅ App functionality unchanged

---

### Phase 2: Visual Consolidation (Week 2)
**Goal:** Move all visual components to `features/visual-extraction/`

**Steps:**
1. Rename directories:
   - `features/color-extraction/` → `features/visual-extraction/components/color/`
   - Delete `features/spacing-analysis/`, etc.
2. Move 24 visual components
3. Update imports in App.tsx
4. Test after each batch

**Success Criteria:**
- ✅ Zero components in `components/` root (except infrastructure)
- ✅ All visual components in `features/visual-extraction/`
- ✅ Tests passing

---

### Phase 3: Adapter Extraction (Week 3)
**Goal:** Extract domain logic into adapters

**Steps:**
1. Create 4 visual adapters (Color, Spacing, Typography, Shadow)
2. Update generic components to use adapters
3. Remove hardcoded domain logic
4. Register adapters in registry

**Success Criteria:**
- ✅ Generic components have zero domain knowledge
- ✅ All rendering delegated to adapters
- ✅ Easy to add new adapters

---

### Phase 4: Multimodal POC (Week 4)
**Goal:** Prove architecture supports non-visual tokens

**Steps:**
1. Define `W3CAudioToken` schema
2. Create `UiAudioToken` interface
3. Create `AudioVisualAdapter`
4. Add mock audio tokens to graph
5. Verify `TokenCard` renders them

**Success Criteria:**
- ✅ Audio tokens visible in Token Graph Explorer
- ✅ No changes to shared components
- ✅ Architecture validated

---

## 💡 Key Architectural Insights

### Insight #1: Feature Names Were Wrong

**Mistake:**
```
features/color-extraction/      ❌ Color isn't a modality!
features/spacing-analysis/      ❌ Spacing isn't a modality!
```

**Correct:**
```
features/visual-extraction/     ✅ Visual IS a modality!
  ├── color/
  ├── spacing/
  └── typography/
```

**Why?** Color, spacing, typography are all **visual domain** concepts. The modality is "visual" (vs "audio" or "video").

---

### Insight #2: useTokenGraph() Already Perfect

Your hook built today is **already multimodal**:
```typescript
getNodes(category: TokenCategory)  // Works for ANY category!
getDependencies(tokenId: string)   // Works across modalities!
```

No changes needed - just add new categories when ready.

---

### Insight #3: Adapter Pattern is Key

**Without adapters:**
- Every new token type requires changes to shared components
- TokenCard has 10+ if/else branches for token types
- Can't scale beyond 5-6 token types

**With adapters:**
- New token type = new adapter (zero changes to shared components)
- TokenCard stays simple (just calls adapter.renderSwatch)
- Scales to 100+ token types

---

## 📋 Component Migration Matrix

### What Goes Where (Complete Mapping)

| Current Component | New Location | Reason |
|-------------------|--------------|--------|
| TokenCard.tsx | shared/components/ | Generic with adapters |
| ColorTokenDisplay.tsx | visual-extraction/components/color/ | Visual rendering |
| SpacingRuler.tsx | visual-extraction/components/spacing/ | Visual rendering |
| TypographyInspector.tsx | visual-extraction/components/typography/ | Visual rendering |
| ShadowInspector.tsx | visual-extraction/components/shadow/ | Visual rendering |
| ImageUploader.tsx | components/ | App infrastructure |
| MetricsOverview.tsx | components/ | App infrastructure |

**See full 44-component mapping in analysis above**

---

## 🚀 Next Session Plan

### **Before Next Session:**
1. Review this document
2. Review existing architecture docs:
   - `MODULAR_TOKEN_PLATFORM_VISION.md`
   - `STRATEGIC_VISION_AND_ARCHITECTURE.md`
   - `COMPONENT_REFACTORING_ROADMAP.md`
3. Decide on Phase 1 approach

### **Next Session Start:**
1. Create `TokenVisualAdapter` interface (30 min)
2. Create `ColorVisualAdapter` implementation (1 hour)
3. Refactor `TokenCard` to use adapters (1 hour)
4. Test that color tokens still render (30 min)

**Estimated Time:** 3-4 hours for Phase 1, Day 1-2

---

## 🎯 Success Metrics

### Phase 1 Goals:
- ✅ 8 shared components in `shared/`
- ✅ Adapter interface defined
- ✅ ColorVisualAdapter working
- ✅ TokenCard refactored
- ✅ All tests passing

### Ultimate Goals:
- 44 → 20 root components (55% reduction)
- Audio/video tokens supported (multimodal)
- Zero cross-feature dependencies
- 100% test pass rate maintained

---

**Document Version:** 1.0
**Last Updated:** 2025-12-09
**Next Update:** After Phase 1 implementation
