# Testing Guide

Comprehensive test automation for the Copy This design token pipeline.

## Overview

The test suite covers:
- **Python tests**: Color extraction, spacing detection, WCAG validation
- **TypeScript tests**: Schema validation, token normalization, backward compatibility
- **Integration tests**: Full pipeline validation (via Makefile)
- **Regression tests**: v1.0, v1.1, v1.2 format compatibility

## Quick Start

### Install Test Dependencies

```bash
make install-test-deps
```

This installs:
- `pytest` and `pytest-cov` for Python testing
- `vitest` for TypeScript testing

### Run All Tests

```bash
make test
```

This runs both Python and TypeScript test suites.

### Run Tests Individually

```bash
# Python tests only
make test-py

# TypeScript tests only
make test-ts
```

## Python Tests (Ingest Pipeline)

Location: `/extractors/tests/`

### Test Files

- `test_color_extraction.py` - Color conversion, palette extraction, role mapping
- `test_wcag_validation.py` - WCAG contrast ratio calculations
- `test_spacing_extraction.py` - Spacing scale detection from UI images

### Running Python Tests

```bash
cd ingest
../.venv/bin/pytest
```

#### With Coverage Report

```bash
cd ingest
../.venv/bin/pytest --cov=. --cov-report=html
open htmlcov/index.html
```

#### Run Specific Test File

```bash
cd ingest
../.venv/bin/pytest tests/test_color_extraction.py
```

#### Run Specific Test

```bash
cd ingest
../.venv/bin/pytest tests/test_color_extraction.py::TestColorConversions::test_hex_of_valid_rgb
```

### Python Test Coverage

Current coverage focuses on:
- Color space conversions (RGB, HSL, LAB)
- Color scale generation (50-900 shades)
- K-means palette extraction
- Semantic role mapping
- WCAG contrast validation
- Spacing scale extraction

## TypeScript Tests (Generators)

Location: `/generators/tests/`

### Test Files

- `schema.test.ts` - Zod schema validation, backward compatibility
- `normalize.test.ts` - Token reference resolution, normalization
- `export-react.test.ts` - React exporter compatibility validation

### Running TypeScript Tests

```bash
cd generators
pnpm test
```

#### Watch Mode (Re-run on File Changes)

```bash
cd generators
pnpm test:watch
```

#### With Coverage Report

```bash
cd generators
pnpm exec vitest run --coverage
```

#### Run Specific Test File

```bash
cd generators
pnpm exec vitest run tests/schema.test.ts
```

### TypeScript Test Coverage

Current coverage focuses on:
- Schema validation (v1.0, v1.1, v1.2)
- Token reference resolution (`{orange.500}` → `#F15925`)
- Backward compatibility (old tokens work with new exporters)
- Normalization logic
- Export format validation

## Test Fixtures

### Python Fixtures

Located in: `/extractors/tests/fixtures/`

Python tests generate sample images programmatically using NumPy for:
- Color extraction testing
- Spacing detection testing
- Edge detection validation

### TypeScript Fixtures

Located in: `/generators/tests/fixtures/`

Static JSON files representing different schema versions:
- `v1.0-tokens.json` - Minimal v1.0 schema (palette, radius, shadow, typography, grid)
- `v1.1-tokens.json` - v1.1 schema with primitive colors and semantic tokens
- `v1.2-tokens.json` - v1.2 schema with spacing, animation, breakpoints

## Integration Testing

### Full Pipeline Test

```bash
make all
```

This runs the complete pipeline:
1. `make ingest` - Extracts design tokens from reference images
2. `make tokens` - Normalizes to `tokens.json`
3. `make react` - Generates React demo
4. `make juce` - Generates JUCE scaffold

Verify:
- All commands complete without errors
- Generated files exist and are valid
- React demo builds successfully

### Manual Verification

```bash
# 1. Run full pipeline
make all

# 2. Verify generated files
ls -lh style_guide.json
ls -lh generators/tokens.json
ls -lh targets/react/src/App.tsx
ls -lh targets/juce/CopyThis/Source/DesignTokens.h

# 3. Test React demo
make demo
# Visit http://localhost:5173
```

## Regression Testing

### Version Compatibility Matrix

