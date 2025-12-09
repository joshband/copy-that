# Implementation Checklist: Multimodal Architecture Migration

**Document Date:** 2025-12-09
**Purpose:** Step-by-step execution guide for 4-phase refactoring
**Duration:** 4 weeks (80 hours total)
**Reference:** UNIFIED_MULTIMODAL_ARCHITECTURE.md

---

## Overview

This checklist provides concrete tasks for migrating from flat component structure (45 root components) to feature-based multimodal architecture. Each phase builds on the previous, maintaining working state throughout.

**Critical Rules:**
1. ✅ Run tests after EVERY change
2. ✅ Commit after each completed task
3. ✅ Never break working functionality
4. ✅ TypeScript must have zero errors at all times

---

## Phase 1: Foundation (Week 1, 24 hours)

**Goal:** Create adapter pattern and extract token-agnostic components

### Day 1: Adapter Interface (Monday, 4 hours)

**Tasks:**

- [ ] **Task 1.1: Create adapter interface** (1 hour)
  ```bash
  mkdir -p frontend/src/shared/adapters
  touch frontend/src/shared/adapters/TokenVisualAdapter.ts
  ```

  **Code to write:**
  ```typescript
  // TokenVisualAdapter.ts
  import type { ReactNode } from 'react'

  export interface TabDefinition {
    name: string
    component: React.ComponentType<{ token: any }>
  }

  export interface TokenVisualAdapter<T> {
    category: string
    renderSwatch: (token: T) => ReactNode
    renderMetadata: (token: T) => ReactNode
    getDetailTabs: (token: T) => TabDefinition[]
  }
  ```

  **Verify:** `pnpm typecheck` passes
  **Commit:** "feat: Add TokenVisualAdapter interface"

- [ ] **Task 1.2: Create adapter registry** (1 hour)
  ```bash
  touch frontend/src/shared/adapters/registry.ts
  touch frontend/src/shared/adapters/index.ts
  ```

  **Code to write:**
  ```typescript
  // registry.ts
  import type { TokenVisualAdapter } from './TokenVisualAdapter'

  export const ADAPTER_REGISTRY: Record<string, TokenVisualAdapter<any>> = {}

  export function registerAdapter(adapter: TokenVisualAdapter<any>) {
    ADAPTER_REGISTRY[adapter.category] = adapter
  }

  export function getAdapter(category: string): TokenVisualAdapter<any> | null {
    return ADAPTER_REGISTRY[category] ?? null
  }
  ```

  **Verify:** `pnpm typecheck` passes
  **Commit:** "feat: Add adapter registry"

- [ ] **Task 1.3: Write adapter tests** (1 hour)
  ```bash
  mkdir -p frontend/src/shared/adapters/__tests__
  touch frontend/src/shared/adapters/__tests__/registry.test.ts
  ```

  **Test code:**
  ```typescript
  import { describe, it, expect, beforeEach } from 'vitest'
  import { registerAdapter, getAdapter, ADAPTER_REGISTRY } from '../registry'

  describe('Adapter Registry', () => {
    beforeEach(() => {
      // Clear registry before each test
      Object.keys(ADAPTER_REGISTRY).forEach(key => delete ADAPTER_REGISTRY[key])
    })

    it('should register and retrieve adapter', () => {
      const mockAdapter = {
        category: 'test',
        renderSwatch: () => null,
        renderMetadata: () => null,
        getDetailTabs: () => []
      }

      registerAdapter(mockAdapter)
      const retrieved = getAdapter('test')

      expect(retrieved).toBe(mockAdapter)
    })

    it('should return null for unregistered category', () => {
      expect(getAdapter('nonexistent')).toBeNull()
    })
  })
  ```

  **Verify:** `pnpm test registry.test.ts` passes
  **Commit:** "test: Add adapter registry tests"

- [ ] **Task 1.4: Document adapter pattern** (1 hour)
  ```bash
  touch docs/guides/ADAPTER_PATTERN_GUIDE.md
  ```

  Write guide with:
  - What adapters are
  - Why we use them
  - How to create a new adapter
  - Examples

  **Verify:** Documentation is clear and complete
  **Commit:** "docs: Add adapter pattern guide"

