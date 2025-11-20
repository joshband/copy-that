# TypeScript Fixes - Reference Implementation
## Quick Reference for Critical Type Safety Fixes

**Related Report:** TYPESCRIPT_TYPE_SAFETY_REVIEW.md
**Priority:** P1 (Critical Path)
**Estimated Time:** 4-6 hours

---

## Fix 1: Replace 7 `any` Types in types.ts (Lines 544-550)

**File:** `/frontend/src/api/types.ts`
**Current Code:**
```typescript
export interface DesignTokens {
  // ... existing properties ...

  // v2.4 and v2.5 extractors - PROBLEMATIC
  opacity?: any                    // Line 544
  transitions?: any                // Line 545
  blur_filters?: any              // Line 546
  font_family?: any               // Line 547
  component_recognition?: any     // Line 548
  depth_map?: any                 // Line 549
  video_animation?: any           // Line 550

  _metadata?: ExtractionMetadata
}
```

**Fixed Code:**
```typescript
// Add these interfaces BEFORE DesignTokens interface

/**
 * Opacity/transparency tokens (v2.4)
 */
export interface OpacityTokens {
  opacity: {
    scale: Record<string, number>
  }
  _metadata?: {
    detected_values: number
    total_patterns: number
  }
}

/**
 * Transition/timing tokens (v2.4)
 */
export interface TransitionTokens {
  transitions: {
    duration: Record<string, string>
    easing: Record<string, string>
  }
  _metadata?: {
    components: number
    motion_states: number
  }
}

/**
 * Blur & filter tokens (v2.4)
 */
export interface BlurFilterTokens {
  blur: {
    radius: Record<string, string>
    backdrop: Record<string, string>
  }
  filters: Record<string, string>
  _metadata?: {
    blur_regions: number
    backdrop_blur_regions: number
  }
}

/**
 * Font family tokens (v2.5)
 */
export interface FontFamilyTokens {
  fonts: Record<string, {
    family: string
    category: string
    weights?: number[]
  }>
  _metadata?: {
    detected_fonts: number
  }
}

/**
 * Component recognition tokens (v2.5)
 */
export interface ComponentRecognitionTokens {
  components: Array<{
    type: string
    style?: {
      background_color?: string
      border_radius?: string
      [key: string]: string | undefined
    }
    confidence: number
  }>
  _metadata?: {
    total_components: number
    avg_confidence: number
  }
}

/**
 * Depth map tokens (v2.5)
 */
export interface DepthMapTokens {
  elevation: Record<string, number | { pixels: number }>
  _metadata?: {
    depth_levels: number
  }
}

/**
 * Video animation tokens (v2.5 - optional)
 */
export interface VideoAnimationTokens {
  animations: Array<{
    type: string
    duration: number
    easing: string
    direction?: string
  }>
  _metadata?: {
    total_frames: number
    fps?: number
  }
}

// Then update DesignTokens interface
export interface DesignTokens {
  // ... existing properties ...

  // v2.4 and v2.5 extractors - PROPERLY TYPED
  opacity?: OpacityTokens
  transitions?: TransitionTokens
  blur_filters?: BlurFilterTokens
  font_family?: FontFamilyTokens
  component_recognition?: ComponentRecognitionTokens
  depth_map?: DepthMapTokens
  video_animation?: VideoAnimationTokens

  _metadata?: ExtractionMetadata
}
```

---

## Fix 2: Add Missing AI-Enhanced Fields to ColorTokenObject

**File:** `/frontend/src/api/types.ts` (Line 13)
**Current Code:**
```typescript
export interface ColorTokenObject {
  hex: string
  confidence?: number
  votes?: number
  consensus?: boolean
  extractors?: string[]
  semantic_name?: string
  description?: string
}
```

