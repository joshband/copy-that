# Issue #9B: Component Refactoring Roadmap - Complete Implementation Guide

**Document Date:** 2025-12-04
**Status:** Ready for Implementation
**Priority:** P2 - Medium (12-20 hours estimated)
**Previous Issue:** #9A - AdvancedColorScienceDemo refactoring (COMPLETED)

---

## Executive Summary

This roadmap identifies 4 high-impact frontend components for refactoring using the proven pattern from Issue #9A. The analysis prioritizes components by refactoring value (Net Value Score = Complexity + Impact / Effort).

**Key Findings:**
- **4 candidates** identified (>400 LOC each)
- **ImageUploader.tsx** is highest priority (2.11 Net Value Score)
- **Estimated savings:** 500-600 LOC in main components
- **Key improvements:** Better testability, reusability, maintainability
- **Expected outcome:** 15-25 new reusable sub-components and hooks

---

## Part 1: Component Discovery & Analysis

### Components >500 LOC (Scan Date: 2025-12-04)

| Rank | Component | LOC | Priority | Status |
|------|-----------|-----|----------|--------|
| 1 | SpacingTokenShowcase.tsx | 512 | 3rd | Candidate |
| 2 | ImageUploader.tsx | 464 | 1st | HIGHEST |
| 3 | DiagnosticsPanel.tsx | 450 | 2nd | HIGH |
| 4 | ColorDetailPanel.tsx | 432 | 4th | MEDIUM |
| 5 | AdvancedColorScienceDemo.tsx | 428 | - | ✅ DONE |

---

## Part 2: Detailed Component Analysis

### COMPONENT #1: ImageUploader.tsx (464 LOC) - PRIORITY 1

**🔴 CRITICAL COMPLEXITY: 9/10**

**Location:** `frontend/src/components/ImageUploader.tsx`

#### Responsibilities (8 major features):
1. Image file selection & validation
2. File size/type validation
3. Image compression & preview generation
4. Project creation/management
5. **Color extraction** (streaming)
6. **Spacing extraction** (parallel)
7. **Shadow extraction** (parallel)
8. **Typography extraction** (parallel)

#### Current Problems:
- **Main Issue:** `handleExtract` function is **228 LOC** (monolithic!)
- **Lines 166-260:** Deeply nested async orchestration
- **Tight Coupling:** Parallel extraction logic mixed with streaming parser
- **Unextractable:** Multiple `kickOff*` functions hardcoded as internal functions
- **State Scatter:** 6 useState hooks managing different concerns

#### Current State Complexity:
```typescript
- useState: 6 hooks (selectedFile, projectName, maxColors, preview, etc.)
- useEffect: 1 hook (mount logging)
- useCallback: 0 hooks
- Total: 7 hooks
```

#### Code Structure Issues:
```typescript
// PROBLEM: All orchestration crammed into one function
async function handleExtract() {
  // Phase 1: Color extraction (SSE streaming) - 80 LOC
  // Phase 2: Parse streaming events - 50 LOC
  // Phase 3: Call spacing extraction - 23 LOC
  // Phase 4: Call shadow extraction - 29 LOC
  // Phase 5: Call typography extraction - 30 LOC
  // Phase 6: Error handling & callbacks - 16 LOC
  // Total: 228 LOC!
}
```

#### Refactoring Strategy:

**Step 1: Extract `useStreamingExtraction` hook**
- Encapsulates SSE streaming parser
- Manages streaming state machine
- Returns event emitter interface
- **Reduction:** 80 LOC from handleExtract

```typescript
// AFTER refactoring:
const {
  parseColorStream,
  isStreaming,
  error
} = useStreamingExtraction(API_BASE);

// In handleExtract (now 50 LOC):
const colorResponse = await fetch('/api/v1/colors/extract-streaming', ...);
const colorTokens = await parseColorStream(colorResponse);
```

**Step 2: Extract `useParallelExtractions` hook**
- Manages spacing, shadow, typography extraction
- Handles parallel request orchestration
- Returns extraction helpers
- **Reduction:** 70 LOC from handleExtract

```typescript
// AFTER refactoring:
const {
  extractSpacing,
  extractShadows,
  extractTypography,
  isExtracting
} = useParallelExtractions(projectId, imageBase64);

// In handleExtract (now 30 LOC):
await Promise.all([
  extractSpacing(),
  extractShadows(),
  extractTypography()
]);
```