**End of Day 1 Checkpoint:**
- ✅ Adapter interface defined
- ✅ Registry implemented and tested
- ✅ Documentation complete
- ✅ All tests passing
- ✅ Zero TypeScript errors

---

### Day 2: First Adapter (Tuesday, 6 hours)

**Tasks:**

- [ ] **Task 2.1: Create ColorVisualAdapter** (2 hours)
  ```bash
  mkdir -p frontend/src/features/visual-extraction/adapters
  touch frontend/src/features/visual-extraction/adapters/ColorVisualAdapter.ts
  ```

  **Code to write:**
  ```typescript
  // ColorVisualAdapter.ts
  import type { ReactNode } from 'react'
  import type { UiColorToken } from '@/store/tokenGraphStore'
  import type { TokenVisualAdapter, TabDefinition } from '@/shared/adapters/TokenVisualAdapter'

  function extractHex(token: UiColorToken): string {
    const raw = token.raw as any
    const val = raw?.$value
    return (typeof val === 'object' && val?.hex)
      || raw?.hex
      || raw?.attributes?.hex
      || '#cccccc'
  }

  export const ColorVisualAdapter: TokenVisualAdapter<UiColorToken> = {
    category: 'color',

    renderSwatch: (token: UiColorToken): ReactNode => {
      const hex = extractHex(token)
      return (
        <div
          style={{ backgroundColor: hex }}
          className="w-8 h-8 rounded border border-gray-300"
          title={hex}
        />
      )
    },

    renderMetadata: (token: UiColorToken): ReactNode => {
      const hex = extractHex(token)
      const raw = token.raw as any
      const confidence = raw?.confidence ?? raw?.attributes?.confidence
      const name = raw?.name ?? raw?.attributes?.name

      return (
        <div className="text-sm space-y-1">
          <div className="font-mono">{hex}</div>
          {name && <div className="text-gray-600">{name}</div>}
          {confidence && (
            <div className="text-gray-500">
              Confidence: {(confidence * 100).toFixed(0)}%
            </div>
          )}
        </div>
      )
    },

    getDetailTabs: (token: UiColorToken): TabDefinition[] => {
      // Return empty for now - will integrate later
      return []
    }
  }
  ```

  **Verify:** `pnpm typecheck` passes
  **Commit:** "feat: Add ColorVisualAdapter"

- [ ] **Task 2.2: Register ColorVisualAdapter** (30 min)
  ```typescript
  // Update shared/adapters/registry.ts
  import { ColorVisualAdapter } from '@/features/visual-extraction/adapters/ColorVisualAdapter'

  // Pre-register known adapters
  registerAdapter(ColorVisualAdapter)
  ```

  **Verify:** `pnpm typecheck` passes
  **Commit:** "feat: Register ColorVisualAdapter"

- [ ] **Task 2.3: Test ColorVisualAdapter** (2 hours)
  ```bash
  touch frontend/src/features/visual-extraction/adapters/__tests__/ColorVisualAdapter.test.tsx
  ```

  **Test code:**
  ```typescript
  import { describe, it, expect } from 'vitest'
  import { render, screen } from '@testing-library/react'
  import { ColorVisualAdapter } from '../ColorVisualAdapter'
  import type { UiColorToken } from '@/store/tokenGraphStore'

  describe('ColorVisualAdapter', () => {
    const mockColorToken: UiColorToken = {
      id: 'color.primary',
      category: 'color',
      isAlias: false,
      raw: {
        $type: 'color',
        $value: { hex: '#FF0000' },
        name: 'Primary Red',
        confidence: 0.95
      }
    }

    it('should render swatch with correct color', () => {
      const swatch = ColorVisualAdapter.renderSwatch(mockColorToken)
      const { container } = render(<>{swatch}</>)
      const div = container.querySelector('div')

      expect(div).toHaveStyle({ backgroundColor: '#FF0000' })
    })

    it('should render metadata with hex and name', () => {
      const metadata = ColorVisualAdapter.renderMetadata(mockColorToken)
      render(<>{metadata}</>)

      expect(screen.getByText('#FF0000')).toBeInTheDocument()
      expect(screen.getByText('Primary Red')).toBeInTheDocument()
    })

    it('should handle missing confidence gracefully', () => {
      const tokenWithoutConfidence = {
        ...mockColorToken,
        raw: { ...mockColorToken.raw, confidence: undefined }
      }

      const metadata = ColorVisualAdapter.renderMetadata(tokenWithoutConfidence)
      render(<>{metadata}</>)

      expect(screen.queryByText(/Confidence/)).not.toBeInTheDocument()
    })
  })
  ```

  **Verify:** `pnpm test ColorVisualAdapter.test.tsx` passes
  **Commit:** "test: Add ColorVisualAdapter tests"