**Fixed Code:**
```typescript
/**
 * Color token with source attribution, confidence scoring, and AI enhancement (v3.0+)
 */
export interface ColorTokenObject {
  // Core properties
  hex: string
  confidence?: number
  votes?: number
  consensus?: boolean
  extractors?: string[]

  // AI-enhanced semantic properties (v3.0+)
  name?: string              // AI-generated primary name
  semantic_name?: string     // Alternative semantic name
  usage?: string             // Usage context / application
  description?: string       // Detailed description
  design_intent?: string     // Design rationale / purpose
  accessibility?: string     // Accessibility notes / contrast info

  // Future extensibility
  [key: string]: unknown
}
```

---

## Fix 3: Fix comprehensive-types.ts Import Errors

**File:** `/frontend/src/api/comprehensive-types.ts`
**Current Code (Problematic):**
```typescript
/**
 * Comprehensive Design Token Type System - v3.1
 */

// ... 550 lines of type definitions ...

export interface ComprehensiveDesignTokens {
  palette: Record<string, ColorToken>;  // ERROR: Cannot find name 'ColorToken'
  spacing: Record<string, SpacingToken>; // ERROR: Cannot find name 'SpacingToken'
  shadow: Record<string, ShadowToken>;   // ERROR: Cannot find name 'ShadowToken'
  // ... more errors ...
}

// Re-export at end (TOO LATE)
export * from './types';
```

**Fixed Code:**
```typescript
/**
 * Comprehensive Design Token Type System - v3.1
 */

// IMPORT BASE TYPES FIRST
import type {
  ColorToken,
  ColorTokenObject,
  SpacingToken,
  SpacingTokenObject,
  ShadowToken,
  ShadowTokenObject,
  BoxShadow,
  RadiusToken,
  RadiusTokenObject,
  TypographyToken,
  TypographyTokenObject,
  TypographyExtended,
  Ontology,
  ExtractionMetadata,
  DesignTokens
} from './types'

// Now define extended types
// ... 550 lines of type definitions ...

export interface ComprehensiveDesignTokens {
  palette: Record<string, ColorToken>     // NOW RESOLVES
  spacing: Record<string, SpacingToken>   // NOW RESOLVES
  shadow: Record<string, ShadowToken>     // NOW RESOLVES
  typography_extended?: TypographyExtended // NOW RESOLVES
  radius?: Record<string, RadiusToken>    // NOW RESOLVES
  ontology?: Ontology                     // NOW RESOLVES
  _metadata?: ExtractionMetadata          // NOW RESOLVES

  // Extended types
  materials?: MaterialTokens
  lighting?: LightingTokens
  // ... etc
}

// Re-export base types for convenience
export type {
  ColorToken,
  ColorTokenObject,
  SpacingToken,
  ShadowToken,
  RadiusToken,
  TypographyExtended,
  Ontology,
  ExtractionMetadata,
  DesignTokens
}

// Re-export all other types
export * from './types'
```

---

## Fix 4: Create Test Utility for Mock Tokens