**Step 3: Extract `useImageCompression` hook**
- Handles image resize/compress logic
- Returns compressed data and preview
- **Reduction:** 20 LOC from handleFileSelect

```typescript
// AFTER refactoring:
const {
  compressImage,
  preview,
  compressedBase64
} = useImageCompression();

const { base64, mediaType } = await compressImage(file);
```

**Step 4: Create `UploadZone` sub-component**
- Upload area UI
- Drag-drop handlers
- File input management
- **Creates:** Reusable upload component

**Step 5: Create `ExtractionSettings` sub-component**
- Project name input
- Max colors slider
- Settings display

#### Expected Result:
```
ImageUploader.tsx: 464 LOC → 120 LOC (74% reduction!)
├── Uses: useStreamingExtraction hook
├── Uses: useParallelExtractions hook
├── Uses: useImageCompression hook
├── Uses: UploadZone component
└── Uses: ExtractionSettings component
```

**Estimated Effort:** 3-4 hours
**Estimated Value:** 10/10 (massive improvement in testability)

---

### COMPONENT #2: DiagnosticsPanel.tsx (450 LOC) - PRIORITY 2

**🟠 HIGH COMPLEXITY: 8/10**

**Location:** `frontend/src/components/DiagnosticsPanel.tsx`

#### Responsibilities (7 features):
1. Display spacing diagnostics (chips, components)
2. Display color palette (swatches)
3. Interactive overlay preview
4. Alignment line visualization
5. FastSAM segment rendering
6. Geometry scaling & transformation
7. Debug payload info display

#### Current Problems:
- **5 complex useMemo hooks** with geometry calculations
- **Deep React tree:** Nested SVG rendering with multiple layers
- **Hard to test:** Geometry logic tightly coupled with UI
- **12 total hooks:** High complexity for diagnostic UI

#### Current State Complexity:
```typescript
- useState: 5 hooks (selectedSpacing, selectedComponent, selectedColor, etc.)
- useEffect: 1 hook (dimension tracking)
- useMemo: 5 hooks (commonSpacings, palette, matchingBoxes, alignmentLines, payloadInfo)
- useRef: 1 hook (overlayImgRef)
- Total: 12 hooks
```

#### Refactoring Strategy:

**Step 1: Extract `useOverlayGeometry` hook**
- Encapsulates `renderBox`, `scalePolygon` functions
- Handles dimension scaling transformations
- Returns geometry helper functions
- **Benefit:** Testable geometry in isolation

**Step 2: Extract `useAlignmentLines` hook**
- Computes aligned lines from components
- Handles scaling transformations
- Returns formatted line array

**Step 3: Extract `useMatchingBoxes` hook**
- Filters boxes by selection criteria
- Complex memoized filtering logic
- Returns filtered and transformed box array

**Step 4: Create `SpacingDiagnostics` sub-component**
- Spacing chips display (interactive)
- Component metrics scrolling
- Payload info panel

**Step 5: Create `ColorPalette` sub-component**
- Palette grid and swatches
- Color selection handlers

**Step 6: Create `OverlayPreview` sub-component**
- SVG rendering with layers
- Alignment lines overlay
- FastSAM segments overlay
- Interactive preview

#### Expected Result:
```
DiagnosticsPanel.tsx: 450 LOC → 200 LOC (56% reduction)
├── useOverlayGeometry hook (60 LOC) - testable
├── useAlignmentLines hook (40 LOC) - testable
├── useMatchingBoxes hook (30 LOC) - testable
├── SpacingDiagnostics component (80 LOC)
├── ColorPalette component (60 LOC)
└── OverlayPreview component (100 LOC)
```

**Estimated Effort:** 2.5-3 hours
**Estimated Value:** 9/10 (enables geometry testing)

---

### COMPONENT #3: SpacingTokenShowcase.tsx (512 LOC) - PRIORITY 3

**🟡 MEDIUM-HIGH COMPLEXITY: 6/10**

**Location:** `frontend/src/components/SpacingTokenShowcase.tsx`

