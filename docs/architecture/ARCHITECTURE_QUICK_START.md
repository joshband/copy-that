# Architecture Quick Start Guide

**Last Updated:** 2025-12-09
**Purpose:** 5-minute primer on Copy That multimodal architecture
**For:** Developers starting next session

---

## The Big Picture (30 seconds)

**Copy That** extracts design tokens from images (current) and will support audio/video/text (future). Architecture uses:

1. **Token Graph** - All tokens stored as graph with relationships (working)
2. **Feature Modules** - Organized by modality (visual, audio, video) not token type
3. **Adapter Pattern** - Generic components render any token type via pluggable adapters
4. **W3C Tokens** - Industry standard format with references (`{color.primary}`)

---

## Key Architectural Decisions (1 minute)

### Decision #1: Feature Names = Modalities

❌ **Wrong:** `features/color-extraction/` (color is not a modality)
✅ **Right:** `features/visual-extraction/components/color/` (visual IS the modality)

**Why:** Visual extraction produces 30+ token types (color, spacing, typography, shadows, borders, opacity, etc.). Creating 30+ features would be chaos.

### Decision #2: Adapters for Rendering

**Problem:** How do generic components (TokenCard, TokenTable) render different token types without hardcoding logic?

**Solution:** Visual Adapter Pattern
```typescript
// Generic component delegates to adapter
function TokenCard({ token }: { token: TokenNode }) {
  const adapter = getAdapter(token.category)  // Auto-select
  return <div>{adapter.renderSwatch(token)}</div>
}

// Color adapter implements rendering
const ColorVisualAdapter = {
  category: 'color',
  renderSwatch: (token) => <div style={{ backgroundColor: token.hex }} />
}
```

**Why:** Adding audio tokens requires creating `AudioVisualAdapter` - zero changes to shared components.

### Decision #3: Graph-First Data Model

All tokens stored as directed graph (not flat arrays):
```typescript
const graph = useTokenGraph()
graph.getNode('color.primary')           // Get single token
graph.getAliases('color.primary')        // What aliases this?
graph.getDependents('color.primary')     // What uses this?
```

**Why:** Enables relationship queries ("where is this color used?"), supports cross-modal dependencies, scales to 1000+ tokens.

---

## Directory Structure (1 minute)

```
src/
├── features/                    # Feature modules (by modality)
│   └── visual-extraction/       # Visual modality (images)
│       ├── components/
│       │   ├── color/          # 12 color components
│       │   ├── spacing/        # 8 spacing components
│       │   ├── typography/     # 5 typography components
│       │   └── shadow/         # 2 shadow components
│       ├── adapters/           # Visual rendering adapters
│       │   ├── ColorVisualAdapter.ts
│       │   ├── SpacingVisualAdapter.ts
│       │   ├── TypographyVisualAdapter.ts
│       │   └── ShadowVisualAdapter.ts
│       └── hooks/              # Feature-specific hooks
│
├── shared/                      # Token-agnostic components
│   ├── components/             # Generic UI (TokenCard, TokenTable, etc.)
│   ├── hooks/                  # useTokenGraph (11 methods, 17 tests passing)
│   ├── adapters/               # Adapter interface definition
│   └── types/
│
├── components/                  # App-level infrastructure
│   ├── MetricsOverview/
│   ├── SessionCreator/
│   └── ...
│
└── store/
    ├── tokenGraphStore.ts      # ✅ Graph store (production, multimodal-ready)
    └── tokenStore.ts           # ⚠️ Legacy (deprecate after migration)
```

---

## Working Implementation (1 minute)

### Token Graph (Production, Tested)

**Location:** `src/store/tokenGraphStore.ts` + `src/shared/hooks/useTokenGraph.ts`

**Status:** ✅ 17 tests passing

**Usage:**
```typescript
import { useTokenGraph } from '@/shared/hooks/useTokenGraph'

function MyComponent() {
  const graph = useTokenGraph()

  // Get tokens
  const colors = graph.getNodes('color')         // All color tokens
  const primary = graph.getNode('color.primary') // Single token

  // Find relationships
  const aliases = graph.getAliases('color.primary')      // Tokens aliasing this
  const dependencies = graph.getDependencies('shadow.card') // What it depends on
  const dependents = graph.getDependents('color.primary')  // What depends on it

  // Resolve references
  const resolved = graph.resolveAlias('color.button')    // Follow alias chain
}
```

