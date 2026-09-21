import { test, expect } from '@playwright/test'
import path from 'path'
import { fileURLToPath } from 'url'

const OVERLAY_BASE64 =
  'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/Pi5c+QAAAABJRU5ErkJggg=='
const SPACING_OVERLAY_BASE64 =
  'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMBAqW9n9kAAAAASUVORK5CYII='
const TYPOGRAPHY_OVERLAY_BASE64 =
  'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMBAqW9n9kAAAAASUVORK5CYII='
const SHADOW_ARTIFACT_BASE64 =
  'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMBAqW9n9kAAAAASUVORK5CYII='
const GEOMETRY_DEPTH_BASE64 =
  'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMBAqW9n9kAAAAASUVORK5CYII='
const GEOMETRY_NORMALS_BASE64 =
  'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMBAqW9n9kAAAAASUVORK5CYII='

const colorToken = {
  id: 'color.primary',
  hex: '#111111',
  rgb: 'rgb(17, 17, 17)',
  name: 'Primary',
  confidence: 0.92,
}

const streamBody = [
  {
    phase: 1,
    status: 'colors_streaming',
    progress: 0.5,
    colors: [colorToken],
  },
  {
    phase: 2,
    status: 'extraction_complete',
    colors: [colorToken],
    debug: {
      overlay_png_base64: OVERLAY_BASE64,
      segmented_palette: [{ hex: '#111111', coverage: 0.6 }],
    },
    summary: 'Monochrome palette',
  },
  {
    phase: 3,
    status: 'ai_enhancement_complete',
    colors: [{ name: 'Primary', confidence: 0.98 }],
  },
]
  .map((event) => `data: ${JSON.stringify(event)}`)
  .join('\n') + '\n'

const spacingResponse = {
  tokens: [
    {
      value_px: 8,
      value_rem: 0.5,
      name: 'spacing-08',
      confidence: 0.8,
    },
  ],
  scale_system: 'custom',
  base_unit: 8,
  grid_compliance: 0.9,
  extraction_confidence: 0.85,
  unique_values: [8],
  min_spacing: 8,
  max_spacing: 8,
}
const spacingResponseWithOverlay = {
  ...spacingResponse,
  debug_overlay: SPACING_OVERLAY_BASE64,
}

const w3cExport = {
  color: {
    'token/color/primary': { $type: 'color', $value: '#111111' },
  },
  spacing: {
    'token/spacing/primary': { $type: 'dimension', $value: { value: 8, unit: 'px' } },
  },
  shadow: {},
  typography: {
    'token/typography/body/01': {
      $type: 'typography',
      $value: {
        fontFamily: ['Inter'],
        fontSize: { value: 16, unit: 'px' },
        lineHeight: { value: 24, unit: 'px' },
      },
      extraction_metadata: { baseline_overlay: TYPOGRAPHY_OVERLAY_BASE64, source: 'cv' },
    },
  },
  layout: {},
  meta: { typography_recommendation: { style_attributes: {}, confidence: null } },
}

const geometryResponse = {
  meta: {
    profile_requested: 'auto',
    profile_resolved: 'cpu_fast',
    device: 'cpu',
    depth_model: 'mock',
    normals_source: 'depth',
    normals_smoothing_sigma: 1.1,
    warnings: [],
  },
  images: {
    depth_png: GEOMETRY_DEPTH_BASE64,
    normals_png: GEOMETRY_NORMALS_BASE64,
  },
}

