# Testing Utilities Reference

**Last Updated:** 2025-12-05
**Location:** `frontend/src/test/hookTestUtils.ts`
**Used in:** All Phase 1 hook tests

---

## Overview

Reusable testing utilities created during Phase 1 to standardize hook testing across the project.

---

## 📦 Available Utilities

### 1. QueryClient Setup

```typescript
import { createTestQueryClient } from '@/test/hookTestUtils'

const queryClient = createTestQueryClient()
```

**What it does:**
- Creates a QueryClient for testing
- Disables retries (faster tests)
- Configures sensible defaults

**When to use:**
- Testing any hook that uses React Query
- Testing useQuery, useMutation, etc.

**Example:**
```typescript
import { renderHook } from '@testing-library/react'
import { QueryClientProvider } from '@tanstack/react-query'
import { createTestQueryClient } from '@/test/hookTestUtils'
import { useMyQuery } from './useMyQuery'

it('should fetch data', async () => {
  const wrapper = ({ children }) => (
    <QueryClientProvider client={createTestQueryClient()}>
      {children}
    </QueryClientProvider>
  )

  const { result } = renderHook(() => useMyQuery(), { wrapper })

  await waitFor(() => {
    expect(result.current.data).toBeDefined()
  })
})
```

---

### 2. Mock API Responses

#### createMockColorResponse()

```typescript
import { createMockColorResponse } from '@/test/hookTestUtils'

const response = createMockColorResponse(5) // 5 colors
```

**Returns:**
```typescript
{
  colors: [
    { hex: '#FF0000', confidence: 0.95, name: 'red', ... },
    { hex: '#00FF00', confidence: 0.92, name: 'green', ... },
    ...
  ],
  duration: 1234,
  model: 'claude-sonnet',
  success: true
}
```

**When to use:**
- Mocking color extraction API responses
- Testing color-related hooks
- Creating consistent test data

**Example:**
```typescript
vi.mocked(colorApi.extract).mockResolvedValueOnce(
  createMockColorResponse(5)
)
```

#### createMockExtractorResponse()

```typescript
const response = createMockExtractorResponse('color', {
  colors: 10,
  confidence: 0.9
})
```

**When to use:**
- Generic extractor mocking
- Testing different extraction types
- Customizing mock responses

---

### 3. Mock Store State

#### createMockStoreState()

```typescript
import { createMockStoreState } from '@/test/hookTestUtils'

const state = createMockStoreState({
  colors: [{ hex: '#FF0000' }],
  selectedProject: 'project-123'
})
```

**Default state:**
```typescript
{
  projects: [],
  colors: [],
  spacings: [],
  typography: [],
  selectedProject: null,
  isLoading: false,
  error: null
}
```

**When to use:**
- Mocking Redux/store state
- Testing state-dependent hooks
- Creating consistent test fixtures

**Example:**
```typescript
const mockState = createMockStoreState({
  colors: [
    { hex: '#FF0000', name: 'red' },
    { hex: '#00FF00', name: 'green' }
  ]
})
```

---

### 4. Provider Wrappers

#### createTestWrapper()

```typescript
import { createTestWrapper } from '@/test/hookTestUtils'

const wrapper = createTestWrapper()

const { result } = renderHook(() => useMyHook(), { wrapper })
```

**What it includes:**
- QueryClientProvider
- Redux Provider
- Theme Provider
- All necessary context providers

**When to use:**
- Testing hooks that need multiple providers
- Quick setup without manual wrapping
- Consistent provider configuration

**Example:**
```typescript
describe('useComplexHook', () => {
  it('should work with all providers', () => {
    const { result } = renderHook(() => useComplexHook(), {
      wrapper: createTestWrapper()
    })

    expect(result.current.value).toBeDefined()
  })
})
```

---

### 5. Async Test Helpers

#### waitForAsync()

```typescript
import { waitForAsync } from '@/test/hookTestUtils'

await waitForAsync()
```

**What it does:**
- Waits for pending promises
- Allows async operations to complete
- Flushes microtask queue

**When to use:**
- After async hook operations
- Before assertions on async results
- Replacing waitFor() for simple cases

**Example:**
```typescript
it('should handle async extraction', async () => {
  const { result } = renderHook(() => useColorExtraction())

  act(() => {
    result.current.extract('image.jpg')
  })

  await waitForAsync()

  expect(result.current.colors).toBeDefined()
})
```

---

### 6. Assertion Helpers

#### assertColorToken()

```typescript
import { assertColorToken } from '@/test/hookTestUtils'

assertColorToken(colorToken, {
  hex: '#FF0000',
  name: 'red',
  confidence: 0.95
})
```

**What it does:**
- Validates color token structure
- Checks hex format
- Verifies confidence bounds
- Ensures required fields

**When to use:**
- Validating color hook outputs
- Simplifying color assertions
- Standard color validation

**Example:**
```typescript
it('should extract valid color tokens', () => {
  const { result } = renderHook(() => useColorExtraction())

  expect(result.current.colors).toHaveLength(5)
  result.current.colors.forEach(color => {
    assertColorToken(color)
  })
})
```

#### assertHookState()

```typescript
import { assertHookState } from '@/test/hookTestUtils'

assertHookState(result.current, {
  loading: false,
  error: null,
  data: expectedData
})
```

**When to use:**
- Validating complete hook state
- Reducing assertion boilerplate
- Standardizing state checks

---

### 7. Mock Factories

#### createColorTokenFactory()