**11 Methods Available:**
- `getNode()`, `getNodes()`, `getAllNodes()`
- `getAliases()`, `getDependencies()`, `getDependents()`
- `resolveAlias()`, `resolveReferences()`
- `getRootTokens()`, `getLeafTokens()`
- `hasToken()`, `getTokensByIds()`

---

## Migration Status (30 seconds)

**Current State:**
- ✅ Token graph working (17 tests passing)
- ✅ 44 components (flat, disorganized)
- ✅ 4 token types (color, spacing, typography, shadow)
- ❌ No adapter pattern yet
- ❌ Components scattered in root

**Target State (4 weeks):**
- ✅ Adapter pattern implemented
- ✅ 8 shared components (token-agnostic)
- ✅ 27 visual components (organized by type)
- ✅ 6 infrastructure components (root level)
- ✅ Multimodal-ready architecture

---

## 4-Phase Migration Plan (1 minute)

### Phase 1: Foundation (Week 1)
**Goal:** Create adapter pattern
**Tasks:** Adapter interface → ColorVisualAdapter → Refactor TokenCard
**Effort:** 24 hours

### Phase 2: Visual Consolidation (Week 2)
**Goal:** Move all visual components to features/
**Tasks:** Move 27 components to visual-extraction/components/{color,spacing,typography,shadow}/
**Effort:** 24 hours

### Phase 3: Adapter Extraction (Week 3)
**Goal:** Create all visual adapters
**Tasks:** SpacingVisualAdapter → TypographyVisualAdapter → ShadowVisualAdapter
**Effort:** 24 hours

### Phase 4: Multimodal POC (Week 4)
**Goal:** Prove architecture with audio tokens
**Tasks:** Audio schema → AudioVisualAdapter → Mock audio tokens → Demo
**Effort:** 8 hours

**Total:** ~80 hours (2 weeks full-time)

---

## Key Documents (30 seconds)

**Must Read (in order):**
1. **UNIFIED_MULTIMODAL_ARCHITECTURE.md** - This document (30 min read)
2. **IMPLEMENTATION_CHECKLIST_PHASE_1_4.md** - Step-by-step tasks (15 min)
3. **COMPONENT_MIGRATION_MATRIX.md** - What goes where (5 min)

**Reference:**
- `TOKEN_GRAPH_DATA_MODEL_2025_12_09.md` - Graph implementation details
- `PLAN_AGENT_MULTIMODAL_ARCHITECTURE_2025_12_09.md` - Adapter pattern design

---

## First 3 Hours Roadmap (Next Session)

**Hour 1: Setup**
- [ ] Read UNIFIED_MULTIMODAL_ARCHITECTURE.md (30 min)
- [ ] Run `pnpm test` to verify baseline (5 min)
- [ ] Run `pnpm typecheck` (5 min)
- [ ] Create feature branch: `git checkout -b feat/multimodal-architecture` (5 min)

**Hour 2: Adapter Interface**
- [ ] Create `shared/adapters/TokenVisualAdapter.ts` (30 min)
- [ ] Create `shared/adapters/registry.ts` (30 min)

**Hour 3: First Adapter**
- [ ] Create `visual-extraction/adapters/ColorVisualAdapter.ts` (1 hour)

**Expected Deliverable:** Adapter pattern foundation working

---

## Critical Rules (30 seconds)

1. ✅ **Test after every change** - `pnpm test`
2. ✅ **Zero TypeScript errors** - `pnpm typecheck`
3. ✅ **Commit after each task** - Clean git history
4. ✅ **Never break working functionality** - App must always work
5. ✅ **Use working implementation** - Don't rewrite tokenGraphStore!

---

## Common Questions (1 minute)

**Q: Why not just add audio extraction to current structure?**
A: Current flat structure (45 root components) doesn't scale. Adding audio = +20 components. Adding video = +25 more. We'd have 90+ root components with no organization.

**Q: Why adapters instead of inheritance?**
A: Composition over inheritance. Adapters enable adding token types without changing shared components. AudioVisualAdapter plugs in with zero changes to TokenCard.

