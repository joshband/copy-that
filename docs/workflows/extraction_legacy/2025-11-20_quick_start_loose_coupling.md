# Quick Start: Loose Coupling Architecture

**Version**: v3.1 (Week 5 Complete)
**Last Updated**: 2025-11-13
**Audience**: Users & Developers

---

## What is Loose Coupling?

Loose coupling allows you to **run only the extractors you need**, with the system automatically providing sensible defaults for missing token categories. This enables faster extraction and more flexible workflows.

### Key Benefits

✅ **Faster Extraction**: Color-only extraction completes in <1s (vs 6.6s for all extractors)
✅ **Graceful Degradation**: Missing categories automatically use defaults
✅ **Clear Feedback**: Warning banners show which categories use defaults
✅ **Valid Output**: Generators produce working code even with partial tokens

---

## Common Use Cases

### Use Case 1: Color Palette Extraction (Photo Archive)

**Scenario**: You're building a photo management app and need to extract color palettes from thousands of images quickly.

**Solution**: Run color extractor only

**Speed**: <1s per image (vs 6.6s full extraction)

**Steps**:
1. Upload image to Copy This
2. Extraction completes in <1s
3. ⚠️ Warning banner appears: "Using default values for spacing, shadow, typography, radius"
4. Color palette displays immediately
5. Export to Figma/React/MUI with warning comments in code
6. Customize defaults manually if needed

**Expected Output**:
```json
{
  "palette": {
    "primary": "#FF5733",
    "secondary": "#C70039",
    "accent": "#FFC300"
  },
  "spacing": {
    "xs": 4,
    "sm": 8,
    "md": 16
  }
}
```

**Warning Comment** (in generated code):
```html
<!-- WARNING: The following token categories are using default values (not extracted): -->
<!-- spacing, shadow, typography, radius -->
<!-- To extract these tokens, enable the corresponding extractors in your configuration. -->
```

### Use Case 2: Data Visualization UI (Color + Spacing)

**Scenario**: You're extracting tokens from a chart/graph UI that has custom colors and spacing but no typography or shadows.

**Solution**: Run color + spacing extractors

**Speed**: ~2s per image

**Steps**:
1. Upload data viz screenshot
2. Extraction completes in ~2s
3. ⚠️ Warning banner: "Using default values for typography, shadow, radius"
4. Color palette + spacing scale display
5. Export with partial warnings

**Expected Output**:
```json
{
  "palette": {
    "primary": "#4A90E2",
    "secondary": "#50E3C2"
  },
  "spacing": {
    "xs": 8,
    "sm": 16,
    "md": 24,
    "lg": 32
  }
}
```

### Use Case 3: Complete Design System (All Extractors)

**Scenario**: You're extracting a full design system from a Figma mockup.

**Solution**: Run all extractors (default behavior)

**Speed**: ~3.2s per image (2.0x faster than before due to parallel extraction)

**Steps**:
1. Upload UI screenshot
2. Extraction completes in ~3.2s
3. ✅ No warning banner (all categories extracted)
4. All token categories display
5. Export with no warnings

**Expected Output**:
```json
{
  "palette": { "primary": "#3b82f6", ... },
  "spacing": { "xs": 4, "sm": 8, ... },
  "typography": { "family": "Inter", ... },
  "shadow": { "level1": "0 1px 3px ...", ... },
  "radius": { "sm": 4, "md": 8, ... }
}
```

---

## User Interface Guide

### Warning Banner

When token categories are missing, a warning banner appears:

```
⚠️  Using Default Values
Using default values for 3 categories: spacing, shadow, typography

To extract these tokens, enable the corresponding extractors in your extraction
configuration. The UI will work with defaults, but extracted values will provide
better results.

[spacing] [shadow] [typography]            [×]
```

**Features**:
- **Dismissible**: Click [×] to hide (persists for session)
- **Informative**: Lists missing categories with badges
- **Actionable**: Explains how to extract missing categories
- **Non-blocking**: UI continues to work with defaults

### Token Display

**With All Categories Extracted**:
```
┌─────────────────────────────┐
│ Extracted Design Tokens     │
├─────────────────────────────┤
│ ✅ Color Palette    (12)    │
│ ✅ Spacing Scale    (6)     │
│ ✅ Typography       (4)     │
│ ✅ Shadows          (4)     │
│ ✅ Border Radius    (5)     │
└─────────────────────────────┘
```

**With Partial Extraction** (Color Only):
```
┌─────────────────────────────┐
│ ⚠️  Using Default Values    │
│ spacing, shadow, typography │
├─────────────────────────────┤
│ ✅ Color Palette    (12)    │
│ ⚠️ Spacing Scale    (6)     │
│ ⚠️ Typography       (4)     │
│ ⚠️ Shadows          (4)     │
│ ⚠️ Border Radius    (5)     │
└─────────────────────────────┘
```

---

## Exported Code Examples

### Figma Tokens (W3C DTCG Format)

**Partial Extraction** (Color Only):

