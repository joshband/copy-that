# Color Science Component Library

Modular component system for color token extraction, analysis, and visualization. Designed to be reusable, testable, and maintainable.

## Architecture

```
color-science/
├── types.ts                    # Shared TypeScript interfaces
├── hooks.ts                    # Custom React hooks
├── UploadSection.tsx          # File upload UI
├── ProjectControls.tsx        # Project management UI
├── PipelineVisualization.tsx  # Pipeline status visualization
├── EducationPanel.tsx         # Educational content sections
├── StatsPanel.tsx             # Statistics display
├── ColorGrid.tsx              # Color grid & spacing grid display
├── ColorDetailsPanel.tsx      # Detailed color analysis panel
├── index.ts                   # Central exports
└── README.md                  # This file
```

## Component Guide

### Types (`types.ts`)

**ColorToken** - Represents an extracted color with metadata
```typescript
interface ColorToken {
  hex: string              // Hex color code
  confidence: number       // Extraction confidence (0-1)
  name: string            // Human-readable name
  harmony?: string        // Color harmony type
  wcag_contrast_on_white?: number  // WCAG contrast ratio
  // ... 20+ additional properties
}
```

**PipelineStage** - Represents extraction pipeline stage
```typescript
interface PipelineStage {
  id: string
  name: string
  description: string
  status: 'pending' | 'running' | 'done' | 'error'
  duration?: number
}
```

### Hooks (`hooks.ts`)

#### `useColorConversion()`
Utilities for color analysis and manipulation.

```typescript
const { getVibrancy, copyToClipboard } = useColorConversion()

// Determine vibrancy level
const vibrancy = getVibrancy(color)  // 'vibrant' | 'muted' | 'balanced'

// Copy hex to clipboard
copyToClipboard(color.hex)
```

#### `useContrastCalculation()`
Utilities for accessibility analysis.

```typescript
const { getWCAGCompliance, getAccessibilityBadges } = useContrastCalculation()

// Check WCAG compliance
const compliance = getWCAGCompliance(color)
// { hasOnWhiteContrast, hasOnBlackContrast, onWhitePasses, onBlackPasses }

// Get accessibility badges
const badges = getAccessibilityBadges(color)
// ['AA', 'AAA', 'Colorblind Safe']
```

### UI Components

#### `UploadSection`
File upload with drag-and-drop support.

**Props:**
```typescript
interface UploadSectionProps {
  preview: string | null
  isExtracting: boolean
  onFileChange: (e: React.ChangeEvent<HTMLInputElement>) => void
  onDrop: (e: React.DragEvent<HTMLDivElement>) => void
  onExtract: () => void
  selectedFile: File | null
}
```

#### `ProjectControls`
Project management interface (save, load, snapshots).

**Props:**
```typescript
interface ProjectControlsProps {
  projectName: string
  projectId: number
  loadProjectId: string
  colors: any[]
  spacingTokens: any[]
  imageBase64: string | null
  imageMediaType: string
  onProjectNameChange: (name: string) => void
  onSaveProject: () => void
  onLoadProjectIdChange: (id: string) => void
  onLoadProject: () => void
  onLoadSnapshot: () => void
}
```

#### `PipelineVisualization`
Displays 5-stage extraction pipeline with status indicators.

**Props:**
```typescript
interface PipelineVisualizationProps {
  stages: PipelineStage[]
}
```

#### `EducationPanel`
6 collapsible sections with color science education content.

**Props:**
```typescript
interface EducationPanelProps {
  expandedEducation: string | null
  onExpandTopic: (topic: string | null) => void
  paletteDescription: string
}
```

Topics:
1. Algorithm Pipeline
2. Delta-E (CIEDE2000)
3. WCAG Accessibility
4. Color Spaces
5. Semantic Naming
6. Palette Narrative

#### `StatsPanel`
Statistics overview (color count, confidence, WCAG compliance).

**Props:**
```typescript
interface StatsPanelProps {
  colors: ColorToken[]
  extractorUsed: string
  paletteDescription: string
}
```

#### `ColorGrid` & `SpacingGrid`
Color grid display with selection and metadata.

