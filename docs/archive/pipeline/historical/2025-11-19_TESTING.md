# Testing Guide - Copy This Project

## ✅ Current Status

**Test Suite Health**: 446/458 tests passing (97.4%)

- ✅ **Backend**: 90/94 tests passing (95.7%) - **+4 E2E tests added**
- ✅ **Extractors**: 356/364 tests passing (97.8%)
- ✅ **E2E Tests**: 4/4 passing (100%) - **NEW: Week 5 deliverable complete**
- 🔄 **Recent Improvements**: +13 tests fixed/added in November 2025
  - Fixed Visual DNA test (adapters module optional)
  - Fixed 8 component tokens API tests (removed database fixtures)
  - Fixed database initialization (explicit model imports)
  - Fixed async fixture scope mismatch
  - **Added 4 E2E architecture tests** (full pipeline validation)

**Known Issues** (7 remaining):

- 2 test_extraction.py errors (database table creation)
- 5 test failures (AI extractor retry logic, API contracts)

## 🎯 E2E Tests (Week 5 Deliverable)

**New:** Simplified end-to-end tests validate the complete extraction pipeline:

- ✅ `test_full_extraction_pipeline` - Full extraction completes in <10s
- ✅ `test_multi_image_extraction` - Multi-image aggregation works
- ✅ `test_token_json_serialization` - Tokens are JSON serializable
- ✅ `test_invalid_image_handling` - Graceful error handling

**Results:**
- Extraction completes successfully with 32 token categories
- Performance: ~1.5s for single image, ~4s for 3 images
- All tokens JSON serializable for export
- Invalid images handled gracefully

**File:** [backend/tests/test_e2e_simple.py](backend/tests/test_e2e_simple.py)

## 🎯 Overview

This project has a **unified, path-independent test infrastructure** that works for all packages:
- **Backend** (Python/FastAPI - pytest)
- **Extractors** (Python/OpenCV - pytest)
- **Generators** (TypeScript - vitest)
- **Frontend** (TypeScript/React - vitest)

**Key Feature**: Tests can be run from **anywhere** in the project without path issues!

## 🚀 Quick Start

### Run All Tests
```bash
# From project root
python run_tests.py

# Or run specific packages
python run_tests.py --backend
python run_tests.py --extractors
python run_tests.py --generators
python run_tests.py --frontend
python run_tests.py --all  # Everything!
```

### Run From Any Directory
```bash
# Works from project root
cd /path/to/copy_this
python run_tests.py

# Works from backend/
cd backend && python ../run_tests.py

# Works from extractors/tests/
cd extractors/tests && python ../../run_tests.py

# Works from anywhere!
```

## 📦 Package-Specific Testing

### Backend Tests (Python/pytest)

```bash
# All backend tests
python run_tests.py --backend

# Specific test file
python run_tests.py backend/tests/test_api_contracts.py

# Specific test class
python run_tests.py backend/tests/test_api_contracts.py::TestExtractionContracts

# Pattern matching
python run_tests.py -k "test_extract"

# With markers
python run_tests.py -m "backend and unit"
python run_tests.py -m "backend and not slow"
```

### Extractors Tests (Python/pytest)

```bash
# All extractor tests
python run_tests.py --extractors

# Specific test
python run_tests.py extractors/tests/test_color_extraction.py

# Fast tests only
python run_tests.py -m "extractors and unit"
```

### Generators Tests (TypeScript/vitest)

```bash
# TypeScript tests
python run_tests.py --generators

# Or directly with pnpm
cd generators && pnpm test
```

### Frontend Tests (TypeScript/vitest)

```bash
# TypeScript tests
python run_tests.py --frontend

# Or directly with pnpm
cd frontend && pnpm test
```

## 🏷️ Test Markers

Filter tests by category using markers:

| Marker | Description | Usage |
|--------|-------------|-------|
| `backend` | Backend tests | `pytest -m backend` |
| `extractors` | Extractor tests | `pytest -m extractors` |
| `generators` | Generator tests | `pytest -m generators` |
| `unit` | Fast unit tests | `pytest -m unit` |
| `integration` | Integration tests | `pytest -m integration` |
| `slow` | Slow tests | `pytest -m "not slow"` |
| `api` | API tests | `pytest -m api` |
| `extraction` | Extraction pipeline | `pytest -m extraction` |
| `export` | Export functionality | `pytest -m export` |
| `auth` | Auth tests | `pytest -m auth` |
| `contracts` | API contracts | `pytest -m contracts` |
| `ai` | AI features | `pytest -m ai` |
| `wcag` | WCAG validation | `pytest -m wcag` |
| `vision` | Computer vision | `pytest -m vision` |