```json
{
  "color": {
    "primary": {
      "$value": "#FF5733",
      "$type": "color"
    },
    "secondary": {
      "$value": "#C70039",
      "$type": "color"
    }
  },
  "spacing": {
    "xs": {
      "$value": "4px",
      "$type": "dimension",
      "$description": "Spacing xs"
    },
    "sm": {
      "$value": "8px",
      "$type": "dimension",
      "$description": "Spacing sm"
    }
  }
}
```

**Warning Comment** (in separate file):
```html
<!-- WARNING: The following token categories are using default values (not extracted): -->
<!-- spacing, shadow, typography, radius -->
<!-- To extract these tokens, enable the corresponding extractors in your configuration. -->
```

### React/CSS Variables

**Partial Extraction** (Color Only):

```css
/* WARNING: The following token categories are using default values (not extracted): */
/* spacing, shadow, typography */
/* To extract these tokens, enable the corresponding extractors in your configuration. */

:root {
  /* Colors (extracted) */
  --primary: #FF5733;
  --secondary: #C70039;
  --accent: #FFC300;

  /* Spacing (defaults) */
  --space-xs: 4px;
  --space-sm: 8px;
  --space-md: 16px;
  --space-lg: 24px;

  /* Shadows (defaults) */
  --shadow1: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
}
```

### Material-UI Theme

**Partial Extraction** (Color Only):

```typescript
// WARNING: The following token categories are using default values (not extracted):
// spacing, shadow, typography
// To extract these tokens, enable the corresponding extractors in your configuration.

import { createTheme } from '@mui/material/styles';

const theme = createTheme({
  palette: {
    primary: {
      main: '#FF5733', // extracted
    },
    secondary: {
      main: '#C70039', // extracted
    },
  },
  spacing: 8, // default (not extracted)
  shadows: [
    'none',
    '0 1px 3px 0 rgba(0, 0, 0, 0.1)', // default
    // ... more defaults
  ],
});

export default theme;
```

---

## Developer Guide

### Frontend Integration

**Check if Token Category is Available**:

```tsx
import { isTokenCategoryAvailable, getMissingCategories } from '../utils/tokenDefaults'

function MyComponent({ tokens }) {
  // Check specific category
  const hasColors = isTokenCategoryAvailable(tokens, 'palette')

  // Get list of missing categories
  const missing = getMissingCategories(tokens)

  return (
    <>
      {missing.length > 0 && (
        <DefaultWarningBanner tokens={tokens} />
      )}

      {hasColors ? (
        <ColorPalette palette={tokens.palette} />
      ) : (
        <EmptyState message="No colors extracted" />
      )}
    </>
  )
}
```

**Get User-Friendly Warning Message**:

```tsx
import { getDefaultUsageMessage } from '../utils/tokenDefaults'

const message = getDefaultUsageMessage(tokens)
// Returns: "Using default values for 2 categories: spacing, shadow"
// Or null if no defaults used
```

### Generator Integration

**Create New Generator with Defensive Patterns**:

```typescript
import {
  safeGetTokens,
  generateWarningComment,
  hasTokenCategory,
  getExtractionSummary
} from './utils/tokenHelpers.js'

export function exportMyFormat(tokens: any): string {
  // Safe access - always returns valid tokens (extracted + defaults)
  const colors = safeGetTokens(tokens, 'color')
  const spacing = safeGetTokens(tokens, 'spacing')
  const typography = safeGetTokens(tokens, 'typography')

  // Generate warning comment for your format
  const warningComment = generateWarningComment(tokens, 'js') // or 'css', 'cpp', 'html'

  // Get extraction summary for metadata
  const summary = getExtractionSummary(tokens)
  // { extractionRate: 75, extractedCategories: ['color'], defaultCategories: ['spacing', 'typography'] }

  // Conditional inclusion based on extracted vs defaults
  let output = warningComment + '\n\n'

  // Always include color (extracted or default)
  output += `const colors = ${JSON.stringify(colors, null, 2)};\n\n`

  // Only include primitive tokens if actually extracted
  if (hasTokenCategory(tokens, 'color') && tokens.primitive) {
    output += `const primitiveColors = ${JSON.stringify(tokens.primitive, null, 2)};\n\n`
  }

  // Add metadata comment
  output += `// Extraction completeness: ${summary.extractionRate}%\n`

  return output
}
```

**Test Your Generator**:

```bash
# Run automated test suite
cd generators
node test-partial-tokens.js

# Or test manually
node -e "
const { exportMyFormat } = require('./dist/export-my-format.js');

// Test with color-only tokens
const partialTokens = {
  palette: { primary: '#FF5733' }
};

