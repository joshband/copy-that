# Component Migration Matrix

**Document Date:** 2025-12-09
**Purpose:** Complete mapping of all 44 components to new locations
**Quick Reference:** What goes where

---

## Migration Summary

| Metric | Current | Target | Change |
|--------|---------|--------|--------|
| **Root Components** | 45 | 6 | -87% |
| **Feature Modules** | 0 | 1 | +1 |
| **Shared Components** | 0 | 8 | +8 |
| **Visual Components** | 27 (scattered) | 27 (organized) | Consolidated |

---

## Layer 1: Shared Components (Token-Agnostic)

**Target:** `src/shared/components/`

| # | Current Location | New Location | Refactor Needed |
|---|------------------|--------------|-----------------|
| 1 | `components/TokenCard.tsx` | `shared/components/TokenCard/` | ✅ Add adapter support |
| 2 | `components/TokenGraphPanel.tsx` | `shared/components/TokenGraphPanel/` | ❌ Move as-is |
| 3 | `components/TokenGrid.tsx` | `shared/components/TokenGrid/` | ❌ Move as-is |
| 4 | `components/TokenToolbar.tsx` | `shared/components/TokenToolbar/` | ❌ Move as-is |
| 5 | `components/RelationsTable.tsx` | `shared/components/RelationsTable/` | ❌ Move as-is |
| 6 | `components/RelationsDebugPanel.tsx` | `shared/components/RelationsDebugPanel/` | ❌ Move as-is |
| 7 | `components/TokenInspectorSidebar.tsx` | `shared/components/TokenInspectorSidebar/` | ⚠️ Minor adapter updates |
| 8 | `components/TokenPlaygroundDrawer.tsx` | `shared/components/TokenPlaygroundDrawer/` | ⚠️ Minor adapter updates |

**Phase:** Week 1 (Phase 1)
**Effort:** 8-12 hours
**Priority:** HIGH (enables all other work)

---

## Layer 2A: Color Components (Visual-Specific)

**Target:** `features/visual-extraction/components/color/`

| # | Current Location | New Location | New Name |
|---|------------------|--------------|----------|
| 1 | `components/ColorTokenDisplay.tsx` | `visual-extraction/components/color/ColorDisplay/` | ColorDisplay |
| 2 | `components/ColorGraphPanel.tsx` | `visual-extraction/components/color/ColorGraph/` | ColorGraph |
| 3 | `components/ColorsTable.tsx` | `visual-extraction/components/color/ColorTable/` | ColorTable |
| 4 | `components/ColorPrimaryPreview.tsx` | `visual-extraction/components/color/ColorPreview/` | ColorPreview |
| 5 | `components/ColorPaletteSelector.tsx` | `visual-extraction/components/color/ColorPalette/` | ColorPalette |
| 6 | `components/CompactColorGrid.tsx` | `visual-extraction/components/color/ColorGrid/` | ColorGrid |
| 7 | `components/HarmonyVisualizer.tsx` | `visual-extraction/components/color/HarmonyVisualizer/` | HarmonyVisualizer |
| 8 | `components/EducationalColorDisplay.tsx` | `visual-extraction/components/color/EducationalDisplay/` | EducationalDisplay |
| 9 | `components/ColorNarrative.tsx` | `visual-extraction/components/color/ColorNarrative/` | ColorNarrative |
| 10 | `components/color-detail-panel/` (5 tabs) | `visual-extraction/components/color/ColorDetailPanel/` | ColorDetailPanel |
| 11 | `components/color-science/` (7 files) | `visual-extraction/components/color/color-science/` | Keep as-is |
| 12 | `components/OverviewNarrative.tsx` | `visual-extraction/components/color/OverviewNarrative/` | OverviewNarrative |

**Phase:** Week 2, Day 2-3 (Phase 2)
**Effort:** 12 hours
**Priority:** HIGH

---

## Layer 2B: Spacing Components (Visual-Specific)

**Target:** `features/visual-extraction/components/spacing/`

| # | Current Location | New Location | New Name |
|---|------------------|--------------|----------|
| 1 | `components/SpacingScalePanel.tsx` | `visual-extraction/components/spacing/SpacingScale/` | SpacingScale |
| 2 | `components/SpacingTable.tsx` | `visual-extraction/components/spacing/SpacingTable/` | SpacingTable |
| 3 | `components/SpacingGraphList.tsx` | `visual-extraction/components/spacing/SpacingGraph/` | SpacingGraph |
| 4 | `components/SpacingRuler.tsx` | `visual-extraction/components/spacing/SpacingRuler/` | SpacingRuler |
| 5 | `components/SpacingGapDemo.tsx` | `visual-extraction/components/spacing/SpacingDemo/` | SpacingDemo |
| 6 | `components/SpacingDetailCard.tsx` | `visual-extraction/components/spacing/SpacingDetails/` | SpacingDetails |
| 7 | `components/SpacingResponsivePreview.tsx` | `visual-extraction/components/spacing/SpacingPreview/` | SpacingPreview |
| 8 | `components/spacing-showcase/` (6 files) | `visual-extraction/components/spacing/SpacingShowcase/` | SpacingShowcase |

