# Testing Strategy

> Comprehensive testing plan for frontend components and infrastructure validation

---

## Table of Contents

1. [Current Testing State](#current-testing-state)
2. [Frontend Testing](#frontend-testing)
3. [Infrastructure Testing](#infrastructure-testing)
4. [E2E Testing](#e2e-testing)
5. [Performance Testing](#performance-testing)
6. [Testing Automation](#testing-automation)

---

## Current Testing State

### Frontend Testing Coverage

| Category | Files | Tests | Coverage |
|----------|-------|-------|----------|
| Component Tests | 12 | ~50 | ~45% |
| Store Tests | 1 | ~15 | ~80% |
| Config Tests | 1 | ~10 | ~70% |
| Accessibility Tests | 1 | 6 | Minimal |
| Integration Tests | 1 | ~5 | ~10% |
| **Total** | **16** | **~86** | **~40%** |

### Test File Inventory

```
frontend/src/
├── components/__tests__/
│   ├── AccessibilityVisualizer.test.tsx
│   ├── BatchImageUploader.test.tsx
│   ├── ColorDisplay.a11y.test.tsx
│   ├── ColorDisplay.integration.test.tsx
│   ├── ColorNarrative.test.tsx
│   ├── ColorTokenDisplay.test.tsx
│   ├── ExportDownloader.test.tsx
│   ├── HarmonyVisualizer.test.tsx
│   ├── LibraryCurator.test.tsx
│   ├── SessionCreator.test.tsx
│   ├── SessionWorkflow.test.tsx
│   └── TokenCard.test.tsx
├── store/__tests__/
│   └── tokenStore.test.ts
└── config/__tests__/
    └── tokenTypeRegistry.test.ts
```

### Missing Test Coverage

**Components Without Tests:**
- ImageUploader.tsx
- TokenGrid.tsx
- TokenInspectorSidebar.tsx
- TokenPlaygroundDrawer.tsx
- TokenToolbar.tsx
- ColorDetailPanel.tsx
- ColorPaletteSelector.tsx
- CompactColorGrid.tsx
- EducationalColorDisplay.tsx
- LearningSidebar.tsx
- PlaygroundSidebar.tsx

---

## Frontend Testing

### Unit Test Requirements

#### Component Test Template

```typescript
// __tests__/ComponentName.test.tsx
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { ComponentName } from '../ComponentName'

// Mock dependencies
vi.mock('../../store/tokenStore', () => ({
  useTokenStore: vi.fn()
}))

vi.mock('../../api/hooks', () => ({
  useQuery: vi.fn()
}))

describe('ComponentName', () => {
  const defaultProps = {
    // Default test props
  }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('Rendering', () => {
    it('renders without crashing', () => {
      render(<ComponentName {...defaultProps} />)
      expect(screen.getByRole('...'));
    })

    it('displays correct content', () => {
      render(<ComponentName {...defaultProps} />)
      expect(screen.getByText('...'))
    })

    it('handles empty state', () => {
      render(<ComponentName {...defaultProps} items={[]} />)
      expect(screen.getByText('No items'))
    })

    it('handles loading state', () => {
      render(<ComponentName {...defaultProps} isLoading />)
      expect(screen.getByRole('progressbar'))
    })

    it('handles error state', () => {
      render(<ComponentName {...defaultProps} error="Error message" />)
      expect(screen.getByRole('alert'))
    })
  })

  describe('User Interactions', () => {
    it('calls onClick when button clicked', async () => {
      const onClick = vi.fn()
      render(<ComponentName {...defaultProps} onClick={onClick} />)

      await userEvent.click(screen.getByRole('button'))

      expect(onClick).toHaveBeenCalledTimes(1)
    })

    it('updates input value on change', async () => {
      render(<ComponentName {...defaultProps} />)

      const input = screen.getByRole('textbox')
      await userEvent.type(input, 'test value')

      expect(input).toHaveValue('test value')
    })

    it('handles keyboard navigation', async () => {
      render(<ComponentName {...defaultProps} />)

      const element = screen.getByRole('button')
      element.focus()

      await userEvent.keyboard('{Enter}')
      // Assert expected behavior
    })
  })

  describe('Accessibility', () => {
    it('has accessible name', () => {
      render(<ComponentName {...defaultProps} />)
      expect(screen.getByRole('button', { name: /submit/i }))
    })

    it('announces dynamic content', async () => {
      render(<ComponentName {...defaultProps} />)

      // Trigger update
      await userEvent.click(screen.getByRole('button'))

      // Check aria-live region
      expect(screen.getByRole('status')).toHaveTextContent('Updated')
    })
  })
})
```

#### TokenGrid Tests

```typescript
// __tests__/TokenGrid.test.tsx
import { describe, it, expect, vi } from 'vitest'
import { render, screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { TokenGrid } from '../TokenGrid'
import { useTokenStore } from '../../store/tokenStore'

vi.mock('../../store/tokenStore')

const mockTokens = [
  {
    id: '1',
    name: 'Primary Blue',
    hex: '#0066CC',
    confidence: 0.95
  },
  {
    id: '2',
    name: 'Secondary Green',
    hex: '#00CC66',
    confidence: 0.88
  }
]

describe('TokenGrid', () => {
  beforeEach(() => {
    vi.mocked(useTokenStore).mockReturnValue({
      tokens: mockTokens,
      filters: {},
      sortBy: 'name',
      selectedTokenId: null,
      selectToken: vi.fn(),
      deleteToken: vi.fn(),
      duplicateToken: vi.fn()
    })
  })

  describe('Rendering', () => {
    it('renders all tokens', () => {
      render(<TokenGrid />)

      expect(screen.getByText('Primary Blue')).toBeInTheDocument()
      expect(screen.getByText('Secondary Green')).toBeInTheDocument()
    })

    it('shows empty state when no tokens', () => {
      vi.mocked(useTokenStore).mockReturnValue({
        tokens: [],
        filters: {},
        sortBy: 'name',
        selectedTokenId: null
      })

      render(<TokenGrid />)

      expect(screen.getByText(/no tokens/i)).toBeInTheDocument()
    })

    it('applies grid layout', () => {
      render(<TokenGrid />)

      const grid = screen.getByRole('grid')
      expect(grid).toHaveClass('token-grid')
    })
  })

  describe('Filtering', () => {
    it('filters tokens by name', () => {
      vi.mocked(useTokenStore).mockReturnValue({
        tokens: mockTokens,
        filters: { search: 'Primary' },
        sortBy: 'name',
        selectedTokenId: null
      })

      render(<TokenGrid />)

      expect(screen.getByText('Primary Blue')).toBeInTheDocument()
      expect(screen.queryByText('Secondary Green')).not.toBeInTheDocument()
    })

    it('filters by color property', () => {
      vi.mocked(useTokenStore).mockReturnValue({
        tokens: mockTokens,
        filters: { temperature: 'cool' },
        sortBy: 'name',
        selectedTokenId: null
      })

      render(<TokenGrid />)
      // Assert filtered results
    })
  })

  describe('Sorting', () => {
    it('sorts by name ascending', () => {
      vi.mocked(useTokenStore).mockReturnValue({
        tokens: mockTokens,
        filters: {},
        sortBy: 'name',
        selectedTokenId: null
      })

      render(<TokenGrid />)

      const cards = screen.getAllByRole('gridcell')
      expect(within(cards[0]).getByText('Primary Blue')).toBeInTheDocument()
      expect(within(cards[1]).getByText('Secondary Green')).toBeInTheDocument()
    })

    it('sorts by confidence descending', () => {
      vi.mocked(useTokenStore).mockReturnValue({
        tokens: mockTokens,
        filters: {},
        sortBy: 'confidence-desc',
        selectedTokenId: null
      })

      render(<TokenGrid />)

      const cards = screen.getAllByRole('gridcell')
      // Primary Blue has higher confidence (0.95)
      expect(within(cards[0]).getByText('Primary Blue')).toBeInTheDocument()
    })
  })

  describe('Selection', () => {
    it('highlights selected token', () => {
      vi.mocked(useTokenStore).mockReturnValue({
        tokens: mockTokens,
        filters: {},
        sortBy: 'name',
        selectedTokenId: '1'
      })

      render(<TokenGrid />)

      const selectedCard = screen.getByText('Primary Blue').closest('.token-card')
      expect(selectedCard).toHaveClass('selected')
    })

    it('calls selectToken on click', async () => {
      const selectToken = vi.fn()
      vi.mocked(useTokenStore).mockReturnValue({
        tokens: mockTokens,
        filters: {},
        sortBy: 'name',
        selectedTokenId: null,
        selectToken
      })

      render(<TokenGrid />)

      await userEvent.click(screen.getByText('Primary Blue'))

      expect(selectToken).toHaveBeenCalledWith('1')
    })
  })

  describe('Performance', () => {
    it('memoizes filtered results', () => {
      const { rerender } = render(<TokenGrid />)

      // Re-render with same props
      rerender(<TokenGrid />)

      // Assert no unnecessary recalculations (would need to spy on useMemo)
    })
  })
})
```

#### Store Tests

```typescript
// __tests__/tokenStore.test.ts
import { describe, it, expect, beforeEach } from 'vitest'
import { act, renderHook } from '@testing-library/react'
import { useTokenStore } from '../tokenStore'

describe('tokenStore', () => {
  beforeEach(() => {
    // Reset store before each test
    const { result } = renderHook(() => useTokenStore())
    act(() => {
      result.current.setTokens([])
      result.current.selectToken(null)
    })
  })

  describe('Token Management', () => {
    it('sets tokens', () => {
      const { result } = renderHook(() => useTokenStore())

      const tokens = [
        { id: '1', name: 'Test', hex: '#000' }
      ]

      act(() => {
        result.current.setTokens(tokens)
      })

      expect(result.current.tokens).toEqual(tokens)
    })

    it('selects a token', () => {
      const { result } = renderHook(() => useTokenStore())

      act(() => {
        result.current.selectToken('1')
      })

      expect(result.current.selectedTokenId).toBe('1')
    })

    it('deletes a token', () => {
      const { result } = renderHook(() => useTokenStore())

      act(() => {
        result.current.setTokens([
          { id: '1', name: 'Test 1' },
          { id: '2', name: 'Test 2' }
        ])
        result.current.deleteToken('1')
      })

      expect(result.current.tokens).toHaveLength(1)
      expect(result.current.tokens[0].id).toBe('2')
    })

    it('duplicates a token', () => {
      const { result } = renderHook(() => useTokenStore())

      act(() => {
        result.current.setTokens([
          { id: '1', name: 'Original' }
        ])
        result.current.duplicateToken('1')
      })

      expect(result.current.tokens).toHaveLength(2)
      expect(result.current.tokens[1].name).toContain('Copy')
    })
  })

  describe('Filtering', () => {
    it('sets filter', () => {
      const { result } = renderHook(() => useTokenStore())

      act(() => {
        result.current.setFilter('temperature', 'warm')
      })

      expect(result.current.filters.temperature).toBe('warm')
    })

    it('clears filters', () => {
      const { result } = renderHook(() => useTokenStore())

      act(() => {
        result.current.setFilter('temperature', 'warm')
        result.current.setFilter('saturation', 'vibrant')
        result.current.clearFilters()
      })

      expect(result.current.filters).toEqual({})
    })
  })

  describe('Extraction Progress', () => {
    it('updates extraction progress', () => {
      const { result } = renderHook(() => useTokenStore())

      act(() => {
        result.current.startExtraction()
        result.current.updateExtractionProgress(50, 'Processing images')
      })

      expect(result.current.isExtracting).toBe(true)
      expect(result.current.extractionProgress).toBe(50)
      expect(result.current.extractionStage).toBe('Processing images')
    })

    it('completes extraction', () => {
      const { result } = renderHook(() => useTokenStore())

      act(() => {
        result.current.startExtraction()
        result.current.completeExtraction(25)
      })

      expect(result.current.isExtracting).toBe(false)
      expect(result.current.extractionProgress).toBe(100)
      expect(result.current.extractionTokenCount).toBe(25)
    })
  })
})
```

### Integration Test Scenarios

```typescript
// __tests__/ColorDisplay.integration.test.tsx
import { describe, it, expect, vi } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { SessionWorkflow } from '../SessionWorkflow'

// Mock API
vi.mock('../../api/client', () => ({
  apiClient: {
    post: vi.fn(),
    get: vi.fn()
  }
}))

const createTestQueryClient = () =>
  new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false }
    }
  })

describe('Session Workflow Integration', () => {
  it('completes full extraction workflow', async () => {
    const queryClient = createTestQueryClient()

    // Mock API responses
    vi.mocked(apiClient.post).mockResolvedValueOnce({
      data: { session_id: 'test-session' }
    })

    vi.mocked(apiClient.get).mockResolvedValueOnce({
      data: {
        status: 'completed',
        tokens: [
          { id: '1', name: 'Blue', hex: '#0066CC' }
        ]
      }
    })

    render(
      <QueryClientProvider client={queryClient}>
        <SessionWorkflow />
      </QueryClientProvider>
    )

    // Step 1: Create session
    await userEvent.type(
      screen.getByLabelText(/project name/i),
      'Test Project'
    )
    await userEvent.click(screen.getByRole('button', { name: /create/i }))

    // Step 2: Upload images
    const file = new File(['image'], 'test.png', { type: 'image/png' })
    const input = screen.getByLabelText(/upload/i)
    await userEvent.upload(input, file)

    // Step 3: Start extraction
    await userEvent.click(screen.getByRole('button', { name: /extract/i }))

    // Step 4: Wait for completion
    await waitFor(() => {
      expect(screen.getByText('Blue')).toBeInTheDocument()
    })

    // Verify API calls
    expect(apiClient.post).toHaveBeenCalledWith('/api/sessions', {
      name: 'Test Project'
    })
  })

  it('handles extraction errors gracefully', async () => {
    const queryClient = createTestQueryClient()

    vi.mocked(apiClient.post).mockRejectedValueOnce(
      new Error('Extraction failed')
    )

    render(
      <QueryClientProvider client={queryClient}>
        <SessionWorkflow />
      </QueryClientProvider>
    )

    // Trigger extraction
    await userEvent.click(screen.getByRole('button', { name: /extract/i }))

    // Verify error display
    await waitFor(() => {
      expect(screen.getByRole('alert')).toHaveTextContent('Extraction failed')
    })
  })
})
```

### Accessibility Testing Automation

```typescript
// __tests__/accessibility.test.tsx
import { describe, it, expect } from 'vitest'
import { render } from '@testing-library/react'
import { axe, toHaveNoViolations } from 'jest-axe'
import { TokenCard } from '../TokenCard'
import { TokenGrid } from '../TokenGrid'
import { AccessibilityVisualizer } from '../AccessibilityVisualizer'

expect.extend(toHaveNoViolations)

describe('Accessibility Compliance', () => {
  const mockToken = {
    id: '1',
    name: 'Test Color',
    hex: '#FF5733',
    rgb: 'rgb(255, 87, 51)',
    confidence: 0.95
  }

  describe('TokenCard', () => {
    it('has no accessibility violations', async () => {
      const { container } = render(
        <TokenCard
          token={mockToken}
          onSelect={() => {}}
          onEdit={() => {}}
          onDelete={() => {}}
        />
      )

      const results = await axe(container)
      expect(results).toHaveNoViolations()
    })
  })

  describe('AccessibilityVisualizer', () => {
    it('has no accessibility violations', async () => {
      const { container } = render(
        <AccessibilityVisualizer
          hex="#FF5733"
          wcagContrastWhite={6.5}
          wcagContrastBlack={3.2}
          wcagAACompliantText={true}
        />
      )

      const results = await axe(container)
      expect(results).toHaveNoViolations()
    })
  })

  describe('Color Contrast', () => {
    it('meets WCAG AA for text', async () => {
      const { container } = render(<TokenGrid />)

      const results = await axe(container, {
        rules: {
          'color-contrast': { enabled: true }
        }
      })

      expect(results).toHaveNoViolations()
    })
  })

  describe('Keyboard Navigation', () => {
    it('all interactive elements are focusable', async () => {
      const { container } = render(<TokenGrid />)

      const results = await axe(container, {
        rules: {
          'focus-order-semantics': { enabled: true },
          'tabindex': { enabled: true }
        }
      })

      expect(results).toHaveNoViolations()
    })
  })
})
```

### Visual Regression Testing

```typescript
// __tests__/visual/TokenCard.visual.test.tsx
import { describe, it } from 'vitest'
import { render } from '@testing-library/react'
import { TokenCard } from '../../components/TokenCard'

// Using Playwright for visual snapshots
import { test, expect } from '@playwright/experimental-ct-react'

test.describe('TokenCard Visual', () => {
  const mockToken = {
    id: '1',
    name: 'Primary Blue',
    hex: '#0066CC',
    rgb: 'rgb(0, 102, 204)',
    confidence: 0.95
  }

  test('default state', async ({ mount }) => {
    const component = await mount(
      <TokenCard token={mockToken} />
    )

    await expect(component).toHaveScreenshot('token-card-default.png')
  })

  test('selected state', async ({ mount }) => {
    const component = await mount(
      <TokenCard token={mockToken} isSelected />
    )

    await expect(component).toHaveScreenshot('token-card-selected.png')
  })

  test('hover state', async ({ mount }) => {
    const component = await mount(
      <TokenCard token={mockToken} />
    )

    await component.hover()
    await expect(component).toHaveScreenshot('token-card-hover.png')
  })

  test('dark theme', async ({ mount }) => {
    const component = await mount(
      <div data-theme="dark">
        <TokenCard token={mockToken} />
      </div>
    )

    await expect(component).toHaveScreenshot('token-card-dark.png')
  })
})
```

---

## Infrastructure Testing

### Terraform Validation

```yaml
# .github/workflows/terraform-validate.yml
name: Terraform Validation

on:
  pull_request:
    paths:
      - 'deploy/terraform/**'

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: hashicorp/setup-terraform@v3
        with:
          terraform_version: 1.6.0

      - name: Terraform Format
        run: terraform fmt -check -recursive -diff
        working-directory: deploy/terraform

      - name: Terraform Init
        run: terraform init -backend=false
        working-directory: deploy/terraform

      - name: Terraform Validate
        run: terraform validate
        working-directory: deploy/terraform

      - name: TFLint
        uses: terraform-linters/setup-tflint@v4
        with:
          tflint_version: v0.50.0

      - name: Run TFLint
        run: |
          tflint --init
          tflint --recursive --format compact
        working-directory: deploy/terraform

      - name: Checkov Security Scan
        uses: bridgecrewio/checkov-action@v12
        with:
          directory: deploy/terraform
          framework: terraform
          output_format: cli
          soft_fail: false
          skip_check: CKV_GCP_62  # Known exception

      - name: Infracost
        uses: infracost/actions/setup@v2
        with:
          api-key: ${{ secrets.INFRACOST_API_KEY }}

      - name: Generate cost estimate
        run: |
          infracost breakdown --path deploy/terraform \
            --format json --out-file infracost.json

      - name: Post cost comment
        uses: infracost/actions/comment@v1
        with:
          path: infracost.json
          behavior: update
```

### Container Security Scanning

```yaml
# .github/workflows/container-scan.yml
name: Container Security

on:
  push:
    paths:
      - 'Dockerfile*'
      - 'docker-compose.yml'

jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Build image
        run: docker build -t app:test --target production .

      - name: Trivy vulnerability scan
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: app:test
          format: table
          exit-code: 1
          severity: CRITICAL,HIGH
          ignore-unfixed: true

      - name: Dockle lint
        uses: goodwithtech/dockle-action@v0.1.2
        with:
          image: app:test
          format: list
          exit-code: 1
          ignore: DKL-DI-0006  # Allow ADD for health check

      - name: Grype SBOM scan
        uses: anchore/scan-action@v3
        with:
          image: app:test
          fail-build: true
          severity-cutoff: high
```

### Load Testing Strategy

```typescript
// k6/load-test.js
import http from 'k6/http'
import { check, sleep } from 'k6'
import { Rate } from 'k6/metrics'

const errorRate = new Rate('errors')

export const options = {
  stages: [
    { duration: '2m', target: 10 },   // Ramp up
    { duration: '5m', target: 10 },   // Stay at 10 users
    { duration: '2m', target: 50 },   // Ramp up
    { duration: '5m', target: 50 },   // Stay at 50 users
    { duration: '2m', target: 100 },  // Ramp up
    { duration: '5m', target: 100 },  // Stay at 100 users
    { duration: '5m', target: 0 },    // Ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'],  // 95% under 500ms
    http_req_failed: ['rate<0.01'],    // <1% errors
    errors: ['rate<0.01'],
  },
}

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000'

export default function () {
  // Health check
  const healthRes = http.get(`${BASE_URL}/health`)
  check(healthRes, {
    'health status is 200': (r) => r.status === 200,
  })

  // Get projects
  const projectsRes = http.get(`${BASE_URL}/api/projects`)
  check(projectsRes, {
    'projects status is 200': (r) => r.status === 200,
    'projects returned array': (r) => Array.isArray(JSON.parse(r.body)),
  })

  // Create session
  const sessionRes = http.post(
    `${BASE_URL}/api/sessions`,
    JSON.stringify({ name: `Load Test ${Date.now()}` }),
    { headers: { 'Content-Type': 'application/json' } }
  )
  check(sessionRes, {
    'session created': (r) => r.status === 201,
  })

  if (sessionRes.status !== 201) {
    errorRate.add(1)
  }

  sleep(1)
}

export function handleSummary(data) {
  return {
    'summary.json': JSON.stringify(data),
    stdout: textSummary(data, { indent: ' ', enableColors: true }),
  }
}
```

### Disaster Recovery Testing

```bash
#!/bin/bash
# deploy/scripts/dr-test.sh

set -e

echo "=== Disaster Recovery Test ==="

PROJECT_ID="${GCP_PROJECT_ID}"
REGION="us-central1"
BACKUP_REGION="us-east1"

# Test 1: Database failover (if HA enabled)
echo "Testing database failover..."
gcloud sql instances failover "${PROJECT_ID}-db-production" \
  --project "$PROJECT_ID" \
  --async

# Wait for failover
sleep 60

# Verify database is accessible
gcloud sql instances describe "${PROJECT_ID}-db-production" \
  --project "$PROJECT_ID" \
  --format "value(state)"

# Test 2: Cloud Run traffic migration
echo "Testing traffic migration to backup region..."

# Get current revision
CURRENT_REVISION=$(gcloud run services describe "${PROJECT_ID}-api-production" \
  --region "$REGION" \
  --format "value(status.latestReadyRevisionName)")

echo "Current revision: $CURRENT_REVISION"

# Deploy to backup region (if configured)
# gcloud run services update "${PROJECT_ID}-api-production" \
#   --region "$BACKUP_REGION" \
#   --image "..."

# Test 3: Restore from backup
echo "Testing database restore from backup..."

BACKUP_ID=$(gcloud sql backups list \
  --instance "${PROJECT_ID}-db-production" \
  --project "$PROJECT_ID" \
  --format "value(id)" \
  --limit 1)

echo "Latest backup ID: $BACKUP_ID"

# Create test instance from backup
gcloud sql instances restore-backup "${PROJECT_ID}-db-dr-test" \
  --project "$PROJECT_ID" \
  --backup-instance "${PROJECT_ID}-db-production" \
  --backup-id "$BACKUP_ID" \
  --async

echo "=== DR Test Complete ==="
echo "Review results and clean up test resources"
```

---

## E2E Testing

### Playwright Configuration

```typescript
// playwright.config.ts
import { defineConfig, devices } from '@playwright/test'

export default defineConfig({
  testDir: './e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: [
    ['html'],
    ['junit', { outputFile: 'results.xml' }]
  ],
  use: {
    baseURL: process.env.BASE_URL || 'http://localhost:5173',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
    {
      name: 'mobile-chrome',
      use: { ...devices['Pixel 5'] },
    },
  ],
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:5173',
    reuseExistingServer: !process.env.CI,
  },
})
```

### E2E Test Scenarios

```typescript
// e2e/extraction-workflow.spec.ts
import { test, expect } from '@playwright/test'

test.describe('Color Extraction Workflow', () => {
  test('complete extraction from upload to export', async ({ page }) => {
    // Navigate to app
    await page.goto('/')

    // Step 1: Create project
    await page.getByLabel('Project Name').fill('E2E Test Project')
    await page.getByRole('button', { name: 'Create Project' }).click()

    // Step 2: Upload images
    const fileInput = page.locator('input[type="file"]')
    await fileInput.setInputFiles([
      'e2e/fixtures/test-image-1.png',
      'e2e/fixtures/test-image-2.jpg'
    ])

    // Verify uploads
    await expect(page.getByText('2 images uploaded')).toBeVisible()

    // Step 3: Configure extraction
    await page.getByLabel('Max Colors').fill('25')
    await page.getByLabel('Include Accessibility').check()

    // Step 4: Start extraction
    await page.getByRole('button', { name: 'Extract Colors' }).click()

    // Wait for extraction to complete
    await expect(page.getByText('Extraction Complete')).toBeVisible({
      timeout: 30000
    })

    // Step 5: Review tokens
    const tokenCards = page.locator('.token-card')
    await expect(tokenCards).toHaveCount({ min: 1, max: 25 })

    // Step 6: Select and inspect a token
    await tokenCards.first().click()
    await expect(page.getByRole('complementary')).toContainText('Color Details')

    // Step 7: Export
    await page.getByRole('button', { name: 'Export' }).click()
    await page.getByRole('menuitem', { name: 'CSS Variables' }).click()

    // Verify download
    const download = await page.waitForEvent('download')
    expect(download.suggestedFilename()).toMatch(/\.css$/)
  })

  test('handles extraction errors gracefully', async ({ page }) => {
    await page.goto('/')

    // Upload invalid file
    const fileInput = page.locator('input[type="file"]')
    await fileInput.setInputFiles('e2e/fixtures/invalid.txt')

    // Verify error message
    await expect(page.getByRole('alert')).toContainText('Invalid file type')
  })

  test('supports keyboard navigation', async ({ page }) => {
    await page.goto('/')

    // Navigate with Tab
    await page.keyboard.press('Tab')
    await expect(page.getByLabel('Project Name')).toBeFocused()

    await page.keyboard.press('Tab')
    await expect(page.getByRole('button', { name: 'Create' })).toBeFocused()

    // Submit with Enter
    await page.keyboard.press('Enter')
  })
})
```

### Accessibility E2E Tests

```typescript
// e2e/accessibility.spec.ts
import { test, expect } from '@playwright/test'
import AxeBuilder from '@axe-core/playwright'

test.describe('Accessibility', () => {
  test('home page has no accessibility violations', async ({ page }) => {
    await page.goto('/')

    const results = await new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa'])
      .analyze()

    expect(results.violations).toEqual([])
  })

  test('token grid is keyboard navigable', async ({ page }) => {
    await page.goto('/')

    // Create session and load tokens (setup)
    // ...

    // Navigate to grid
    await page.getByRole('grid').focus()

    // Arrow key navigation
    await page.keyboard.press('ArrowRight')
    await expect(page.locator('.token-card:nth-child(2)')).toBeFocused()

    await page.keyboard.press('ArrowDown')
    // Assert correct card focused based on grid layout

    // Enter to select
    await page.keyboard.press('Enter')
    await expect(page.locator('.token-card.selected')).toBeVisible()
  })

  test('focus trap in modal', async ({ page }) => {
    await page.goto('/')

    // Open modal
    await page.getByRole('button', { name: 'Export' }).click()

    // Verify focus is trapped
    const modal = page.getByRole('dialog')
    await expect(modal).toBeFocused()

    // Tab through modal
    await page.keyboard.press('Tab')
    await expect(modal.getByRole('button').first()).toBeFocused()

    // Shift+Tab wraps to last element
    await page.keyboard.press('Shift+Tab')
    await expect(modal.getByRole('button', { name: 'Close' })).toBeFocused()

    // Escape closes modal
    await page.keyboard.press('Escape')
    await expect(modal).not.toBeVisible()
  })
})
```

---

## Performance Testing

### Frontend Performance

```typescript
// e2e/performance.spec.ts
import { test, expect } from '@playwright/test'

test.describe('Performance', () => {
  test('page loads under performance budget', async ({ page }) => {
    await page.goto('/')

    // Measure Core Web Vitals
    const metrics = await page.evaluate(() => {
      return new Promise((resolve) => {
        new PerformanceObserver((list) => {
          const entries = list.getEntries()
          const result = {}

          entries.forEach(entry => {
            if (entry.name === 'first-contentful-paint') {
              result.fcp = entry.startTime
            }
            if (entry.entryType === 'largest-contentful-paint') {
              result.lcp = entry.startTime
            }
          })

          resolve(result)
        }).observe({ entryTypes: ['paint', 'largest-contentful-paint'] })

        // Fallback timeout
        setTimeout(() => resolve({}), 5000)
      })
    })

    // Assert performance budgets
    expect(metrics.fcp).toBeLessThan(1800)  // FCP < 1.8s
    expect(metrics.lcp).toBeLessThan(2500)  // LCP < 2.5s
  })

  test('handles 100+ tokens without lag', async ({ page }) => {
    await page.goto('/')

    // Load 100 tokens
    await page.evaluate(() => {
      window.__test_load_tokens(100)
    })

    // Measure scroll performance
    const scrollStart = Date.now()
    await page.mouse.wheel(0, 5000)
    const scrollEnd = Date.now()

    expect(scrollEnd - scrollStart).toBeLessThan(500)

    // Measure filter performance
    const filterStart = Date.now()
    await page.getByLabel('Search').fill('blue')
    await page.waitForSelector('.token-card')
    const filterEnd = Date.now()

    expect(filterEnd - filterStart).toBeLessThan(100)
  })
})
```

### Lighthouse CI

```yaml
# .github/workflows/lighthouse.yml
name: Lighthouse CI

on:
  pull_request:
    paths:
      - 'frontend/**'

jobs:
  lighthouse:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Node
        uses: actions/setup-node@v4
        with:
          node-version: 20

      - name: Install dependencies
        run: npm ci

      - name: Build
        run: npm run build

      - name: Run Lighthouse
        uses: treosh/lighthouse-ci-action@v11
        with:
          uploadArtifacts: true
          configPath: .lighthouserc.json
          temporaryPublicStorage: true
```

```json
// .lighthouserc.json
{
  "ci": {
    "collect": {
      "startServerCommand": "npm run preview",
      "url": ["http://localhost:4173"],
      "numberOfRuns": 3
    },
    "assert": {
      "assertions": {
        "categories:performance": ["error", { "minScore": 0.8 }],
        "categories:accessibility": ["error", { "minScore": 0.9 }],
        "categories:best-practices": ["error", { "minScore": 0.9 }],
        "categories:seo": ["warn", { "minScore": 0.8 }],
        "first-contentful-paint": ["error", { "maxNumericValue": 2000 }],
        "largest-contentful-paint": ["error", { "maxNumericValue": 3000 }],
        "cumulative-layout-shift": ["error", { "maxNumericValue": 0.1 }],
        "total-blocking-time": ["error", { "maxNumericValue": 300 }]
      }
    },
    "upload": {
      "target": "temporary-public-storage"
    }
  }
}
```

---

## Testing Automation

### Test Scripts

```json
// package.json
{
  "scripts": {
    "test": "vitest",
    "test:run": "vitest --run",
    "test:ui": "vitest --ui",
    "test:coverage": "vitest --coverage",
    "test:watch": "vitest --watch",

    "test:unit": "vitest --run src/**/*.test.{ts,tsx}",
    "test:integration": "vitest --run src/**/*.integration.test.{ts,tsx}",
    "test:a11y": "vitest --run src/**/*.a11y.test.{ts,tsx}",

    "test:e2e": "playwright test",
    "test:e2e:ui": "playwright test --ui",
    "test:e2e:debug": "playwright test --debug",

    "test:all": "npm run test:run && npm run test:e2e",
    "test:ci": "npm run test:coverage && npm run test:e2e"
  }
}
```

### Coverage Configuration

```typescript
// vitest.config.ts
import { defineConfig } from 'vitest/config'

export default defineConfig({
  test: {
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html', 'lcov'],
      exclude: [
        'node_modules/',
        'dist/',
        '**/*.d.ts',
        '**/*.test.{ts,tsx}',
        '**/types/',
        '**/index.ts'
      ],
      thresholds: {
        global: {
          branches: 70,
          functions: 80,
          lines: 80,
          statements: 80
        },
        'src/components/': {
          branches: 60,
          functions: 70,
          lines: 70,
          statements: 70
        },
        'src/store/': {
          branches: 90,
          functions: 90,
          lines: 90,
          statements: 90
        }
      }
    }
  }
})
```

### CI Test Job

```yaml
# .github/workflows/ci.yml (test job)
test:
  runs-on: ubuntu-latest
  needs: lint

  services:
    postgres:
      image: postgres:16-alpine
      env:
        POSTGRES_PASSWORD: test
        POSTGRES_DB: test
      options: >-
        --health-cmd pg_isready
        --health-interval 10s
        --health-timeout 5s
        --health-retries 5
      ports:
        - 5432:5432

  steps:
    - uses: actions/checkout@v4

    - uses: actions/setup-node@v4
      with:
        node-version: 20
        cache: npm

    - name: Install dependencies
      run: npm ci

    - name: Run unit tests
      run: npm run test:coverage

    - name: Run E2E tests
      run: |
        npx playwright install --with-deps
        npm run test:e2e

    - name: Upload coverage
      uses: codecov/codecov-action@v4
      with:
        files: coverage/lcov.info
        fail_ci_if_error: true

    - name: Upload test results
      uses: actions/upload-artifact@v4
      if: always()
      with:
        name: test-results
        path: |
          coverage/
          playwright-report/
```

---

## Testing Roadmap

### Phase 1: Foundation (Weeks 1-2)

- [ ] Add tests for 10 missing components
- [ ] Achieve 60% unit test coverage
- [ ] Set up Playwright E2E framework
- [ ] Configure coverage thresholds in CI

### Phase 2: Quality (Weeks 3-4)

- [ ] Add accessibility tests with jest-axe
- [ ] Implement visual regression tests
- [ ] Create integration test suite
- [ ] Achieve 80% coverage

### Phase 3: Performance (Weeks 5-6)

- [ ] Set up Lighthouse CI
- [ ] Create load testing suite (k6)
- [ ] Add performance budgets
- [ ] Monitor Core Web Vitals

### Phase 4: Infrastructure (Weeks 7-8)

- [ ] Terraform validation in CI
- [ ] Container security scanning
- [ ] Disaster recovery testing
- [ ] Chaos engineering experiments

---

*See [Implementation Roadmap](./05-implementation-roadmap.md) for timeline and priorities.*
