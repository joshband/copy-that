# React Frontend Architecture: Token Explorer

**Status:** Design Phase Complete, Implementation Ready
**Date:** 2025-11-20
**Version:** v0.1.0 (Architecture Plan)

## Overview

Generic, schema-driven React frontend for Token Explorer. Works for:
- **Color Tokens** (reference implementation)
- **Future:** Typography, Spacing, Shadow, Animation tokens
- **Goal:** 80% code reuse across token types

---

## Core Architecture Principles

### 1. Schema-Driven UI Rendering

**Never hardcode token-specific logic. Let schema drive everything.**

```typescript
// Single source of truth: tokenTypeRegistry
const tokenTypeRegistry: Record<TokenType, TokenTypeSchema> = {
  color: {
    name: 'Color',
    icon: PaletteIcon,
    primaryVisual: ColorTokenVisual,
    formatTabs: [
      { name: 'RGB', component: RGBFormatTab },
      { name: 'HSL', component: HSLFormatTab },
      { name: 'Oklch', component: OklchFormatTab },
    ],
    playgroundTabs: [
      { name: 'Adjuster', component: ColorAdjuster },
      { name: 'Harmony', component: HarmonyVisualizer },
      { name: 'Temperature', component: TemperatureVisualizer },
      { name: 'Saturation', component: SaturationVisualizer },
    ],
    filters: [
      { key: 'temperature', label: 'Temperature', values: ['cool', 'neutral', 'warm'] },
      { key: 'saturation', label: 'Saturation', values: ['vivid', 'moderate', 'muted'] },
    ],
  },

  typography: {
    name: 'Typography',
    icon: TypeIcon,
    primaryVisual: TypographyTokenVisual,
    formatTabs: [
      { name: 'Tech', component: TechFormatTab },
      { name: 'Design', component: DesignFormatTab },
    ],
    playgroundTabs: [
      { name: 'Adjuster', component: TypographyAdjuster },
      { name: 'Hierarchy', component: HierarchyVisualizer },
      { name: 'Contrast', component: ContrastChecker },
      { name: 'Preview', component: PreviewInContext },
    ],
    filters: [
      { key: 'fontFamily', label: 'Font', values: [...] },
      { key: 'weight', label: 'Weight', values: ['300', '400', '600', '700'] },
    ],
  },

  // ... spacing, shadow, animation follow same pattern
};

// Usage: Zero hardcoding
const TokenCard = ({ token, tokenType }: Props) => {
  const schema = tokenTypeRegistry[tokenType];
  const PrimaryVisual = schema.primaryVisual;

  return (
    <Card>
      <PrimaryVisual token={token} />
      <SemanticName token={token} />
      <ConfidenceBadge confidence={token.confidence} />
    </Card>
  );
};
```

### 2. State Management with Zustand

**Single, centralized store. No prop drilling.**

```typescript
import { create } from 'zustand';

interface TokenState {
  // Data
  tokens: Token[];
  tokenType: TokenType;
  projectId: string;

  // Selection & Editing
  selectedTokenId: string | null;
  editingToken: Partial<Token> | null;
  playgroundToken: Partial<Token> | null;

  // View State
  filters: Record<string, string>;
  sortBy: SortOption;
  viewMode: 'grid' | 'list' | 'table';
  sidebarOpen: boolean;
  playgroundOpen: boolean;
  playgroundActiveTab: string;

  // Extraction State
  isExtracting: boolean;
  extractionProgress: number;
  extractionStage: string;
  extractionTokenCount: number;

  // Actions
  setTokens: (tokens: Token[]) => void;
  selectToken: (id: string | null) => void;
  startEditing: (token: Token) => void;
  updateEditingField: (field: string, value: unknown) => void;
  saveEdit: () => Promise<void>;
  cancelEdit: () => void;
  deleteToken: (id: string) => Promise<void>;
  duplicateToken: (id: string) => Promise<void>;
  applyPlaygroundChanges: () => void;
  resetPlayground: () => void;
  setFilter: (key: string, value: string) => void;
  clearFilters: () => void;
  setSortBy: (option: SortOption) => void;
  setViewMode: (mode: 'grid' | 'list' | 'table') => void;
  toggleSidebar: () => void;
  togglePlayground: () => void;
  setPlaygroundTab: (tab: string) => void;
  updateExtractionProgress: (progress: number, stage: string, count: number) => void;
  completeExtraction: () => void;
}

export const useTokenStore = create<TokenState>((set) => ({
  // Initial state
  tokens: [],
  tokenType: 'color',
  projectId: '',
  selectedTokenId: null,
  editingToken: null,
  playgroundToken: null,
  filters: {},
  sortBy: 'hue',
  viewMode: 'grid',
  sidebarOpen: false,
  playgroundOpen: false,
  playgroundActiveTab: 'adjuster',
  isExtracting: false,
  extractionProgress: 0,
  extractionStage: 'uploading',
  extractionTokenCount: 0,

  // Actions
  selectToken: (id) => set({ selectedTokenId: id }),
  startEditing: (token) => set({ editingToken: { ...token } }),
  updateEditingField: (field, value) =>
    set((state) => ({
      editingToken: { ...state.editingToken, [field]: value },
    })),
  saveEdit: async () => {
    // Call API, invalidate query
  },
  // ... etc
}));
```