Tests ensure backward compatibility:

| Tokens Version | Exporters | Status |
|---------------|-----------|--------|
| v1.0 | v1.2 | ✅ Valid |
| v1.1 | v1.2 | ✅ Valid |
| v1.2 | v1.2 | ✅ Valid |

### Testing Backward Compatibility

```typescript
// Schema accepts old formats
StyleGuide.safeParse(v1_0_tokens); // ✅ success: true
StyleGuide.safeParse(v1_1_tokens); // ✅ success: true
StyleGuide.safeParse(v1_2_tokens); // ✅ success: true

// Optional fields are truly optional
const minimal = { palette: {...}, radius: {...}, ... };
StyleGuide.safeParse(minimal); // ✅ success: true
```

## Continuous Integration

### Pre-commit Testing

Recommended workflow before committing:

```bash
# 1. Run tests
make test

# 2. Run full pipeline
make all

# 3. Verify no errors
echo $?  # Should output 0
```

### GitHub Actions (Optional)

If setting up CI/CD, add to `.github/workflows/test.yml`:

```yaml
name: Test Suite

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - uses: pnpm/action-setup@v2
      - uses: actions/setup-node@v3
        with:
          node-version: '20'
          cache: 'pnpm'

      - name: Install dependencies
        run: make install-test-deps

      - name: Run tests
        run: make test

      - name: Test full pipeline
        run: make all
```

## Writing New Tests

### Adding Python Tests

1. Create test file in `/extractors/tests/test_*.py`
2. Follow pytest conventions:
   ```python
   import pytest

   class TestFeature:
       def test_specific_behavior(self):
           result = my_function()
           assert result == expected
   ```
3. Use fixtures for reusable test data:
   ```python
   @pytest.fixture
   def sample_data():
       return create_test_data()
   ```

### Adding TypeScript Tests

1. Create test file in `/generators/tests/*.test.ts`
2. Follow Vitest conventions:
   ```typescript
   import { describe, it, expect } from 'vitest';

   describe('Feature', () => {
     it('should behave correctly', () => {
       const result = myFunction();
       expect(result).toBe(expected);
     });
   });
   ```
3. Use beforeEach/afterEach for setup/teardown

## Test Philosophy

### What We Test

✅ **Critical paths**: Color extraction, schema validation, token resolution
✅ **Regression prevention**: Backward compatibility, version migrations
✅ **Logic correctness**: WCAG contrast, color scale generation
✅ **Error handling**: Missing files, invalid schemas, unresolved references

### What We Don't Test

❌ **Implementation details**: Internal helper functions not exposed
❌ **Generated code formatting**: React/JUCE output formatting (changes often)
❌ **External dependencies**: OpenCV algorithms, Zod internals
❌ **Visual rendering**: How colors appear in browser (use Playwright for that)

### Coverage Goals

- **Target**: >70% coverage of core logic
- **Focus**: Critical business logic, not boilerplate
- **Quality over quantity**: Meaningful tests that catch real bugs

## Troubleshooting

### Python Tests Fail to Import Modules

```bash
# Ensure virtual environment is activated
source .venv/bin/activate

# Install package in editable mode
pip install -e "ingest[test]"
```

### TypeScript Tests Can't Find Modules

```bash
# Install dependencies
cd generators
pnpm install
```

### "tokens.json already exists" Error

```bash
# Clean up generated files
rm -f generators/tokens.json
rm -f style_guide.json
```

### Tests Pass but Pipeline Fails

```bash
# Check file permissions
ls -l extractors/build_style_guide.py

# Verify Python virtual environment
which python
.venv/bin/python --version

# Verify Node/pnpm setup
node --version
pnpm --version
```

## Performance

- **Python tests**: ~2-5 seconds (depends on image generation)
- **TypeScript tests**: ~1-3 seconds
- **Full pipeline**: ~5-10 seconds

Tests are designed to be fast for rapid iteration.

## Additional Resources

- [pytest documentation](https://docs.pytest.org/)
- [Vitest documentation](https://vitest.dev/)
- [Zod schema validation](https://zod.dev/)
- [WCAG contrast guidelines](https://www.w3.org/WAI/WCAG21/Understanding/contrast-minimum.html)
