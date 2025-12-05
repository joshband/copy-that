# Comprehensive Testing Strategy - Copy That

## Executive Summary

This document outlines a systematic approach to building comprehensive test coverage across the project, focusing on:
- **Unit tests** for 34 custom hooks
- **Component integration tests** for refactored components
- **Validation tests** for schemas and data integrity
- **Visual regression tests** using Playwright
- **E2E tests** for critical user flows

**Current Status:**
- Vitest + Playwright infrastructure already in place
- ~40 existing tests across components and utilities
- Zero hooks currently have dedicated unit tests
- Playwright e2e tests partially implemented (14 spec files)

---

## 1. Audit Results

### 1.1 Existing Test Infrastructure

**Frontend Testing Stack:**
- **Unit/Component Testing:** Vitest + React Testing Library + JSDOM
- **E2E Testing:** Playwright (14 spec files, Chrome only)
- **Coverage:** Not currently measured, but ~40 tests exist
- **Configuration:** `vitest.setup.ts`, `vite.config.ts`, `playwright.config.ts`

**Test Files Location:**
- Unit/Component tests: `frontend/src/**/__tests__/` (34 files)
- Playwright specs: `frontend/tests/playwright/` (14 files)
- Additional: `tests/playwright/` (2 Python-based tests)

**Existing Test Distribution:**
```
frontend/src/components/__tests__/        8 components
frontend/src/components/spacing-showcase/__tests__/  2 files
frontend/src/components/image-uploader/__tests__/    3 files
frontend/src/config/__tests__/            1 file
frontend/src/store/__tests__/             1 file
frontend/src/api/__tests__/               2 files
```

### 1.2 Gap Analysis

| Category | Count | Status | Gap |
|----------|-------|--------|-----|
| Custom Hooks | 34 | 0% tested | **HIGH** - Need unit tests for all |
| Components | ~15 | ~30% | Medium - Selective testing needed |
| Schemas | 10+ | Basic validation | Medium - Need comprehensive validation |
| E2E Tests | 14 specs | Partial | Low - Core flows covered |
| Visual Regression | 0 | N/A | Medium - Need visual baselines |

### 1.3 Critical Untested Hooks

**Hooks in core modules:**
- Color/harmony hooks (5+)
- Typography hooks (3+)
- Extraction/processing hooks (8+)
- UI state hooks (10+)
- Utility hooks (8+)

---

## 2. Testing Strategy by Layer

### 2.1 Unit Tests for Custom Hooks

**Scope:** All 34 custom hooks across the codebase

**Approach:**
- Use `@testing-library/react` renderHook utility
- Test hook logic independently of components
- Mock external dependencies (API calls, store updates)
- Use `act()` for state updates
- Test both sync and async hooks

**Example Structure:**
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

**Priority Order:**
1. **Tier 1 (Critical):** Extraction hooks, color harmony hooks (8 hooks)
2. **Tier 2 (High):** State management hooks, form hooks (12 hooks)
3. **Tier 3 (Medium):** Utility hooks, computed property hooks (14 hooks)

### 2.2 Validation Tests for Schemas

**Scope:** All Zod schemas and data validation

**Files to Test:**
- `frontend/src/types/**/*.zod.ts` (generated from JSON schemas)
- API response validation
- Form data validation
- Token schema validation

**Approach:**
```typescript
describe('ColorTokenSchema validation', () => {
  it('should validate correct color token', () => {
    const valid = { hex: '#FF0000', confidence: 0.95, name: 'red' }
    const result = ColorTokenSchema.safeParse(valid)
    expect(result.success).toBe(true)
  })

  it('should reject invalid hex format', () => {
    const invalid = { hex: 'red', confidence: 0.95, name: 'red' }
    const result = ColorTokenSchema.safeParse(invalid)
    expect(result.success).toBe(false)
  })
})
```

**Schema Categories:**
1. **Color schemas** (3+ schemas)
2. **Typography schemas** (3+ schemas)
3. **Spacing schemas** (2+ schemas)
4. **API request/response schemas** (5+ schemas)

### 2.3 Component Integration Tests

**Approach:** Test component behavior with mocked hooks and stores

**Scope:**
- Phase 3 refactored components (5 components)
- Key UI components (image uploader, token display, etc.)
- Component composition and prop passing

**Example:**
```typescript
describe('ColorTokenDisplay integration', () => {
  it('should render token with extracted colors', () => {
    const colors = [{ hex: '#FF0000', name: 'red' }]
    render(<ColorTokenDisplay colors={colors} />)
    expect(screen.getByText('red')).toBeInTheDocument()
  })
})
```

### 2.4 Visual Regression Tests

**Tool:** Playwright with visual comparisons

