# UI Regression Fixtures

Store non-committed screenshots here (PNG/JPEG). Update `manifest.json` with entries like:

```json
{
  "cases": [
    {
      "file": "light_form.png",
      "expect": {
        "min_components": 8,
        "max_spacing_tokens": 12,
        "expected_gaps": [8, 16]
      }
    }
  ]
}
```

Notes:
- Files are gitignored; keep them small (<1MB each) and diverse (light/dark themes, dashboards, mobile).
- Expectations are heuristic (min/max counts, representative gaps). Adjust as extraction improves.
- Tests will skip if files are missing or manifest has no cases.
