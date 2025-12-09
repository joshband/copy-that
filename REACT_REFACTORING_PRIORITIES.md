# React Refactoring Priorities
**Quick Reference Guide**

## Critical Issues Found

### 1. App.tsx Anti-Pattern (646 lines)
- **Problem:** 25+ useState hooks, 80+ imports, god component
- **Impact:** Every state change re-renders entire app
- **Fix:** Decompose into feature containers + route splitting

### 2. State Management Chaos
- **Problem:** 3 competing Zustand stores (tokenStore, tokenGraphStore, shadowStore)
- **Impact:** Duplicate data, manual sync, race conditions
- **Fix:** Unified feature slices pattern

### 3. Tight Component Coupling
- **Problem:** Direct store imports in components
- **Impact:** 35/100 reusability score, untestable
- **Fix:** Props-first pattern + facade hooks

### 4. Zero Error Boundaries
- **Problem:** Any error crashes entire app
- **Impact:** White screen of death, lost work
- **Fix:** Layered ErrorBoundary components

---

## Quick Wins (This Week)

### 1. Add Top-Level ErrorBoundary (1 hour)
```typescript
// Prevents app crashes
<ErrorBoundary fallback={<AppCrashFallback />}>
  <App />
</ErrorBoundary>
```

### 2. Extract EmptyState Component (2 hours)
```typescript
// Replace 12+ duplicate implementations
<EmptyState icon="🎨" title="No colors yet" />
```

### 3. Create useUIState Hook (2 hours)
```typescript
// Consolidate 6+ UI-only useState calls
const { activeTab, setActiveTab, showDebug, setShowDebug } = useUIState()
```

### 4. Add useMemo to Expensive Computations (3 hours)
```typescript
// Prevent unnecessary re-renders
const colorDisplay = useMemo(() => {
  // transformation logic
}, [colors, graphColors])
```

### 5. Performance Monitoring (2 hours)
```typescript
// Identify re-render hotspots
useRenderCount('ColorTokenDisplay')
```

**Total Time:** 10 hours
**Impact:** Immediate stability + performance improvement

---

## 6-Week Refactoring Plan

### Week 1: Foundation
- [ ] New folder structure (features/, components/)
- [ ] Unified Zustand store
- [ ] 10 primitive components (Button, Card, EmptyState, Tabs)
- [ ] ErrorBoundary infrastructure

### Week 2: Color Feature Migration
- [ ] colorSlice + useColors() hook
- [ ] ColorTokenDisplay props-first refactor
- [ ] ColorExplorer container
- [ ] 20+ unit tests

### Week 3: Spacing + Typography
- [ ] spacingSlice + typographySlice
- [ ] Feature folder extraction
- [ ] 30+ additional tests
- [ ] Delete legacy stores

### Week 4: App.tsx Decomposition
- [ ] Extract upload to features/upload/
- [ ] AppLayout component
- [ ] Lazy-loaded routes
- [ ] App.tsx < 150 lines

### Week 5: Performance + Testing
- [ ] React.memo on pure components
- [ ] Virtual scrolling
- [ ] 80% test coverage
- [ ] E2E test suite

### Week 6: Documentation + Cleanup
- [ ] Storybook for primitives
- [ ] Architecture decision records
- [ ] Delete old code
- [ ] Final review

---

## Recommended Architecture

```
src/
├── components/              # Shared primitives
│   ├── Button/
│   ├── Card/
│   ├── EmptyState/
│   └── Tabs/
│
├── features/               # Domain-driven features
│   ├── colors/
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── store/
│   │   └── api/
│   ├── spacing/
│   ├── typography/
│   └── upload/
│
├── store/
│   └── index.ts            # Unified store
│
└── api/
    ├── client.ts
    └── endpoints/
```

---

## Success Metrics

| Metric | Current | Target |
|--------|---------|--------|
| App.tsx LOC | 646 | < 100 |
| Component Reusability | 35/100 | 85/100 |
| Test Coverage | 19% | 85% |
| Zustand Stores | 3 | 1 |
| Re-renders per Action | ~50 | ~5 |

---

## Full Review Document

See: `/docs/sessions/REACT_ARCHITECTURE_REVIEW_2025_12_09.md`

**Sections:**
1. React Patterns Audit (what's working, anti-patterns)
2. Component Architecture Analysis
3. State Management Refactoring Plan
4. Performance Optimization
5. Error Boundaries & Resilience
6. Testing Strategy
7. Code Quality Improvements
8. Migration Roadmap
9. Quick Wins (This Week)
10. Long-Term Vision

**Length:** 850+ lines, 35+ code examples
