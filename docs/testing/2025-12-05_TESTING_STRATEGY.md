# Comprehensive Testing Strategy - Copy That

**Last Updated:** 2025-12-05
**Phase:** 1 - Tier 1 Hook Tests ✅ COMPLETE

---

## Executive Summary

Systematic approach to building comprehensive test coverage:

- ✅ **Unit tests** for 34 custom hooks (Phase 1: 108 tests complete)
- 🟡 **Schema validation tests** for data integrity (Phase 2)
- 🟡 **Visual regression tests** using Playwright (Phase 3)
- 🟡 **E2E tests** for critical user flows (Phase 4)
- 🟡 **Performance tests** and CI/CD integration (Phase 5)

**Current Infrastructure:**
- ✅ Vitest + React Testing Library + JSDOM
- ✅ Playwright E2E (14 spec files)
- ✅ Hook testing utilities (`frontend/src/test/hookTestUtils.ts`)
- ✅ 108+ Tier 1 hook tests running

---

## 1. Testing Strategy by Layer

### 1.1 Unit Tests for Custom Hooks

**Scope:** All 34 custom hooks across the codebase

**Approach:**
- Use `@testing-library/react` renderHook utility
- Test hook logic independently of components
- Mock external dependencies (API calls, store updates)
- Use `act()` for state updates
- Test both sync and async hooks

**Tier System:**
1. **Tier 1 (Critical)** ✅ COMPLETE: Extraction/color/harmony hooks (108 tests)
2. **Tier 2 (High)** 🟡 Planned: State management hooks (12 hooks, ~100 tests)
3. **Tier 3 (Medium)** 🟡 Planned: Utility hooks (14 hooks, ~80 tests)

**Example Pattern:**
```typescript
import { renderHook, act } from '@testing-library/react'
import { useMyHook } from './useMyHook'

describe('useMyHook', () => {
  it('should initialize with default values', () => {
    const { result } = renderHook(() => useMyHook())
    expect(result.current.value).toBe(initialValue)
  })

  it('should update state when action is called', async () => {
    const { result } = renderHook(() => useMyHook())
    await act(async () => {
      result.current.updateValue(newValue)
    })
    expect(result.current.value).toBe(newValue)
  })
})
```

### 1.2 Schema Validation Tests

**Scope:** All Zod schemas and data validation

**Files to Test:**
- `frontend/src/types/**/*.zod.ts` (generated from JSON schemas)
- API response validation
- Form data validation
- Token schema validation (20+ schemas)

**Example Pattern:**
```typescript
describe('ColorTokenSchema validation', () => {
  it('should validate correct color token', () => {
    const valid = { hex: '#FF0000', confidence: 0.95 }
    expect(ColorTokenSchema.safeParse(valid).success).toBe(true)
  })

  it('should reject invalid hex format', () => {
    const invalid = { hex: 'not-hex', confidence: 0.95 }
    expect(ColorTokenSchema.safeParse(invalid).success).toBe(false)
  })
})
```

### 1.3 Component Integration Tests

**Scope:**
- Refactored components (5+ components)
- Key UI components (image uploader, token display, etc.)
- Component composition and prop passing

**Approach:** Test component behavior with mocked hooks and stores

**Example Pattern:**
```typescript
describe('ColorTokenDisplay', () => {
  it('should render token with extracted colors', () => {
    const colors = [{ hex: '#FF0000', name: 'red' }]
    render(<ColorTokenDisplay colors={colors} />)
    expect(screen.getByText('red')).toBeInTheDocument()
  })
})
```

### 1.4 Visual Regression Tests

**Tool:** Playwright with visual comparisons

**Scope:**
- Component snapshots at different viewport sizes
- Dark/light mode rendering
- State variations (loading, error, success)
- Accessibility features

**Example Pattern:**
```typescript
test('ColorDisplay should match snapshot', async ({ page }) => {
  await page.goto('/color-display')
  await expect(page.locator('.color-display')).toHaveScreenshot()
})
```

### 1.5 E2E Tests for Critical Flows

**Current:** 14 Playwright spec files

**Coverage:**
- ✅ Homepage loading
- ✅ Image extraction workflow
- ✅ Token display and interaction
- ✅ Export functionality
- ✅ Layout responsiveness

**Gaps to Fill:**
- Error handling (invalid inputs, network errors)
- Cross-browser compatibility (Firefox, Safari)
- Accessibility (ARIA labels, keyboard navigation)

