/**
 * Hook Testing Utilities
 *
 * Provides reusable utilities for testing custom React hooks.
 * Includes mock factories, setup helpers, and common patterns.
 */

import { ReactNode } from 'react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'

/**
 * Create a wrapper provider for hooks that depend on React Query
 */
export function createQueryClientWrapper() {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  })

  const wrapper = ({ children }: { children: ReactNode }) => (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  )

  return { wrapper, queryClient }
}

/**
 * Create mock API response helpers
 */
export const mockApiResponses = {
  colorTokens: (count = 3) => {
    return Array.from({ length: count }, (_, i) => ({
      hex: `#${Math.floor(Math.random() * 16777215).toString(16).padStart(6, '0')}`,
      confidence: 0.8 + Math.random() * 0.2,
      semantic_name: `color_${i}`,
      token_type: 'color' as const,
      created_at: new Date().toISOString(),
    }))
  },

  spacingTokens: (count = 3) => {
    return Array.from({ length: count }, (_, i) => ({
      value: (i + 1) * 8,
      unit: 'px' as const,
      semantic_name: `spacing_${i}`,
      token_type: 'spacing' as const,
    }))
  },

  typographyTokens: (count = 2) => {
    return Array.from({ length: count }, (_, i) => ({
      font_family: `Font ${i}`,
      font_size: 12 + i * 4,
      font_weight: 400 + i * 100,
      line_height: 1.5,
      semantic_name: `typography_${i}`,
      token_type: 'typography' as const,
    }))
  },
}

/**
 * Create mock store state for hooks that use Zustand stores
 */
export const createMockStoreState = (overrides = {}) => ({
  tokens: [],
  projects: [],
  extractionHistory: [],
  selectedToken: null,
  isLoading: false,
  error: null,
  ...overrides,
})

/**
 * Delay helper for async operations
 */
export const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms))

/**
 * Setup hook test with common utilities
 */
export function setupHookTest() {
  return {
    queryWrapper: createQueryClientWrapper(),
    mockResponses: mockApiResponses,
    mockStore: createMockStoreState,
    delay,
  }
}

/**
 * Wait for hook state updates with retry logic
 */
export async function waitForHookState<T>(
  condition: () => T,
  timeout = 1000,
  interval = 50
): Promise<T> {
  const startTime = Date.now()
  while (Date.now() - startTime < timeout) {
    try {
      const result = condition()
      if (result !== undefined && result !== null) {
        return result
      }
    } catch (e) {
      // Continue waiting
    }
    await delay(interval)
  }
  throw new Error(`Timeout waiting for hook state after ${timeout}ms`)
}

/**
 * Assert hook behavior patterns
 */
export const hookAssertions = {
  /**
   * Verify hook returns expected structure
   */
  hasStructure: <T extends Record<string, unknown>>(
    result: unknown,
    expectedKeys: (keyof T)[]
  ) => {
    const obj = result as T
    for (const key of expectedKeys) {
      if (!(key in obj)) {
        throw new Error(`Expected key "${String(key)}" not found in hook result`)
      }
    }
    return true
  },

  /**
   * Verify hook state is immutable (reference changes)
   */
  stateIsImmutable: (prevState: unknown, nextState: unknown) => {
    if (prevState === nextState && prevState !== null) {
      throw new Error('State object reference should change on update')
    }
    return true
  },

  /**
   * Verify hook properly memoizes results
   */
  resultIsMemoized: (prevResult: unknown, nextResult: unknown) => {
    if (prevResult !== nextResult) {
      throw new Error('Memoized result reference should not change')
    }
    return true
  },
}

export type HookTestUtils = ReturnType<typeof setupHookTest>