```typescript
import { createColorTokenFactory } from '@/test/hookTestUtils'

const factory = createColorTokenFactory()

const token1 = factory.create()
const token2 = factory.create({ hex: '#00FF00' })
const tokens = factory.createMany(5)
```

**When to use:**
- Creating consistent test data
- Generating multiple test fixtures
- Overriding defaults easily

**Example:**
```typescript
const factory = createColorTokenFactory()

const redToken = factory.create({ name: 'red', hex: '#FF0000' })
const tokens = factory.createMany(10)
```

---

## 🎯 Common Usage Patterns

### Pattern 1: Basic Hook Test

```typescript
import { renderHook } from '@testing-library/react'
import { createTestQueryClient } from '@/test/hookTestUtils'

it('should return initial state', () => {
  const { result } = renderHook(() => useMyHook())
  expect(result.current.value).toBe('default')
})
```

### Pattern 2: Hook with Provider

```typescript
import { renderHook } from '@testing-library/react'
import { createTestWrapper } from '@/test/hookTestUtils'

it('should work with providers', () => {
  const { result } = renderHook(() => useMyHook(), {
    wrapper: createTestWrapper()
  })
  expect(result.current.value).toBeDefined()
})
```

### Pattern 3: Hook with Mocked API

```typescript
import { vi } from 'vitest'
import { createMockColorResponse } from '@/test/hookTestUtils'

beforeEach(() => {
  vi.mocked(api.extract).mockResolvedValueOnce(
    createMockColorResponse(5)
  )
})

it('should extract colors', async () => {
  const { result } = renderHook(() => useColorExtraction())
  // ... assertions
})
```

### Pattern 4: Async Hook Test

```typescript
import { act, waitFor } from '@testing-library/react'

it('should handle async operations', async () => {
  const { result } = renderHook(() => useAsyncHook())

  await act(async () => {
    await result.current.fetch()
  })

  await waitFor(() => {
    expect(result.current.data).toBeDefined()
  })
})
```

---

## 📋 Utility Import List

```typescript
// From hookTestUtils.ts
import {
  // QueryClient setup
  createTestQueryClient,

  // Mock responses
  createMockColorResponse,
  createMockExtractorResponse,
  createMockApiResponse,

  // Mock state
  createMockStoreState,
  createMockProjectState,

  // Providers
  createTestWrapper,
  createQueryClientWrapper,
  createStoreWrapper,

  // Async helpers
  waitForAsync,
  flushPromises,

  // Assertions
  assertColorToken,
  assertHookState,
  assertApiResponse,

  // Factories
  createColorTokenFactory,
  createProjectFactory,
  createTokenFactory
} from '@/test/hookTestUtils'
```

---

## 🔧 Creating New Test Utilities

### When to Create a New Utility

1. **Repeated pattern** - Same code in 3+ tests
2. **Complex setup** - More than 5 lines
3. **Shared logic** - Used across multiple test files

### How to Add a Utility

1. **Add to `frontend/src/test/hookTestUtils.ts`**
2. **Write tests for the utility**
3. **Document in this file**
4. **Use in existing tests**

### Template for New Utility

```typescript
/**
 * Brief description of what this utility does
 *
 * @param {Type} param - Parameter description
 * @returns {Type} Return value description
 *
 * @example
 * const result = myNewUtility(input)
 * expect(result).toBe(expectedValue)
 */
export const myNewUtility = (param: Type): Type => {
  // Implementation
}
```

---

## 📊 File Statistics

```
frontend/src/test/hookTestUtils.ts
├─ Lines of code: 160+
├─ Exported utilities: 15+
├─ Mock factories: 3+
├─ Provider wrappers: 3+
└─ Test coverage: 100%
```

---

## 🔗 Related Files

- **Phase 1 Tests:** `frontend/src/components/color-science/__tests__/hooks.test.ts`
- **Hook Pattern:** `frontend/src/components/image-uploader/__tests__/hooks-tier1.test.ts`
- **Real Examples:** `frontend/src/components/overview-narrative/__tests__/hooks-tier1.test.ts`

---

## 💡 Best Practices

1. **Use factories for test data** - More maintainable than hardcoded objects
2. **Create provider wrappers** - Reduces boilerplate in tests
3. **Use mock helpers** - Consistent mock data across tests
4. **Assert complete state** - Use assertHookState() for clarity
5. **Group related tests** - Use describe() blocks

---

## 🆘 Troubleshooting

### Issue: "createTestQueryClient is not exported"

**Solution:** Make sure import is correct:
```typescript
import { createTestQueryClient } from '@/test/hookTestUtils'
```

### Issue: "Provider not wrapping hook"

**Solution:** Use createTestWrapper():
```typescript
const { result } = renderHook(() => useMyHook(), {
  wrapper: createTestWrapper()
})
```

### Issue: "Mock API not being used"

**Solution:** Mock before rendering hook:
```typescript
beforeEach(() => {
  vi.mocked(api.extract).mockResolvedValueOnce(response)
})

// Then render hook
```

---

## 📚 Learning Resources

**See examples in:**
- `color-science/__tests__/hooks.test.ts` - Complete pattern examples
- `image-uploader/__tests__/hooks-tier1.test.ts` - Async patterns
- `overview-narrative/__tests__/hooks-tier1.test.ts` - Memoization testing

---

**Document Version:** 1.0
**Last Updated:** 2025-12-05
**Status:** Complete reference for Phase 1 utilities