---

## 2. Test Coverage Progress

### Phase 1: Tier 1 Hook Tests ✅ COMPLETE

```
✅ useColorConversion            32 tests | frontend/src/components/color-science/__tests__/hooks.test.ts
✅ useContrastCalculation        14 tests | frontend/src/components/color-science/__tests__/hooks.test.ts
✅ useImageFile                  12 tests | frontend/src/components/image-uploader/__tests__/hooks-tier1.test.ts
✅ useStreamingExtraction        10 tests | frontend/src/components/image-uploader/__tests__/hooks-tier1.test.ts
✅ usePaletteAnalysis            18 tests | frontend/src/components/overview-narrative/__tests__/hooks-tier1.test.ts
✅ useArtMovementClassification  22 tests | frontend/src/components/overview-narrative/__tests__/hooks-tier1.test.ts

Total: 108 tests ✅ ALL PASSING
```

**Infrastructure Created:**
- ✅ `frontend/src/test/hookTestUtils.ts` - Reusable test utilities
  - QueryClient wrapper for React Query hooks
  - Mock API response factories
  - Mock store state helpers
  - Hook assertion patterns
  - Async test helpers

### Phase 2: Schema Validation Tests 🟡 PLANNED

- Color token schemas (20 tests)
- Component token schemas (30 tests)
- Data integrity validation (15 tests)
- **Target:** 50+ tests

### Phase 3: Visual Regression Tests 🟡 PLANNED

- Component visual baselines
- Responsive design tests
- Theme variation tests
- **Target:** 50+ visual snapshots

### Phase 4: E2E Coverage Expansion 🟡 PLANNED

- Existing: 14 spec files (~20% coverage)
- Target: 80% user flow coverage
- **Target:** 20+ new E2E tests

### Phase 5: Performance & Load Testing 🟡 PLANNED

- Lighthouse CI integration
- Load testing (Locust)
- Performance budgets
- **Target:** Performance baselines established

---

## 3. Test Coverage Goals

| Layer | Current | Target | Priority |
|-------|---------|--------|----------|
| Hooks | ✅ 108 tests | 290+ tests | CRITICAL ✅ |
| Schemas | 0 tests | 95%+ | HIGH |
| Components | ~30 tests | 70%+ | MEDIUM |
| Integration | ~10 tests | 60%+ | MEDIUM |
| E2E | 14 specs | Critical flows | MEDIUM |
| Visual | 0 baselines | 50+ baselines | MEDIUM |

---

## 4. Test Execution

### Quick Commands

```bash
# All tests
pnpm test:run

# Specific suites
pnpm test:hooks       # Hook unit tests
pnpm test:schemas     # Schema validation
pnpm test:components  # Component tests
pnpm test:e2e         # E2E tests

# Watch mode
pnpm test

# Interactive UI
pnpm test:ui

# Coverage report
pnpm test:coverage
```

### Test Scripts (package.json)

```json
{
  "test": "vitest",
  "test:run": "vitest --run",
  "test:ui": "vitest --ui",
  "test:coverage": "vitest --coverage",
  "test:hooks": "vitest --run src/**/hooks/__tests__",
  "test:schemas": "vitest --run src/types/__tests__",
  "test:components": "vitest --run src/components/__tests__",
  "test:e2e": "playwright test",
  "test:e2e:debug": "playwright test --debug",
  "test:visual": "playwright test --update-snapshots",
  "test:all": "vitest --run && playwright test",
  "test:ci": "vitest --run --coverage && playwright test"
}
```

---

## 5. Testing Standards & Patterns

### 5.1 Unit Test Template

```typescript
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { renderHook, act } from '@testing-library/react'
import { useMyHook } from './useMyHook'

describe('useMyHook', () => {
  beforeEach(() => {
    // Reset mocks, setup fixtures
  })

  afterEach(() => {
    vi.clearAllMocks()
  })

  describe('happy path', () => {
    it('should initialize with correct state', () => {
      const { result } = renderHook(() => useMyHook())
      expect(result.current.value).toBeDefined()
    })
  })

  describe('error handling', () => {
    it('should handle errors gracefully', async () => {
      const { result } = renderHook(() => useMyHook())
      // Test error handling
    })
  })

  describe('edge cases', () => {
    it('should handle null/undefined inputs', () => {
      const { result } = renderHook(() => useMyHook(null))
      expect(result.current).toBeDefined()
    })
  })
})
```