**Phase:** Week 2, Day 4 (Phase 2)
**Effort:** 4 hours
**Priority:** MEDIUM

---

## Layer 2C: Typography Components (Visual-Specific)

**Target:** `features/visual-extraction/components/typography/`

| # | Current Location | New Location | New Name |
|---|------------------|--------------|----------|
| 1 | `components/TypographyInspector.tsx` | `visual-extraction/components/typography/TypographyInspector/` | TypographyInspector |
| 2 | `components/TypographyDetailCard.tsx` | `visual-extraction/components/typography/TypographyDetails/` | TypographyDetails |
| 3 | `components/TypographyCards.tsx` | `visual-extraction/components/typography/TypographyCards/` | TypographyCards |
| 4 | `components/FontFamilyShowcase.tsx` | `visual-extraction/components/typography/FontShowcase/` | FontShowcase |
| 5 | `components/FontSizeScale.tsx` | `visual-extraction/components/typography/FontSizeScale/` | FontSizeScale |

**Phase:** Week 2, Day 5 (Phase 2)
**Effort:** 2 hours
**Priority:** MEDIUM

---

## Layer 2D: Shadow Components (Visual-Specific)

**Target:** `features/visual-extraction/components/shadow/`

| # | Current Location | New Location | New Name |
|---|------------------|--------------|----------|
| 1 | `components/ShadowInspector.tsx` | `visual-extraction/components/shadow/ShadowInspector/` | ShadowInspector |
| 2 | `components/shadows/` (8 files) | `visual-extraction/components/shadow/ShadowTokenList/` | ShadowTokenList |

**Phase:** Week 2, Day 5 (Phase 2)
**Effort:** 2 hours
**Priority:** MEDIUM

---

## Layer 3: App Infrastructure Components

**Target:** `components/` (keep at root)

| # | Current Location | Keep At | Reason |
|---|------------------|---------|--------|
| 1 | `components/MetricsOverview.tsx` | `components/MetricsOverview/` | System-wide metrics |
| 2 | `components/SessionCreator.tsx` | `components/SessionCreator/` | Project management |
| 3 | `components/SessionWorkflow.tsx` | `components/SessionWorkflow/` | Multi-step workflow |
| 4 | `components/LibraryCurator.tsx` | `components/LibraryCurator/` | Token library mgmt |
| 5 | `components/ExportDownloader.tsx` | `components/ExportDownloader/` | Multi-token export |
| 6 | `components/image-uploader/` (7 files) | `features/image-upload/` | Infrastructure feature |

**Phase:** Week 2-3 (Phase 2)
**Effort:** 4 hours (just move image-uploader)
**Priority:** LOW

---

## Layer 4: Educational/Demo Components

**Target:** `features/education/` OR deprecate

| # | Current Location | Decision | Reason |
|---|------------------|----------|--------|
| 1 | `components/LearningSidebar.tsx` | ⚠️ Evaluate | Educational content |
| 2 | `components/PlaygroundSidebar.tsx` | ⚠️ Evaluate | Demo playground |
| 3 | `components/AdvancedColorScienceDemo.tsx` | ✅ Keep in color-science/ | Already organized |
| 4 | `components/AccessibilityVisualizer.tsx` | ✅ Keep in color/ | Used in color features |
| 5 | `components/BatchImageUploader.tsx` | ❌ Deprecate | Unused |
| 6 | `components/CostDashboard.tsx` | ❌ Deprecate | Unused |

**Phase:** Week 2-3 (Phase 2)
**Effort:** 2 hours (deprecation only)
**Priority:** LOW

---

## Adapters (New Files)

**Target:** `features/visual-extraction/adapters/`

| # | New File | Implements | Lines Est. |
|---|----------|------------|------------|
| 1 | `ColorVisualAdapter.ts` | Color token rendering | ~80 |
| 2 | `SpacingVisualAdapter.ts` | Spacing token rendering | ~80 |
| 3 | `TypographyVisualAdapter.ts` | Typography token rendering | ~80 |
| 4 | `ShadowVisualAdapter.ts` | Shadow token rendering | ~80 |

**Phase:** Week 3 (Phase 3)
**Effort:** 12 hours
**Priority:** HIGH

---

## Migration Order (Recommended)