**File:** `/frontend/src/test/mockTokens.ts` (NEW FILE)
```typescript
import type { DesignTokens } from '../api/types'

/**
 * Create a complete DesignTokens object with sensible defaults
 * and optional partial overrides for testing.
 *
 * @example
 * const tokens = createMockDesignTokens({
 *   palette: { primary: '#007bff' }
 * })
 */
export function createMockDesignTokens(
  partial?: Partial<DesignTokens>
): DesignTokens {
  const defaults: DesignTokens = {
    // Required properties with defaults
    palette: {},
    primitive: {},
    semantic: {},
    spacing: {},
    shadow: {},
    elevation: {},
    zindex: {},
    zindex_docs: {},
    icon_sizes: {},
    typography: {
      family: 'system-ui, -apple-system, sans-serif',
      weights: [400, 500, 700]
    }
  }

  return {
    ...defaults,
    ...partial,
    // Deep merge nested objects if provided
    palette: { ...defaults.palette, ...partial?.palette },
    spacing: { ...defaults.spacing, ...partial?.spacing },
    shadow: { ...defaults.shadow, ...partial?.shadow },
  }
}

/**
 * Create minimal tokens with only palette
 */
export function createMinimalTokens(
  palette: Record<string, string> = {}
): DesignTokens {
  return createMockDesignTokens({ palette })
}

/**
 * Create complete tokens with all categories populated
 */
export function createCompleteTokens(): DesignTokens {
  return createMockDesignTokens({
    palette: {
      primary: '#007bff',
      secondary: '#6c757d',
      success: '#28a745',
      danger: '#dc3545',
      warning: '#ffc107',
      info: '#17a2b8'
    },
    spacing: {
      xs: 4,
      sm: 8,
      md: 16,
      lg: 24,
      xl: 32
    },
    shadow: {
      sm: '0 1px 2px rgba(0,0,0,0.1)',
      md: '0 4px 6px rgba(0,0,0,0.1)',
      lg: '0 10px 15px rgba(0,0,0,0.1)'
    },
    icon_sizes: {
      sm: 16,
      md: 24,
      lg: 32
    },
    _metadata: {
      tier: 3,
      elapsed_seconds: 1.5,
      total_cost: 0.05,
      confidence_threshold: 0.8
    }
  })
}
```

**Usage in Tests:**
```typescript
// Before (FAILS)
const mockTokens = { palette: { primary: '#000' } }
render(<TokenDisplay tokens={mockTokens} />) // Type Error

// After (WORKS)
import { createMockDesignTokens } from '@/test/mockTokens'

const mockTokens = createMockDesignTokens({
  palette: { primary: '#000' }
})
render(<TokenDisplay tokens={mockTokens} />) // Type Safe!
```

---

## Fix 5: Replace Unsafe Type Assertions

### 5.1 Fix TokenDisplay.tsx Map Callbacks

**File:** `/frontend/src/components/TokenDisplay.tsx`
**Current Code (Lines 625, 657, 704, 739, 770, 946):**
```typescript
// Line 625 - UNSAFE
{Object.entries(tokens.font_family.fonts).map(([name, fontData]: [string, any]) => (
  <div key={name}>
    <span>{fontData.family}</span>
  </div>
))}

// Line 657 - UNSAFE
{tokens.component_recognition.components.map((comp: any, idx: number) => (
  <div key={idx}>{comp.type}</div>
))}
```

**Fixed Code:**
```typescript
// Add type definitions at top of file
interface FontData {
  family: string
  category: string
  weights?: number[]
}

interface RecognizedComponent {
  type: string
  style?: {
    background_color?: string
    border_radius?: string
  }
  confidence: number
}

// Then use in map callbacks
{Object.entries(tokens.font_family.fonts).map(([name, fontData]: [string, FontData]) => (
  <div key={name} className="font-family-item">
    <span className="font-family-name">{fontData.family}</span>
    <span className="font-family-category">{fontData.category}</span>
    {fontData.weights && (
      <span className="font-family-weights">
        Weights: {Array.isArray(fontData.weights) ? fontData.weights.join(', ') : fontData.weights}
      </span>
    )}
  </div>
))}

{tokens.component_recognition.components.map((comp: RecognizedComponent, idx: number) => (
  <div key={idx} className="component-item">
    <div className="component-type-badge">{comp.type}</div>
    <span className="component-confidence">
      {Math.round(comp.confidence * 100)}% confidence
    </span>
  </div>
))}
```

### 5.2 Fix interceptors.ts Type Assertion

**File:** `/frontend/src/api/interceptors.ts` (Line 147)
**Current Code:**
```typescript
if (status === 400 || status === 422) {
  const errorData = error.response.data as any
  console.warn('[Validation Error]', errorData)
  return Promise.reject(error)
}
```

