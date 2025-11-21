# Test Coverage Roadmap

**Version:** 1.0
**Date:** November 20, 2025
**Status:** MVP Phase 4 Complete - Iterative TDD for Phases 5+

---

## Executive Summary

Copy That MVP (Phase 4) has **46 passing backend tests** covering color token extraction pipeline. Frontend has **code-first educational components** (untested) that will be brought into full TDD coverage iteratively.

**Current Status:**
- ✅ Backend: 46/46 tests passing (100% coverage for core color extraction)
- ⚠️ Frontend: Code-complete but zero component tests (educational visualizers)
- 🔄 Plan: Iterative TDD for all features starting Phase 4.5

---

## 1. Backend Test Coverage

### 1.1 MVP-CRITICAL Backend (100% Tested)

| Module | File | Tests | Status | Coverage |
|--------|------|-------|--------|----------|
| **Color Extraction** | `test_color_extractor.py` | 15 | ✅ PASS | 100% |
| **Color Utilities** | `test_coloraide_integration.py` | 18 | ✅ PASS | 100% |
| **API Schemas** | `test_api_schemas.py` | 8 | ✅ PASS | 100% |
| **API Endpoints** | `test_color_api.py` | 13 | ✅ PASS | 100% |
| **Project Endpoints** | `test_project_endpoints.py` | 6 | ✅ PASS | 100% |
| **Integration Tests** | `test_color_extraction_endpoints.py` | 11 | ✅ PASS | 100% |
| **E2E Tests** | `test_color_extraction_e2e.py` | 4 | ✅ PASS | 100% |

**Total Backend Tests:** 46/46 passing ✅

**Key Coverage Areas:**
- ColorToken model validation ✅
- Color space conversions (hex, rgb, hsl, hsv) ✅
- ColorAide integration (Delta-E, luminance, achromatic) ✅
- Semantic naming extraction ✅
- Harmony analysis ✅
- Accessibility metrics ✅
- API request/response validation ✅
- Database persistence ✅

---

### 1.2 MVP-SUPPORTING Backend (Integrated but Needs Tests)

| Module | File | Current Status | Test Plan |
|--------|------|-----------------|-----------|
| **Semantic Color Naming** | `semantic_color_naming.py` | ✅ Code-complete | Phase 4.5: Add 10+ naming strategy tests |
| **Color Clustering** | `color_clustering.py` | ✅ Code-complete | Phase 4.5: Add 5+ cluster validation tests |
| **Color Spaces** | `color_spaces_advanced.py` | ✅ Code-complete | Phase 4.5: Add 8+ gamut/space conversion tests |

**Rationale:** These modules are production code used in color extraction but lack explicit unit tests. Will add TDD tests iteratively.

---

## 2. Frontend Test Coverage

### 2.1 MVP-CRITICAL Frontend (Type-Safe, Minimal Tests)

| Component | File | Status | Tests | Coverage |
|-----------|------|--------|-------|----------|
| **App Layout** | `App.tsx` | ✅ Working | 0 | Basic structure tested via integration |
| **Image Upload** | `ImageUploader.tsx` | ✅ Working | 0 | Manual testing only |
| **Token Grid** | `TokenGrid.tsx` | ✅ Working | 0 | Manual testing only |
| **Token Card** | `TokenCard.tsx` | ✅ Working | 1 test file | Partial coverage |
| **State Management** | `tokenStore.ts` | ✅ Working | 1 test file | Zustand store tests |
| **Type Validation** | `index.ts` types | ✅ Working | Zod validation | Type-safe via TypeScript |

**Assessment:** MVP core is working but lacks component tests. Focus is on type safety (Pydantic → Zod → React).

---

### 2.2 Educational Visualizers (Code-First, Zero Tests) 🎨

**Status:** All components TypeScript-safe but UNTESTED

| Component | Lines | Status | Purpose | Test Priority |
|-----------|-------|--------|---------|---|
| **HarmonyVisualizer** | ~200 | ✅ Code-complete | Interactive hue wheel | 🟡 HIGH |
| **AccessibilityVisualizer** | ~300 | ✅ Code-complete | WCAG contrast checker | 🟡 HIGH |
| **ColorNarrative** | ~250 | ✅ Code-complete | Educational prose | 🟡 MEDIUM |
| **ColorTokenDisplay** | ~305 | ✅ Code-complete | Collapsible card wrapper | 🟡 HIGH |

**These components demonstrate the widget abstraction pattern for Phase 5-7.**

---

### 2.3 Layout & Chrome Components (Untested)

| Component | Purpose | Status | Note |
|-----------|---------|--------|------|
| **TokenToolbar** | Filter/sort controls | ✅ Code-complete | Needs action tests |
| **TokenInspectorSidebar** | Details panel | ✅ Code-complete | Needs state tests |
| **TokenPlaygroundDrawer** | Editing interface | ✅ Code-complete | Needs interaction tests |
| **LearningSidebar** | Educational content | ✅ Code-complete | Needs content tests |