**Q: Why features/visual-extraction not features/color-extraction?**
A: Visual is the modality (input type). Color is a token type within visual modality. Visual extraction produces 30+ token types - we don't want 30+ features.

**Q: Can I still use legacy tokenStore?**
A: Yes, but migrate to `useTokenGraph()` ASAP. `tokenGraphStore` provides backward-compatible methods during transition. Plan to deprecate `tokenStore` by Phase 3.

**Q: What if I break something during migration?**
A: Stop immediately. Run tests. Check TypeScript. Review last commit. Rollback if needed: `git reset --hard HEAD~1`. Don't continue with broken state.

---

## Success Metrics (30 seconds)

**Baseline (Now):**
- 17 tests passing
- 44 components (disorganized)
- 4 token types
- No adapters

**Phase 1 (Week 1):**
- Adapter pattern working
- TokenCard refactored
- 8 shared components

**Phase 2 (Week 2):**
- All components organized
- Clean directory structure
- All imports using path aliases

**Phase 3 (Week 3):**
- 4 visual adapters working
- Generic components domain-agnostic
- All tests passing

**Phase 4 (Week 4):**
- Audio token POC working
- Architecture validated
- Ready for real audio extraction

---

## Troubleshooting (1 minute)

**Tests failing?**
```bash
pnpm test --reporter=verbose
# Look for import errors, missing mocks
```

**TypeScript errors?**
```bash
pnpm typecheck | grep "error TS"
# Check barrel exports, path aliases
```

**Build failing?**
```bash
rm -rf node_modules
pnpm install
pnpm build
```

**Circular imports?**
```bash
# Check barrel exports - don't re-export from other barrels
# Use direct imports in barrel files
```

**App not working?**
```bash
# Clear Vite cache
rm -rf node_modules/.vite
pnpm dev
```

---

## Quick Commands (30 seconds)

```bash
# Start dev server
pnpm dev

# Run all tests
pnpm test

# Run specific test
pnpm test TokenCard.test.tsx

# TypeScript check
pnpm typecheck

# Build
pnpm build

# Create feature branch
git checkout -b feat/multimodal-architecture

# Commit
git add .
git commit -m "feat: Add TokenVisualAdapter interface"

# Push
git push origin feat/multimodal-architecture
```

---

## Next Steps (30 seconds)

**Before next session:**
1. Read UNIFIED_MULTIMODAL_ARCHITECTURE.md (30 min)
2. Read IMPLEMENTATION_CHECKLIST_PHASE_1_4.md (15 min)
3. Review working implementation (tokenGraphStore.ts, useTokenGraph.ts) (10 min)

**First task:**
- Create adapter interface (Task 1.1 in checklist)
- Estimated: 1 hour
- Deliverable: `shared/adapters/TokenVisualAdapter.ts`

**Goal for first session (4 hours):**
- Complete Phase 1, Day 1 (adapter interface + registry)
- Tests passing
- Documentation complete

---

## Resources

**Architecture Docs:**
- `UNIFIED_MULTIMODAL_ARCHITECTURE.md` - Complete architecture spec
- `IMPLEMENTATION_CHECKLIST_PHASE_1_4.md` - Task-by-task guide
- `COMPONENT_MIGRATION_MATRIX.md` - Component mapping

**Working Code:**
- `src/store/tokenGraphStore.ts` - Graph store (don't change!)
- `src/shared/hooks/useTokenGraph.ts` - Graph API (17 tests passing)
- `src/shared/components/TokenGraphDemo.tsx` - Example usage

**Tests:**
- `src/shared/hooks/__tests__/useTokenGraph.test.ts` - 17 tests

---

## Contact & Help

**Stuck?** Review:
1. IMPLEMENTATION_CHECKLIST (step-by-step tasks)
2. Working implementation (tokenGraphStore, useTokenGraph)
3. Test files (see examples)

**Still stuck?** Document:
- What you tried
- Error messages
- Expected vs actual behavior

**Document status feedback in:**
- Session notes
- Commit messages
- Code comments

---

**Document Status:** Quick Reference
**Read Time:** 5 minutes
**Last Updated:** 2025-12-09
**Start Here:** Read this first, then UNIFIED_MULTIMODAL_ARCHITECTURE.md
