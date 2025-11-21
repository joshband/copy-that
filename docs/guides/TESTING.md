# Testing Guide

**Version:** 1.0 | **Date:** 2025-11-19 | **Status:** Complete

Comprehensive guide to testing in Copy That, covering unit tests, integration tests, and end-to-end tests.

---

## 🎯 Testing Philosophy

Copy That follows **Test-Driven Development (TDD)** principles:

1. **Write tests first** (Red: tests fail)
2. **Write code to pass** (Green: tests pass)
3. **Refactor** (Refactor: improve code without changing behavior)

**Test Coverage Target:** 80%+

---

## 🏗️ Test Structure

```
tests/
├── unit/                    # Unit tests (no dependencies)
│   ├── test_color_adapter.py
│   ├── test_color_extractor.py
│   └── test_token_validator.py
│
├── integration/             # Integration tests (with DB, API)
│   ├── test_extraction_pipeline.py
│   ├── test_api_endpoints.py
│   └── test_database_queries.py
│
└── e2e/                     # End-to-end tests
    ├── test_full_extraction.py
    └── test_ui_workflow.py
```

---

## 🧪 Backend Testing (Python)

### Framework: pytest + pytest-asyncio

### Run Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/unit/test_color_adapter.py

# Run specific test
pytest tests/unit/test_color_adapter.py::TestColorTokenAdapter::test_to_api_schema

# Run with verbose output
pytest -v

# Run with coverage report
pytest --cov=src/copy_that --cov-report=html

# Run tests in watch mode (requires pytest-watch)
ptw
```

### Unit Test Example

```python
# tests/unit/test_color_adapter.py
import pytest
from datetime import datetime
from copy_that.adapters.color_adapter import ColorTokenAdapter
from copy_that.domain.schemas import CoreColorToken, APIColorToken

class TestColorTokenAdapter:
    """Test ColorTokenAdapter transformations"""

    @pytest.fixture
    def adapter(self):
        """Create adapter instance"""
        return ColorTokenAdapter()

    @pytest.fixture
    def core_token(self):
        """Create sample core token"""
        return CoreColorToken(
            hex='#FF6B35',
            confidence=0.95,
            token_type='color'
        )

    def test_to_api_schema_adds_metadata(self, adapter, core_token):
        """Test Core → API adds semantic name and timestamp"""
        api_token = adapter.to_api_schema(core_token)

        assert api_token.hex == '#FF6B35'
        assert api_token.confidence == 0.95
        assert api_token.semantic_name is not None
        assert isinstance(api_token.created_at, datetime)

    def test_from_api_schema_strips_metadata(self, adapter):
        """Test API → Core removes extra fields"""
        api_token = APIColorToken(
            hex='#FF6B35',
            confidence=0.95,
            token_type='color',
            semantic_name='vibrant-orange',
            created_at=datetime.utcnow()
        )

        core_token = adapter.from_api_schema(api_token)

        # Core has only essentials
        assert core_token.hex == '#FF6B35'
        assert core_token.confidence == 0.95
        assert not hasattr(core_token, 'semantic_name')

    def test_bidirectional_transformation(self, adapter, core_token):
        """Test Core → API → Core preserves core fields"""
        api_token = adapter.to_api_schema(core_token)
        restored_core = adapter.from_api_schema(api_token)

        assert restored_core.hex == core_token.hex
        assert restored_core.confidence == core_token.confidence
```

### Integration Test Example

```python
# tests/integration/test_extraction_pipeline.py
import pytest
import asyncio
from io import BytesIO
from PIL import Image
from sqlalchemy.ext.asyncio import AsyncSession
from copy_that.infrastructure.extractors.color import ColorExtractor
from copy_that.adapters.color_adapter import ColorTokenAdapter
from copy_that.domain.models import ColorToken, ExtractionJob
from copy_that.infrastructure.database import AsyncSessionLocal