### 3. Component Hierarchy

```
src/components/
├── tokens/
│   ├── TokenExplorer.tsx              ← Main container
│   ├── UploadSection.tsx              ← Generic upload
│   ├── ExtractionProgress.tsx         ← Generic progress
│   ├── MainLayout.tsx                 ← Flex layout
│   ├── TokenGrid.tsx                  ← Generic grid (schema-driven)
│   ├── TokenCard.tsx                  ← Generic card (schema-driven)
│   ├── Toolbar.tsx                    ← Generic toolbar (schema-driven)
│   ├── TokenInspectorSidebar.tsx      ← Generic sidebar (schema-driven)
│   ├── TokenPlaygroundDrawer.tsx      ← Generic drawer (schema-driven)
│   ├── color/
│   │   ├── ColorTokenVisual.tsx       ← Large swatch preview
│   │   ├── ColorFormatTabs.tsx        ← RGB/HSL/Oklch tabs
│   │   ├── ColorAdjuster.tsx          ← HSL sliders
│   │   ├── HarmonyVisualizer.tsx      ← Color wheel
│   │   ├── TemperatureVisualizer.tsx  ← Warm/cool spectrum
│   │   ├── SaturationVisualizer.tsx   ← Saturation scale
│   │   └── ColorRelationshipsPanel.tsx
│   ├── typography/ (future - same structure)
│   ├── spacing/ (future)
│   └── shared/
│       ├── SemanticNameEditor.tsx     ← Editable field with suggestions
│       └── ConfidenceBreakdown.tsx    ← Multi-source AI breakdown
├── hooks/
│   ├── useTokens.ts                   ← React Query hook (generic)
│   ├── useToken.ts                    ← Single token with edit state
│   ├── useTokenFilters.ts             ← Filter logic
│   ├── useExtractionProgress.ts       ← WebSocket progress
│   ├── useExport.ts                   ← Export functionality
│   └── useSemanticNameSuggestions.ts  ← AI suggestions
├── store/
│   └── tokenStore.ts                  ← Zustand (single source of truth)
├── types/
│   ├── generated/
│   │   ├── color.zod.ts               ← From backend schema
│   │   ├── typography.zod.ts          ← Future
│   │   └── spacing.zod.ts             ← Future
│   ├── token.ts                       ← Generic token interfaces
│   └── registry.ts                    ← TokenType registry
├── config/
│   └── tokenTypeRegistry.ts           ← Schema-driven registry
├── utils/
│   ├── tokenFilters.ts                ← Filter functions
│   ├── tokenSort.ts                   ← Sort functions
│   └── colorUtils.ts                  ← Color-specific utilities
└── api/
    └── tokenApi.ts                    ← API calls (React Query)
```

---

## State Management Flow

```
User Action (Click, Edit, etc)
        ↓
Zustand Store Updates
        ↓
Component Re-renders (only affected)
        ↓
If API call needed: React Query handles it
        ↓
Cache invalidated → Store re-syncs
```

**Example: Select a token**

```typescript
// User clicks a card
<TokenCard onClick={() => useTokenStore.getState().selectToken(token.id)} />

// Store updates
const selectedTokenId = useTokenStore((state) => state.selectedTokenId);

// Sidebar & Inspector re-render automatically
useEffect(() => {
  if (!selectedTokenId) return;

  const token = tokens.find((t) => t.id === selectedTokenId);
  // Show inspector for this token
}, [selectedTokenId, tokens]);
```

---

## API Integration with React Query

**All tokens are cached, stale for 5 minutes.**

