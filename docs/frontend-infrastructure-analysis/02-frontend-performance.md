# Frontend Performance Analysis

> Deep dive into React architecture, TypeScript quality, build optimization, and accessibility

---

## Table of Contents

1. [Current State Assessment](#current-state-assessment)
2. [React Component Optimization](#react-component-optimization)
3. [TypeScript Enhancement](#typescript-enhancement)
4. [Build & Bundle Optimization](#build--bundle-optimization)
5. [W3C Design Token Integration](#w3c-design-token-integration)
6. [Accessibility Improvements](#accessibility-improvements)
7. [State Management Evaluation](#state-management-evaluation)

---

## Current State Assessment

### Component Architecture Overview

**Directory Structure:**
```
frontend/src/
├── components/          # 22 React components (flat structure)
│   ├── __tests__/      # 12 test files
│   └── *.css           # 22 CSS files (1:1 ratio)
├── store/              # Zustand state management
├── api/                # TanStack Query hooks + client
├── types/              # Centralized TypeScript interfaces
├── config/             # Token type registry
├── design/             # CSS design tokens
├── App.tsx             # Main application
└── main.tsx            # Entry point
```

**File Statistics:**
| Metric | Count | Notes |
|--------|-------|-------|
| Components | 22 | All functional components |
| Test Files | 14 | 12 component + 2 config/store |
| CSS Files | 22 | Component-scoped styling |
| Type Files | 1 | Centralized in types/index.ts |
| Total Lines | ~4,070 | Components only |

### Architecture Patterns

#### ✅ Strengths

1. **Schema-Driven Design**
   - `tokenTypeRegistry.tsx` defines all token configurations
   - Enables 80% code reuse across token types
   - Easy to extend for new token types (Typography, Spacing, etc.)

2. **Strong Separation of Concerns**
   - Components handle rendering
   - Store manages state
   - API layer handles data fetching
   - Types provide contracts

3. **Modern React Patterns**
   - 100% functional components
   - Hooks for state and effects
   - No class components or legacy patterns

4. **Excellent Type Safety**
   - Comprehensive interfaces for ColorToken (50+ fields)
   - Type guards (`isValidColorToken`)
   - Factory functions (`getDefaultColorToken`)

#### ⚠️ Concerns

1. **Performance Optimizations Missing**
   - No `React.memo` on any component
   - No `useCallback` for event handlers
   - Only 4 instances of `useMemo`

2. **Flat Component Structure**
   - All 22 components in single directory
   - No logical grouping by feature/domain
   - Scalability concern as app grows

3. **CSS Architecture**
   - 22 separate CSS files = maintenance burden
   - No CSS-in-JS or utility framework
   - Design tokens exist but inconsistently used

4. **Mixed Export Patterns**
   - 8 default exports
   - 14 named exports
   - Inconsistent style across codebase

### Performance Metrics (Estimated)

| Metric | Estimated Value | Target | Status |
|--------|-----------------|--------|--------|
| Bundle Size | ~800KB (unoptimized) | < 500KB gzipped | ⚠️ |
| Initial Load | ~3-4s (no splitting) | < 2s | ⚠️ |
| Render Performance | Degrades at 50+ tokens | 100+ tokens smooth | ⚠️ |
| Type Coverage | ~95% | 100% | ✅ |
| Accessibility Score | ~70 | 90+ | ⚠️ |

---

## React Component Optimization

### Current Performance Issues

#### 1. Missing Memoization

**Problem:** Components re-render unnecessarily when parent state changes.

**Affected Components:**
- `TokenCard` - Rendered in list, re-renders on any grid change
- `TokenGrid` - Re-renders on filter/sort changes
- `HarmonyVisualizer` - Complex SVG calculations on each render
- `AccessibilityVisualizer` - WCAG calculations repeated

**Current Implementation (TokenCard):**
```tsx
// No memoization - re-renders on every parent change
export const TokenCard: React.FC<TokenCardProps> = ({ token, ... }) => {
  // Component body
}
```

**Recommended Implementation:**
```tsx
// Memoized - only re-renders when props change
export const TokenCard = React.memo<TokenCardProps>(function TokenCard({
  token,
  onSelect,
  onEdit,
  onDelete
}) {
  // Stable callback references
  const handleSelect = useCallback(() => onSelect(token.id), [onSelect, token.id])
  const handleEdit = useCallback(() => onEdit(token), [onEdit, token])
  const handleDelete = useCallback(() => onDelete(token.id), [onDelete, token.id])

  return (
    // Component JSX with stable handlers
  )
})
```

#### 2. No List Virtualization

**Problem:** `TokenGrid` renders all tokens, even those off-screen.

**Current Implementation:**
```tsx
// Renders ALL tokens - performance issue at scale
{filteredAndSortedTokens.map(token => (
  <TokenCard key={token.id} token={token} />
))}
```

**Recommended Implementation:**
```tsx
import { useVirtualizer } from '@tanstack/react-virtual'

export function TokenGrid() {
  const parentRef = useRef<HTMLDivElement>(null)

  const virtualizer = useVirtualizer({
    count: filteredAndSortedTokens.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 200, // Token card height
    overscan: 5
  })

  return (
    <div ref={parentRef} style={{ height: '100%', overflow: 'auto' }}>
      <div style={{ height: `${virtualizer.getTotalSize()}px` }}>
        {virtualizer.getVirtualItems().map(virtualRow => (
          <TokenCard
            key={filteredAndSortedTokens[virtualRow.index].id}
            token={filteredAndSortedTokens[virtualRow.index]}
          />
        ))}
      </div>
    </div>
  )
}
```

### Component Refactoring Opportunities

#### 1. Extract Shared Logic

**Current:** Each visualizer calculates color values independently.

```tsx
// In AccessibilityVisualizer.tsx
const parseHex = (hex: string) => { /* implementation */ }
const getLuminance = (color: string) => { /* implementation */ }

// Same functions duplicated in HarmonyVisualizer.tsx
```

**Recommended:** Create shared color utilities.

```tsx
// utils/colorCalculations.ts
export const parseHex = (hex: string): RGB => { /* implementation */ }
export const getLuminance = (color: string): number => { /* implementation */ }
export const calculateContrast = (color1: string, color2: string): number => { /* */ }
export const generateHarmony = (baseHue: number, type: HarmonyType): number[] => { /* */ }
```

#### 2. Component Organization

**Current Structure:**
```
components/
├── AccessibilityVisualizer.tsx
├── BatchImageUploader.tsx
├── ColorDetailPanel.tsx
├── ColorNarrative.tsx
├── ... (18 more files)
```

**Recommended Structure:**
```
components/
├── color/
│   ├── AccessibilityVisualizer/
│   │   ├── index.tsx
│   │   ├── AccessibilityVisualizer.css
│   │   └── AccessibilityVisualizer.test.tsx
│   ├── HarmonyVisualizer/
│   ├── ColorNarrative/
│   └── ColorDetailPanel/
├── tokens/
│   ├── TokenCard/
│   ├── TokenGrid/
│   ├── TokenToolbar/
│   └── TokenInspectorSidebar/
├── workflow/
│   ├── SessionCreator/
│   ├── SessionWorkflow/
│   ├── BatchImageUploader/
│   └── ExportDownloader/
└── shared/
    ├── ImageUploader/
    └── ColorPaletteSelector/
```

### Code Splitting Strategy

#### Route-Based Splitting

```tsx
// App.tsx - Lazy load major routes
import { lazy, Suspense } from 'react'

const TokenExplorer = lazy(() => import('./features/TokenExplorer'))
const SessionWorkflow = lazy(() => import('./features/SessionWorkflow'))
const ExportManager = lazy(() => import('./features/ExportManager'))

function App() {
  return (
    <Suspense fallback={<LoadingSpinner />}>
      <Routes>
        <Route path="/tokens" element={<TokenExplorer />} />
        <Route path="/session" element={<SessionWorkflow />} />
        <Route path="/export" element={<ExportManager />} />
      </Routes>
    </Suspense>
  )
}
```

#### Component-Based Splitting

```tsx
// Lazy load heavy visualization components
const HarmonyVisualizer = lazy(() =>
  import('./components/HarmonyVisualizer').then(m => ({ default: m.HarmonyVisualizer }))
)

const AccessibilityVisualizer = lazy(() =>
  import('./components/AccessibilityVisualizer').then(m => ({ default: m.AccessibilityVisualizer }))
)

// Use in TokenInspectorSidebar
function TokenInspectorSidebar() {
  return (
    <Suspense fallback={<TabSkeleton />}>
      {activeTab === 'harmony' && <HarmonyVisualizer {...props} />}
      {activeTab === 'accessibility' && <AccessibilityVisualizer {...props} />}
    </Suspense>
  )
}
```

### Re-render Optimization Strategies

#### 1. Selective Store Subscriptions

**Current (Zustand):**
```tsx
// Subscribes to entire store - re-renders on any change
const { tokens, selectedTokenId, filters } = useTokenStore()
```

**Optimized:**
```tsx
// Subscribe only to needed slices
const tokens = useTokenStore(state => state.tokens)
const selectedTokenId = useTokenStore(state => state.selectedTokenId)
const filters = useTokenStore(state => state.filters)

// Or with shallow comparison for objects
import { shallow } from 'zustand/shallow'
const { filters, sortBy } = useTokenStore(
  state => ({ filters: state.filters, sortBy: state.sortBy }),
  shallow
)
```

#### 2. Derived State Memoization

**Current:**
```tsx
// Recalculates on every render
const filteredTokens = tokens.filter(t => matchesFilters(t, filters))
const sortedTokens = [...filteredTokens].sort(sortFn)
```

**Optimized:**
```tsx
const filteredAndSortedTokens = useMemo(() => {
  const filtered = tokens.filter(t => matchesFilters(t, filters))
  return [...filtered].sort(sortFn)
}, [tokens, filters, sortBy])
```

---

## TypeScript Enhancement

### Current Configuration Analysis

**Root tsconfig.json:**
```json
{
  "compilerOptions": {
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "forceConsistentCasingInFileNames": true
  }
}
```

**Frontend tsconfig.json:**
```json
{
  "compilerOptions": {
    "strict": true,
    "noUnusedLocals": false,      // ⚠️ Disabled
    "noUnusedParameters": false,  // ⚠️ Disabled
    "noImplicitReturns": true
  }
}
```

### Strict Mode Compliance Gaps

| Rule | Root | Frontend | Status |
|------|------|----------|--------|
| strict | ✅ | ✅ | ✅ Compliant |
| noImplicitAny | ✅ | ✅ | ✅ Compliant |
| strictNullChecks | ✅ | ✅ | ✅ Compliant |
| strictFunctionTypes | ✅ | ✅ | ✅ Compliant |
| noUnusedLocals | ✅ | ❌ | ⚠️ Inconsistent |
| noUnusedParameters | ✅ | ❌ | ⚠️ Inconsistent |
| noImplicitReturns | - | ✅ | ✅ Compliant |

### Type Safety Improvements

#### 1. Discriminated Unions for Token Types

**Current:**
```tsx
interface Token {
  type: 'color' | 'typography' | 'spacing'
  // All possible fields mixed together
  hex?: string
  fontFamily?: string
  value?: number
}
```

**Recommended:**
```tsx
interface BaseToken {
  id: string
  name: string
  type: TokenType
}

interface ColorToken extends BaseToken {
  type: 'color'
  hex: string
  rgb: string
  hsl: string
  wcagContrastWhite: number
  // ... color-specific fields
}

interface TypographyToken extends BaseToken {
  type: 'typography'
  fontFamily: string
  fontSize: number
  lineHeight: number
  // ... typography-specific fields
}

type Token = ColorToken | TypographyToken | SpacingToken
```

#### 2. Strict Event Handler Types

**Current:**
```tsx
const handleClick = (e) => {
  // e is implicitly 'any'
}
```

**Recommended:**
```tsx
const handleClick: React.MouseEventHandler<HTMLButtonElement> = (e) => {
  e.preventDefault()
  // e is properly typed
}

// Or inline
const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
  setValue(e.target.value)
}
```

#### 3. Generic Component Patterns

**For Reusable Components:**
```tsx
interface SelectProps<T> {
  options: T[]
  value: T
  onChange: (value: T) => void
  getLabel: (item: T) => string
  getValue: (item: T) => string | number
}

function Select<T>({ options, value, onChange, getLabel, getValue }: SelectProps<T>) {
  return (
    <select
      value={getValue(value)}
      onChange={(e) => {
        const selected = options.find(o => String(getValue(o)) === e.target.value)
        if (selected) onChange(selected)
      }}
    >
      {options.map(option => (
        <option key={getValue(option)} value={getValue(option)}>
          {getLabel(option)}
        </option>
      ))}
    </select>
  )
}
```

### Utility Type Usage

**Recommended Utility Types:**

```tsx
// Partial for optional updates
type TokenUpdate = Partial<Omit<ColorToken, 'id'>>

// Pick for specific properties
type TokenPreview = Pick<ColorToken, 'id' | 'name' | 'hex'>

// Record for maps
type TokensByType = Record<TokenType, Token[]>

// Extract/Exclude for unions
type ColorHarmony = Extract<HarmonyType, 'complementary' | 'triadic' | 'analogous'>

// ReturnType for inferred types
type StoreState = ReturnType<typeof useTokenStore.getState>
```

---

## Build & Bundle Optimization

### Current Vite Configuration

```typescript
// vite.config.ts
export default defineConfig({
  root: 'frontend',
  plugins: [react()],
  build: {
    outDir: '../dist',
    sourcemap: true
  },
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  }
})
```

### Recommended Optimizations

#### 1. Code Splitting Configuration

```typescript
export default defineConfig({
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          // Vendor chunks
          'react-vendor': ['react', 'react-dom'],
          'query-vendor': ['@tanstack/react-query'],
          'state-vendor': ['zustand'],

          // Feature chunks
          'color-visualizers': [
            './src/components/HarmonyVisualizer',
            './src/components/AccessibilityVisualizer',
            './src/components/ColorNarrative'
          ]
        }
      }
    },
    chunkSizeWarningLimit: 500
  }
})
```

#### 2. Asset Optimization

```typescript
export default defineConfig({
  build: {
    // Minification
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true,
        drop_debugger: true
      }
    },

    // Asset handling
    assetsInlineLimit: 4096, // Inline < 4KB assets

    // CSS optimization
    cssCodeSplit: true,
    cssMinify: true
  }
})
```

#### 3. Bundle Analysis

```typescript
import { visualizer } from 'rollup-plugin-visualizer'

export default defineConfig({
  plugins: [
    react(),
    visualizer({
      filename: 'dist/stats.html',
      open: true,
      gzipSize: true,
      brotliSize: true
    })
  ]
})
```

### Tree-Shaking Opportunities

**Ensure Proper Exports:**
```typescript
// ❌ Barrel exports can hurt tree-shaking
export * from './components'

// ✅ Named exports enable tree-shaking
export { TokenCard } from './components/TokenCard'
export { TokenGrid } from './components/TokenGrid'
```

**Mark Side-Effect Free:**
```json
// package.json
{
  "sideEffects": [
    "**/*.css",
    "./src/index.tsx"
  ]
}
```

### Bundle Size Reduction Strategies

1. **Analyze Current Bundle**
   - Add `rollup-plugin-visualizer`
   - Identify large dependencies
   - Find duplicate code

2. **Optimize Dependencies**
   - Use `date-fns` instead of `moment`
   - Use `lodash-es` with direct imports
   - Lazy load heavy visualizations

3. **Remove Unused Code**
   - Enable `noUnusedLocals/Parameters`
   - Remove commented code
   - Audit unused exports

4. **Compression**
   - Enable gzip/brotli compression
   - Use CDN for static assets
   - Optimize images

---

## W3C Design Token Integration

### Current Token Implementation

**Location:** `frontend/src/design/tokens.css`

```css
:root {
  /* Colors */
  --color-bg: #ffffff;
  --color-text-primary: #1a1a1a;
  --color-neutral-100: #f5f5f5;
  --color-error: #dc3545;

  /* Spacing */
  --space-sm: 0.5rem;
  --space-md: 1rem;
  --space-lg: 1.5rem;

  /* Typography */
  --font-size-sm: 0.875rem;
  --font-size-md: 1rem;
  --font-size-lg: 1.25rem;
}
```

### Token Consumption Patterns

**Current Usage (Inconsistent):**
```css
/* Some components use tokens */
.token-card {
  padding: var(--space-md);
  color: var(--color-text-primary);
}

/* Others use hardcoded values */
.harmony-visualizer {
  padding: 16px;  /* Should be var(--space-md) */
  color: #333;    /* Should be var(--color-text-primary) */
}
```

### Recommended Token Structure

**Align with W3C Design Token Format:**

```typescript
// types/tokens.ts
interface DesignToken {
  $value: string | number
  $type: 'color' | 'dimension' | 'fontFamily' | 'fontWeight' | 'duration' | 'cubicBezier'
  $description?: string
}

interface TokenGroup {
  [key: string]: DesignToken | TokenGroup
}

// tokens/color.tokens.json
{
  "color": {
    "primary": {
      "$value": "#0066cc",
      "$type": "color",
      "$description": "Primary brand color"
    },
    "text": {
      "primary": {
        "$value": "#1a1a1a",
        "$type": "color"
      },
      "secondary": {
        "$value": "#666666",
        "$type": "color"
      }
    }
  }
}
```

### Theme Switching Architecture

```typescript
// hooks/useTheme.ts
type Theme = 'light' | 'dark' | 'system'

export function useTheme() {
  const [theme, setTheme] = useState<Theme>('system')

  useEffect(() => {
    const root = document.documentElement

    if (theme === 'system') {
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
      root.setAttribute('data-theme', prefersDark ? 'dark' : 'light')
    } else {
      root.setAttribute('data-theme', theme)
    }
  }, [theme])

  return { theme, setTheme }
}
```

```css
/* tokens.css */
:root,
[data-theme="light"] {
  --color-bg: #ffffff;
  --color-text-primary: #1a1a1a;
}

[data-theme="dark"] {
  --color-bg: #1a1a1a;
  --color-text-primary: #ffffff;
}
```

### Token Typing Strategy

```typescript
// types/tokens.ts
export const tokens = {
  colors: {
    bg: 'var(--color-bg)',
    textPrimary: 'var(--color-text-primary)',
    // ... all colors
  },
  spacing: {
    sm: 'var(--space-sm)',
    md: 'var(--space-md)',
    lg: 'var(--space-lg)',
  },
  typography: {
    fontSizeSm: 'var(--font-size-sm)',
    fontSizeMd: 'var(--font-size-md)',
    fontSizeLg: 'var(--font-size-lg)',
  }
} as const

export type ColorToken = keyof typeof tokens.colors
export type SpacingToken = keyof typeof tokens.spacing
```

---

## Accessibility Improvements

### Current Accessibility State

**Test Coverage:**
- 1 dedicated a11y test file (`ColorDisplay.a11y.test.tsx`)
- 6 test cases covering basic semantic structure
- No automated WCAG validation

**Patterns Found:**

✅ **Strengths:**
- Semantic heading structure (`h3` in visualizers)
- Button elements for interactions
- WCAG contrast information displayed
- Text alternatives for visual elements

⚠️ **Concerns:**
- No ARIA labels on interactive elements
- Tab navigation not fully tested
- No focus management for modals/drawers
- Color-only indicators without text alternatives

### WCAG Compliance Gaps

#### Level A (Minimum)

| Criterion | Current | Gap |
|-----------|---------|-----|
| 1.1.1 Non-text Content | ⚠️ | SVG harmony wheel needs aria-label |
| 1.3.1 Info and Relationships | ✅ | Using semantic HTML |
| 2.1.1 Keyboard | ⚠️ | Tab order needs verification |
| 2.4.1 Bypass Blocks | ❌ | No skip links |
| 4.1.2 Name, Role, Value | ⚠️ | Custom controls need ARIA |

#### Level AA (Standard Target)

| Criterion | Current | Gap |
|-----------|---------|-----|
| 1.4.3 Contrast (Minimum) | ⚠️ | Need to audit all text |
| 1.4.4 Resize Text | ✅ | Using rem units |
| 2.4.6 Headings and Labels | ⚠️ | Some labels missing |
| 2.4.7 Focus Visible | ⚠️ | Custom focus styles needed |

### ARIA Implementation Review

**Current Pattern (Tabs):**
```tsx
// AccessibilityVisualizer.tsx - Missing ARIA
<div className="contrast-tabs">
  <button className={`tab ${activeTab === 'white' ? 'active' : ''}`}>
    On White
  </button>
</div>
```

**Recommended Pattern:**
```tsx
<div role="tablist" aria-label="Background options">
  <button
    role="tab"
    id="tab-white"
    aria-selected={activeTab === 'white'}
    aria-controls="panel-white"
    tabIndex={activeTab === 'white' ? 0 : -1}
    onClick={() => setActiveTab('white')}
  >
    On White
  </button>
</div>

<div
  role="tabpanel"
  id="panel-white"
  aria-labelledby="tab-white"
  hidden={activeTab !== 'white'}
>
  {/* Panel content */}
</div>
```

### Keyboard Navigation Audit

**Required Improvements:**

1. **Focus Trap for Modals/Drawers**
```tsx
import { FocusTrap } from '@headlessui/react'

function TokenPlaygroundDrawer() {
  return (
    <FocusTrap>
      <div className="drawer">
        {/* Drawer content */}
      </div>
    </FocusTrap>
  )
}
```

2. **Roving Tab Index for Grid**
```tsx
function TokenGrid() {
  const [focusIndex, setFocusIndex] = useState(0)

  const handleKeyDown = (e: KeyboardEvent) => {
    switch (e.key) {
      case 'ArrowRight':
        setFocusIndex(i => Math.min(i + 1, tokens.length - 1))
        break
      case 'ArrowLeft':
        setFocusIndex(i => Math.max(i - 1, 0))
        break
      // ... up/down for grid navigation
    }
  }

  return (
    <div role="grid" onKeyDown={handleKeyDown}>
      {tokens.map((token, i) => (
        <TokenCard
          key={token.id}
          tabIndex={i === focusIndex ? 0 : -1}
          ref={i === focusIndex ? focusRef : null}
        />
      ))}
    </div>
  )
}
```

### Screen Reader Compatibility

**Current Issues:**

1. **Color swatch announcements**
```tsx
// Current - not announced
<div className="color-swatch" style={{ background: hex }} />

// Improved - announced
<div
  className="color-swatch"
  style={{ background: hex }}
  role="img"
  aria-label={`Color swatch: ${name}, ${hex}`}
/>
```

2. **Dynamic content updates**
```tsx
// Use aria-live for dynamic updates
<div aria-live="polite" aria-atomic="true">
  {extractionProgress}% complete
</div>
```

### Color Contrast Validation

**The app itself should validate its own UI:**

```typescript
// utils/a11y.ts
export function validateContrast(foreground: string, background: string): {
  ratio: number
  passesAA: boolean
  passesAAA: boolean
  passesAALarge: boolean
} {
  const ratio = calculateContrast(foreground, background)

  return {
    ratio,
    passesAA: ratio >= 4.5,
    passesAAA: ratio >= 7,
    passesAALarge: ratio >= 3
  }
}
```

### Accessibility Testing Automation

**Add to CI Pipeline:**

```typescript
// vitest.setup.ts
import '@testing-library/jest-dom'
import { toHaveNoViolations } from 'jest-axe'

expect.extend(toHaveNoViolations)
```

```tsx
// Component.test.tsx
import { axe } from 'jest-axe'

it('should have no accessibility violations', async () => {
  const { container } = render(<AccessibilityVisualizer {...props} />)
  const results = await axe(container)
  expect(results).toHaveNoViolations()
})
```

---

## State Management Evaluation

### Current Zustand Implementation

**Store Structure:**
```typescript
// tokenStore.ts
interface TokenStore {
  // Data
  tokens: ColorToken[]
  tokenType: TokenType
  projectId: string | null

  // Selection
  selectedTokenId: string | null
  editingToken: ColorToken | null
  playgroundToken: ColorToken | null

  // View State
  filters: FilterState
  sortBy: SortOption
  viewMode: 'grid' | 'list'
  sidebarOpen: boolean
  playgroundOpen: boolean

  // Extraction Progress
  isExtracting: boolean
  extractionProgress: number
  extractionStage: string
  extractionTokenCount: number

  // Actions
  setTokens: (tokens: ColorToken[]) => void
  selectToken: (id: string) => void
  // ... more actions
}
```

### ✅ Strengths

1. **Minimal Boilerplate**
   - No reducers, action creators, or middleware
   - Direct state updates with `set()`

2. **Zero Provider Complexity**
   - No wrapping App in providers
   - Direct hook usage: `useTokenStore()`

3. **Excellent DevTools Support**
   - Zustand DevTools extension
   - State inspection and time-travel

4. **Selector Performance**
   - Can select specific slices
   - Shallow comparison support

### ⚠️ Areas for Improvement

1. **Store Size**
   - Single store handles all state
   - Consider splitting into domain stores

2. **Selector Optimization**
   - Components subscribe to too much state
   - Need more granular selectors

3. **Persistence**
   - No localStorage persistence
   - Filters/preferences reset on reload

### Recommended Store Split

```typescript
// stores/tokenStore.ts
export const useTokenStore = create<TokenState>((set) => ({
  tokens: [],
  selectedTokenId: null,
  setTokens: (tokens) => set({ tokens }),
  selectToken: (id) => set({ selectedTokenId: id })
}))

// stores/uiStore.ts
export const useUIStore = create<UIState>()(
  persist(
    (set) => ({
      sidebarOpen: true,
      viewMode: 'grid',
      filters: {},
      toggleSidebar: () => set(s => ({ sidebarOpen: !s.sidebarOpen }))
    }),
    { name: 'ui-preferences' }
  )
)

// stores/extractionStore.ts
export const useExtractionStore = create<ExtractionState>((set) => ({
  isExtracting: false,
  progress: 0,
  stage: '',
  startExtraction: () => set({ isExtracting: true, progress: 0 }),
  updateProgress: (progress, stage) => set({ progress, stage })
}))
```

### Computed/Derived State

```typescript
// stores/tokenStore.ts
export const useFilteredTokens = () => {
  const tokens = useTokenStore(s => s.tokens)
  const filters = useUIStore(s => s.filters)
  const sortBy = useUIStore(s => s.sortBy)

  return useMemo(() => {
    const filtered = tokens.filter(t => matchesFilters(t, filters))
    return [...filtered].sort(getSortFn(sortBy))
  }, [tokens, filters, sortBy])
}
```

---

## Summary of Frontend Recommendations

### Immediate Actions (This Sprint)

1. Add `React.memo` to TokenCard, HarmonyVisualizer, AccessibilityVisualizer
2. Enable `noUnusedLocals`/`noUnusedParameters` in frontend tsconfig
3. Add ARIA labels to interactive elements
4. Create shared color calculation utilities

### Short-term (Next 2 Sprints)

1. Implement code splitting for routes
2. Add list virtualization to TokenGrid
3. Configure bundle optimization in Vite
4. Split store into domain-specific stores

### Medium-term (This Quarter)

1. Reorganize component folder structure
2. Implement comprehensive accessibility tests
3. Add theme switching support
4. Create component documentation

---

*See [Testing Strategy](./04-testing-strategy.md) for frontend testing recommendations.*