@pytest.mark.asyncio
class TestExtractionPipeline:
    """Test end-to-end extraction: Extract → Adapt → Store"""

    async def test_extraction_pipeline(self, db_session: AsyncSession):
        """Test complete color extraction pipeline"""

        # 1. Create test image
        image = Image.new('RGB', (100, 100), color='red')
        image_bytes = BytesIO()
        image.save(image_bytes, format='PNG')
        image_bytes.seek(0)

        # 2. Extract colors
        extractor = ColorExtractor()
        core_tokens = extractor.extract(image_bytes.getvalue())

        # Verify extraction
        assert len(core_tokens) > 0
        for token in core_tokens:
            assert 'hex' in token
            assert 'confidence' in token

        # 3. Create extraction job
        job = ExtractionJob(
            extraction_type='color',
            status='processing'
        )
        db_session.add(job)
        await db_session.flush()

        # 4. Adapt and store
        adapter = ColorTokenAdapter()
        for core_token in core_tokens:
            api_token = adapter.to_api_schema(core_token)
            db_dict = adapter.to_database_schema(api_token, job.id)

            db_token = ColorToken(**db_dict)
            db_session.add(db_token)

        await db_session.commit()

        # 5. Query from database
        result = await db_session.execute(
            select(ColorToken).where(ColorToken.extraction_job_id == job.id)
        )
        stored_tokens = result.scalars().all()

        # Verify storage
        assert len(stored_tokens) > 0
        for token in stored_tokens:
            assert token.hex is not None
            assert 0 <= token.confidence <= 1
```

### API Test Example

```python
# tests/integration/test_api_endpoints.py
import pytest
from httpx import AsyncClient
from copy_that.interfaces.api.main import app

@pytest.mark.asyncio
class TestColorEndpoints:
    """Test color extraction API endpoints"""

    async def test_get_job_colors(self):
        """Test GET /api/v1/jobs/{id}/colors endpoint"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/api/v1/jobs/1/colors")

            assert response.status_code == 200
            data = response.json()
            assert "colors" in data
            assert isinstance(data["colors"], list)

    async def test_extract_colors_endpoint(self):
        """Test POST /api/v1/extract/colors endpoint"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Create a test image
            image = Image.new('RGB', (100, 100), color='blue')
            image_bytes = BytesIO()
            image.save(image_bytes, format='PNG')
            image_bytes.seek(0)

            # Upload and extract
            response = await client.post(
                "/api/v1/extract/colors",
                files={"file": ("test.png", image_bytes, "image/png")}
            )

            assert response.status_code == 200
            data = response.json()
            assert "colors" in data or "job_id" in data
```

---

## 🧪 Frontend Testing (TypeScript/React)

### Framework: Vitest + React Testing Library

### Run Tests

```bash
# Run all tests
pnpm test

# Run in watch mode
pnpm test:watch

# Run with coverage
pnpm test:coverage

# Run specific test
pnpm test ColorTokenCard
```

### Unit Test Example

```typescript
// src/components/__tests__/ColorTokenCard.test.tsx
import { render, screen } from '@testing-library/react';
import { ColorTokenCard } from '../ColorTokenCard';
import { ColorToken } from '@/types/tokens';

describe('ColorTokenCard', () => {
  const mockToken: ColorToken = {
    id: 1,
    hex: '#FF6B35',
    confidence: 0.95,
    semantic_name: 'vibrant-orange'
  };

  it('renders color swatch with correct background', () => {
    render(<ColorTokenCard token={mockToken} />);

    const swatch = screen.getByRole('img', { hidden: true });
    expect(swatch).toHaveStyle({ backgroundColor: '#FF6B35' });
  });

  it('displays hex value', () => {
    render(<ColorTokenCard token={mockToken} />);

    expect(screen.getByText('#FF6B35')).toBeInTheDocument();
  });

  it('displays semantic name', () => {
    render(<ColorTokenCard token={mockToken} />);

    expect(screen.getByText('vibrant-orange')).toBeInTheDocument();
  });

  it('displays confidence percentage', () => {
    render(<ColorTokenCard token={mockToken} />);

    expect(screen.getByText('95% confident')).toBeInTheDocument();
  });

  it('formats low confidence correctly', () => {
    const lowConfidenceToken = { ...mockToken, confidence: 0.5 };
    render(<ColorTokenCard token={lowConfidenceToken} />);

    expect(screen.getByText('50% confident')).toBeInTheDocument();
  });
});
```

### Integration Test Example

```typescript
// src/components/__tests__/TokenList.integration.test.tsx
import { render, screen, waitFor } from '@testing-library/react';
import { TokenList } from '../TokenList';
import * as apiClient from '@/api/client';

