# Architecture Quality Assessment + Clean Refactor Plan

**Purpose:** Identify what's working, what's messy, and the straightforward migration path
**Scope:** Frontend component layer (where the mess is)
**Status:** Assessment + concrete refactor steps

---

## The Core Problem

Your frontend has **working functionality scattered across messy structure**:

- ✅ **What works:** Color/spacing/shadow/typography extraction, display, tabs, cards, grids
- ❌ **What's messy:** Components scattered in multiple directories, 3 different tab implementations, no clear pattern for "reusable" vs "feature-specific"
- 🎯 **Goal:** Preserve functionality, reorganize to enable new features (streaming token pipeline)

---

## Frontend Architecture Assessment

### Layer 1: Feature-Specific Components (ACTUALLY GOOD)

**Current state:** `frontend/src/features/visual-extraction/components/`

```
visual-extraction/components/
├── color/
│   ├── ColorDetailPanel.tsx      ✅ GOOD - Works well
│   ├── ColorTokenDisplay.tsx     ✅ GOOD
│   ├── HarmonyVisualizer.tsx     ✅ GOOD
│   ├── AccessibilityVisualizer/  ✅ GOOD
│   └── ... (21 color files)
│
├── spacing/
│   ├── SpacingScalePanel.tsx     ✅ GOOD
│   ├── SpacingTable.tsx          ✅ GOOD
│   ├── SpacingRuler.tsx          ✅ GOOD
│   └── ... (21 spacing files)
│
├── typography/
│   └── ... (10 typography files) ✅ GOOD
│
└── shadow/
    └── ... (15 shadow files)     ✅ GOOD
```

**Assessment:** These components are **properly organized by token type and work well**. Keep them exactly as-is.

### Layer 2: Root Components (MESSY)

**Current state:** `frontend/src/components/` (flat or loosely organized)

```
components/
├── TokenCard.tsx                 ⚠️  GENERIC - Could be in library
├── TokenGrid.tsx                 ⚠️  GENERIC - Could be in library
├── TokenInspectorSidebar.tsx     ⚠️  GENERIC - Could be in library
├── image-uploader/
│   ├── ImageUploader.tsx         ⚠️  FEATURE - OK here
│   ├── UploadArea.tsx            ✅ GENERIC - Should be in library
│   ├── ExtractButton.tsx         ⚠️  GENERIC - Could be in library
│   └── ...
├── diagnostics-panel/           ⚠️  FEATURE - OK here
├── metrics-overview/            ⚠️  FEATURE - OK here
├── color/                        ❌ DUPLICATE - Overlaps with features/visual-extraction/color
├── spacing/                      ❌ DUPLICATE - Overlaps with features/visual-extraction/spacing
├── playground-sidebar/          ⚠️  FEATURE - OK here but could be cleaner
├── learning-sidebar/            ⚠️  FEATURE - OK here
├── token-inspector/             ⚠️  FEATURE - OK here
├── extraction-progress/         ✅ GENERIC - Could be in library
├── LearningSidebarUI.tsx        ⚠️  GENERIC - Could be in library
├── PlaygroundSidebarUI.tsx      ⚠️  GENERIC - Could be in library
├── CostDashboard.tsx            ⚠️  GENERIC - Could be in library
└── SectionHeader.tsx            ✅ GENERIC - Should be in library
```

**Real problems:**
1. ❌ Duplicates (color/ and spacing/ in components/ AND in features/visual-extraction/)
2. ⚠️  Mixed concerns (generic components live next to feature-specific ones)
3. ⚠️  No clear "reusable library" boundary
4. ⚠️  Multiple implementations of tabs (need consolidation)
5. ⚠️  Some components are UI library (Badge, Card, Panel) but no dedicated folder

### Layer 3: Hooks & Utils

**Current state:** Scattered

```
hooks/
├── useProgressiveExtraction.ts  ⚠️  LOGIC - OK
├── useColorPalette.ts          ⚠️  LOGIC - OK
└── ...

design/
├── tokens.css                  ✅ GOOD - Design tokens
```

**Assessment:** These are fine. Logic hooks belong at this level.

---

## The Refactor Strategy (Clean, Non-Breaking)

### Phase 0: Assessment (Identify What to Keep/Move/Delete)