**Fixed Code:**
```typescript
interface ValidationErrorData {
  message: string
  errors?: Array<{
    field: string
    message: string
  }>
}

function isValidationError(data: unknown): data is ValidationErrorData {
  return (
    typeof data === 'object' &&
    data !== null &&
    'message' in data &&
    typeof (data as { message: unknown }).message === 'string'
  )
}

// Then use type guard
if (status === 400 || status === 422) {
  const errorData = error.response.data
  if (isValidationError(errorData)) {
    console.warn('[Validation Error]', errorData.message, errorData.errors)
  } else {
    console.warn('[Validation Error]', errorData)
  }
  return Promise.reject(error)
}
```

### 5.3 Fix ComprehensiveExtractor.tsx Error Handling

**File:** `/frontend/src/components/ComprehensiveExtractor.tsx` (Line 62)
**Current Code:**
```typescript
} catch (err: any) {
  setError(err.message || 'Extraction failed')
}
```

**Fixed Code:**
```typescript
} catch (err: unknown) {
  const errorMessage = err instanceof Error
    ? err.message
    : 'Extraction failed'
  setError(errorMessage)
}
```

### 5.4 Fix Test File Assertions

**File:** Multiple test files
**Current Code:**
```typescript
render(<TokenEditor tokens={minimalTokens as any} />)
render(<TokenEditor tokens={stringColorTokens as any} />)
```

**Fixed Code:**
```typescript
import { createMockDesignTokens } from '../../test/mockTokens'

const minimalTokens = createMockDesignTokens({
  palette: { primary: '#000' }
})
render(<TokenEditor tokens={minimalTokens} />)

const stringColorTokens = createMockDesignTokens({
  palette: {
    primary: '#ff0000',
    secondary: '#00ff00'
  }
})
render(<TokenEditor tokens={stringColorTokens} />)
```

---

## Fix 6: Add Type Guards for Token Unions

**File:** `/frontend/src/api/typeGuards.ts` (NEW FILE)
```typescript
import type {
  ColorToken,
  ColorTokenObject,
  SpacingToken,
  SpacingTokenObject,
  ShadowToken,
  ShadowTokenObject,
  RadiusToken,
  RadiusTokenObject,
  TypographyToken,
  TypographyTokenObject
} from './types'

/**
 * Type guard to check if a ColorToken is a ColorTokenObject
 */
export function isColorTokenObject(token: ColorToken): token is ColorTokenObject {
  return typeof token === 'object' && token !== null && 'hex' in token
}

/**
 * Type guard to check if a SpacingToken is a SpacingTokenObject
 */
export function isSpacingTokenObject(token: SpacingToken): token is SpacingTokenObject {
  return typeof token === 'object' && token !== null && 'value' in token
}

/**
 * Type guard to check if a ShadowToken is a ShadowTokenObject
 */
export function isShadowTokenObject(token: ShadowToken): token is ShadowTokenObject {
  return (
    typeof token === 'object' &&
    token !== null &&
    !Array.isArray(token) &&
    'value' in token
  )
}

/**
 * Type guard to check if a RadiusToken is a RadiusTokenObject
 */
export function isRadiusTokenObject(token: RadiusToken): token is RadiusTokenObject {
  return typeof token === 'object' && token !== null && 'value' in token
}

/**
 * Type guard to check if a TypographyToken is a TypographyTokenObject
 */
export function isTypographyTokenObject(
  token: TypographyToken
): token is TypographyTokenObject {
  return typeof token === 'object' && token !== null && 'value' in token
}

/**
 * Extract the primitive value from a token (handles both simple and object forms)
 */
export function extractTokenValue<T extends SpacingToken | RadiusToken | ShadowToken>(
  token: T
): string | number {
  if (typeof token === 'string' || typeof token === 'number') {
    return token
  }

  if (typeof token === 'object' && token !== null) {
    if ('value' in token) {
      const value = token.value
      // Recursively extract if nested
      if (typeof value === 'object' && value !== null && 'value' in value) {
        return extractTokenValue(value as T)
      }
      return value as string | number
    }
  }

  // Fallback
  return String(token)
}

/**
 * Convert token to CSS value string
 */
export function tokenToCssValue(token: SpacingToken | RadiusToken): string {
  const value = extractTokenValue(token)
  return typeof value === 'number' ? `${value}px` : String(value)
}
```