console.log(exportMyFormat(partialTokens));
"
```

---

## Customizing Defaults

### Frontend Defaults

**Location**: [`frontend/src/utils/tokenDefaults.ts`](../../frontend/src/utils/tokenDefaults.ts)

**Customize Color Palette**:

```typescript
export const TOKEN_DEFAULTS = {
  palette: {
    primary: '#YOUR_BRAND_COLOR',    // Change default primary
    secondary: '#YOUR_ACCENT_COLOR',  // Change default secondary
    accent: '#f59e0b',
    // ...
  },
  // ...
}
```

### Generator Defaults

**Location**: [`generators/src/utils/tokenHelpers.ts`](../../generators/src/utils/tokenHelpers.ts)

**Customize Spacing Scale**:

```typescript
export const GENERATOR_DEFAULTS = {
  spacing: {
    xs: 2,   // Tighter spacing
    sm: 4,
    md: 8,
    lg: 16,
    xl: 24,
    xxl: 32
  },
  // ...
}
```

**Note**: Keep frontend and generator defaults in sync for consistency.

---

## Troubleshooting

### Issue: Warning banner won't dismiss

**Cause**: Browser caching or state issue

**Solution**:
```tsx
// Clear dismissal state
localStorage.removeItem('warningDismissed')

// Or handle in component
const [dismissedWarning, setDismissedWarning] = useState(false)
```

### Issue: Generated code has unexpected defaults

**Cause**: Token category not extracted

**Solution**:
1. Check warning banner to see which categories use defaults
2. Enable corresponding extractors in backend config (Phase 2)
3. Or manually edit generated code to replace defaults

### Issue: Export fails with "Invalid token structure"

**Cause**: Token schema mismatch

**Solution**:
```typescript
// Validate token structure before export
import { getExtractionSummary } from './utils/tokenHelpers'

const summary = getExtractionSummary(tokens)
console.log('Extraction rate:', summary.extractionRate + '%')
console.log('Missing categories:', summary.defaultCategories)

// Ensure required categories are present
if (summary.extractionRate < 50) {
  console.warn('Low extraction rate - most tokens are defaults')
}
```

### Issue: TypeScript errors after adding token defaults

**Cause**: Type mismatch between `Partial<DesignTokens>` and `DesignTokens`

**Solution**:
```typescript
import { mergeWithDefaults } from '../utils/tokenDefaults'

// Before (may cause type errors)
const tokens: DesignTokens = apiResponse.tokens

// After (handles partial tokens)
const tokens = mergeWithDefaults(apiResponse.tokens)
```

---

## Performance Comparison

### Extraction Times

| Use Case | Extractors | Time (Before) | Time (After) | Speedup |
|----------|-----------|---------------|--------------|---------|
| Color only | 1 | 6.6s | <1s | **6.6x** |
| Color + Spacing | 2 | 6.6s | ~2s | **3.3x** |
| Color + Spacing + Shadow | 3 | 6.6s | ~2.5s | **2.6x** |
| All extractors | 48 | 6.6s | 3.2s | **2.0x** |

### Test Suite Performance

| Component | Tests | Pass Rate | Time |
|-----------|-------|-----------|------|
| Backend | 218 | 96.3% | ~45s |
| Extractors | 245 | 100% | ~120s |
| Frontend | N/A | 0 errors | ~15s (typecheck) |
| Generators | 3 scenarios | 100% | ~2s |

---

## Next Steps

### For Users

1. **Try color-only extraction** - Upload an image and see <1s extraction
2. **Explore warning banners** - See which categories use defaults
3. **Export with partial tokens** - Generate code with warning comments
4. **Customize defaults** - Edit `tokenDefaults.ts` to match your brand

### For Developers

1. **Read [LOOSE_COUPLING_STATUS.md](../architecture/LOOSE_COUPLING_STATUS.md)** - Implementation details
2. **Study generator examples** - See `export-figma.ts`, `export-react.ts`
3. **Run test suite** - `node generators/test-partial-tokens.js`
4. **Build new generators** - Use `safeGetTokens()` pattern

### Phase 2 Preview (Weeks 6-7)

Coming soon:
- ⏳ **Config-driven extractor selection** - Enable/disable extractors via YAML
- ⏳ **Multi-variant export** - Select dark/light/high-contrast variants
- ⏳ **Variant persistence** - Save preferences in localStorage
- ⏳ **Typography/radius variants** - 3 variants per category

---

## Resources

### Documentation

- [LOOSE_COUPLING_STATUS.md](../architecture/LOOSE_COUPLING_STATUS.md) - Complete implementation status
- [PARALLEL_EXTRACTION_DESIGN.md](../architecture/PARALLEL_EXTRACTION_DESIGN.md) - 2.0x speedup design
- [ROADMAP.md](../../ROADMAP.md) - Project roadmap

### Code Examples

- [`frontend/src/utils/tokenDefaults.ts`](../../frontend/src/utils/tokenDefaults.ts) - Token defaults
- [`frontend/src/components/DefaultWarningBanner.tsx`](../../frontend/src/components/DefaultWarningBanner.tsx) - Warning UI
- [`generators/src/utils/tokenHelpers.ts`](../../generators/src/utils/tokenHelpers.ts) - Generator utilities
- [`generators/test-partial-tokens.js`](../../generators/test-partial-tokens.js) - Test examples

### Support

- **GitHub Issues**: [Report bugs or request features](https://github.com/your-repo/copy-this/issues)
- **Documentation**: [Full docs](../../docs/)
- **Roadmap**: [See what's coming next](../../ROADMAP.md)

---

**Document Version**: v1.0
**Last Updated**: 2025-11-13
**Maintainer**: Copy This Development Team