### Combining Markers

```bash
# Backend unit tests only
pytest -m "backend and unit"

# All tests except slow ones
pytest -m "not slow"

# API or extraction tests
pytest -m "api or extraction"

# Backend integration tests, skip slow
pytest -m "backend and integration and not slow"
```

## 💡 Common Testing Patterns

### During Development (Fast Feedback)

```bash
# Skip slow tests
python run_tests.py -m "not slow"

# Unit tests only (very fast)
python run_tests.py -m unit

# Stop at first failure
python run_tests.py -x

# Run specific test you're working on
python run_tests.py -k "test_color_extraction"
```

### Before Committing

```bash
# Run fast tests
python run_tests.py -m "unit and not slow"

# Or just backend tests
python run_tests.py --backend -m "not slow"
```

### Full Test Suite (CI/CD)

```bash
# All Python tests
python run_tests.py --all

# With coverage
pytest --cov=backend --cov=extractors --cov-report=html
```

### Debugging Tests

```bash
# Verbose output + show print statements
python run_tests.py -v -s

# Very detailed output
python run_tests.py -vv --tb=long

# Drop into debugger on failure
python run_tests.py --pdb
```

## 📁 Project Structure

```
copy_this/
├── pytest.ini                # Project-wide pytest config
├── conftest.py              # Root fixtures & path setup
├── run_tests.py            # Unified test runner
├── TESTING.md              # This file
│
├── backend/
│   ├── conftest.py         # Backend-specific fixtures
│   ├── pytest.ini          # Backend pytest config
│   ├── tests/
│   │   ├── test_api_contracts.py
│   │   ├── test_extraction.py
│   │   └── routers/
│   │       └── extraction/
│   │           ├── conftest.py
│   │           ├── test_routes.py
│   │           └── test_orchestrator.py
│   └── test_*.py           # Root-level tests
│
├── extractors/
│   ├── tests/
│   │   ├── test_color_extraction.py
│   │   ├── test_wcag_validation.py
│   │   └── test_*.py
│   └── test_*.py           # Root-level tests
│
├── generators/
│   ├── tests/
│   │   ├── export-react.test.ts
│   │   ├── schema.test.ts
│   │   └── *.test.ts
│   └── vitest.config.ts
│
└── frontend/
    ├── tests/
    └── vitest.config.ts
```

## ✨ No More Path Issues!

### ❌ Before (Every Test File)
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.main import app
```

### ✅ After (Clean Imports)
```python
# Just import directly - paths handled automatically!
from backend.main import app
from extractors.extractors.color_extractor import ColorExtractor
from generators.export_react import export_react
```

## 🔧 Configuration Files

### Root Level (Project-Wide)
- **`pytest.ini`** - Project-wide pytest configuration
- **`conftest.py`** - Global fixtures and path setup
- **`run_tests.py`** - Unified test runner script

### Package Level (Package-Specific)
- **`backend/pytest.ini`** - Backend-specific config
- **`backend/conftest.py`** - Backend fixtures
- **`extractors/conftest.py`** - Extractor fixtures (if needed)
- **`generators/vitest.config.ts`** - TypeScript test config

## 📝 Writing New Tests

### Python Tests (Backend/Extractors)

```python
import pytest
from backend.models import ExtractionJob  # Clean import!
from extractors.extractors.color_extractor import ColorExtractor

@pytest.mark.unit  # Mark for filtering
def test_something():
    """Test docstring."""
    assert 1 + 1 == 2

@pytest.mark.extractors
@pytest.mark.vision
def test_color_extraction():
    """Test color extraction."""
    extractor = ColorExtractor()
    # ...
```

**Test files must:**
- Start with `test_` or end with `_test.py`
- Have functions starting with `test_`
- Have classes starting with `Test`

### TypeScript Tests (Generators/Frontend)

```typescript
import { describe, it, expect } from 'vitest'
import { exportReact } from '../src/export-react'

describe('React Exporter', () => {
  it('should export valid React code', () => {
    const result = exportReact(tokens)
    expect(result).toContain('export const theme')
  })
})
```

## 🔧 Recent Fixes (November 2025)

### Adapters Module Made Optional

**Problem**: CompositeExtractor (FoundationExtractor, ComponentExtractor, VisualStyleExtractor) failed with `ModuleNotFoundError: No module named 'extractors.adapters'`

**Solution**: Made adapters module optional in `base_extractor.py`:
```python
try:
    from .adapters import ImageInputAdapter
    self._adapter = ImageInputAdapter()