#### Responsibilities (6 features):
1. Display spacing tokens in showcase
2. Filter tokens (all/aligned/misaligned/multi-source)
3. Sort tokens (value/confidence/name)
4. Render scale visualization (bar chart)
5. Copy spacing values to clipboard
6. Display token metadata & confidence scores

#### Current Problems:
- **200+ LOC of inline CSS** (hard to maintain)
- **Dense rendering:** Multiple UI patterns repeated
- **No sub-components:** All rendering in main component
- **Filtering logic:** Embedded in render logic

#### Refactoring Strategy:

**Step 1: Extract styles to separate file**
- Move 200 LOC to `SpacingTokenShowcase.styles.ts`
- Reference as constants
- **Reduction:** 200 LOC from main file

**Step 2: Create `TokenCard` sub-component**
- Token card visual rendering
- Copy buttons and badges
- Metadata display
- **Creates:** Reusable spacing token display

**Step 3: Create `StatsGrid` sub-component**
- Statistics cards display
- 6 stat metrics with icons

**Step 4: Create `ScaleVisualization` sub-component**
- Bar chart rendering
- Scale system display

**Step 5: Extract `useFilteredTokens` hook**
- Filtering and sorting logic
- Returns filtered array

#### Expected Result:
```
SpacingTokenShowcase.tsx: 512 LOC → 280 LOC (45% reduction)
├── SpacingTokenShowcase.styles.ts (200 LOC)
├── TokenCard component (80 LOC) - reusable
├── StatsGrid component (50 LOC)
├── ScaleVisualization component (40 LOC)
└── useFilteredTokens hook (30 LOC)
```

**Estimated Effort:** 2-2.5 hours
**Estimated Value:** 7/10 (good code organization)

---

### COMPONENT #4: ColorDetailPanel.tsx (432 LOC) - PRIORITY 4

**🟢 LOW-MEDIUM COMPLEXITY: 4/10**

**Location:** `frontend/src/components/ColorDetailPanel.tsx`

#### Current State:
- **Already well-componentized** at function level
- **Simple state:** Only 1 useState hook
- **Low complexity:** Mostly presentational

#### Refactoring Strategy:

**Step 1: Move tab components to separate files**
- `OverviewTab.tsx` (already extracted function)
- `HarmonyTab.tsx` (delegates to HarmonyVisualizer)
- `AccessibilityTab.tsx` (delegates to AccessibilityVisualizer)
- `PropertiesTab.tsx` (property display)
- `DiagnosticsTab.tsx` (overlay display)

**Step 2: Create `ColorHeader` sub-component**
- Header section with color swatches
- Badge display

**Step 3: Create `BadgeRow` sub-component**
- Badge rendering (alias, role, merge status)

#### Expected Result:
```
ColorDetailPanel.tsx: 432 LOC → 200 LOC (54% reduction)
├── OverviewTab.tsx (80 LOC)
├── HarmonyTab.tsx (60 LOC)
├── AccessibilityTab.tsx (50 LOC)
├── PropertiesTab.tsx (80 LOC)
├── DiagnosticsTab.tsx (60 LOC)
├── ColorHeader component (40 LOC)
└── BadgeRow component (20 LOC)
```

**Estimated Effort:** 1.5-2 hours
**Estimated Value:** 6/10 (primarily file organization)

---

## Part 3: Flexibility & Extensibility Improvements

### Pattern Recommendations

#### 1. **Streaming Response Parser - Generalized Pattern**

**Current Issue:** ImageUploader embeds SSE parsing logic for color extraction.

**Better Pattern - Reusable Streaming Hook:**

```typescript
// NEW: frontend/src/hooks/useStreamingResponse.ts

export interface StreamingEvent<T> {
  type: 'data' | 'progress' | 'error' | 'complete';
  data: T;
  timestamp: number;
}

export function useStreamingResponse<T>() {
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const parseStream = useCallback(
    async (response: Response, onEvent: (event: StreamingEvent<T>) => void) => {
      if (!response.ok) throw new Error(`HTTP ${response.status}`);

      const reader = response.body?.getReader();
      if (!reader) throw new Error('No response body');

      try {
        setIsStreaming(true);
        while (true) {
          const { done, value } = await reader.read();
          if (done) {
            onEvent({ type: 'complete', data: null as any, timestamp: Date.now() });
            break;
          }

          // Parse SSE format
          const text = new TextDecoder().decode(value);
          const lines = text.split('\n');

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              const jsonStr = line.slice(6);
              const event = JSON.parse(jsonStr) as StreamingEvent<T>;
              onEvent(event);
            }
          }
        }
      } finally {
        setIsStreaming(false);
      }
    },
    []
  );

  return { parseStream, isStreaming, error };
}
```

