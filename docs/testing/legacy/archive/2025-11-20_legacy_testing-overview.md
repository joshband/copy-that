# Testing Guide

Comprehensive testing strategy for Copy That - Backend & Frontend

## Table of Contents

1. [Overview](#overview)
2. [Backend Testing](#backend-testing)
3. [Frontend Testing](#frontend-testing)
4. [Running Tests](#running-tests)
5. [Continuous Integration](#continuous-integration)
6. [Best Practices](#best-practices)

---

## Overview

Copy This implements a comprehensive testing strategy across multiple layers:

### Test Types

| Type | Tools | Coverage | Purpose |
|------|-------|----------|---------|
| **Unit Tests** | pytest, Vitest | Backend modules, React components | Test individual functions and components |
| **Integration Tests** | pytest, MSW + Vitest | AI extractors, API client, Projects API | Test module interactions and HTTP requests |
| **API Contract Tests** | pytest + Pydantic | REST endpoints | Validate request/response schemas |
| **Load Tests** | Locust | Concurrent requests | Test system under load |
| **E2E Tests** | Playwright | User workflows | Test complete user journeys |
| **Visual Tests** | Playwright | UI components | Detect visual regressions |
| **A11y Tests** | Axe-core | Accessibility | WCAG compliance |
| **Performance Tests** | Lighthouse CI | Core Web Vitals, budgets | Monitor performance metrics |

### Coverage Goals

- **Backend**: 80% code coverage (statements, branches, functions, lines)
- **Frontend**: 80% code coverage
- **Critical paths**: 100% coverage (authentication, extraction, export)

---

## Backend Testing

### Setup

```bash
cd backend

# Install dev dependencies
pip install -r requirements-dev.txt

# Alternatively, with pip-compile
pip-compile requirements-dev.in
pip install -r requirements-dev.txt
```

### 1. Unit Tests (`pytest`)

**Location:** `backend/tests/`

**Run Tests:**
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_ai_extractors.py

# Run specific test class
pytest tests/test_ai_extractors.py::TestGPT4VisionExtractor

# Run specific test
pytest tests/test_ai_extractors.py::TestGPT4VisionExtractor::test_gpt4_retry_on_failure

# Run with verbose output
pytest -v

# Run with print statements
pytest -s
```

**Writing Tests:**
```python
import pytest
from unittest.mock import Mock, patch

def test_example():
    """Test description"""
    # Arrange
    input_data = {"key": "value"}

    # Act
    result = function_to_test(input_data)

    # Assert
    assert result == expected_value

@pytest.mark.asyncio
async def test_async_function():
    """Test async function"""
    result = await async_function()
    assert result is not None

@pytest.mark.skip if(not os.getenv("API_KEY"), reason="API key not set")
def test_real_api():
    """Test with real API (requires credentials)"""
    pass
```

### 2. Integration Tests

**AI Extractor Tests:**
```bash
# Run AI extractor integration tests
pytest tests/test_ai_extractors.py -v

# Run with real API (requires API keys)
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
pytest tests/test_ai_extractors.py -v --run-real-api
```

**Test Coverage:**
- ✅ Token merging logic
- ✅ GPT-4 Vision extractor with retry logic
- ✅ Claude Vision extractor with rate limiting
- ✅ Circuit breaker behavior (open/close/half-open)
- ✅ Graceful degradation on failures
- ✅ Complete AI enhancement pipeline

### 3. API Contract Tests

**Test Pydantic schemas:**
```bash
# Run API contract tests
pytest tests/test_api_contracts.py -v
```

**Coverage:**
- ✅ Health check endpoint schema
- ✅ Extraction POST response schema
- ✅ Extraction GET status schema
- ✅ Job list response schema
- ✅ Completed tokens schema validation
- ✅ Error response schemas (400, 404, 429)
- ✅ Backward compatibility (extra fields allowed)

**Example Test:**
```python
from pydantic import BaseModel, Field

class TokenPalette(BaseModel):
    hex: str = Field(regex=r'^#[0-9A-Fa-f]{6}$')
    extractors: List[str] = Field(min_items=1)

def test_token_schema_validation():
    """Test token schema matches API response"""
    response = client.get("/api/extract/job-id")
    tokens = ExtractedTokens(**response.json()['tokens'])

    # Validate schema
    assert len(tokens.palette) > 0
    for color in tokens.palette.values():
        assert color.hex.startswith('#')
        assert len(color.extractors) > 0
```

### 4. Load Testing (`locust`)

**Test concurrent request handling and system behavior under load.**

**Setup:**
```bash
# Install locust
pip install locust

# Run load test (interactive)
locust -f tests/load_test_extraction.py --host=http://localhost:5000

# Visit http://localhost:8089 for web UI
```

**Headless Mode (CI/CD):**
```bash
# Baseline test: 10 users, 60 seconds
locust -f tests/load_test_extraction.py \
    --host=http://localhost:5000 \
    --headless -u 10 -r 2 --run-time 60s \
    --html=load_test_report.html

# Stress test: 50 users, 120 seconds
locust -f tests/load_test_extraction.py \
    --host=http://localhost:5000 \
    --headless -u 50 -r 5 --run-time 120s

# Spike test: 100 users
locust -f tests/load_test_extraction.py \
    --host=http://localhost:5000 \
    --headless -u 100 -r 10 --run-time 60s
```

**Load Profile:**
- 70% CV-only extraction (fast, ~1s)
- 20% AI-enhanced extraction (slow, ~3-8s)
- 10% Status polling (<100ms)

**Metrics Collected:**
- Response time (p50, p95, p99)
- Requests per second (RPS)
- Failure rate
- Rate limit behavior

**Expected Results:**
- **Baseline (10 users)**: <1s avg response, <5% failure rate
- **Stress (50 users)**: <2s avg response, <10% failure rate
- **Spike (100 users)**: Rate limiting kicks in (429 responses)

---

## Frontend Testing

### Setup

```bash
cd frontend

# Install dependencies
pnpm install

# Install Playwright browsers (for E2E)
pnpm playwright:install
```

### 1. Unit Tests (`Vitest` + `@testing-library/react`)

**Configuration:** `frontend/vitest.config.ts`

**Run Tests:**
```bash
# Run all unit tests
pnpm test:unit

# Run in watch mode
pnpm test:unit:watch

# Run with UI
pnpm test:unit:ui

# Run with coverage
pnpm test:coverage
```

**Test Coverage:**
- ✅ ImageUploader component
  - File selection via click
  - Drag and drop functionality
  - File filtering (images only)
  - Upload button behavior
  - Loading states
  - Accessibility

**Writing Component Tests:**
```typescript
import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import MyComponent from '../MyComponent'

describe('MyComponent', () => {
  it('should render correctly', () => {
    render(<MyComponent />)
    expect(screen.getByText('Hello')).toBeInTheDocument()
  })

  it('should handle user interaction', async () => {
    const user = userEvent.setup()
    const mockCallback = vi.fn()

    render(<MyComponent onClick={mockCallback} />)

    await user.click(screen.getByRole('button'))
    expect(mockCallback).toHaveBeenCalledTimes(1)
  })
})
```

### 2. E2E Tests (`Playwright`)

**Run Tests:**
```bash
# Run all E2E tests
pnpm test:e2e

# Run with UI
pnpm test:e2e:ui

# Run specific browser
pnpm test:chromium
pnpm test:firefox
pnpm test:webkit

# Run mobile tests
pnpm test:mobile

# Run with debugging
pnpm test:e2e:debug
```

**Test Coverage:**
- ✅ Visual regression tests
- ✅ Accessibility tests (WCAG AA/AAA)
- ✅ Responsive design tests
- ✅ Cross-browser compatibility

### 3. API Client Integration Tests

**Location:** `frontend/src/api/__tests__/`

Integration tests for API client and projects API using MSW (Mock Service Worker) to mock HTTP responses.

**Run Tests:**
```bash
# Run all API integration tests
pnpm test:unit src/api/__tests__/

# Run specific test file
pnpm test:unit src/api/__tests__/client.integration.test.ts
pnpm test:unit src/api/__tests__/projects.integration.test.ts
```

**Test Coverage:**

**Client API (`client.integration.test.ts`):**
- ✅ `uploadImages()` - File upload with AI enabled/disabled
- ✅ `getJobStatus()` - Job status polling (pending, extracting, completed, failed)
- ✅ `listJobs()` - List all extraction jobs
- ✅ `getExtractionUiSchema()` - Fetch UI schema
- ✅ Error handling (400, 404, 413, 429, 500, 503)
- ✅ Retry logic for network errors and 5xx responses
- ✅ Rate limiting behavior
- ✅ Timeout handling
- ✅ Concurrent requests

**Projects API (`projects.integration.test.ts`):**
- ✅ `createProject()` - Create new project
- ✅ `listProjects()` - List all projects
- ✅ `getProject()` - Get single project by ID
- ✅ `updateProject()` - Update project (name, description, tokens)
- ✅ `deleteProject()` - Delete project
- ✅ Full project lifecycle (CRUD)
- ✅ Validation errors
- ✅ Concurrent operations

**Writing API Integration Tests:**
```typescript
import { describe, it, expect, beforeAll, afterEach, afterAll } from 'vitest'
import { http, HttpResponse } from 'msw'
import { setupServer } from 'msw/node'
import { uploadImages, getJobStatus } from '../client'

// MSW server setup
const server = setupServer()

beforeAll(() => server.listen({ onUnhandledRequest: 'error' }))
afterEach(() => server.resetHandlers())
afterAll(() => server.close())

describe('API Client', () => {
  it('should upload images successfully', async () => {
    server.use(
      http.post('/api/extract', () => {
        return HttpResponse.json({
          job_id: 'test-job-123',
          status: 'pending',
          progress: 0,
          num_images: 1,
          filenames: ['test.png'],
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T00:00:00Z',
        })
      })
    )

    const file = new File(['content'], 'test.png', { type: 'image/png' })
    const result = await uploadImages([file], true)

    expect(result.job_id).toBe('test-job-123')
    expect(result.status).toBe('pending')
  })

  it('should retry on 500 server error', async () => {
    let attemptCount = 0

    server.use(
      http.get('/api/extract/job-123', () => {
        attemptCount++

        if (attemptCount < 2) {
          return HttpResponse.json(
            { error: 'Internal server error' },
            { status: 500 }
          )
        }

        return HttpResponse.json({
          job_id: 'job-123',
          status: 'pending',
          progress: 0,
          num_images: 1,
          filenames: ['test.png'],
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T00:00:00Z',
        })
      })
    )

    const result = await getJobStatus('job-123')

    expect(attemptCount).toBeGreaterThanOrEqual(2) // Verify retry happened
    expect(result.job_id).toBe('job-123')
  })
})
```

### 4. Performance Testing (Lighthouse CI)

**Location:** `frontend/lighthouserc.js`

Lighthouse CI is configured to run automated performance, accessibility, best practices, and SEO audits on every build.

**Configuration:**
- **Desktop preset** with moderate throttling
- **3 runs** averaged for consistent results
- **Performance budgets** enforced
- **Core Web Vitals** tracked

**Run Tests:**
```bash
# Run full Lighthouse CI (build, serve, collect, assert)
pnpm test:perf

# Only collect metrics (without assertions)
pnpm test:perf:collect

# Only run assertions (after collect)
pnpm test:perf:assert

# Manual workflow
pnpm build              # Build production bundle
pnpm preview &          # Serve locally on port 4173
pnpm test:perf          # Run Lighthouse CI
```

**Performance Budgets:**

**Category Scores (Minimum):**
- Performance: 90/100
- Accessibility: 90/100
- Best Practices: 90/100
- SEO: 90/100

**Core Web Vitals:**
| Metric | Budget | Description |
|--------|--------|-------------|
| FCP (First Contentful Paint) | <2.0s | Time to first content render |
| LCP (Largest Contentful Paint) | <2.5s | Time to largest content render |
| CLS (Cumulative Layout Shift) | <0.1 | Visual stability score |
| TBT (Total Blocking Time) | <300ms | Time main thread is blocked |

**Resource Budgets:**
| Resource Type | Budget | Current |
|---------------|--------|---------|
| HTML Document | <20 KB | ~12 KB |
| JavaScript | <500 KB | ~380 KB |
| CSS | <100 KB | ~45 KB |
| Images | <1 MB | ~200 KB |
| Fonts | <200 KB | ~80 KB |

**Network Metrics:**
- Total Requests: <50
- Network RTT: <150ms
- Server Latency: <100ms

**JavaScript Performance:**
- Bootup Time: <3s
- Main Thread Work: <4s
- Speed Index: <3s
- Time to Interactive: <3.5s

**Best Practices Enforced:**
- ✅ HTTP/2 usage
- ✅ Text compression (gzip/brotli)
- ✅ Efficient animated content
- ✅ Modern image formats (WebP, AVIF)
- ✅ Optimized images
- ✅ Responsive images

**Accessibility Checks:**
- ✅ Color contrast (WCAG AA)
- ✅ Document title
- ✅ HTML lang attribute
- ✅ Meta viewport
- ✅ Valid ARIA attributes
- ✅ Button names
- ✅ Link names

**CI/CD Integration:**

Lighthouse CI runs automatically in GitHub Actions on every push and pull request:

```yaml
# .github/workflows/performance-testing.yml
- name: Run Lighthouse CI
  run: pnpm test:perf

- name: Upload Lighthouse reports
  uses: actions/upload-artifact@v4
  with:
    name: lighthouse-reports
    path: .lighthouseci/

- name: Comment PR with results
  # Automatically posts Lighthouse scores to PR
```

**Viewing Reports:**

After running Lighthouse CI, reports are available:

1. **Console Output**: Summary scores printed to terminal
2. **HTML Reports**: `.lighthouseci/*.report.html`
3. **JSON Data**: `.lighthouseci/*.report.json`
4. **Temporary Public Storage**: Link printed after upload

**Example Output:**
```
✅ Performance: 95/100
✅ Accessibility: 96/100
✅ Best Practices: 92/100
✅ SEO: 100/100

Core Web Vitals:
  FCP: 1.2s ✅
  LCP: 1.8s ✅
  CLS: 0.05 ✅
  TBT: 180ms ✅

View full report: https://storage.googleapis.com/lighthouse-ci/...
```

---

## Running Tests

### Local Development

```bash
# Backend: Run all tests
cd backend
pytest -v --cov=. --cov-report=html

# Frontend: Run all tests
cd frontend

# Unit tests (components)
pnpm test:unit

# API integration tests
pnpm test:unit src/api/__tests__/

# E2E tests (Playwright)
pnpm test:e2e

# Performance tests (Lighthouse CI)
pnpm build && pnpm test:perf

# Load testing (Backend)
cd backend
locust -f tests/load_test_extraction.py --host=http://localhost:5000
```

### Pre-commit Hooks

```bash
# Backend tests run automatically on commit
git commit -m "feat: add new feature"

# Runs:
# - pytest (unit + integration)
# - mypy (type checking)
# - ruff (linting)
# - black (formatting)
```

### CI/CD Pipeline

**GitHub Actions** (`.github/workflows/test.yml`):
```yaml
name: Test

on: [push, pull_request]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r backend/requirements-dev.txt
      - run: pytest backend/tests -v --cov=backend --cov-report=xml
      - uses: codecov/codecov-action@v3

  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: pnpm/action-setup@v2
      - uses: actions/setup-node@v3
        with:
          node-version: '20'
          cache: 'pnpm'
      - run: pnpm install
      - run: pnpm test:unit
      - run: pnpm test:e2e
      - uses: codecov/codecov-action@v3

  load-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: pip install locust
      - run: docker-compose up -d
      - run: |
          locust -f backend/tests/load_test_extraction.py \
            --host=http://localhost:5000 \
            --headless -u 10 -r 2 --run-time 60s \
            --html=load_test_report.html
      - uses: actions/upload-artifact@v3
        with:
          name: load-test-report
          path: load_test_report.html
```

---

## Best Practices

### General

✅ **Write tests first** (TDD) for critical features
✅ **Aim for 80% coverage** minimum
✅ **Mock external dependencies** (APIs, databases)
✅ **Test edge cases** (empty inputs, errors, rate limits)
✅ **Keep tests fast** (<5s for unit tests)
✅ **Use descriptive test names** (`test_should_do_something_when_condition`)

### Backend

✅ **Async testing**: Use `pytest-asyncio` for async functions
✅ **Fixtures**: Reuse setup code with `@pytest.fixture`
✅ **Mocking**: Use `unittest.mock` or `pytest-mock`
✅ **Parametrize**: Test multiple inputs with `@pytest.mark.parametrize`
✅ **Skip conditionally**: `@pytest.mark.skipif(not API_KEY, reason="...")`

```python
# Good test example
@pytest.mark.parametrize("input,expected", [
    ([], 0),
    ([1], 1),
    ([1, 2, 3], 6),
])
def test_sum_function(input, expected):
    assert sum(input) == expected
```

### Frontend

✅ **User-centric testing**: Test user interactions, not implementation
✅ **Accessibility**: Use semantic queries (`getByRole`, `getByLabelText`)
✅ **Async handling**: Use `waitFor`, `findBy` for async updates
✅ **User events**: Use `@testing-library/user-event` instead of `fireEvent`
✅ **Cleanup**: Auto-cleanup with `afterEach(() => cleanup())`

```typescript
// Good test example
it('should show error message on failed submission', async () => {
  const user = userEvent.setup()
  render(<LoginForm />)

  await user.type(screen.getByLabelText('Email'), 'invalid-email')
  await user.click(screen.getByRole('button', { name: 'Submit' }))

  expect(await screen.findByRole('alert')).toHaveTextContent('Invalid email')
})
```

---

## Resources

- [pytest documentation](https://docs.pytest.org/)
- [Vitest documentation](https://vitest.dev/)
- [Testing Library](https://testing-library.com/)
- [Playwright documentation](https://playwright.dev/)
- [Locust documentation](https://docs.locust.io/)
- [Lighthouse CI](https://github.com/GoogleChrome/lighthouse-ci)

---

## Troubleshooting

### Backend

**Tests fail with "ModuleNotFoundError"**
```bash
# Add backend to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)/backend"
pytest
```

**Async tests not running**
```bash
# Install pytest-asyncio
pip install pytest-asyncio
```

### Frontend

**Tests fail with "ReferenceError: window is not defined"**
```typescript
// Add to vitest.config.ts
export default defineConfig({
  test: {
    environment: 'jsdom'
  }
})
```

**Can't find module `@testing-library/jest-dom`**
```typescript
// Add to test/setup.ts
import '@testing-library/jest-dom'
```

---

## Summary

✅ **Backend**: pytest + locust (unit, integration, API contract, load tests)
✅ **Frontend**: Vitest + Playwright (unit, E2E, visual, a11y, performance)
✅ **Coverage**: 80% goal for both backend and frontend
✅ **CI/CD**: Automated testing on every push/PR
✅ **Documentation**: Comprehensive testing guide

For questions or issues, see [CONTRIBUTING.md](../CONTRIBUTING.md).