```typescript
// src/api/tokenApi.ts

export const useColorTokens = (projectId: string) => {
  return useQuery({
    queryKey: ['tokens', 'color', projectId],
    queryFn: () => api.get(`/api/projects/${projectId}/colors`),
    staleTime: 5 * 60 * 1000,  // 5 minutes
    gcTime: 10 * 60 * 1000,    // 10 minutes (garbage collect)
  });
};

export const useUpdateColorToken = (projectId: string) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: ColorToken) =>
      api.put(`/api/projects/${projectId}/colors/${data.id}`, data),
    onSuccess: () => {
      // Invalidate cache, refetch
      queryClient.invalidateQueries({
        queryKey: ['tokens', 'color', projectId],
      });
    },
  });
};

export const useExtractTokens = (projectId: string) => {
  return useMutation({
    mutationFn: (files: File[]) => {
      const formData = new FormData();
      files.forEach((file) => formData.append('images', file));
      return api.post(`/api/projects/${projectId}/colors/extract`, formData);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ['tokens', 'color', projectId],
      });
    },
  });
};

// Generic pattern for ANY token type
export const useTokens = (projectId: string, tokenType: TokenType) => {
  return useQuery({
    queryKey: ['tokens', tokenType, projectId],
    queryFn: () => api.get(`/api/projects/${projectId}/${tokenType}`),
    staleTime: 5 * 60 * 1000,
  });
};
```

---

## WebSocket Integration: Real-Time Extraction

**Users see live progress as tokens extract.**

```typescript
// src/hooks/useExtractionProgress.ts

export const useExtractionProgress = (projectId: string, enabled: boolean) => {
  const store = useTokenStore();

  useEffect(() => {
    if (!enabled) return;

    const ws = new WebSocket(
      `${WS_URL}/api/projects/${projectId}/colors/extract/progress`
    );

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);

      if (data.type === 'progress') {
        store.updateExtractionProgress(
          data.percentage,
          data.stage,
          data.tokenCount
        );
      }

      if (data.type === 'complete') {
        store.completeExtraction();
        // Refetch tokens
        queryClient.invalidateQueries({
          queryKey: ['tokens', 'color', projectId],
        });
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    return () => ws.close();
  }, [enabled, projectId, store, queryClient]);
};
```

---

## Performance Optimization

### 1. Virtualization for Large Token Lists

```typescript
// src/components/tokens/TokenGrid.tsx

import { useVirtualizer } from '@tanstack/react-virtual';

export const TokenGrid = ({ tokens }: Props) => {
  const parentRef = useRef<HTMLDivElement>(null);

  const virtualizer = useVirtualizer({
    count: tokens.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 200,  // Card height in px
    overscan: 10,             // Render 10 items beyond visible
  });

  const virtualItems = virtualizer.getVirtualItems();
  const totalSize = virtualizer.getTotalSize();

  return (
    <div
      ref={parentRef}
      style={{
        height: '100vh',
        overflow: 'auto',
      }}
    >
      <div style={{ height: `${totalSize}px`, position: 'relative' }}>
        {virtualItems.map((virtualItem) => (
          <div
            key={tokens[virtualItem.index].id}
            style={{
              transform: `translateY(${virtualItem.start}px)`,
            }}
          >
            <TokenCard token={tokens[virtualItem.index]} />
          </div>
        ))}
      </div>
    </div>
  );
};
```

**Result:** 1000 tokens visible, but only 20-30 rendered in DOM.

### 2. Component Memoization

```typescript
// TokenCard only re-renders if token content changed
export const TokenCard = React.memo(
  ({ token, isSelected, onSelect }: Props) => {
    return (
      <div onClick={() => onSelect(token.id)}>
        {/* Card content */}
      </div>
    );
  },
  (prev, next) => {
    // Return true if props are equal (skip re-render)
    return (
      JSON.stringify(prev.token) === JSON.stringify(next.token) &&
      prev.isSelected === next.isSelected
    );
  }
);
```

### 3. Debounced Search

```typescript
// Debounce token search (300ms)
const [searchTerm, setSearchTerm] = useState('');
const debouncedSearch = useDebouncedCallback((term: string) => {
  store.setFilter('search', term);
}, 300);

const handleSearch = (e: ChangeEvent<HTMLInputElement>) => {
  setSearchTerm(e.target.value);
  debouncedSearch(e.target.value);
};
```

---

## Type Safety: Zod from Backend