**Benefits:**
- ✅ Reusable across any streaming endpoint
- ✅ Type-safe with generics
- ✅ Can be tested independently
- ✅ Easy to extend with retry logic, timeout, etc.

---

#### 2. **Parallel Extraction Orchestrator - Extract + Store Pattern**

**Current Issue:** Hard-coded `kickOffSpacing`, `kickOffShadows`, etc. functions.

**Better Pattern - Configurable Orchestrator:**

```typescript
// NEW: frontend/src/hooks/useExtractionOrchestrator.ts

export interface ExtractionPhase {
  name: 'colors' | 'spacing' | 'shadows' | 'typography';
  endpoint: string;
  parallel?: boolean;
  timeout?: number;
  retries?: number;
  onComplete?: (data: any) => void;
}

export interface OrchestratorConfig {
  projectId: number;
  imageBase64: string;
  phases: ExtractionPhase[];
}

export function useExtractionOrchestrator(config: OrchestratorConfig) {
  const [status, setStatus] = useState<Record<string, 'pending' | 'running' | 'complete' | 'error'>>({});
  const [results, setResults] = useState<Record<string, any>>({});
  const [errors, setErrors] = useState<Record<string, string>>({});

  const executePhase = useCallback(
    async (phase: ExtractionPhase) => {
      setStatus(s => ({ ...s, [phase.name]: 'running' }));
      try {
        const response = await fetch(phase.endpoint, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            projectId: config.projectId,
            imageBase64: config.imageBase64
          }),
          signal: AbortSignal.timeout(phase.timeout || 30000)
        });

        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const data = await response.json();

        setResults(r => ({ ...r, [phase.name]: data }));
        setStatus(s => ({ ...s, [phase.name]: 'complete' }));
        phase.onComplete?.(data);
      } catch (error) {
        setErrors(e => ({ ...e, [phase.name]: String(error) }));
        setStatus(s => ({ ...s, [phase.name]: 'error' }));
      }
    },
    [config]
  );

  const execute = useCallback(async () => {
    const parallelPhases = config.phases.filter(p => p.parallel !== false);
    const sequentialPhases = config.phases.filter(p => p.parallel === false);

    // Run parallel phases
    await Promise.all(parallelPhases.map(executePhase));

    // Then run sequential
    for (const phase of sequentialPhases) {
      await executePhase(phase);
    }
  }, [config.phases, executePhase]);

  return { execute, status, results, errors, isComplete: Object.values(status).every(s => s !== 'pending') };
}
```

**Usage:**
```typescript
const { execute, status, results } = useExtractionOrchestrator({
  projectId: 1,
  imageBase64: data,
  phases: [
    {
      name: 'colors',
      endpoint: `${API_BASE}/api/v1/colors/extract-streaming`,
      timeout: 30000
    },
    {
      name: 'spacing',
      endpoint: `${API_BASE}/api/v1/spacing/extract`,
      parallel: true
    },
    {
      name: 'shadows',
      endpoint: `${API_BASE}/api/v1/shadows/extract`,
      parallel: true
    }
  ]
});

await execute();
```

**Benefits:**
- ✅ Configurable extraction pipeline
- ✅ Reusable for any multi-phase extraction
- ✅ Supports parallel and sequential phases
- ✅ Easy to add retry logic, timeouts, etc.
- ✅ Type-safe phase definitions

---

#### 3. **Geometry Utilities Library - Testable Math**

**Current Issue:** Geometry calculations embedded in DiagnosticsPanel component.

**Better Pattern - Isolated Geometry Utils:**