**Usage in DemoShowcase.tsx:**
```typescript
import { tokenToCssValue } from '../api/typeGuards'

// Before (TYPE ERROR)
<Box
  sx={{
    padding: tokens.spacing.md,  // Error: Type mismatch
    borderRadius: tokens.radius.md,  // Error: Type mismatch
  }}
/>

// After (TYPE SAFE)
<Box
  sx={{
    padding: tokenToCssValue(tokens.spacing.md),  // Works!
    borderRadius: tokenToCssValue(tokens.radius.md),  // Works!
  }}
/>
```

---

## Fix 7: Fix setTimeout Type in useProgressiveExtraction.ts

**File:** `/frontend/src/hooks/useProgressiveExtraction.ts`
**Current Code (Lines 209-210, 404):**
```typescript
const reconnectTimeoutRef = useRef<number | null>(null)
const heartbeatIntervalRef = useRef<number | null>(null)

// Later...
reconnectTimeoutRef.current = setTimeout(() => {...}, delay)
// Error: Type 'Timeout' is not assignable to type 'number'
```

**Fixed Code:**
```typescript
// Use ReturnType for proper typing
const reconnectTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null)
const heartbeatIntervalRef = useRef<ReturnType<typeof setInterval> | null>(null)

// Now works correctly
reconnectTimeoutRef.current = setTimeout(() => {
  reconnectAttemptsRef.current++
  connect()
}, delay)

heartbeatIntervalRef.current = setInterval(() => {
  if (wsRef.current?.readyState === WebSocket.OPEN) {
    wsRef.current.send(JSON.stringify({ action: 'ping' }))
  }
}, heartbeatInterval)
```

---

## Fix 8: Update Test Imports (All Test Files)

**Pattern to Apply:**
```typescript
// Before
import { render, screen, within } from '@testing-library/react'
// 'within' is never used - warning

// After - Remove unused imports
import { render, screen } from '@testing-library/react'

// OR prefix with underscore if potentially useful
import { render, screen, within as _within } from '@testing-library/react'
```

**Files to Update:**
- `src/components/__tests__/DemoShowcase.test.tsx`
- `src/components/__tests__/TokenEditor.test.tsx`
- `src/components/__tests__/ExportPanel.test.tsx`
- `src/components/__tests__/ImageUploader.test.tsx`
- `src/components/__tests__/ProcessingAnimation.test.tsx`
- `src/components/__tests__/TokenDisplay.test.tsx`
- `src/api/__tests__/client.integration.test.ts`

---

## Validation Steps

After applying fixes, run these commands to verify:

```bash
# 1. Type check
cd frontend
npx tsc --noEmit

# Expected: 200 errors → ~60 errors after P1 fixes

# 2. Build check
pnpm build

# Expected: Successful build with no type errors

# 3. Test check
pnpm test:unit

# Expected: All tests pass with proper types

# 4. Lint check
pnpm lint

# Expected: No unused variable warnings
```

---

## Success Criteria

After applying all P1 fixes:
- ✓ Zero `any` types in production code
- ✓ All 7 comprehensive-types.ts errors resolved
- ✓ Test fixtures properly typed
- ✓ All unsafe assertions replaced
- ✓ Build completes without type errors
- ✓ Type safety grade: C+ → B+

---

**Next Steps:**
1. Apply fixes in order (1-8)
2. Run validation after each fix
3. Commit with message: "fix: resolve critical TypeScript type safety issues"
4. Move to P2 fixes (type guards, strict flags)

**Estimated Time:** 4-6 hours for all P1 fixes
**Impact:** ~70% reduction in type errors (200 → 60)