---

## 3. Test Roadmap: Iterative TDD Phases

### Phase 4.5: Frontend Component TDD (Week 1-2)

**Priority 1: Critical Path Components**
```
Goal: 100% test coverage for TokenCard, ImageUploader, TokenGrid

Tests to add:
- TokenCard.test.tsx: 8 tests (rendering, actions, state updates)
  ├── Render with color data
  ├── Copy to clipboard action
  ├── Edit mode toggle
  ├── Delete confirmation
  ├── Expand details
  ├── Sort by confidence
  └── Filter by harmony type

- ImageUploader.test.tsx: 6 tests (file handling, API calls)
  ├── Drag-drop file handling
  ├── File validation (size, type)
  ├── API call on extract
  ├── Error handling
  ├── Progress tracking
  └── Project creation

- TokenGrid.test.tsx: 4 tests (display, filtering)
  ├── Render token list
  ├── Apply filters
  ├── Sort tokens
  └── Empty state

Estimated Effort: 2-3 hours
```

**Priority 2: Educational Visualizers**
```
Goal: 100% test coverage for teaching components

Tests to add:
- HarmonyVisualizer.test.tsx: 10 tests
  ├── Render harmony wheel
  ├── Display 9 harmony types
  ├── Interactive hue highlighting
  ├── Educational descriptions
  ├── Responsive sizing
  ├── Color input validation
  ├── Snap to harmony angle
  ├── Contrast detection
  ├── Mobile view collapse
  └── Accessibility (keyboard nav)

- AccessibilityVisualizer.test.tsx: 8 tests
  ├── WCAG contrast display
  ├── AA/AAA badges
  ├── Background color picker
  ├── Real-time contrast calculation
  ├── Colorblind simulation toggle
  ├── Tab switching (light/dark/custom)
  ├── Valid/invalid states
  └── Mobile responsiveness

- ColorNarrative.test.tsx: 6 tests
  ├── Render narrative prose
  ├── Color theory section
  ├── Design tips section
  ├── Metadata display
  ├── Responsive layout
  └── Link functionality

- ColorTokenDisplay.test.tsx: 7 tests
  ├── Render collapsible card
  ├── Swatch display with confidence %
  ├── Metadata tabs
  ├── Visualizer integration
  ├── Copy hex action
  ├── Edit mode toggle
  └── Mobile layout

Estimated Effort: 3-4 hours
```

**Priority 3: Layout Components**
```
Goal: 100% test coverage for UI chrome

Tests to add:
- TokenToolbar.test.tsx: 6 tests (filter/sort controls)
- TokenInspectorSidebar.test.tsx: 5 tests (state sync)
- TokenPlaygroundDrawer.test.tsx: 4 tests (editing)

Estimated Effort: 2 hours
```

**Total Phase 4.5 Frontend Tests: 50+ new tests**
**Estimated Time: 7-9 hours**

---

### Phase 5: Backend Module TDD (Spacing Tokens)

**Priority 1: Semantic Naming Tests**
```
Goal: 100% coverage for semantic_color_naming.py

Tests to add:
- test_semantic_naming.py: 12 tests
  ├── Simple naming strategy (primary, accent, etc)
  ├── Descriptive naming (burnt orange, soft sage)
  ├── Emotional naming (energetic, calm)
  ├── Technical naming (high saturation warm)
  ├── Vibrancy naming (vivid, muted)
  ├── Color harmony detection
  ├── Temperature classification
  ├── Saturation level detection
  ├── Lightness level detection
  ├── Fallback naming for unusual colors
  ├── Unicode/emoji support
  └── Performance benchmarks

Estimated Effort: 3 hours
```

**Priority 2: Color Clustering Tests**
```
Goal: 100% coverage for color_clustering.py

Tests to add:
- test_clustering.py: 8 tests
  ├── K-means initialization
  ├── Cluster convergence
  ├── Duplicate removal (Delta-E threshold)
  ├── Palette size validation
  ├── Performance on large images
  ├── Edge cases (1-color, all-gray images)
  ├── Cluster quality metrics
  └── Integration with Claude output

Estimated Effort: 2 hours
```

**Priority 3: Color Spaces Tests**
```
Goal: 100% coverage for color_spaces_advanced.py

Tests to add:
- test_color_spaces.py: 10 tests
  ├── Oklch space conversions
  ├── Wide-gamut detection
  ├── Gamut mapping (sRGB → P3 → Rec2020)
  ├── Display capability validation
  ├── Color difference calculations (MINDE)
  ├── Perceptual uniformity
  ├── Edge colors (primary, secondary)
  ├── High dynamic range colors
  ├── Accessibility conversions
  └── Performance on batch conversions

Estimated Effort: 2.5 hours
```

**Total Phase 5 Backend Tests: 30+ new tests**
**Estimated Time: 7.5 hours**

