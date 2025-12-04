# Visual Guide: Source Badges on Metrics

## What You'll See After Pressing Extract

### Layout of Each Metric Card

```
┌─────────────────────────────────────────────────────┐
│ 🎨 Art Movement ─────────────────────────────────── │
│                [🎨 Colors] [75% • High Confidence]  │
│                                                      │
│ Retro-Futurism                                      │
│ 1950s-1970s sci-fi aesthetic                       │
│ • Space-race optimism and wonder                   │
│ • Chrome-and-plastic modernism                     │
│ • Atomic age revivalism                            │
│ • Golden Age of design futurism                    │
└─────────────────────────────────────────────────────┘
```

## All Metric Cards with Source Badges

### Color-Based Metrics

```
┌─────────────────────────────────────────────────────┐
│ 🎨 Art Movement                                     │
│               [🎨 Colors] [75% • High Confidence]   │
│ Retro-Futurism                                      │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│ 💭 Emotional Tone                                   │
│            [🎨 Colors] [45% • Possible Interp.]   │
│ Balanced                                            │
│ ⚠ This palette is subtle — multiple interpretations│
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│ 🌡️ Temperature Profile                              │
│               [🎨 Colors] [70% • Likely Match]     │
│ Warm Dominant                                       │
│ • Solar and inviting atmosphere                    │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│ ✨ Saturation Character                             │
│             [🎨 Colors] [37% • Possible Interp.]   │
│ Muted & Subdued                                     │
│ • Soft chromatic restraint                         │
└─────────────────────────────────────────────────────┘
```

### Multi-Token Metrics

```
┌─────────────────────────────────────────────────────┐
│ ⏱️ Design Complexity                                 │
│               [📊 All Tokens] [75% • High Conf.]   │
│ Moderate                                            │
│ • Well-rounded system foundation                   │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│ 💪 System Health                                    │
│              [📊 All Tokens] [55% • Possible I.]   │
│ 21 total tokens across all categories              │
│ • Foundation tokens in place                       │
└─────────────────────────────────────────────────────┘
```

## Badge Colors and Meanings

### 🎨 Colors Badge
```
┌──────────────────────────┐
│ 🎨 Colors  (Blue Badge)  │
├──────────────────────────┤
│ Meaning:                 │
│ Extracted from colors    │
│ (Real extraction data)   │
└──────────────────────────┘
```

### 📊 All Tokens Badge
```
┌──────────────────────────┐
│ 📊 All Tokens (Blue)     │
├──────────────────────────┤
│ Meaning:                 │
│ From multiple token      │
│ categories (More data)   │
└──────────────────────────┘
```

### Database Badge (Gray - No extraction)
```
┌──────────────────────────┐
│ Database   (Gray Badge)  │
├──────────────────────────┤
│ Meaning:                 │
│ No extracted data yet    │
│ (Fallback/old data)      │
└──────────────────────────┘
```

## Real-World Example: You Upload an Image

### Timeline

**T=0s: Image Uploaded**
```
Header: "Processing image…" (loading indicator)
Metrics: Hidden (waiting for extraction)
```

**T=1s-3s: Extraction Running**
```
Colors extracted ✓
Spacing extracted ✓
Typography in progress...

Metrics: Starting to appear
Art Movement: [🎨 Colors] [75% • High Confidence]
```

**T=3s-5s: Extraction Complete**
```
All tokens extracted ✓

Metrics: Fully displayed with source badges
🎨 Art Movement: [🎨 Colors] [75% • High Confidence]
💭 Emotional Tone: [🎨 Colors] [45% • Possible]
🌡️ Temperature: [🎨 Colors] [70% • Likely Match]
✨ Saturation: [🎨 Colors] [37% • Possible]
⏱️ Complexity: [📊 All Tokens] [75% • High Confidence]
💪 Health: [📊 All Tokens] [55% • Possible]
```

## Comparison: Before vs After

### BEFORE (Without Source Badges)
```
🎨 Art Movement — Retro-Futurism — 75% • High Confidence
🎨 Art Movement — Retro-Futurism — 75% • High Confidence
🎨 Art Movement — Retro-Futurism — 75% • High Confidence

❓ User thinks: "Wait, is this from my image or a default?"
```

### AFTER (With Source Badges)
```
🎨 Art Movement — Retro-Futurism — [🎨 Colors] [75% • High Confidence]
💭 Emotional Tone — Balanced — [🎨 Colors] [45% • Possible Interpretation]
🌡️ Temperature — Warm Dominant — [🎨 Colors] [70% • Likely Match]

✅ User thinks: "Clear! These are from my extracted colors!"
```

## Key Visual Differences

| Element | Before | After |
|---------|--------|-------|
| Confidence Badge | `75% • High Confidence` | `[🎨 Colors] [75% • High Confidence]` |
| Badge Color | Single gold/orange | Single badge + blue source badge |
| Clarity | Ambiguous source | Clear data source indicator |
| User Understanding | "Is this real?" | "Yes, from extracted colors" |

## When Source Badges Appear

✅ **Appear when:**
- Image extraction completes
- Tokens are in the database
- Metrics page is refreshed
- New extraction happens

❌ **Don't appear when:**
- App first loads (no data yet)
- During extraction (still processing)
- Before any image upload

## Interaction Notes

### Hover Effects (Coming Soon)
When you hover over a source badge:
```
[🎨 Colors]
  ↓
"Inferred from 12 extracted colors"
"Last updated: 2 minutes ago"
```

### What Doesn't Change
- Confidence percentages still show (e.g., "75%")
- Confidence labels still show (e.g., "High Confidence")
- Metric titles and descriptions unchanged
- Overall layout preserved

## Accessibility

Source badges are:
- ✅ Semantic HTML (not just visual)
- ✅ Screen reader accessible
- ✅ Clear text alternative
- ✅ High contrast colors
- ✅ Large enough touch targets

## Mobile View

On mobile devices, the layout adapts:

```
┌─────────────────────┐
│ 🎨 Art Movement     │
│ [🎨 Colors]        │
│ [75% • High Conf.]  │
│                     │
│ Retro-Futurism     │
└─────────────────────┘
```

(Badges stack vertically for smaller screens)
