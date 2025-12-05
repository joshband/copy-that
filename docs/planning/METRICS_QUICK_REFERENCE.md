# Metrics Inference - Quick Reference

## What Changed (TL;DR)

Your muted pastel image now shows:
- ❌ ~~"Brutalism"~~ → ✅ "Pastel Dream"
- ❌ ~~"Warm"~~ → ✅ "Balanced Thermal"
- ❌ ~~"Sophisticated & Refined"~~ → ✅ "Soft & Accessible"

## Files to Know

```
src/copy_that/services/overview_metrics_service.py
  └─ Lines 837-925: New color theory functions
  └─ Lines 398-412: Brutalism (tightened)
  └─ Lines 675-716: Temperature (weighted)
  └─ Lines 557-618: Emotional Tone (simplified)

frontend/src/App.tsx
  └─ Line 67: metricsRefreshTrigger state
  └─ Lines 101,109,117,122: Increment on extraction
  └─ Line 506: Pass trigger to MetricsOverview

frontend/src/components/MetricsOverview.tsx
  └─ Line 41: refreshTrigger prop
  └─ Line 67: Added to useEffect deps
```

## Key Functions Added

| Function | Purpose | Returns |
|----------|---------|---------|
| `_calculate_lightness_variance()` | Measure brightness spread | float (variance) |
| `_calculate_saturation_variance()` | Measure intensity consistency | float (variance) |
| `_calculate_weighted_temperature_ratio()` | Saturation-weighted warm/cool | float (0.0-1.0) |

## Temperature Logic (New)

```python
# Before: warm_count / total (naive)
# After: warm_saturation_sum / (warm_saturation_sum + cool_saturation_sum)
# Result: Desaturated colors don't skew temperature
```

**Example**:
- 3 warm muted + 3 cool muted = "Balanced" ✅ (was "Warm" ❌)

## Emotional Tone Categories (New)

Only 4 categories, all data-driven:

1. **Soft & Accessible** = Low saturation + High lightness
2. **Energetic & Inviting** = High saturation + Warm
3. **Playful & Bold** = High saturation + Cool
4. **Professional & Serious** = Low saturation + Low lightness
5. **Balanced & Versatile** = Mixed characteristics

## Test Command

```bash
# Quick local test (no Docker needed)
python /tmp/test_metrics.py

# Backend tests
python -m pytest src/copy_that/services/tests/test_overview_metrics_e2e.py -v

# Type check
pnpm type-check
```

## Next Phase (Phase 4)

Add confidence scoring (0-100) to each metric. Show/hide based on threshold (60+%).

---

**Ready to test? Start with `/tmp/test_metrics.py` or deploy to Docker after running `alembic upgrade head`**
