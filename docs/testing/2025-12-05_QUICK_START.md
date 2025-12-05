# Testing Quick Start

**Last Updated:** 2025-12-05

---

## 🚀 Run Tests Instantly

```bash
# All tests (fastest overview)
pnpm test:run

# Watch mode (auto-rerun on file changes)
pnpm test

# UI dashboard (visual browser interface)
pnpm test:ui

# Coverage report
pnpm test:coverage
```

---

## 📋 Available Commands

```bash
# Run all tests
pnpm test:run

# Run specific test suites
pnpm test:hooks       # Hook unit tests (108 tests)
pnpm test:schemas     # Schema validation tests
pnpm test:components  # Component tests
pnpm test:e2e         # E2E tests (Playwright)
pnpm test:backend     # Backend tests (pytest)

# Watch mode for development
pnpm test             # All tests in watch mode
pnpm test:hooks       # Only hooks in watch mode

# View results
pnpm test:ui          # Interactive test UI
pnpm test:coverage    # Generate coverage report

# Debug specific test
pnpm test -- <test-name-pattern>
```

---

## ✅ Current Test Coverage

### Phase 1: Tier 1 Hook Tests ✅ ACTIVE

| Hook | Tests | Status |
|------|-------|--------|
| useColorConversion | 32 | ✅ Complete |
| useContrastCalculation | 14 | ✅ Complete |
| useImageFile | 12 | ✅ Complete |
| useStreamingExtraction | 10 | ✅ Complete |
| usePaletteAnalysis | 18 | ✅ Complete |
| useArtMovementClassification | 22 | ✅ Complete |
| **Total** | **108** | **✅ COMPLETE** |

**Location:**
- `frontend/src/components/color-science/__tests__/hooks.test.ts`
- `frontend/src/components/image-uploader/__tests__/hooks-tier1.test.ts`
- `frontend/src/components/overview-narrative/__tests__/hooks-tier1.test.ts`

### Upcoming Phases

- **Phase 2** 🟡 Planned: Schema validation tests (50+ tests)
- **Phase 3** 🟡 Planned: Visual regression tests
- **Phase 4** 🟡 Planned: E2E coverage expansion (80% target)
- **Phase 5** 🟡 Planned: Performance & load testing

---

## 🔧 Setup & Environment

### Prerequisites
```bash
# Node and pnpm installed
node --version  # v18+
pnpm --version  # v9+

# Backend (optional, for integration tests)
python --version  # 3.10+
```

### First-Time Setup
```bash
# Install dependencies (already done)
pnpm install

# Setup test environment
pnpm test:run --reporter=verbose

# Check environment
pnpm test:run -- --reporter=verbose 2>&1 | head -20
```

---

## 🐛 Common Issues & Fixes

### Issue: "Cannot find module '@testing-library/react'"
**Solution:**
```bash
# Reinstall dependencies
pnpm install

# Clear cache
rm -rf node_modules/.vite
pnpm install
```

### Issue: Tests timeout
**Solution:**
```bash
# Increase timeout
pnpm test:run --reporter=verbose -- --test-timeout=10000

# Or run specific test
pnpm test -- hooks.test.ts
```

### Issue: "JSDOM not configured"
**Solution:**
- Check `vitest.setup.ts` exists in root
- Verify `environment: 'jsdom'` in `vite.config.ts`

### Issue: "Port 5173 already in use"
**Solution:**
```bash
# Kill existing process
lsof -i :5173 | awk 'NR!=1 {print $2}' | xargs kill -9

# Or use different port
pnpm test -- --reporter=verbose
```

### Issue: "Cannot find test files"
**Solution:**
```bash
# Verify test file locations
find frontend/src -name "*.test.ts" -o -name "*.test.tsx"

# Should return:
# frontend/src/components/color-science/__tests__/hooks.test.ts
# frontend/src/components/image-uploader/__tests__/hooks-tier1.test.ts
# frontend/src/components/overview-narrative/__tests__/hooks-tier1.test.ts
```

---

## 📊 Understanding Test Output

### Success Output
```
✓ frontend/src/components/color-science/__tests__/hooks.test.ts (32 tests) 1234ms
✓ frontend/src/components/image-uploader/__tests__/hooks-tier1.test.ts (12 tests) 567ms
✓ frontend/src/components/overview-narrative/__tests__/hooks-tier1.test.ts (40 tests) 890ms

Test Files  3 passed (3)
Tests  108 passed (108)
Duration  2.69s
```

### Failure Output
```
✗ frontend/src/components/__tests__/Component.test.ts (1 failed)
  ✗ Component
    ✗ should render correctly
    AssertionError: expected 'Actual' to equal 'Expected'
```

---

## 🎯 Quick Test Writing

### Basic Hook Test Template
```typescript
import { renderHook, act } from '@testing-library/react'
import { useMyHook } from './useMyHook'

describe('useMyHook', () => {
  it('should initialize with default values', () => {
    const { result } = renderHook(() => useMyHook())
    expect(result.current.value).toBe('expected')
  })

  it('should update state on action', async () => {
    const { result } = renderHook(() => useMyHook())
    await act(async () => {
      result.current.updateValue('new')
    })
    expect(result.current.value).toBe('new')
  })
})
```

**Location:** See `PATTERNS.md` for more examples

---

## 📚 Next Steps

| Goal | Document |
|------|----------|
| Understand full strategy | [TESTING_STRATEGY.md](./TESTING_STRATEGY.md) |
| See test examples | [PATTERNS.md](./PATTERNS.md) |
| Using test utilities | [TEST_UTILITIES.md](./TEST_UTILITIES.md) |
| Multi-phase roadmap | [ROADMAP.md](./ROADMAP.md) |
| More troubleshooting | [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) |
| Full index | [INDEX.md](./INDEX.md) |

---

## 💡 Pro Tips

1. **Run only changed tests** in watch mode:
   ```bash
   pnpm test -- --reporter=verbose
   # Then press 'p' to filter by file pattern
   ```

2. **Debug a specific test:**
   ```bash
   node --inspect-brk ./node_modules/.bin/vitest run frontend/src/components/color-science/__tests__/hooks.test.ts
   ```

3. **Watch specific test file:**
   ```bash
   pnpm test -- hooks.test.ts
   ```

4. **Generate coverage for specific files:**
   ```bash
   pnpm test:coverage -- frontend/src/components/
   ```

5. **Use test UI for better visualization:**
   ```bash
   pnpm test:ui
   # Opens http://localhost:51204 with interactive dashboard
   ```

---

**Last Updated:** 2025-12-05
**Phase:** 1 (Tier 1 Hooks ✅ Complete)
