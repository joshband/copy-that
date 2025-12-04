# Metrics Source Badges Enhancement

## Overview

Added source badges to the metrics overview cards to clearly indicate which data sources are used for each metric calculation. This solves the issue where metrics appeared to load with defaults instead of waiting for actual extraction analysis.

## Changes Made

### 1. Backend API Enhancement (`src/copy_that/interfaces/api/design_tokens.py`)

**Added source tracking to the `/overview/metrics` endpoint:**

```python
"source": {
    "has_extracted_colors": len(colors) > 0,
    "has_extracted_spacing": len(spacing) > 0,
    "has_extracted_typography": len(typography) > 0,
}
```

This allows the frontend to know:
- Whether colors were actually extracted (from image analysis)
- Whether spacing tokens were extracted
- Whether typography tokens were extracted

### 2. Frontend Type Definitions (`frontend/src/components/MetricsOverview.tsx`)

**Extended `OverviewMetricsData` interface:**

```typescript
source?: {
  has_extracted_colors: boolean;
  has_extracted_spacing: boolean;
  has_extracted_typography: boolean;
};
```

### 3. UI Component Updates

**Enhanced `DesignInsightCard` component:**
- Added `source` parameter to track data source
- Display source badge in blue (🎨 Colors, 📊 All Tokens, or Database)
- Badge appears next to confidence score

**Source badge colors and labels:**
- **🎨 Colors** (Blue badge) - Metrics from extracted color tokens
- **📊 All Tokens** (Blue badge) - Metrics from multiple token types
- **Database** (Gray) - Fallback when no extraction data available

### 4. Metric Source Assignments

**Color-based metrics:**
- Art Movement → 🎨 Colors
- Emotional Tone → 🎨 Colors
- Temperature Profile → 🎨 Colors
- Saturation Character → 🎨 Colors

**Multi-token metrics:**
- Design Complexity → 📊 All Tokens
- System Health → 📊 All Tokens

## Visual Examples

### Before (No Source Indicators)
```
🎨 Art Movement — Retro-Futurism
   [75% • High Confidence]
   (No indication of data source)
```

### After (With Source Badges)
```
🎨 Art Movement — Retro-Futurism
   [🎨 Colors] [75% • High Confidence]
   (Clear indication from extracted colors)
```

## How It Works

### Data Flow

1. **User uploads image** → Image is extracted to color/spacing/typography tokens
2. **Metrics API called** → Backend queries database for tokens
3. **Source tracking** → Backend returns `source` object indicating which token types were found
4. **Frontend renders** → Each metric card displays appropriate source badge
5. **User sees** → Blue "🎨 Colors" badge = real extracted data, Gray "Database" = potential defaults

### Behavior

- **During extraction**: Metrics refresh with source badges showing active extractions
- **After extraction**: Badges indicate which data types contributed to each metric
- **Without extraction**: Source shows "Database" (fallback data)

## Testing

### Playwright Test
Location: `frontend/playwright/metrics-extraction.spec.ts`

Tests the full extraction flow:
1. Initial empty state
2. Image upload and extraction
3. Metrics display with source indicators
4. Async loading behavior

Run with:
```bash
pnpm exec playwright test metrics-extraction.spec.ts
```

### Manual Testing

1. Go to http://localhost:5173
2. Upload an image
3. Wait for extraction to complete
4. Switch to "Overview" tab
5. Look for blue source badges next to each metric (🎨 Colors or 📊 All Tokens)
6. Verify badges appear alongside confidence scores

## Benefits

✅ **Transparency** - Users know which data is from actual extraction vs. defaults
✅ **Clarity** - Source badges provide instant visual feedback
✅ **Trust** - Clear indication of metric reliability
✅ **Debugging** - Easy to identify when metrics are recalculated after new extraction
✅ **UX** - No confusion about whether metrics are "real" or placeholder data

## Future Enhancements

- Add timestamp to source badges (e.g., "Colors (2 min ago)")
- Allow filtering metrics by source type
- Add "data source" tooltip on hover with detailed breakdown
- Show extraction progress per token type