### 5.2 Naming Conventions

```
Hooks:      useFeature.test.ts
Schemas:    schema.validation.test.ts
Components: Component.integration.test.tsx
E2E:        feature-workflow.spec.ts
Visual:     component.visual.spec.ts
```

---

## 6. Playwright Configuration

### Multi-Browser Setup

```typescript
projects: [
  {
    name: 'chromium',
    use: { ...devices['Desktop Chrome'] }
  },
  {
    name: 'firefox',
    use: { ...devices['Desktop Firefox'] }
  },
  {
    name: 'webkit',
    use: { ...devices['Desktop Safari'] }
  }
]
```

### Accessibility Testing

```bash
pnpm add -D @axe-core/playwright
```

```typescript
import { injectAxe, checkA11y } from '@axe-core/playwright'

test('should pass accessibility check', async ({ page }) => {
  await page.goto('/color-display')
  await injectAxe(page)
  await checkA11y(page)
})
```

---

## 7. Coverage Measurement

**Vitest Configuration (vite.config.ts):**

```typescript
test: {
  coverage: {
    provider: 'v8',
    reporter: ['text', 'json', 'html', 'lcov'],
    exclude: [
      'node_modules/',
      'frontend/src/test/',
      '**/*.d.ts',
      '**/*.config.*'
    ],
    branches: 70,
    lines: 75,
    functions: 75,
    statements: 75
  }
}
```

---

## 8. GitHub Actions CI/CD

### Test Workflow

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: pnpm/action-setup@v2
      - uses: actions/setup-node@v3
        with:
          node-version: 18
          cache: 'pnpm'

      - run: pnpm install
      - run: pnpm test:run --coverage
      - run: pnpm test:e2e

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage/coverage-final.json
```

---

## 9. Resources & References

### Documentation
- [Vitest Documentation](https://vitest.dev)
- [React Testing Library](https://testing-library.com/react)
- [Playwright Testing](https://playwright.dev/docs/intro)

### Example Test Files
- `frontend/src/components/color-science/__tests__/hooks.test.ts` (comprehensive)
- `frontend/src/components/image-uploader/__tests__/hooks-tier1.test.ts` (patterns)
- `frontend/tests/playwright/extraction.spec.ts` (E2E example)

---

## 10. Success Metrics

### Quantitative

| Metric | Current | Target | Status |
|--------|---------|--------|--------|
| Hook test coverage | 108 | 290+ | ✅ Phase 1 |
| Schema test coverage | 0 | 95%+ | 🟡 Phase 2 |
| E2E test count | 14 | 25+ | 🟡 Phase 4 |
| Component test count | 30 | 50+ | 🟡 Phase 3 |
| Visual baselines | 0 | 50+ | 🟡 Phase 3 |
| Code coverage overall | ? | 75%+ | 🟡 Phase 5 |

### Qualitative

- Regression prevention through automated testing
- Developer confidence in refactoring
- Tests as living documentation
- 50%+ reduction in bug fix time

---

## 11. Known Issues & Constraints

### Limitations

1. **Limited browser support** - Need Firefox/Safari (currently Chrome only in E2E)
2. **No visual baselines** - Need to establish and maintain snapshots
3. **Slow E2E tests** - Consider parallelization for large suites
4. **No accessibility testing** - axe-core integration needed

### Mitigation Strategies

- Use test parallelization to speed up E2E
- Implement test result caching
- Use mock servers for deterministic E2E tests
- Establish visual diff thresholds to avoid flaky tests

---

## 12. Next Steps

### Immediate (Week of 2025-12-05)
- ✅ Complete Tier 1 hook tests (done)
- Fix remaining test assertions
- Run full test suite with coverage

### Week 2 (Phase 2)
- Implement schema validation tests (50+ tests)
- Setup coverage measurement
- Create schema test documentation

### Week 3-4 (Phase 3-4)
- Establish visual regression baselines
- Expand E2E coverage to 25+ tests
- Add accessibility tests

### Week 5+ (Phase 5)
- CI/CD integration with GitHub Actions
- Performance testing setup
- Team training on new test infrastructure

---

**Document Version:** 2.0
**Last Updated:** 2025-12-05
**Status:** Phase 1 Complete, Phase 2 Ready