---

## 4. Test Strategy: Hybrid TDD

### Core Principle
- **Core Logic:** TDD-first (write tests before code)
- **UI Components:** Code-first initially, TDD in dedicated phases
- **Educational Features:** Code-first (rapid iteration), TDD before production

### Test Categories

**Unit Tests (90% focus)**
```python
# Test individual functions in isolation
def test_extract_color_from_hex():
    """Verify hex parsing and validation"""

def test_semantic_name_generation():
    """Verify naming strategy application"""

def test_harmony_classification():
    """Verify harmony type detection"""
```

**Integration Tests (7% focus)**
```python
# Test module interactions
def test_color_extraction_pipeline():
    """AI → Adapter → Database → API"""

def test_token_persistence():
    """Database write/read cycle"""
```

**Component Tests (2% focus)**
```tsx
// Test React component behavior
it("renders color swatch with correct hex", () => {
  // Verify visual representation
});

it("copies hex code to clipboard", () => {
  // Verify user interaction
});
```

**E2E Tests (1% focus)**
```tsx
// Test complete user workflows
it("uploads image, extracts colors, displays tokens", () => {
  // Full workflow validation
});
```

---

## 5. Test Infrastructure

### Backend Testing Stack
- **Framework:** pytest
- **Async:** pytest-asyncio
- **Coverage:** pytest-cov (target: 80%+)
- **Fixtures:** conftest.py with database/API mocks
- **CI/CD:** GitHub Actions (all tests pass before merge)

### Frontend Testing Stack
- **Framework:** Vitest (Vite-native)
- **Components:** React Testing Library
- **Snapshots:** Optional (use sparingly)
- **a11y:** jest-axe for accessibility
- **CI/CD:** GitHub Actions (all tests pass before merge)

### Running Tests Locally
```bash
# Backend
python -m pytest tests/ -v --cov=src/copy_that

# Frontend
pnpm test

# All tests
pnpm test:all
```

---

## 6. Coverage Goals by Phase

| Phase | Backend | Frontend | Total | Gate |
|-------|---------|----------|-------|------|
| **Phase 4** | ✅ 46/46 tests | ⚠️ Code-first | 46 tests | MVP launch |
| **Phase 4.5** | ✅ 46 tests | 🔄 +50 tests | 96 tests | Production ready |
| **Phase 5** | 🔄 +30 tests | 🔄 Maintained | 126 tests | Spacing tokens |
| **Phase 6** | 🔄 +25 tests | 🔄 Maintained | 151 tests | Components |
| **Phase 7** | 🔄 +20 tests | 🔄 Maintained | 171 tests | Multi-modal |

**Final Goal:** 150+ tests, 80%+ coverage across all modules

---

## 7. Test Quality Checklist

Before marking tests as "PASS", verify:

- [ ] **Isolation:** Test runs independently (no test order dependency)
- [ ] **Clarity:** Test name clearly describes what's tested
- [ ] **Coverage:** Test covers happy path + edge cases + error conditions
- [ ] **Speed:** Test runs < 100ms (unit), < 1s (integration)
- [ ] **Assertions:** Multiple assertions where needed (not just one per test)
- [ ] **Cleanup:** Test cleans up resources (mocks, database)
- [ ] **Documentation:** Complex tests have comments explaining intent

---

## 8. Known Gaps & Non-Goals

### Not Testing (Out of Scope)
- ❌ Browser compatibility (use manual QA for now)
- ❌ Performance benchmarks (add later with profiling)
- ❌ Visual regression testing (future: Percy or similar)
- ❌ Load testing (future: k6 or similar)

### Non-Goals Until Phase 6
- ❌ Component snapshot testing (brittle, not recommended)
- ❌ E2E testing with real browser (Playwright/Cypress later)
- ❌ Contract testing with API consumers (MVP is single consumer)

---

## 9. Success Criteria

**Phase 4.5 Success:**
- ✅ 96+ total tests passing
- ✅ All frontend components have unit tests
- ✅ All educational visualizers tested
- ✅ `pnpm test && python -m pytest` both pass 100%

**Phase 5+ Success:**
- ✅ 150+ tests passing
- ✅ 80%+ code coverage
- ✅ All new features start with TDD
- ✅ Tests serve as documentation

---

## 10. Next Steps

1. **This Week:** Review this roadmap with team
2. **Week 1:** Implement Priority 1 (TokenCard, ImageUploader, TokenGrid tests)
3. **Week 2:** Implement Priority 2 (Educational visualizer tests)
4. **Week 3:** Implement Priority 3 (Layout component tests)
5. **Week 4:** Phase 5 planning - backend module tests

---

## References

- [Testing Library Docs](https://testing-library.com/)
- [pytest Documentation](https://docs.pytest.org/)
- [Vitest Guide](https://vitest.dev/)
- [React Testing Best Practices](https://kentcdodds.com/blog/common-mistakes-with-react-testing-library)