except ImportError:
    self._adapter = None  # Graceful fallback
```

**Impact**: Fixed Visual DNA test + 3 composite extractor failures

### Database Initialization Fixed

**Problem**: `init_db()` wasn't creating tables because models weren't registered with `Base.metadata`

**Solution**: Explicitly import models in `database.py`:
```python
async def init_db() -> None:
    from backend.models import APIKey, ExtractionJob, Project
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
```

### Component Tokens API Tests Fixed

**Problem**: 8 tests failing with `sqlalchemy.exc.OperationalError: no such table`

**Solution**: Removed unnecessary database fixtures since tests use full mocking:

- Removed `_setup_database` fixture
- Removed `_clear_jobs` fixture
- Tests work with mocked `create_job_record`, `get_job`, `serialize_job`

### Async Fixture Scope Fixed

**Problem**: `ScopeMismatch: function scoped fixture with module scoped request`

**Solution**: Changed `_setup_database` fixture from `scope="module"` to `scope="function"` to align with pytest-asyncio's function-scoped event loops

## 🆘 Troubleshooting

### Import Errors

**Problem**: `ModuleNotFoundError: No module named 'backend'`

**Solutions**:
1. Make sure you're using the test runner:
   ```bash
   python run_tests.py
   ```

2. Or run from project root:
   ```bash
   cd /path/to/copy_this
   pytest
   ```

3. Check `pytest.ini` exists at project root

### Tests Not Found

**Problem**: Pytest can't find tests

**Solutions**:
1. Check file naming:
   - Files: `test_*.py` or `*_test.py`
   - Functions: `test_*`
   - Classes: `Test*`

2. Check `testpaths` in `pytest.ini`:
   ```ini
   testpaths = backend/tests backend extractors/tests extractors
   ```

3. Run with verbose discovery:
   ```bash
   pytest --collect-only
   ```

### Slow Tests

**Problem**: Test suite takes too long

**Solutions**:
```bash
# Skip slow tests
pytest -m "not slow"

# Run in parallel (requires pytest-xdist)
pip install pytest-xdist
pytest -n auto

# Run specific package
python run_tests.py --backend -m unit
```

### Path Issues in Old Tests

**Problem**: Tests have manual `sys.path` manipulation

**Solution**: Remove it! The infrastructure handles paths:
```python
# ❌ Remove this
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

# ✅ Just import directly
from backend.main import app
```

## 🎯 Best Practices

1. **Use markers** to categorize tests
   ```python
   @pytest.mark.unit
   @pytest.mark.backend
   def test_fast_function():
       pass
   ```

2. **Skip slow tests during development**
   ```bash
   pytest -m "not slow"
   ```

3. **Use the unified runner**
   ```bash
   python run_tests.py  # Works from anywhere!
   ```

4. **No manual path setup** - Let the infrastructure handle it

5. **Run relevant tests** - Use markers to filter
   ```bash
   pytest -m "extractors and unit"
   ```

6. **Descriptive test names**
   ```python
   def test_color_extractor_handles_invalid_image():
       pass  # Clear what it tests
   ```

7. **Use fixtures** - Defined in `conftest.py` files
   ```python
   def test_with_temp_dir(temp_dir):
       # temp_dir automatically provided
       test_file = temp_dir / "test.txt"
   ```

## 🔄 CI/CD Integration

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r backend/requirements.txt
          pip install pytest pytest-cov pytest-asyncio

      - name: Run Python tests
        run: python run_tests.py --cov

      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'

      - name: Install Node dependencies
        run: pnpm install

      - name: Run TypeScript tests
        run: python run_tests.py --generators --frontend
```

### Pre-commit Hook

```bash
#!/bin/sh
# .git/hooks/pre-commit

# Run fast tests before commit
python run_tests.py -m "unit and not slow"
```

## 📚 Additional Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Vitest Documentation](https://vitest.dev/)
- [Testing Best Practices](https://docs.pytest.org/en/stable/goodpractices.html)

## 🤝 Contributing

When adding new tests:
1. Place them in the appropriate package's `tests/` directory
2. Follow naming conventions (`test_*.py`, `*.test.ts`)
3. Add appropriate markers (`@pytest.mark.unit`, etc.)
4. No manual path setup needed - just import!
5. Run tests before committing: `python run_tests.py -m "not slow"`

---

**Questions?** Check the package-specific test infrastructure:
- Backend: `backend/TESTING_QUICK_REFERENCE.md`
- Extractors: `extractors/tests/README.md` (if exists)
- Generators: `generators/README.md` (if exists)