// Mock the API client
vi.mock('@/api/client');

describe('TokenList Integration', () => {
  it('fetches and displays tokens', async () => {
    // Mock API response
    vi.mocked(apiClient.get).mockResolvedValue({
      data: {
        colors: [
          { id: 1, hex: '#FF6B35', confidence: 0.95, semantic_name: 'orange' },
          { id: 2, hex: '#0066CC', confidence: 0.88, semantic_name: 'blue' }
        ]
      }
    });

    render(<TokenList jobId={1} />);

    // Wait for tokens to load
    await waitFor(() => {
      expect(screen.getByText('#FF6B35')).toBeInTheDocument();
    });

    // Verify all tokens rendered
    expect(screen.getByText('#FF6B35')).toBeInTheDocument();
    expect(screen.getByText('#0066CC')).toBeInTheDocument();
  });

  it('shows loading state initially', () => {
    render(<TokenList jobId={1} />);

    expect(screen.getByText('Loading tokens...')).toBeInTheDocument();
  });

  it('shows error on API failure', async () => {
    // Mock API failure
    vi.mocked(apiClient.get).mockRejectedValue(
      new Error('API Error')
    );

    render(<TokenList jobId={1} />);

    await waitFor(() => {
      expect(screen.getByText(/Error:/)).toBeInTheDocument();
    });
  });
});
```

---

## 📊 Test Coverage

### View Coverage Report

```bash
# Generate coverage report
pytest --cov=src/copy_that --cov-report=html

# Open in browser
open htmlcov/index.html
```

### Coverage Targets

| Component | Target |
|-----------|--------|
| Adapters | 100% |
| Models | 85%+ |
| API Routes | 80%+ |
| Extractors | 90%+ |
| Utilities | 85%+ |

---

## 🔄 CI/CD Testing

### Pre-commit Tests (Run Locally)

```bash
# Run before committing
pytest                          # Backend tests
pnpm test                       # Frontend tests
pnpm typecheck                  # Type checking
pnpm lint                       # Linting
```

### GitHub Actions (Automated on Push)

See `.github/workflows/ci.yml` for automated testing on:
- Every push to any branch
- Every pull request
- Scheduled nightly runs

---

## 📝 Writing New Tests

### Step 1: Write Failing Test

```python
def test_new_feature():
    result = new_function()
    assert result == expected_value
```

**Result:** RED ❌ (test fails because function doesn't exist)

### Step 2: Write Code to Pass Test

```python
def new_function():
    return expected_value
```

**Result:** GREEN ✅ (test passes)

### Step 3: Refactor

```python
def new_function():
    # Improved implementation
    return compute_expected_value()
```

**Result:** GREEN ✅ (test still passes, code is better)

---

## 🐛 Common Testing Issues

### Issue: Async Test Hangs

**Solution:** Use `@pytest.mark.asyncio` decorator:
```python
@pytest.mark.asyncio
async def test_async_function():
    result = await my_async_function()
    assert result == expected
```

### Issue: Database Not Available in Tests

**Solution:** Use database fixtures:
```python
@pytest.fixture
async def db_session():
    """Provide test database session"""
    # Create in-memory or test database
    # Return session
    # Cleanup after test
```

### Issue: Mocking API Calls Fails

**Solution:** Use pytest mocking:
```python
from unittest.mock import patch

@patch('copy_that.api.client.get')
def test_with_mocked_api(mock_get):
    mock_get.return_value = {'colors': []}
    # Test code
```

---

## 📚 Related Documentation

- **setup/start_here.md** - Quick navigation
- **workflows/phase_4_color_vertical_slice.md** - Implementation with tests
- **adapter_pattern.md** - Adapter testing examples
- **extractor_patterns.md** - Extractor testing examples

---

**Version:** 1.0 | **Last Updated:** 2025-11-19 | **Status:** Complete