### Week 1: Foundation
1. Create adapter interface (1 hour)
2. Create adapter registry (1 hour)
3. Create ColorVisualAdapter (2 hours)
4. Refactor TokenCard (4 hours)
5. Move 7 remaining shared components (4 hours)

**Total:** 12 hours

### Week 2: Visual Components
1. Create directory structure (2 hours)
2. Move 12 color components (12 hours)
3. Move 8 spacing components (4 hours)
4. Move 5 typography components (2 hours)
5. Move 2 shadow components (2 hours)
6. Move image-uploader to features/ (2 hours)

**Total:** 24 hours

### Week 3: Adapters
1. Create SpacingVisualAdapter (3 hours)
2. Create TypographyVisualAdapter (3 hours)
3. Create ShadowVisualAdapter (3 hours)
4. Refactor remaining shared components (8 hours)
5. Testing and documentation (4 hours)

**Total:** 21 hours

### Week 4: Validation
1. Create audio schema (4 hours)
2. Create AudioVisualAdapter (2 hours)
3. Mock audio tokens (2 hours)
4. Documentation and demo (8 hours)

**Total:** 16 hours

**Grand Total:** 73 hours (just under 2 weeks of full-time work)

---

## Import Update Patterns

### Before (Flat Structure)
```typescript
// App.tsx
import ColorTokenDisplay from './components/ColorTokenDisplay'
import SpacingTable from './components/SpacingTable'
import TokenCard from './components/TokenCard'
import MetricsOverview from './components/MetricsOverview'
```

### After (Feature-Based)
```typescript
// App.tsx
import { ColorDisplay } from '@/features/visual-extraction/components/color'
import { SpacingTable } from '@/features/visual-extraction/components/spacing'
import { TokenCard } from '@/shared/components/TokenCard'
import { MetricsOverview } from '@/components/MetricsOverview'
```

### Batch Update Script
```bash
# Find all color imports
rg "from.*components/(Color)" frontend/src/App.tsx

# Replace pattern (manual or with sed)
# Old: from './components/ColorTokenDisplay'
# New: from '@/features/visual-extraction/components/color/ColorDisplay'
```

---

## Verification Checklist

**After each component move:**
- [ ] File moved to correct location
- [ ] Barrel export created/updated
- [ ] Imports in App.tsx updated
- [ ] Tests still passing
- [ ] Component renders in browser
- [ ] Clean commit made

**After each phase:**
- [ ] All components in correct locations
- [ ] All barrel exports working
- [ ] All imports using path aliases
- [ ] All tests passing
- [ ] App works identically
- [ ] TypeScript has zero errors

---

## Rollback Plan

**If migration breaks:**

1. Identify last working commit: `git log --oneline`
2. Rollback to last working state: `git reset --hard <commit>`
3. Review what broke: `git diff <commit> HEAD`
4. Fix issue or pause migration
5. Document issue in rollback log

**Common issues:**
- Circular imports (check barrel exports)
- Missing types (check index.ts files)
- Broken tests (check mock data paths)
- Build errors (clear cache and rebuild)

---

## Component Count Verification

**Before migration:**
```bash
# Count components in root
ls frontend/src/components/*.tsx | wc -l
# Expected: ~45

# Count subdirectories
ls -d frontend/src/components/*/ | wc -l
# Expected: ~14
```

**After migration:**
```bash
# Count shared components
ls frontend/src/shared/components/*/index.ts | wc -l
# Expected: 8

# Count visual-extraction components
find frontend/src/features/visual-extraction/components -name "*.tsx" | wc -l
# Expected: 27

# Count root components
ls frontend/src/components/*.tsx | wc -l
# Expected: 0 (all in subdirs)
```

---

## Quick Reference: Component Locations

### Shared (8)
- TokenCard, TokenGraphPanel, TokenGrid, TokenToolbar
- RelationsTable, RelationsDebugPanel
- TokenInspectorSidebar, TokenPlaygroundDrawer

### Color (12)
- ColorDisplay, ColorGraph, ColorTable, ColorPreview
- ColorPalette, ColorGrid, HarmonyVisualizer
- EducationalDisplay, ColorNarrative, ColorDetailPanel
- color-science/, OverviewNarrative

### Spacing (8)
- SpacingScale, SpacingTable, SpacingGraph, SpacingRuler
- SpacingDemo, SpacingDetails, SpacingPreview, SpacingShowcase

### Typography (5)
- TypographyInspector, TypographyDetails, TypographyCards
- FontShowcase, FontSizeScale

### Shadow (2)
- ShadowInspector, ShadowTokenList

### Infrastructure (6)
- MetricsOverview, SessionCreator, SessionWorkflow
- LibraryCurator, ExportDownloader, image-upload/

---

**Document Status:** Migration Reference
**Last Updated:** 2025-12-09
**Use For:** Quick lookups during migration