**KEEP (Don't touch):**
- ✅ `frontend/src/features/visual-extraction/` - Entire directory
- ✅ `frontend/src/hooks/` - All logic hooks
- ✅ `frontend/src/design/tokens.css` - Design system
- ✅ `frontend/src/pages/` - All page components
- ✅ `frontend/src/store/` - Zustand stores
- ✅ All styling, CSS, layout

**MOVE to library (no code changes):**
- `components/TokenCard.tsx` → `components/ui/card/TokenCard.tsx`
- `components/TokenGrid.tsx` → `components/ui/grid/TokenGrid.tsx`
- `components/extraction-progress/ExtractionProgressBar.tsx` → `components/ui/progress/ExtractionProgressBar.tsx`
- `components/SectionHeader.tsx` → `components/ui/sidebar/SectionHeader.tsx`
- `components/image-uploader/UploadArea.tsx` → `components/ui/input/UploadArea.tsx`
- `components/CostDashboard.tsx` → `components/ui/dashboard/CostDashboard.tsx`
- `components/LearningSidebarUI.tsx` → `components/ui/sidebar/LearningSidebarUI.tsx`
- `components/PlaygroundSidebarUI.tsx` → `components/ui/sidebar/PlaygroundSidebarUI.tsx`

**DELETE (Duplicates):**
- ❌ `components/color/` - Entire directory (keep features/visual-extraction/color/)
- ❌ `components/spacing/` - Entire directory (keep features/visual-extraction/spacing/)

**REFACTOR (Consolidate):**
- Tab implementations: 3 custom implementations → 1 generic `<Tabs>` component
- Panel with tabs: Extract common pattern → `<PanelTabs>` component
- Sidebar sections: Extract pattern → reusable Sidebar + Section components

---

## Phase-by-Phase Refactor Plan

### Phase 1: Delete Duplicates (30 min)

```bash
# Remove duplicate directories
rm -rf frontend/src/components/color
rm -rf frontend/src/components/spacing

# Verify: these features are in features/visual-extraction/ ✅
```

**Test:** Run e2e tests, all should pass (these dirs weren't being used)

### Phase 2: Create Library Structure (30 min)

```bash
mkdir -p frontend/src/components/ui/{card,grid,progress,sidebar,input,dashboard}

# Verify structure created
ls -la frontend/src/components/ui/
```

### Phase 3: Move Files (1 hour)

For each file, use git mv to track move:

```bash
# Card components
git mv frontend/src/components/TokenCard.tsx frontend/src/components/ui/card/TokenCard.tsx
git mv frontend/src/components/token-inspector/TokenInspectorSidebar.tsx frontend/src/components/ui/card/TokenInspectorSidebar.tsx

# Grid components
git mv frontend/src/components/TokenGrid.tsx frontend/src/components/ui/grid/TokenGrid.tsx

# Progress components
git mv frontend/src/components/extraction-progress/ExtractionProgressBar.tsx frontend/src/components/ui/progress/ExtractionProgressBar.tsx

# Sidebar components
git mv frontend/src/components/SectionHeader.tsx frontend/src/components/ui/sidebar/SectionHeader.tsx
git mv frontend/src/components/LearningSidebarUI.tsx frontend/src/components/ui/sidebar/LearningSidebarUI.tsx
git mv frontend/src/components/PlaygroundSidebarUI.tsx frontend/src/components/ui/sidebar/PlaygroundSidebarUI.tsx

# Input components
git mv frontend/src/components/image-uploader/UploadArea.tsx frontend/src/components/ui/input/UploadArea.tsx

# Dashboard
git mv frontend/src/components/CostDashboard.tsx frontend/src/components/ui/dashboard/CostDashboard.tsx
```

**Test:** Code won't compile yet (broken imports)

### Phase 4: Fix Imports (1.5 hours)

Using your IDE's "Find and Replace" feature:

```typescript
// Search for: from '@/components/TokenCard'
// Replace with: from '@/components/ui/card/TokenCard'

// Search for: from '@/components/SectionHeader'
// Replace with: from '@/components/ui/sidebar/SectionHeader'

// etc. for each moved file
```

**Quick script option:**
```bash
# Find all broken imports
grep -r "from '@/components/TokenCard" frontend/src/

# Use sed to fix (caution: test first)
find frontend/src -name "*.tsx" -type f | xargs sed -i '' \
  "s|from '@/components/TokenCard'|from '@/components/ui/card/TokenCard'|g"
```

**Test:** `pnpm typecheck` passes

### Phase 5: Consolidate Tabs (1-2 hours)

**Identify the implementations:**

```typescript
// Implementation 1: ColorDetailPanel
// Implementation 2: ShadowAnalysisPanel
// Implementation 3: SpacingScalePanel (slightly different)
```

**Create generic:**

```typescript
// frontend/src/components/ui/tabs/Tabs.tsx
export interface TabDef {
  id: string
  label: string
  content: ReactNode
}

export function Tabs({ tabs, defaultTab }: { tabs: TabDef[], defaultTab?: string }) {
  const [activeTab, setActiveTab] = useState(defaultTab || tabs[0].id)

  return (
    <div className="tabs">
      <div className="tab-buttons">
        {tabs.map(tab => (
          <button
            key={tab.id}
            className={activeTab === tab.id ? 'active' : ''}
            onClick={() => setActiveTab(tab.id)}
          >
            {tab.label}
          </button>
        ))}
      </div>
      <div className="tab-content">
        {tabs.find(t => t.id === activeTab)?.content}
      </div>
    </div>
  )
}
```

**Migrate ColorDetailPanel:**

```typescript
// BEFORE:
export function ColorDetailPanel({ color }: { color: Token }) {
  const [tab, setTab] = useState('overview')

  return (
    <div>
      <button onClick={() => setTab('overview')}>Overview</button>
      <button onClick={() => setTab('harmony')}>Harmony</button>
      {tab === 'overview' && <OverviewTab color={color} />}
      {tab === 'harmony' && <HarmonyTab color={color} />}
    </div>
  )
}

// AFTER:
export function ColorDetailPanel({ color }: { color: Token }) {
  return (
    <Tabs tabs={[
      { id: 'overview', label: 'Overview', content: <OverviewTab color={color} /> },
      { id: 'harmony', label: 'Harmony', content: <HarmonyTab color={color} /> },
      // ... other tabs
    ]} />
  )
}
```

**Test:** ColorDetailPanel works identically (no visual change)

### Phase 6: Create PanelTabs (1 hour)

This is for the new token inspector feature:

```typescript
// frontend/src/components/ui/panel/PanelTabs.tsx
export interface PanelTab {
  id: string
  label: string
  content: ReactNode
}

export function PanelTabs({
  title,
  subtitle,
  tabs,
  onClose
}: {
  title: string
  subtitle?: string
  tabs: PanelTab[]
  onClose?: () => void
}) {
  return (
    <Panel>
      <PanelHeader>
        <div>
          <h2>{title}</h2>
          {subtitle && <p>{subtitle}</p>}
        </div>
        {onClose && <button onClick={onClose}>✕</button>}
      </PanelHeader>
      <PanelBody>
        <Tabs tabs={tabs} />
      </PanelBody>
    </Panel>
  )
}
```

**Test:** Render component, verify structure

### Phase 7: Integrate into Playground (2-3 hours)

Connect streaming to UI:

```typescript
// frontend/src/pages/Playground.tsx
export function Playground() {
  const { tokens, addToken, selectToken, selectedTokenId } = useTokenGraphStore()
  const [isExtracting, setIsExtracting] = useState(false)

  async function handleImageUpload(file: File) {
    setIsExtracting(true)

    // Connect to SSE stream
    const response = await fetch('/api/v1/extract/stream', {
      method: 'POST',
      body: JSON.stringify({ image: await fileToBase64(file) })
    })

    const reader = response.body?.getReader()
    const decoder = new TextDecoder()

    // Stream results
    while (true) {
      const { done, value } = await reader!.read()
      if (done) break

      const text = decoder.decode(value)
      const lines = text.split('\n')

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = JSON.parse(line.slice(6))
          addToken(data)  // Add to store immediately
        }
      }
    }

    setIsExtracting(false)
  }

  return (
    <div className="playground">
      <header>
        <UploadArea onDrop={files => handleImageUpload(files[0])} />
        <ExtractionProgressBar isExtracting={isExtracting} />
      </header>

      <main className="explorer">
        <Sidebar>
          <Grid>
            {tokens.map(token => (
              <TokenCard
                key={token.id}
                token={token}
                isSelected={selectedTokenId === token.id}
                onClick={() => selectToken(token.id)}
              />
            ))}
          </Grid>
        </Sidebar>

        {selectedTokenId && (
          <PanelTabs
            title={`${tokens[selectedTokenId].type}: ${tokens[selectedTokenId].name}`}
            tabs={getTabs(tokens[selectedTokenId])}
            onClose={() => selectToken(null)}
          />
        )}
      </main>
    </div>
  )
}
```

**Test:** Upload image → tokens appear in real-time → click token → shows detail panel with tabs

---

## The Big Picture After Refactor

```
frontend/src/
├── components/
│   ├── ui/                      ← REUSABLE LIBRARY (18-20 components)
│   │   ├── card/
│   │   ├── grid/
│   │   ├── tabs/
│   │   ├── panel/
│   │   ├── sidebar/
│   │   ├── progress/
│   │   ├── input/
│   │   └── dashboard/
│   │
│   └── features/                ← FEATURE-SPECIFIC (80+ components)
│       ├── visual-extraction/   ← COLOR, SPACING, TYPOGRAPHY, SHADOW
│       ├── image-uploader/
│       ├── diagnostics-panel/
│       ├── metrics-overview/
│       ├── learning-sidebar/
│       └── token-explorer/      ← NEW
│
├── pages/                        ← PAGE COMPONENTS
├── store/                        ← ZUSTAND STORES
├── hooks/                        ← LOGIC HOOKS
└── design/                       ← DESIGN TOKENS
```

**Benefits:**
- ✅ Clear separation: library vs feature-specific
- ✅ Zero duplication
- ✅ Easy to add new token types (no touching ui/)
- ✅ All existing functionality preserved
- ✅ Can migrate features incrementally

---

## What Actually Gets Cleaned Up

| What | Before | After | Impact |
|------|--------|-------|--------|
| Duplicate dirs | color/ in 2 places | 1 place | Cleaner |
| Tab implementations | 3 custom | 1 generic + 2 users | Easier to maintain |
| Component discovery | Scattered in 6+ dirs | Organized in ui/ | Easier to find |
| Import paths | Mix of patterns | Consistent structure | Less confusion |
| Unused code | Maybe, hard to tell | Clear hierarchy | Easier to delete |

---

## What Does NOT Change

✅ Feature functionality (color/spacing/typography/shadow)
✅ Design system (colors, spacing, typography in CSS)
✅ Page routes and navigation
✅ API integration
✅ State management
✅ Tests (just update imports)
✅ Performance
✅ User experience

---

## Timeline

| Phase | Task | Time | Status |
|-------|------|------|--------|
| 0 | Assessment | Done | ✅ |
| 1 | Delete duplicates | 30 min | ⏳ |
| 2 | Create structure | 30 min | ⏳ |
| 3 | Move files | 1 hour | ⏳ |
| 4 | Fix imports | 1.5 hours | ⏳ |
| 5 | Consolidate tabs | 1-2 hours | ⏳ |
| 6 | Create PanelTabs | 1 hour | ⏳ |
| 7 | Integration + streaming | 2-3 hours | ⏳ |
| **Total** | | **~7-9 hours** | ⏳ |

---

## Risk Assessment

### Low Risk
- Deleting duplicate dirs (not used)
- Moving files with git mv (tracks history)
- Creating new component library structure (additive)

### Medium Risk
- Updating imports (tedious but straightforward with find/replace)
- Consolidating tabs (needs testing on each panel)

### High Risk
- None identified if we follow this plan

---

## Success Criteria

After refactor:
1. ✅ `pnpm typecheck` passes (zero errors)
2. ✅ `pnpm test` passes (all tests)
3. ✅ E2E tests pass (functionality unchanged)
4. ✅ All color/spacing/shadow features work
5. ✅ New token streaming works
6. ✅ Components are discoverable (organized in ui/)

---

## Next Decision

**Want to start Phase 1 now?** It's safe and quick:
1. Delete `components/color` and `components/spacing`
2. Create `components/ui/` structure
3. Run tests → should pass
4. Commit as "refactor: organize component library structure"

Or do you want to take a different approach?