**Scope:**
- Component snapshots at different viewport sizes
- Dark/light mode rendering
- State variations (loading, error, success)
- Accessibility features

**Implementation:**
```typescript
test('ColorDisplay should match snapshot', async ({ page }) => {
  await page.goto('/color-display')
  await expect(page.locator('.color-display')).toHaveScreenshot()
})
```

**Browsers:** Chrome, Firefox, Safari (expand from current Chrome-only)

### 2.5 E2E Tests for Critical Flows

**Current:** 14 Playwright spec files covering:
- Homepage loading
- Image extraction workflow
- Token display and interaction
- Export functionality
- Layout responsiveness

**Gaps to Fill:**
1. **Happy path workflows** - Complete image → extraction → export
2. **Error handling** - Invalid inputs, network errors, timeout
3. **Cross-browser compatibility** - Firefox, Safari
4. **Accessibility** - ARIA labels, keyboard navigation, screen reader

---

## 3. Implementation Roadmap

### Phase 1: Hook Unit Tests (Week 1)

**Goal:** Achieve 80% coverage of hook logic

**Tasks:**
1. Create `frontend/src/hooks/__tests__/` directory structure
2. Setup hook testing utilities and test fixtures
3. Implement tests for Tier 1 critical hooks (8 hooks)
4. Run coverage report

**Deliverables:**
- 8 hook test files (8+ tests per file = 64+ tests)
- Coverage report showing hook logic coverage
- Test utility library for hook mocking

### Phase 2: Schema Validation Tests (Week 2)

**Goal:** Comprehensive validation test suite

**Tasks:**
1. Create `frontend/src/types/__tests__/` for schema tests
2. Generate test cases for all Zod schemas
3. Test edge cases and error scenarios
4. Add negative test cases

**Deliverables:**
- 10+ schema test files
- 100+ validation test cases
- Validation error documentation

### Phase 3: Visual Regression Testing (Week 2-3)

**Goal:** Establish visual baselines and prevent regressions

**Tasks:**
1. Add Firefox and Safari to Playwright config
2. Capture visual baselines for all components
3. Setup visual diff reporting
4. Add responsive design tests

**Deliverables:**
- Visual baselines for all components
- Responsive design tests (mobile, tablet, desktop)
- Visual diff report setup

### Phase 4: E2E Test Expansion (Week 3-4)

**Goal:** Cover critical user paths and error scenarios

**Tasks:**
1. Expand happy path E2E tests
2. Add error scenario tests
3. Add accessibility tests (axe-core integration)
4. Cross-browser E2E tests

**Deliverables:**
- 20+ complete E2E test scenarios
- Accessibility test suite
- Cross-browser test matrix

### Phase 5: CI/CD Integration (Week 4)

**Goal:** Automated testing in pipeline

**Tasks:**
1. Configure GitHub Actions for test automation
2. Setup coverage thresholds and reporting
3. Add test results to PR checks
4. Setup visual diff reporting in CI

**Deliverables:**
- GitHub Actions workflow for tests
- Coverage reports in PRs
- Visual diff artifacts in CI

---

## 4. Testing Standards & Patterns

### 4.1 Unit Test Template

```typescript
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { renderHook, act } from '@testing-library/react'
import { useMyHook } from './useMyHook'

describe('useMyHook', () => {
  // Setup
  beforeEach(() => {
    // Reset mocks, setup fixtures
  })

  afterEach(() => {
    // Cleanup
    vi.clearAllMocks()
  })

  // Happy path
  describe('happy path', () => {
    it('should initialize with correct state', () => {
      const { result } = renderHook(() => useMyHook())
      expect(result.current.value).toBeDefined()
    })
  })

  // Error cases
  describe('error handling', () => {
    it('should handle errors gracefully', async () => {
      const { result } = renderHook(() => useMyHook())
      // Test error handling
    })
  })

  // Edge cases
  describe('edge cases', () => {
    it('should handle null/undefined inputs', () => {
      const { result } = renderHook(() => useMyHook(null))
      expect(result.current).toBeDefined()
    })
  })
})
```

### 4.2 Test Coverage Goals

| Layer | Target | Priority |
|-------|--------|----------|
| Hooks | 80%+ | HIGH |
| Schemas | 95%+ | CRITICAL |
| Components | 70%+ | MEDIUM |
| Integration | 60%+ | MEDIUM |
| E2E | Critical flows | MEDIUM |

### 4.3 Naming Conventions

```
Hooks:      useFeature.test.ts
Schemas:    schema.validation.test.ts
Components: Component.integration.test.tsx
E2E:        feature-workflow.spec.ts
Visual:     component.visual.spec.ts
```

---

## 5. Test Execution