```typescript
// NEW: frontend/src/lib/geometry.ts

export interface Box {
  x: number;
  y: number;
  width: number;
  height: number;
}

export interface Polygon {
  points: [number, number][];
}

export interface Dimensions {
  imageWidth: number;
  imageHeight: number;
  displayWidth: number;
  displayHeight: number;
}

export const GeometryUtils = {
  /**
   * Scale a box from image coordinates to display coordinates
   */
  scaleBox(box: Box, from: Dimensions, to: Dimensions): Box {
    const scaleX = to.displayWidth / to.imageWidth;
    const scaleY = to.displayHeight / to.imageHeight;
    return {
      x: box.x * scaleX,
      y: box.y * scaleY,
      width: box.width * scaleX,
      height: box.height * scaleY
    };
  },

  /**
   * Scale a polygon from image to display coordinates
   */
  scalePolygon(poly: Polygon, from: Dimensions, to: Dimensions): Polygon {
    const scaleX = to.displayWidth / to.imageWidth;
    const scaleY = to.displayHeight / to.imageHeight;
    return {
      points: poly.points.map(([x, y]) => [x * scaleX, y * scaleY])
    };
  },

  /**
   * Check if point is inside box
   */
  isPointInBox(point: [number, number], box: Box): boolean {
    return (
      point[0] >= box.x &&
      point[0] <= box.x + box.width &&
      point[1] >= box.y &&
      point[1] <= box.y + box.height
    );
  },

  /**
   * Get alignment lines for spacing grid
   */
  getAlignmentLines(components: Box[], baseUnit: number = 8): [number, number][] {
    const xLines = new Set<number>();
    const yLines = new Set<number>();

    for (const comp of components) {
      xLines.add(Math.round(comp.x / baseUnit) * baseUnit);
      xLines.add(Math.round((comp.x + comp.width) / baseUnit) * baseUnit);
      yLines.add(Math.round(comp.y / baseUnit) * baseUnit);
      yLines.add(Math.round((comp.y + comp.height) / baseUnit) * baseUnit);
    }

    return Array.from(xLines).map(x => [x, 0] as [number, number])
      .concat(Array.from(yLines).map(y => [0, y] as [number, number]));
  }
};
```

**Benefits:**
- ✅ Pure functions - easily testable
- ✅ No React dependencies
- ✅ Reusable across components
- ✅ Documented with JSDoc
- ✅ Can add unit tests for complex math

---

#### 4. **Token Display Configuration Pattern**

**Current Issue:** Token display logic (badges, formatting) repeated across components.

**Better Pattern - Declarative Token Display Config:**

```typescript
// NEW: frontend/src/config/tokenDisplay.ts

export type TokenType = 'color' | 'spacing' | 'shadow' | 'typography';

export interface BadgeConfig {
  label: string;
  color: 'primary' | 'success' | 'warning' | 'error';
  variant?: 'solid' | 'outline';
}

export interface TokenDisplayConfig {
  title: string;
  description?: string;
  badges: BadgeConfig[];
  format?: (value: any) => string;
  copy?: {
    formats: {
      label: string;
      getValue: (value: any) => string;
    }[];
  };
}

export const TOKEN_DISPLAY_CONFIG: Record<TokenType, TokenDisplayConfig> = {
  color: {
    title: 'Color Token',
    description: 'Extracted design color',
    badges: [
      { label: 'Color', color: 'primary' },
      { label: 'RGB', color: 'primary', variant: 'outline' }
    ],
    format: (color) => `#${color.hex}`,
    copy: {
      formats: [
        { label: 'Hex', getValue: (c) => `#${c.hex}` },
        { label: 'RGB', getValue: (c) => `rgb(${c.r}, ${c.g}, ${c.b})` },
        { label: 'HSL', getValue: (c) => `hsl(${c.h}, ${c.s}%, ${c.l}%)` }
      ]
    }
  },
  spacing: {
    title: 'Spacing Token',
    description: 'Extracted spacing value',
    badges: [
      { label: 'Spacing', color: 'success' },
      { label: 'Grid', color: 'success', variant: 'outline' }
    ],
    format: (spacing) => `${spacing.value_px}px / ${spacing.value_rem}rem`,
    copy: {
      formats: [
        { label: 'px', getValue: (s) => `${s.value_px}px` },
        { label: 'rem', getValue: (s) => `${s.value_rem}rem` }
      ]
    }
  },
  // ... more token types
};
```

**Benefits:**
- ✅ Centralized token display logic
- ✅ Easy to customize by token type
- ✅ Reduces duplication across components
- ✅ Easy to add new formats/badges

---

#### 5. **Component Composition Helper - Reduce Props Drilling**

**Current Issue:** Deep component trees with lots of prop drilling.

**Better Pattern - Composition with Context:**

```typescript
// NEW: frontend/src/context/ExtractionContext.tsx