**ColorGrid Props:**
```typescript
interface ColorGridProps {
  colors: ColorToken[]
  selectedColorIndex: number | null
  onSelectColor: (index: number) => void
  onCopyHex: (hex: string) => void
}
```

#### `ColorDetailsPanel`
Comprehensive color analysis display showing all color properties.

**Props:**
```typescript
interface ColorDetailsPanelProps {
  selectedColor: ColorToken | null
  paletteDescription?: string
}
```

Features:
- Color swatch display
- Color values (HEX, RGB, HSL, HSV)
- Properties (temperature, saturation, lightness, harmony)
- WCAG accessibility ratios and badges
- Color variants (tint, shade, tone)
- Semantic names
- Design intent narrative
- Web integration (web-safe, CSS named)
- Provenance tracking

## Usage Examples

### Basic Import
```typescript
import { ColorToken, ColorGrid, useColorConversion } from './color-science'
```

### Using Individual Components
```typescript
import { ColorDetailsPanel } from './color-science'

export function MyColorAnalyzer() {
  const [selectedColor, setSelectedColor] = useState<ColorToken | null>(null)

  return (
    <ColorDetailsPanel
      selectedColor={selectedColor}
      paletteDescription="Warm palette"
    />
  )
}
```

### Using Hooks
```typescript
import { useColorConversion, useContrastCalculation } from './color-science'

export function ColorAnalyzer({ color }: { color: ColorToken }) {
  const { getVibrancy, copyToClipboard } = useColorConversion()
  const { getAccessibilityBadges } = useContrastCalculation()

  const vibrancy = getVibrancy(color)
  const badges = getAccessibilityBadges(color)

  return (
    <div>
      <p>Vibrancy: {vibrancy}</p>
      <p>Accessibility: {badges.join(', ')}</p>
      <button onClick={() => copyToClipboard(color.hex)}>
        Copy {color.hex}
      </button>
    </div>
  )
}
```

## CSS Classes

All components use BEM-style CSS classes defined in `AdvancedColorScienceDemo.css`:

- `.color-card` - Individual color display
- `.color-swatch` - Color preview square
- `.detail-swatch` - Large color detail preview
- `.wcag-*` - WCAG compliance indicators
- `.pipeline-stage` - Pipeline visualization stages
- `.edu-topic` - Collapsible education sections
- `.stats-grid` - Statistics grid layout

## Contributing

When adding new features:

1. **Types** - Add interfaces to `types.ts`
2. **Logic** - Extract reusable logic to `hooks.ts`
3. **Components** - Create focused UI components
4. **Exports** - Add to `index.ts`

## Testing

Components are designed for easy unit testing:

```typescript
// Test a hook
import { useColorConversion } from './hooks'

it('should determine vibrant color', () => {
  const { getVibrancy } = useColorConversion()
  const color = { hsl: 'hsl(0, 80%, 60%)' }
  expect(getVibrancy(color)).toBe('vibrant')
})

// Test a component
import { StatsPanel } from './StatsPanel'

it('should display color count', () => {
  const colors = [{ confidence: 0.95 }, { confidence: 0.87 }]
  render(<StatsPanel colors={colors} extractorUsed="AI" paletteDescription="" />)
  expect(screen.getByText('2')).toBeInTheDocument()
})
```

## Performance Considerations

- Components use `React.memo` when appropriate
- Callbacks are memoized with `useCallback`
- Large lists use efficient rendering patterns
- Event handlers properly cleaned up

## Accessibility

- Semantic HTML structure
- ARIA labels on interactive elements
- Color contrast ratios validated
- Keyboard navigation supported
- Screen reader friendly

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Roadmap

- [ ] Component storybook
- [ ] Vitest unit tests
- [ ] E2E tests with Playwright
- [ ] CSS modularization
- [ ] Theme support
- [ ] Internationalization (i18n)

## License

Part of Copy That project - see root LICENSE

## Related Documentation

- [Issue #9A: Component Refactoring Completion](../ISSUE_9A_COMPLETION_SUMMARY.md)
- [Issue #9B: Future Refactoring Plan](../ISSUE_9B_PLAN.md)
- [AdvancedColorScienceDemo Component](../AdvancedColorScienceDemo.tsx)