### 5.1 Test Scripts

Add to `package.json`:

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
  "test:e2e:ui": "playwright test --ui",
  "test:visual": "playwright test --update-snapshots",
  "test:all": "vitest --run && playwright test",
  "test:ci": "vitest --run --coverage && playwright test"
}
```

### 5.2 Running Tests Locally

```bash
# Watch mode for development
pnpm test

# Run specific test suite
pnpm test:hooks
pnpm test:schemas
pnpm test:components

# Run E2E tests
pnpm test:e2e

# View coverage
pnpm test:coverage

# Update visual snapshots
pnpm test:visual
```

### 5.3 Coverage Measurement

Configure Vitest coverage in `vite.config.ts`:

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

## 6. Playwright Configuration Enhancements

### 6.1 Multi-Browser Testing

Update `playwright.config.ts`:

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
  },
  {
    name: 'Mobile Chrome',
    use: { ...devices['Pixel 5'] }
  }
]
```

### 6.2 Accessibility Testing

Add axe-core integration:

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

## 7. GitHub Actions CI/CD

### 7.1 Test Workflow

Create `.github/workflows/tests.yml`:

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

  accessibility:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: pnpm/action-setup@v2
      - uses: actions/setup-node@v3
        with:
          node-version: 18
          cache: 'pnpm'

      - run: pnpm install
      - run: pnpm test:e2e
```

---

## 8. Success Metrics

### 8.1 Quantitative Targets

| Metric | Current | Target | Timeline |
|--------|---------|--------|----------|
| Hook test coverage | 0% | 80% | Week 1 |
| Schema test coverage | 20% | 95% | Week 2 |
| E2E test count | 14 | 25+ | Week 3-4 |
| Component test count | 8 | 20+ | Week 2-3 |
| Visual baselines | 0 | 50+ | Week 3 |
| Code coverage overall | ? | 75%+ | Week 4 |

### 8.2 Qualitative Targets

- **Regression Prevention:** Visual and behavioral regressions caught before deploy
- **Developer Confidence:** Tests give developers confidence in refactoring
- **Documentation:** Tests serve as living documentation of API contracts
- **Maintenance:** Tests reduce bug fix time by 50%+

---

## 9. Known Issues & Constraints

### 9.1 Current Limitations

1. **No coverage reporting** - Need to setup v8 coverage provider
2. **Limited browser support** - Currently Chrome only (need Firefox/Safari)
3. **No visual baselines** - Need to establish and maintain snapshots
4. **Slow E2E tests** - Consider parallelization for large suites
5. **No accessibility testing** - axe-core integration needed

### 9.2 Mitigation Strategies

- Use test parallelization to speed up E2E execution
- Implement test result caching for faster reruns
- Use mock servers for deterministic E2E tests
- Establish visual diff thresholds to avoid flaky tests

---

## 10. Resources & References

### 10.1 Documentation Links

- [Vitest Documentation](https://vitest.dev)
- [React Testing Library](https://testing-library.com/react)
- [Playwright Testing](https://playwright.dev/docs/intro)
- [Testing Best Practices](https://github.com/goldbergyoni/javascript-testing-best-practices)

### 10.2 Example Test Files

Reference existing tests:
- `frontend/src/components/spacing-showcase/__tests__/hooks.test.ts` (330 lines, comprehensive hook testing)
- `frontend/src/components/__tests__/TokenCard.test.tsx` (232 lines, component integration)
- `frontend/tests/playwright/extraction.spec.ts` (E2E workflow)

---

## 11. Next Steps

### Immediate Actions (Today)

1. ✅ Review this strategy document
2. ✅ Identify which hook tests to implement first (Tier 1)
3. ✅ Setup hook test directory structure
4. ✅ Create test utility helpers for hook mocking

### Week 1 Priorities

1. Implement 8 hook tests for critical hooks
2. Setup coverage measurement
3. Create test documentation for team
4. Review and adjust strategy based on initial implementation

### Communication

- Share this strategy with the team
- Establish testing standards in code review
- Create runbook for running tests locally and in CI

---

## Appendix: Hook Categories

### Critical Hooks (Tier 1) - 8 hooks
Focus on extraction pipeline and color processing:
- Color extraction hooks (3)
- Harmony calculation hooks (2)
- Token processing hooks (3)

### Important Hooks (Tier 2) - 12 hooks
State management and form handling:
- Store/context hooks (6)
- Form input hooks (6)

### Utility Hooks (Tier 3) - 14 hooks
Computed properties and data transformation:
- Memo/computed hooks (7)
- Transformation hooks (7)

---

**Document Version:** 1.0
**Last Updated:** 2025-12-04
**Next Review:** After Phase 1 completion
