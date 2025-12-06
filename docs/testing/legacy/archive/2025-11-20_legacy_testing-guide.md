# Testing Guide: Metrics Source Badges

## Status Check

✅ **Containers Running**
- API: http://localhost:8000 (Healthy)
- Frontend: http://localhost:3000 or http://localhost:5173 (Healthy)
- Database: PostgreSQL (Connected)

✅ **Code Quality**
- TypeScript: pnpm type-check ✓ (No errors)
- Changes: 2 files modified, 50 lines added
- Type Safety: Full

## Quick Test (5 minutes)

### 1. Access the Application
```
Open browser → http://localhost:5173
```

### 2. Upload an Image
- Click the upload area or drag-and-drop an image
- Watch the "Processing image…" indicator in the header

### 3. View Metrics with Source Badges
1. Click "Overview" tab
2. Scroll to metrics section
3. Look for blue source badges next to each metric

**Expected Result:**
```
🎨 Art Movement — [🎨 Colors] [75% • High Confidence]
💭 Emotional Tone — [🎨 Colors] [45% • Possible]
🌡️ Temperature — [🎨 Colors] [70% • Likely Match]
✨ Saturation — [🎨 Colors] [37% • Possible]
⏱️ Complexity — [📊 All Tokens] [75% • High Confidence]
💪 Health — [📊 All Tokens] [55% • Possible]
```

## Detailed Test Scenarios

### Scenario 1: Fresh Upload with All Extractions
**Goal:** Verify badges appear when all token types are extracted

**Steps:**
1. Upload image (any image with colors)
2. Wait for extraction (watch header)
3. Go to Overview tab
4. Verify source badges appear: `[🎨 Colors]` or `[📊 All Tokens]`

**Expected:** All badges show extraction source

### Scenario 2: Partial Extraction
**Goal:** Verify badges update based on what was extracted

**Steps:**
1. Upload image
2. Wait for extraction
3. View metrics

**Expected:**
- Color metrics: `[🎨 Colors]`
- Complexity/Health: `[📊 All Tokens]` (multiple types)

### Scenario 3: Multiple Uploads
**Goal:** Verify badges update correctly on each extraction

**Steps:**
1. Upload image 1 → note metrics and badges
2. Wait for extraction
3. Upload image 2 (different style)
4. Wait for extraction
5. Check Overview tab

**Expected:**
- Metrics update for image 2
- Badges remain visible
- No stale data shown

### Scenario 4: Tab Switching
**Goal:** Verify badges persist across tab navigation

**Steps:**
1. Upload image
2. Go to Overview → see metrics with badges
3. Switch to Colors tab
4. Back to Overview tab

**Expected:** Badges still visible, no flicker

## Testing the Backend API

### Test Endpoint Directly
```bash
# Get metrics for project 1
curl http://localhost:8000/api/v1/design-tokens/overview/metrics?project_id=1 | jq '.source'
```

**Expected Response:**
```json
{
  "has_extracted_colors": true,
  "has_extracted_spacing": false,
  "has_extracted_typography": false
}
```

### Test with Project ID
1. Note the project ID from header (e.g., "Project #1")
2. Use that ID in the curl command above
3. Verify source flags match extracted data

## Automated Testing

### Run Playwright Test
```bash
# From project root
pnpm exec playwright test frontend/playwright/metrics-extraction.spec.ts
```

**What it tests:**
- Initial empty state
- Image upload and extraction
- Metrics display with source indicators
- Async loading behavior

**Expected:**
- All tests pass ✓
- Screenshots created in `playwright/screenshots/`

## Visual Verification Checklist

### During Extraction
- [ ] Header shows "Processing image…"
- [ ] Colors appear in Colors tab
- [ ] Extraction progress visible

### After Extraction (Overview Tab)
- [ ] Metrics cards display
- [ ] Each metric has a source badge
- [ ] Badges are blue colored
- [ ] Badges show: `🎨 Colors` or `📊 All Tokens`
- [ ] Badges appear next to confidence score
- [ ] Text is readable and not cut off
- [ ] No console errors in DevTools