**Generate TypeScript types from backend JSON schemas, no manual duplication.**

```typescript
// src/types/generated/color.zod.ts
// (Generated from backend schemas/core/color-token-v1.json)

import { z } from 'zod';

export const ColorTokenSchema = z.object({
  id: z.string().uuid(),
  hex: z.string().regex(/^#[0-9A-F]{6}$/),
  rgb: z.object({
    r: z.number().min(0).max(255),
    g: z.number().min(0).max(255),
    b: z.number().min(0).max(255),
  }),
  hsl: z.object({
    h: z.number().min(0).max(360),
    s: z.number().min(0).max(100),
    l: z.number().min(0).max(100),
  }),
  oklch: z.object({
    o: z.number().min(0).max(1),
    l: z.number().min(0).max(1),
    c: z.number().min(0).max(0.4),
    h: z.number().min(0).max(360),
  }),
  semanticName: z.string().min(3).max(50),
  designIntent: z.string(),
  confidence: z.number().min(0).max(100),
  metadata: z.object({
    sources: z.array(z.string()),
    temperature: z.enum(['cool', 'neutral', 'warm']),
    saturation: z.enum(['vivid', 'moderate', 'muted']),
    lightness: z.enum(['dark', 'medium', 'light']),
    harmony: z.array(z.string()),
    usage: z.array(z.string()),
  }),
  extractedAt: z.string().datetime(),
  createdAt: z.string().datetime(),
  updatedAt: z.string().datetime(),
});

export type ColorToken = z.infer<typeof ColorTokenSchema>;
```

**Usage in components:**

```typescript
// Type-safe token handling
const response = await api.get(`/api/colors/${id}`);
const token: ColorToken = ColorTokenSchema.parse(response);

// Partial updates also type-safe
const updateColor = (token: ColorToken, updates: Partial<ColorToken>) => {
  const validated = ColorTokenSchema.partial().parse(updates);
  return api.put(`/api/colors/${token.id}`, validated);
};
```

---

## Directory Structure

```
src/
├── components/
│   ├── tokens/
│   │   ├── TokenExplorer.tsx          # Main page component
│   │   ├── UploadSection.tsx          # Generic drag-drop
│   │   ├── ExtractionProgress.tsx     # Generic progress bar
│   │   ├── MainLayout.tsx             # Main flex layout
│   │   ├── TokenGrid.tsx              # Generic virtualized grid
│   │   ├── TokenCard.tsx              # Generic card (memoized)
│   │   ├── Toolbar.tsx                # Generic toolbar
│   │   ├── TokenInspectorSidebar.tsx  # Generic inspector
│   │   ├── TokenPlaygroundDrawer.tsx  # Generic playground
│   │   │
│   │   ├── color/
│   │   │   ├── ColorTokenVisual.tsx
│   │   │   ├── ColorFormatTabs.tsx
│   │   │   ├── ColorAdjuster.tsx
│   │   │   ├── HarmonyVisualizer.tsx
│   │   │   ├── TemperatureVisualizer.tsx
│   │   │   ├── SaturationVisualizer.tsx
│   │   │   └── ColorRelationshipsPanel.tsx
│   │   │
│   │   ├── typography/ (future)
│   │   ├── spacing/ (future)
│   │   │
│   │   └── shared/
│   │       ├── SemanticNameEditor.tsx
│   │       ├── ConfidenceBreakdown.tsx
│   │       └── FormatTabsContainer.tsx
│   │
│   └── layout/
│       ├── Header.tsx
│       └── Sidebar.tsx
│
├── hooks/
│   ├── useTokens.ts                  # React Query - list
│   ├── useToken.ts                   # React Query + edit state
│   ├── useTokenFilters.ts            # Filter state logic
│   ├── useExtractionProgress.ts      # WebSocket listener
│   ├── useExport.ts                  # Export handler
│   └── useSemanticNameSuggestions.ts # AI suggestions
│
├── store/
│   └── tokenStore.ts                 # Zustand store
│
├── types/
│   ├── generated/
│   │   ├── color.zod.ts              # Generated from backend
│   │   └── typography.zod.ts         # Future
│   ├── token.ts                      # Generic types
│   └── registry.ts                   # TokenType registry
│
├── config/
│   └── tokenTypeRegistry.ts          # Schema-driven config
│
├── utils/
│   ├── tokenFilters.ts               # Filter functions
│   ├── tokenSort.ts                  # Sort functions
│   ├── colorUtils.ts                 # Color conversions
│   └── export.ts                     # Export helpers
│
├── api/
│   └── tokenApi.ts                   # React Query hooks
│
├── styles/
│   ├── tokens.css                    # Design tokens
│   └── animations.css                # Transitions
│
└── pages/
    ├── TokenExplorer.tsx             # Route page
    └── ProjectTokens.tsx             # Project view
```