test.describe('Streaming artifacts', () => {
  test.beforeEach(async ({ page }) => {
    await page.addInitScript(() => {
      class MockEventSource {
        url: string
        onmessage: ((event: MessageEvent) => void) | null = null
        onerror: ((event: Event) => void) | null = null
        readyState = 1

        constructor(url: string) {
          this.url = url
          setTimeout(() => {
            const complete = new MessageEvent('message', {
              data: JSON.stringify({ event: 'complete', total_time: 0.01 }),
            })
            this.onmessage?.(complete)
            this.readyState = 2
          }, 10)
        }

        close() {
          this.readyState = 2
        }

        addEventListener() {
          return undefined
        }

        removeEventListener() {
          return undefined
        }
      }

      // @ts-expect-error - override EventSource for test stability
      window.EventSource = MockEventSource
    })

    await page.route('**/api/v1/projects', async (route) => {
      if (route.request().method() !== 'POST') return route.continue()
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ id: 1 }),
      })
    })

    await page.route('**/api/v1/colors/extract-streaming', async (route) => {
      await route.fulfill({
        status: 200,
        headers: { 'content-type': 'text/event-stream' },
        body: streamBody,
      })
    })

    await page.route('**/api/v1/spacing/extract', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(spacingResponse),
      })
    })

    await page.route('**/api/v1/shadows/extract', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          tokens: [],
          extraction_confidence: 0.7,
          extraction_metadata: {
            shadowlab: {
              pipeline: {
                ml_backend: 'u2net',
                geometry_backends: ['lsd', 'vanishing'],
              },
              artifacts: ['shadow_mask.png', 'penumbra_map.png'],
              duration_ms: 1200,
            },
          },
          artifacts: {
            images: [
              {
                type: 'shadow_overlay',
                mime: 'image/png',
                base64: SHADOW_ARTIFACT_BASE64,
                stage: 'shadowlab',
                description: 'Shadow overlay',
              },
              {
                type: 'final_shadow_mask',
                mime: 'image/png',
                base64: SHADOW_ARTIFACT_BASE64,
                stage: 'shadowlab',
                description: 'Final shadow mask',
              },
            ],
            json: [
              {
                type: 'pipeline_results',
                payload: { shadow_count: 2, mean_strength: 0.45 },
                stage: 'shadowlab',
              },
            ],
          },
        }),
      })
    })

    await page.route('**/api/v1/typography/extract', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ tokens: [] }),
      })
    })

    await page.route('**/api/v1/design-tokens/export/w3c**', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(w3cExport),
      })
    })

    await page.route('**/api/v1/geometry/extract', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(geometryResponse),
      })
    })

    await page.goto('/')
  })

  test('shows diagnostics overlay from streamed artifacts', async ({ page }) => {
    const uploadInput = page.locator('#file-input')
    const __dirname = path.dirname(fileURLToPath(import.meta.url))
    const testImagePath = path.join(__dirname, 'fixtures', 'sample.png')

    await uploadInput.setInputFiles(testImagePath)

    const extractButton = page.locator('.extract-btn')
    await expect(extractButton).toBeEnabled()
    await extractButton.click()

    const overlayImage = page.locator('img[alt="Diagnostics overlay"]')
    await expect(overlayImage).toBeVisible({ timeout: 10000 })
    await expect(overlayImage).toHaveAttribute(
      'src',
      `data:image/png;base64,${OVERLAY_BASE64}`
    )
  })

  test('uses spacing overlay when available', async ({ page }) => {
    await page.route('**/api/v1/spacing/extract', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(spacingResponseWithOverlay),
      })
    })

    const uploadInput = page.locator('#file-input')
    const __dirname = path.dirname(fileURLToPath(import.meta.url))
    const testImagePath = path.join(__dirname, 'fixtures', 'sample.png')

    await uploadInput.setInputFiles(testImagePath)

    const extractButton = page.locator('.extract-btn')
    await expect(extractButton).toBeEnabled()
    await extractButton.click()

    const overlayImage = page.locator('img[alt="Diagnostics overlay"]')
    await expect(overlayImage).toBeVisible({ timeout: 10000 })
    await expect(overlayImage).toHaveAttribute(
      'src',
      `data:image/png;base64,${SPACING_OVERLAY_BASE64}`
    )
  })

  test('shows typography baseline overlay from export', async ({ page }) => {
    const uploadInput = page.locator('#file-input')
    const __dirname = path.dirname(fileURLToPath(import.meta.url))
    const testImagePath = path.join(__dirname, 'fixtures', 'sample.png')

    await uploadInput.setInputFiles(testImagePath)

    const extractButton = page.locator('.extract-btn')
    await expect(extractButton).toBeEnabled()
    await extractButton.click()

    const uploadPanel = page.locator('#uploader-panel')
    await expect(uploadPanel).toHaveAttribute('data-token-graph-ready', 'true', {
      timeout: 10000,
    })

    await page.locator('.header-actions .switch .slider').click()
    await expect(page.getByText('Debug on')).toBeVisible()
    await page.getByRole('button', { name: 'Typography', exact: true }).click()

    const overlayImage = page.locator('img[alt="Typography baseline overlay"]')
    await expect(overlayImage).toBeVisible({ timeout: 10000 })
    await expect(overlayImage).toHaveAttribute(
      'src',
      `data:image/png;base64,${TYPOGRAPHY_OVERLAY_BASE64}`
    )
  })

  test('shows shadowlab artifacts and geometry stage', async ({ page }) => {
    const uploadInput = page.locator('#file-input')
    const __dirname = path.dirname(fileURLToPath(import.meta.url))
    const testImagePath = path.join(__dirname, 'fixtures', 'sample.png')

    await uploadInput.setInputFiles(testImagePath)

    const extractButton = page.locator('.extract-btn')
    await expect(extractButton).toBeEnabled()
    await extractButton.click()

    await expect(page.getByText('Stage 4 (ML mask): u2net')).toBeVisible({ timeout: 10000 })
    await expect(page.getByText('Stage 6 (geometry): lsd,vanishing')).toBeVisible({ timeout: 10000 })
    await expect(page.getByText('Artifacts: 2')).toBeVisible({ timeout: 10000 })
  })

  test('shows shadow artifact thumbnails', async ({ page }) => {
    const uploadInput = page.locator('#file-input')
    const __dirname = path.dirname(fileURLToPath(import.meta.url))
    const testImagePath = path.join(__dirname, 'fixtures', 'sample.png')

    await uploadInput.setInputFiles(testImagePath)

    const extractButton = page.locator('.extract-btn')
    await expect(extractButton).toBeEnabled()
    await extractButton.click()

    await page.locator('.header-actions .switch .slider').click()
    await expect(page.getByText('Debug on')).toBeVisible()
    await page.getByRole('button', { name: 'Shadows', exact: true }).click()

    const artifactImage = page.getByAltText('Shadow artifact Shadow overlay')
    await expect(artifactImage).toBeVisible({ timeout: 10000 })
    await expect(artifactImage).toHaveAttribute(
      'src',
      `data:image/png;base64,${SHADOW_ARTIFACT_BASE64}`
    )

    const jsonSummary = page.getByText('Pipeline results')
    await expect(jsonSummary).toBeVisible({ timeout: 10000 })
  })

  test('shows geometry artifacts preview', async ({ page }) => {
    const lightingTab = page.locator('nav.tabs').getByRole('button', { name: 'Lighting', exact: true })
    test.skip((await lightingTab.count()) === 0, 'Lighting tab is parked off for MVP')

    const uploadInput = page.locator('#file-input')
    const __dirname = path.dirname(fileURLToPath(import.meta.url))
    const testImagePath = path.join(__dirname, 'fixtures', 'sample.png')

    await uploadInput.setInputFiles(testImagePath)

    const extractButton = page.locator('.extract-btn')
    await expect(extractButton).toBeEnabled()
    await extractButton.click()

    await lightingTab.click()

    const geometryButton = page.getByRole('button', { name: 'Extract geometry', exact: true })
    await expect(geometryButton).toBeEnabled()
    await geometryButton.click()

    await expect(page.getByAltText('Geometry Depth map')).toBeVisible({ timeout: 10000 })
    await expect(page.getByAltText('Geometry Normals map')).toBeVisible({ timeout: 10000 })
  })
})
