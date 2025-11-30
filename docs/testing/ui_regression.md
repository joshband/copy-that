# UI Regression Harness (Synthetic Seeds)

This folder documents a lightweight regression harness to catch spacing/alignment regressions without shipping large binary fixtures.

## What’s included
- Synthetic UI scenarios generated in tests (no external assets).
- Expectations encoded as asserts (token counts, containment, gap clustering).

## How to run
```bash
python -m pytest tests/regression/test_ui_regression_synthetic.py
```

## Future work
- Add a small curated set of real screenshots under `tests/regression/fixtures/` plus a manifest of expected counts (buttons, text, containers). See `fixtures/README.md` and `fixtures/manifest.json`.
- Extend checks to text tokens once OCR is wired.
- Export a JSON report for CI to diff against stored expectations.