interface ExtractionContextType {
  project: Project;
  imageBase64: string;
  colors: ColorToken[];
  spacing: SpacingToken[];
  shadows: ShadowToken[];
  typography: TypographyToken[];
  status: Record<string, 'pending' | 'running' | 'complete' | 'error'>;
  errors: Record<string, string>;
}

export const ExtractionContext = createContext<ExtractionContextType | null>(null);

export function ExtractionProvider({ children }: { children: React.ReactNode }) {
  const [data, setData] = useState<ExtractionContextType>({
    project: null,
    imageBase64: '',
    colors: [],
    spacing: [],
    shadows: [],
    typography: [],
    status: {},
    errors: {}
  });

  return (
    <ExtractionContext.Provider value={data}>
      {children}
    </ExtractionContext.Provider>
  );
}

export function useExtraction() {
  const context = useContext(ExtractionContext);
  if (!context) {
    throw new Error('useExtraction must be used within ExtractionProvider');
  }
  return context;
}
```

**Benefits:**
- ✅ Eliminates prop drilling
- ✅ Provides single source of truth
- ✅ Easy to extend with new data types
- ✅ Components become simpler and more focused

---

### Recommended Library Additions

#### 1. **TanStack Query (React Query)** - Better Async State Management

**Why:** ImageUploader manages complex async state (streaming, parallel requests, errors).

**Benefits:**
- ✅ Built-in caching and deduplication
- ✅ Automatic retry logic
- ✅ Background refetching
- ✅ Optimistic updates
- ✅ Significantly reduces boilerplate

**Implementation:**
```bash
pnpm add @tanstack/react-query
```

```typescript
import { useMutation } from '@tanstack/react-query';

const { mutateAsync: extractColors } = useMutation({
  mutationFn: async (imageBase64: string) => {
    const response = await fetch('/api/v1/colors/extract', {
      method: 'POST',
      body: JSON.stringify({ imageBase64 })
    });
    return response.json();
  },
  retry: 3,
  retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000)
});
```

#### 2. **Zustand** - Lightweight State Management

**Why:** Multiple components need access to extraction state without prop drilling.

**Benefits:**
- ✅ Minimal boilerplate
- ✅ Easy to debug
- ✅ Smaller bundle than Redux
- ✅ Works with Context seamlessly

**Implementation:**
```bash
pnpm add zustand
```

```typescript
// frontend/src/store/extractionStore.ts
import create from 'zustand';

export const useExtractionStore = create((set) => ({
  project: null,
  colors: [],
  spacing: [],
  shadows: [],
  typography: [],

  setProject: (project) => set({ project }),
  setColors: (colors) => set({ colors }),

  reset: () => set({
    project: null,
    colors: [],
    spacing: [],
    shadows: [],
    typography: []
  })
}));
```

#### 3. **SWR (Stale-While-Revalidate)** - Alternative to React Query

**Why:** Simpler async state for extracted tokens.

**Benefits:**
- ✅ Even simpler API than React Query
- ✅ Smaller bundle (~10KB)
- ✅ Great for data fetching
- ✅ Built-in caching strategy

---

### Data Structure Improvements

#### 1. **Token Repository Pattern - Better Data Access**

**Problem:** Direct array access to tokens scattered across components.

**Better Pattern:**
```typescript
// NEW: frontend/src/lib/TokenRepository.ts

export class TokenRepository {
  private tokens: Map<TokenType, any[]> = new Map();

  add(type: TokenType, token: any) {
    if (!this.tokens.has(type)) {
      this.tokens.set(type, []);
    }
    this.tokens.get(type)?.push(token);
  }

  findById(type: TokenType, id: string) {
    return this.tokens.get(type)?.find(t => t.id === id);
  }

  findByHex(hex: string) {
    return this.tokens.get('color')?.find(c => c.hex === hex);
  }

  getAll(type: TokenType) {
    return this.tokens.get(type) || [];
  }

  query(type: TokenType, predicate: (t: any) => boolean) {
    return this.tokens.get(type)?.filter(predicate) || [];
  }