- [ ] **Task 2.4: Manual testing in browser** (1.5 hours)
  - Start dev server: `pnpm dev`
  - Open browser console
  - Test adapter in console:
    ```javascript
    import { getAdapter } from '@/shared/adapters/registry'
    const adapter = getAdapter('color')
    console.log('Adapter:', adapter)
    ```
  - Upload test image
  - Verify colors display correctly

  **Verify:** Colors still render in UI
  **Commit:** "chore: Verify ColorVisualAdapter in browser"

**End of Day 2 Checkpoint:**
- ✅ ColorVisualAdapter implemented
- ✅ Adapter registered in registry
- ✅ Tests passing (adapter + registry)
- ✅ Manual browser testing complete
- ✅ All existing tests still passing

---

### Day 3: Refactor TokenCard (Wednesday, 6 hours)

**Tasks:**

- [ ] **Task 3.1: Copy TokenCard to shared/** (30 min)
  ```bash
  mkdir -p frontend/src/shared/components/TokenCard
  cp frontend/src/components/TokenCard.tsx frontend/src/shared/components/TokenCard/TokenCard.tsx
  cp frontend/src/components/TokenCard.css frontend/src/shared/components/TokenCard/TokenCard.css
  touch frontend/src/shared/components/TokenCard/index.ts
  ```

  **Create barrel export:**
  ```typescript
  // index.ts
  export { TokenCard } from './TokenCard'
  ```

  **Verify:** `pnpm typecheck` passes
  **Commit:** "refactor: Copy TokenCard to shared/"

- [ ] **Task 3.2: Add adapter prop to TokenCard** (2 hours)

  **Update TokenCard.tsx:**
  ```typescript
  import type { TokenVisualAdapter } from '@/shared/adapters/TokenVisualAdapter'
  import type { TokenNode } from '@/shared/hooks/useTokenGraph'

  interface TokenCardProps {
    token: TokenNode
    adapter?: TokenVisualAdapter<TokenNode>  // Optional - auto-select if not provided
    onClick?: () => void
  }

  export function TokenCard({ token, adapter: providedAdapter, onClick }: TokenCardProps) {
    // Auto-select adapter if not provided
    const adapter = providedAdapter ?? getAdapter(token.category)

    if (!adapter) {
      return <div className="token-card-error">No adapter for {token.category}</div>
    }

    return (
      <div className="token-card" onClick={onClick}>
        <div className="token-card-swatch">
          {adapter.renderSwatch(token)}
        </div>
        <div className="token-card-metadata">
          {adapter.renderMetadata(token)}
        </div>
      </div>
    )
  }
  ```

  **Verify:** `pnpm typecheck` passes
  **Commit:** "refactor: Add adapter support to TokenCard"

- [ ] **Task 3.3: Remove hardcoded color logic** (1 hour)

  Find and remove:
  - Direct `token.hex` access
  - `if (tokenType === 'color')` conditionals
  - Color-specific rendering

  **Verify:** `pnpm typecheck` passes
  **Commit:** "refactor: Remove hardcoded color logic from TokenCard"

- [ ] **Task 3.4: Update TokenCard tests** (2 hours)
  ```bash
  cp frontend/src/components/__tests__/TokenCard.test.tsx \
     frontend/src/shared/components/TokenCard/__tests__/TokenCard.test.tsx
  ```

  **Update tests to use adapters:**
  ```typescript
  import { TokenCard } from '../TokenCard'
  import type { TokenVisualAdapter } from '@/shared/adapters/TokenVisualAdapter'

  describe('TokenCard', () => {
    const mockAdapter: TokenVisualAdapter<any> = {
      category: 'test',
      renderSwatch: (token) => <div data-testid="swatch">{token.id}</div>,
      renderMetadata: (token) => <div data-testid="metadata">Metadata</div>,
      getDetailTabs: () => []
    }

    const mockToken = {
      id: 'test.token',
      category: 'test',
      raw: {}
    }

    it('should render using provided adapter', () => {
      render(<TokenCard token={mockToken} adapter={mockAdapter} />)
      expect(screen.getByTestId('swatch')).toBeInTheDocument()
      expect(screen.getByTestId('metadata')).toBeInTheDocument()
    })

    it('should auto-select adapter if not provided', () => {
      // Assuming ColorVisualAdapter is registered
      const colorToken = {
        id: 'color.primary',
        category: 'color',
        raw: { $value: { hex: '#FF0000' } }
      }

      render(<TokenCard token={colorToken} />)
      expect(screen.getByTitle('#FF0000')).toBeInTheDocument()
    })
  })
  ```

  **Verify:** `pnpm test TokenCard.test.tsx` passes
  **Commit:** "test: Update TokenCard tests for adapters"

- [ ] **Task 3.5: Update App.tsx imports** (30 min)
  ```typescript
  // Update import
  - import TokenCard from './components/TokenCard'
  + import { TokenCard } from '@/shared/components/TokenCard'
  ```

  **Verify:** App still works in browser
  **Commit:** "refactor: Update TokenCard imports in App.tsx"

**End of Day 3 Checkpoint:**
- ✅ TokenCard moved to shared/
- ✅ TokenCard refactored to use adapters
- ✅ All hardcoded logic removed
- ✅ Tests updated and passing
- ✅ App works identically in browser

---

### Day 4-5: Move Shared Components (Thursday-Friday, 8 hours)

**Goal:** Move remaining 7 generic components to shared/

**Tasks:**

- [ ] **Task 4.1: Move TokenGraphPanel** (1 hour)
  ```bash
  mkdir -p frontend/src/shared/components/TokenGraphPanel
  mv frontend/src/components/TokenGraphPanel.tsx frontend/src/shared/components/TokenGraphPanel/
  ```
  - Update imports
  - Update tests
  - Verify in browser

- [ ] **Task 4.2: Move TokenGrid** (1 hour)
  - Same process as TokenGraphPanel

- [ ] **Task 4.3: Move TokenToolbar** (1 hour)
  - Same process

- [ ] **Task 4.4: Move RelationsTable** (1 hour)
  - Same process

- [ ] **Task 4.5: Move RelationsDebugPanel** (1 hour)
  - Same process

- [ ] **Task 4.6: Move TokenInspectorSidebar** (1.5 hours)
  - Same process

- [ ] **Task 4.7: Move TokenPlaygroundDrawer** (1.5 hours)
  - Same process

**Process for each component:**
1. Create directory in shared/components/
2. Move component file
3. Create barrel export (index.ts)
4. Update imports in App.tsx
5. Run tests
6. Verify in browser
7. Commit

**End of Day 4-5 Checkpoint:**
- ✅ All 8 generic components in shared/
- ✅ All imports updated
- ✅ All tests passing
- ✅ App works identically
- ✅ Clean commit history (1 commit per component)

---

## Phase 2: Visual Consolidation (Week 2, 24 hours)

**Goal:** Move all visual components to features/visual-extraction/

### Day 1: Directory Structure (Monday, 4 hours)

- [ ] **Task 1.1: Create feature directories** (30 min)
  ```bash
  mkdir -p frontend/src/features/visual-extraction/components/{color,spacing,typography,shadow}
  mkdir -p frontend/src/features/visual-extraction/adapters
  mkdir -p frontend/src/features/visual-extraction/hooks
  mkdir -p frontend/src/features/visual-extraction/types
  touch frontend/src/features/visual-extraction/index.ts
  ```

- [ ] **Task 1.2: Create barrel exports** (30 min)
  ```bash
  touch frontend/src/features/visual-extraction/components/color/index.ts
  touch frontend/src/features/visual-extraction/components/spacing/index.ts
  touch frontend/src/features/visual-extraction/components/typography/index.ts
  touch frontend/src/features/visual-extraction/components/shadow/index.ts
  ```

- [ ] **Task 1.3: Document feature structure** (1 hour)
  ```bash
  touch frontend/src/features/visual-extraction/README.md
  ```

  Write:
  - What this feature does
  - Directory structure
  - How to add components
  - How to export from feature

- [ ] **Task 1.4: Setup path aliases** (1 hour)

  **Update tsconfig.json:**
  ```json
  {
    "compilerOptions": {
      "paths": {
        "@/*": ["./src/*"],
        "@/shared/*": ["./src/shared/*"],
        "@/features/*": ["./src/features/*"]
      }
    }
  }
  ```

  **Update vite.config.ts:**
  ```typescript
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
      '@/shared': path.resolve(__dirname, './src/shared'),
      '@/features': path.resolve(__dirname, './src/features')
    }
  }
  ```

- [ ] **Task 1.5: Test path aliases** (1 hour)
  - Create test component in visual-extraction/
  - Import in App.tsx using new path
  - Verify TypeScript resolution
  - Verify Vite HMR works

**End of Day 1 Checkpoint:**
- ✅ Directory structure created
- ✅ Path aliases configured
- ✅ Documentation written
- ✅ Test import works

---

### Day 2-3: Move Color Components (Tuesday-Wednesday, 12 hours)

**12 color components to move:**

**Day 2 Morning (4 hours):**
- [ ] ColorTokenDisplay → ColorDisplay
- [ ] ColorGraphPanel → ColorGraph
- [ ] ColorsTable → ColorTable
- [ ] ColorPrimaryPreview → ColorPreview

**Day 2 Afternoon (4 hours):**
- [ ] ColorPaletteSelector → ColorPalette
- [ ] CompactColorGrid → ColorGrid
- [ ] HarmonyVisualizer → HarmonyVisualizer
- [ ] EducationalColorDisplay → EducationalDisplay

**Day 3 (4 hours):**
- [ ] ColorNarrative → ColorNarrative
- [ ] color-detail-panel/ → ColorDetailPanel/
- [ ] color-science/ → color-science/
- [ ] OverviewNarrative → OverviewNarrative

**Process for each component:**
1. Move file to visual-extraction/components/color/ComponentName/
2. Rename file to match convention (PascalCase)
3. Update internal imports
4. Export from color/index.ts
5. Update App.tsx import
6. Run tests
7. Verify in browser
8. Commit ("refactor: Move ComponentName to visual-extraction")

**End of Day 2-3 Checkpoint:**
- ✅ All 12 color components moved
- ✅ All imports updated
- ✅ All tests passing
- ✅ Colors tab works identically
- ✅ 12 clean commits

---

### Day 4: Move Spacing Components (Thursday, 4 hours)

**8 spacing components to move:**

- [ ] SpacingScalePanel → SpacingScale
- [ ] SpacingTable → SpacingTable
- [ ] SpacingGraphList → SpacingGraph
- [ ] SpacingRuler → SpacingRuler
- [ ] SpacingGapDemo → SpacingDemo
- [ ] SpacingDetailCard → SpacingDetails
- [ ] SpacingResponsivePreview → SpacingPreview
- [ ] spacing-showcase/ → SpacingShowcase/

**Process:** Same as color components

**End of Day 4 Checkpoint:**
- ✅ All 8 spacing components moved
- ✅ Spacing tab works identically
- ✅ 8 clean commits

---

### Day 5: Move Typography + Shadow (Friday, 4 hours)

**Morning (2 hours): Typography (5 components)**
- [ ] TypographyInspector
- [ ] TypographyDetailCard → TypographyDetails
- [ ] TypographyCards
- [ ] FontFamilyShowcase → FontShowcase
- [ ] FontSizeScale

**Afternoon (2 hours): Shadow (2 components)**
- [ ] ShadowInspector
- [ ] shadows/ → ShadowTokenList/

**Process:** Same as before

**End of Day 5 Checkpoint:**
- ✅ All 7 components moved
- ✅ Typography + Shadow tabs work
- ✅ Phase 2 complete!

---

## Phase 3: Adapter Extraction (Week 3, 24 hours)

**Goal:** Create adapters for all visual token types

### Day 1-2: Create Adapters (Monday-Tuesday, 12 hours)

- [ ] **Task 1.1: Create SpacingVisualAdapter** (3 hours)
  ```bash
  touch frontend/src/features/visual-extraction/adapters/SpacingVisualAdapter.ts
  ```

  Implement:
  - renderSwatch (spacing bar visualization)
  - renderMetadata (px, rem, multiplier)
  - getDetailTabs (scale, responsive views)

  Test:
  - Write tests
  - Verify in browser

  Commit: "feat: Add SpacingVisualAdapter"

- [ ] **Task 1.2: Create TypographyVisualAdapter** (3 hours)

  Same process

- [ ] **Task 1.3: Create ShadowVisualAdapter** (3 hours)

  Same process

- [ ] **Task 1.4: Register all adapters** (1 hour)
  ```typescript
  // shared/adapters/registry.ts
  import { ColorVisualAdapter } from '@/features/visual-extraction/adapters/ColorVisualAdapter'
  import { SpacingVisualAdapter } from '@/features/visual-extraction/adapters/SpacingVisualAdapter'
  import { TypographyVisualAdapter } from '@/features/visual-extraction/adapters/TypographyVisualAdapter'
  import { ShadowVisualAdapter } from '@/features/visual-extraction/adapters/ShadowVisualAdapter'

  registerAdapter(ColorVisualAdapter)
  registerAdapter(SpacingVisualAdapter)
  registerAdapter(TypographyVisualAdapter)
  registerAdapter(ShadowVisualAdapter)
  ```

- [ ] **Task 1.5: Test adapter auto-selection** (2 hours)
  - Test TokenCard with each token type
  - Verify correct adapter selected
  - Verify rendering works
  - Write integration tests

**End of Day 1-2 Checkpoint:**
- ✅ All 4 visual adapters implemented
- ✅ All adapters tested
- ✅ All adapters registered
- ✅ Auto-selection works

---

### Day 3-4: Refactor Remaining Components (Wednesday-Thursday, 10 hours)

- [ ] **Task 2.1: Refactor TokenTable** (3 hours)
  - Add adapter support
  - Remove hardcoded logic
  - Test with all token types

- [ ] **Task 2.2: Refactor TokenGraph** (3 hours)
  - Same process

- [ ] **Task 2.3: Refactor TokenInspectorSidebar** (2 hours)
  - Same process

- [ ] **Task 2.4: Refactor TokenPlaygroundDrawer** (2 hours)
  - Same process

**End of Day 3-4 Checkpoint:**
- ✅ All shared components use adapters
- ✅ Zero domain logic in shared/
- ✅ All tests passing

---

### Day 5: Documentation (Friday, 2 hours)

- [ ] **Task 3.1: Write adapter guide** (1 hour)
  - How to create adapter
  - Examples for each token type
  - Best practices

- [ ] **Task 3.2: Update architecture docs** (1 hour)
  - Mark Phase 3 complete
  - Document adapter pattern
  - Add examples

**End of Phase 3 Checkpoint:**
- ✅ Adapter pattern fully implemented
- ✅ All documentation complete
- ✅ System is multimodal-ready

---

## Phase 4: Multimodal POC (Week 4, 8 hours)

**Goal:** Prove architecture with audio tokens

### Day 1-2: Audio Schema (Monday-Tuesday, 8 hours)

- [ ] **Task 1.1: Define W3CAudioToken** (2 hours)
  ```typescript
  // types/generated/audio.ts
  export interface W3CAudioToken {
    $type: 'audio'
    $value: {
      bpm: number
      key: string
      duration: number
      waveform?: number[]
    }
    $description?: string
  }
  ```

- [ ] **Task 1.2: Create UiAudioToken** (2 hours)
  ```typescript
  // store/tokenGraphStore.ts
  export interface UiAudioToken extends UiTokenBase<W3CAudioToken> {
    category: 'audio'
    bpm: number
    key: string
  }
  ```

- [ ] **Task 1.3: Update tokenGraphStore** (2 hours)
  - Add audio: UiAudioToken[] to state
  - Add audio parsing in load()
  - Test with mock data

- [ ] **Task 1.4: Create AudioVisualAdapter** (2 hours)
  ```typescript
  export const AudioVisualAdapter: TokenVisualAdapter<UiAudioToken> = {
    category: 'audio',
    renderSwatch: (token) => (
      <div className="audio-waveform-placeholder">
        🎵 {token.bpm} BPM
      </div>
    ),
    renderMetadata: (token) => (
      <div>
        <p>BPM: {token.bpm}</p>
        <p>Key: {token.key}</p>
      </div>
    ),
    getDetailTabs: () => []
  }
  ```

**End of Day 1-2 Checkpoint:**
- ✅ Audio schema defined
- ✅ Audio store integration
- ✅ AudioVisualAdapter created
- ✅ Mock audio tokens work

---

### Day 3: Documentation (Wednesday, 8 hours)

- [ ] **Task 2.1: Update UNIFIED_MULTIMODAL_ARCHITECTURE.md** (2 hours)
  - Mark all phases complete
  - Add audio POC results
  - Update success metrics

- [ ] **Task 2.2: Create migration summary** (2 hours)
  - Before/after metrics
  - Lessons learned
  - Next steps

- [ ] **Task 2.3: Create demo video** (2 hours)
  - Record audio token demo
  - Show adapter pattern
  - Explain multimodal vision

- [ ] **Task 2.4: Plan Phase 5** (2 hours)
  - Real audio extraction roadmap
  - Backend integration plan
  - Timeline estimates

**End of Phase 4 Checkpoint:**
- ✅ Architecture validated
- ✅ Documentation complete
- ✅ Ready for Phase 5

---

## Success Verification Checklist

**After each phase:**

- [ ] All tests passing (`pnpm test`)
- [ ] Zero TypeScript errors (`pnpm typecheck`)
- [ ] Build succeeds (`pnpm build`)
- [ ] App works in browser (`pnpm dev`)
- [ ] Git history is clean (logical commits)
- [ ] Documentation updated

**Final verification:**

- [ ] 44 components → organized structure
- [ ] Adapter pattern working
- [ ] All token types rendering
- [ ] Token graph working
- [ ] 17+ tests passing
- [ ] Performance unchanged
- [ ] Bundle size acceptable

---

## Rollback Procedures

**If something breaks:**

1. **Stop immediately** - Don't continue with broken state
2. **Check tests** - `pnpm test` to identify failures
3. **Check TypeScript** - `pnpm typecheck` for errors
4. **Review last commit** - `git log -1` to see what changed
5. **Rollback if needed** - `git revert HEAD` or `git reset --hard HEAD~1`
6. **Ask for help** - Don't struggle alone
7. **Document issue** - Add to rollback log

**Common issues:**

- **Circular imports** - Check import chains
- **Missing types** - Verify barrel exports
- **Test failures** - Check mock data
- **Build errors** - Clear node_modules and reinstall

---

## Time Tracking Template

**Use this to track actual time:**

```markdown
## Phase 1 Time Log

### Day 1
- Task 1.1: 1.5 hours (estimated 1 hour)
- Task 1.2: 1 hour (on time)
- Task 1.3: 2 hours (estimated 1 hour) - complex test setup
- Task 1.4: 45 min (estimated 1 hour)
- **Total Day 1:** 5.25 hours (estimated 4 hours)

### Day 2
- Task 2.1: 2.5 hours (estimated 2 hours)
- ...

**Phase 1 Total:** X hours (estimated 24 hours)
```

---

## Next Session Quick Start

**Before starting Phase 1:**

1. ✅ Read UNIFIED_MULTIMODAL_ARCHITECTURE.md
2. ✅ Review this checklist
3. ✅ Run `pnpm test` to verify baseline
4. ✅ Run `pnpm typecheck` to verify no errors
5. ✅ Create feature branch: `git checkout -b feat/multimodal-architecture`
6. ✅ Set timer for 4-hour work session

**Start with:**
- Task 1.1: Create adapter interface (1 hour)
- Coffee break
- Task 1.2: Create adapter registry (1 hour)
- Lunch
- Task 1.3: Write adapter tests (1 hour)
- Coffee break
- Task 1.4: Document adapter pattern (1 hour)

**End of first session:**
- ✅ Day 1 complete
- ✅ Commit and push
- ✅ Review tomorrow's tasks

---

**Document Status:** Implementation Guide
**Last Updated:** 2025-12-09
**Maintained By:** Development Team