### Badge Specifics
- [ ] Art Movement: `[🎨 Colors]`
- [ ] Emotional Tone: `[🎨 Colors]`
- [ ] Temperature Profile: `[🎨 Colors]`
- [ ] Saturation Character: `[🎨 Colors]`
- [ ] Design Complexity: `[📊 All Tokens]`
- [ ] System Health: `[📊 All Tokens]`

### Confidence Scores
- [ ] Confidence percentages show (e.g., "75%")
- [ ] Confidence labels show (e.g., "High Confidence")
- [ ] Low confidence shows warning message

### Responsive Design
- [ ] Desktop (1920px): Badges display correctly
- [ ] Tablet (768px): Badges stack properly
- [ ] Mobile (375px): Badges readable and accessible

## Browser Console Check

### Open DevTools
1. Press `F12` or `Ctrl+Shift+I`
2. Go to Console tab
3. Check for errors

**Expected:** No errors related to:
- Source badges
- MetricsOverview component
- API responses

## API Response Validation

### Check Response Structure
```bash
curl -s http://localhost:8000/api/v1/design-tokens/overview/metrics?project_id=1 | jq 'keys'
```

**Should include:**
- `source` (new field)
- `summary`
- `art_movement`
- `emotional_tone`
- `temperature_profile`
- `saturation_character`
- `design_complexity`
- `design_system_insight`

### Full Response Example
```json
{
  "art_movement": {
    "primary": "Retro-Futurism",
    "elaborations": [...],
    "confidence": 75
  },
  "source": {
    "has_extracted_colors": true,
    "has_extracted_spacing": false,
    "has_extracted_typography": false
  },
  "summary": {
    "total_colors": 12,
    "total_spacing": 0,
    "total_typography": 0,
    "total_shadows": 0
  }
}
```

## Performance Testing

### Metrics API Response Time
```bash
# Measure API response time
time curl -s http://localhost:8000/api/v1/design-tokens/overview/metrics?project_id=1 > /dev/null
```

**Expected:** < 100ms

### Frontend Rendering
1. Open DevTools → Performance tab
2. Upload image
3. Switch to Overview tab
4. Record performance

**Expected:** No jank, smooth 60fps rendering

## Regression Testing

### Existing Features Still Work
- [ ] Color extraction works
- [ ] Spacing extraction works
- [ ] Typography extraction works
- [ ] All other tabs display correctly
- [ ] Export functionality works
- [ ] No TypeScript errors

### Backward Compatibility
- [ ] Old API responses still work (without source field)
- [ ] Frontend gracefully handles missing source
- [ ] No breaking changes to other endpoints

## Rollback Procedure

If issues occur:

```bash
# Revert changes
git checkout frontend/src/components/MetricsOverview.tsx
git checkout src/copy_that/interfaces/api/design_tokens.py

# Rebuild
docker-compose rebuild api frontend
docker-compose up -d
```

## Known Limitations

- Source badges only show "extracted" or not, not partial extraction
- No timestamp on badges (enhancement planned)
- No hover tooltip yet (enhancement planned)
- Mobile badges may wrap on very small screens

## Success Criteria

✅ All checks pass if:
1. Source badges display on all metrics
2. Badges show correct data source (🎨 Colors or 📊 All Tokens)
3. No TypeScript errors
4. No console errors
5. API response includes source field
6. Old features still work
7. Playwright tests pass

## Troubleshooting

### Badges Not Showing
1. Check browser console for errors
2. Verify API response includes `source` field
3. Ensure extraction completed (check Colors tab)
4. Reload page

### Wrong Badge Showing
1. Check API response: `has_extracted_colors` value
2. Verify extraction actually ran
3. Check database has token data

### Styling Issues
1. Check CSS for DesignInsightCard
2. Verify Tailwind classes applied
3. Check browser DevTools for CSS conflicts

## Next Steps After Testing

1. ✅ Verify implementation works as expected
2. ⚠️ If issues found, create bug report
3. 📝 Document any edge cases discovered
4. 🚀 Ready for production deployment
5. 📊 Monitor user feedback

## Support

For issues or questions:
1. Check this testing guide
2. Review VISUAL_GUIDE_SOURCE_BADGES.md
3. Check IMPLEMENTATION_SUMMARY.md
4. Review console for detailed errors