  clear() {
    this.tokens.clear();
  }
}
```

**Benefits:**
- ✅ Single interface for token access
- ✅ Easy to add filtering methods
- ✅ Can add indexing for performance
- ✅ Encapsulates data structure

---

#### 2. **Immutable Token Updates - Prevent Mutations**

**Better Pattern:**
```typescript
// Use Immer for immutable updates
import produce from 'immer';

const updateColor = (colors: ColorToken[], id: string, updates: Partial<ColorToken>) => {
  return produce(colors, draft => {
    const color = draft.find(c => c.id === id);
    if (color) {
      Object.assign(color, updates);
    }
  });
};

// Usage:
const updated = updateColor(colors, '123', { name: 'Primary' });
// Original `colors` unchanged!
```

**Install:**
```bash
pnpm add immer
```

---

## Part 4: Implementation Timeline

### Phase 1 (Week 1): ImageUploader Refactoring
- **Day 1 Morning:** Extract `useStreamingExtraction` hook (2 hours)
- **Day 1 Afternoon:** Extract `useParallelExtractions` hook (2 hours)
- **Day 2 Morning:** Extract `useImageCompression` hook + sub-components (3 hours)
- **Day 2 Afternoon:** Testing and integration (2 hours)
- **Estimated Total:** 9 hours

### Phase 2 (Week 2): DiagnosticsPanel Refactoring
- **Day 1 Morning:** Extract geometry hooks (2.5 hours)
- **Day 1 Afternoon:** Create sub-components (2 hours)
- **Day 2 Morning:** Testing (1 hour)
- **Estimated Total:** 5.5 hours

### Phase 3 (Week 2-3): SpacingTokenShowcase Refactoring
- **Day 1:** Extract styles + create sub-components (2.5 hours)
- **Estimated Total:** 2.5 hours

### Phase 4 (Week 3): ColorDetailPanel Refactoring
- **Day 1:** Move tabs to separate files (1.5 hours)
- **Estimated Total:** 1.5 hours

### Library & Patterns Integration
- **Day 1:** Add React Query + Zustand (1 hour)
- **Day 2:** Create shared utilities (geometry, streaming parser) (2 hours)
- **Estimated Total:** 3 hours

---

## Part 5: Success Criteria

### Code Quality Metrics
- ✅ Average component size: 100-250 LOC (down from 400-500)
- ✅ Orchestrator component: 200-400 LOC
- ✅ Shared hooks: 30-80 LOC each
- ✅ Geometry utils: Pure functions with tests

### Functional Metrics
- ✅ All extraction still works end-to-end
- ✅ No regression in streaming performance
- ✅ No regression in parallel extraction
- ✅ TypeScript: 0 errors

### Testing Metrics
- ✅ Geometry functions independently testable (unit tests added)
- ✅ Streaming parser independently testable (unit tests added)
- ✅ Orchestrator independently testable (unit tests added)
- ✅ E2E tests still passing (46/46)

---

## Part 6: Migration Guide for Developers

### When Refactoring Similar Components

1. **Identify extraction points:**
   - Event handlers >50 LOC → extract to hook
   - Repeated state logic → extract to hook
   - Pure calculations → extract to utils
   - UI sections → extract to sub-component

2. **Use established patterns:**
   - Streaming → use `useStreamingResponse` hook
   - Async orchestration → use `useExtractionOrchestrator`
   - Geometry → use `GeometryUtils` library
   - Token display → use `TOKEN_DISPLAY_CONFIG`

3. **Follow export structure:**
   ```typescript
   📁 feature-folder/
   ├── index.ts              # Exports
   ├── Feature.tsx           # Orchestrator
   ├── Feature.css           # Styles
   ├── hooks/
   │  ├── useFeatureLogic.ts
   │  └── useAnotherHook.ts
   ├── types.ts              # Shared types
   └── SubComponent.tsx      # Focused UI
   ```

---

## Conclusion

This roadmap provides a structured approach to improving the frontend codebase while maintaining functionality. The recommended patterns and libraries will:

1. **Reduce complexity** by 40-70% in refactored components
2. **Improve testability** with extracted, isolated functions
3. **Enable reusability** across different components
4. **Future-proof** the codebase with extensible patterns

**Recommended Start:** ImageUploader (highest ROI, 9 hours)