---

## Development Workflow: TDD

**For each component, write tests first:**

```typescript
// src/components/tokens/__tests__/TokenCard.test.tsx

describe('TokenCard (Generic)', () => {
  test('renders color variant', () => {
    const token = createMockColorToken();
    render(<TokenCard token={token} tokenType="color" />);

    expect(screen.getByTestId('color-swatch')).toBeInTheDocument();
    expect(screen.getByText(token.semanticName)).toBeInTheDocument();
  });

  test('shows quick actions on hover', () => {
    const token = createMockColorToken();
    const onEdit = vi.fn();
    render(<TokenCard token={token} tokenType="color" onEdit={onEdit} />);

    fireEvent.mouseEnter(screen.getByTestId('token-card'));
    expect(screen.getByRole('button', { name: /edit/i })).toBeVisible();
  });

  test('applies selected styles when isSelected=true', () => {
    const token = createMockColorToken();
    const { container } = render(
      <TokenCard token={token} tokenType="color" isSelected={true} />
    );

    expect(container.firstChild).toHaveClass('ring-2', 'ring-accent');
  });
});

describe('TokenGrid (Generic)', () => {
  test('virtualizes 1000 tokens', () => {
    const tokens = Array.from({ length: 1000 }, createMockColorToken);
    render(<TokenGrid tokens={tokens} />);

    // Only visible items rendered
    expect(screen.getAllByTestId('token-card')).toBeLessThan(100);
  });

  test('filters tokens by temperature', () => {
    const tokens = [
      createMockColorToken({ metadata: { temperature: 'warm' } }),
      createMockColorToken({ metadata: { temperature: 'cool' } }),
    ];

    render(<TokenGrid tokens={tokens} filters={{ temperature: 'warm' }} />);
    expect(screen.getAllByTestId('token-card')).toHaveLength(1);
  });
});
```

---

## Implementation Phases

### Phase 1: Foundation (Week 1)
- [ ] Setup Zustand store + useTokens hooks
- [ ] Create tokenTypeRegistry (schema-driven config)
- [ ] Build generic TokenCard, TokenGrid, Toolbar
- [ ] Implement React Query integration

### Phase 2: Color Reference (Week 1-2)
- [ ] Build ColorTokenVisual component
- [ ] Build format tabs (RGB, HSL, Oklch)
- [ ] Build Inspector sidebar
- [ ] Build Playground drawer with adjusters

### Phase 3: Extraction & Real-Time (Week 2)
- [ ] UploadSection with drag-drop
- [ ] ExtractionProgress with WebSocket
- [ ] SemanticNameEditor with AI suggestions
- [ ] ConfidenceBreakdown visualization

### Phase 4: Proof of Concept (Week 3)
- [ ] Typography token visual (test 80% reuse)
- [ ] Add typography to tokenTypeRegistry
- [ ] Validate pattern works for non-color tokens

### Phase 5: Polish & Export (Week 3-4)
- [ ] Export modal with multiple formats
- [ ] Animations and micro-interactions
- [ ] Accessibility audit
- [ ] Performance tuning (virtualization, memoization)

---

## Success Criteria

- [x] Generic components work for Color
- [ ] Generic components work for Typography (validates 80% reuse)
- [ ] Generic components work for Spacing
- [ ] 100+ tokens render smoothly (virtualization)
- [ ] Semantic names searchable, editable
- [ ] Confidence & sources transparent
- [ ] WebSocket real-time extraction working
- [ ] Export to 5+ formats
- [ ] Full accessibility (WCAG AAA)
- [ ] Fully type-safe (Zod end-to-end)

---

## Related Documentation

- [`token_explorer_vision.md`](./token_explorer_vision.md) - User flows and design philosophy
- [`COMPONENT_SPECIFICATIONS.md`](./COMPONENT_SPECIFICATIONS.md) - Detailed Tailwind specs
- [`GENERALIZATION_ROADMAP.md`](./GENERALIZATION_ROADMAP.md) - How to add Typography/Spacing/Shadow
