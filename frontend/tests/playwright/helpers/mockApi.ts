import type { Page } from '@playwright/test'

type JsonValue = null | boolean | number | string | JsonValue[] | { [key: string]: JsonValue }

const json = (value: JsonValue) => JSON.stringify(value)

const buildStreamLine = (payload: Record<string, unknown>) => `data: ${JSON.stringify(payload)}\n`

export type MockOptions = {
  projectId?: number
}

export async function installApiMocks(page: Page, options: MockOptions = {}) {
  const projectId = options.projectId ?? 1

  await page.route('**/api/v1/projects', async (route) => {
    if (route.request().method() !== 'POST') return route.fallback()
    return route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: json({ id: projectId }),
    })
  })

  await page.route('**/api/v1/colors/extract-streaming', async (route) => {
    if (route.request().method() !== 'POST') return route.fallback()

    const extractedColors = [
      {
        hex: '#FF5733',
        rgb: 'rgb(255, 87, 51)',
        name: 'Coral Red',
        confidence: 0.95,
        count: 2,
      },
      {
        hex: '#33FF57',
        rgb: 'rgb(51, 255, 87)',
        name: 'Neon Green',
        confidence: 0.87,
      },
      {
        hex: '#3357FF',
        rgb: 'rgb(51, 87, 255)',
        name: 'Bright Blue',
        confidence: 0.84,
      },
    ]

    const aiEnhancements = [
      {
        name: 'Coral Red',
        design_intent: 'Primary brand accent',
        semantic_names: { role: 'accent', usage: ['cta'] },
        confidence: 0.95,
        usage: ['button', 'badge'],
        prominence_percentage: 12.3,
      },
      {
        name: 'Neon Green',
        design_intent: 'Success highlight',
        semantic_names: { role: 'success', usage: ['status'] },
        confidence: 0.87,
        usage: ['success', 'badge'],
        prominence_percentage: 6.7,
      },
      {
        name: 'Bright Blue',
        design_intent: 'Secondary support',
        semantic_names: { role: 'secondary', usage: ['link'] },
        confidence: 0.84,
        usage: ['link', 'badge'],
        prominence_percentage: 4.2,
      },
    ]

    const body =
      buildStreamLine({
        phase: 1,
        status: 'colors_streaming',
        progress: 1,
        message: 'Processed 3/3 colors',
        colors: extractedColors,
      }) +
      buildStreamLine({
        phase: 3,
        status: 'ai_enhancement_complete',
        message: 'AI enhancement complete',
        colors: aiEnhancements,
      }) +
      '\n'

    return route.fulfill({
      status: 200,
      contentType: 'text/plain',
      body,
    })
  })

  await page.route('**/api/v1/spacing/extract', async (route) => {
    if (route.request().method() !== 'POST') return route.fallback()
    return route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: json({
        tokens: [
          { value_px: 4, value_rem: 0.25, name: 'token/spacing/export/project/1/01', confidence: 0.9 },
          { value_px: 8, value_rem: 0.5, name: 'token/spacing/export/project/1/02', confidence: 0.9 },
        ],
        scale_system: 'base-8',
        base_unit: 8,
        grid_compliance: 0.9,
        extraction_confidence: 0.85,
        unique_values: [4, 8],
        min_spacing: 4,
        max_spacing: 8,
        warnings: [],
      }),
    })
  })

  await page.route('**/api/v1/shadows/extract', async (route) => {
    if (route.request().method() !== 'POST') return route.fallback()
    return route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: json({ tokens: [] }),
    })
  })

  await page.route('**/api/v1/typography/extract', async (route) => {
    if (route.request().method() !== 'POST') return route.fallback()
    return route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: json({ typography_tokens: [] }),
    })
  })

  await page.route('**/api/v1/design-tokens/export/w3c**', async (route) => {
    if (route.request().method() !== 'GET') return route.fallback()

    const response = {
      color: {
        'color.text.primary': {
          $type: 'color',
          $value: '#111111',
          attributes: {
            name: 'Text Primary',
            hex: '#111111',
            role: 'primary',
            confidence: 0.98,
            count: 3,
            background_role: 'base',
            contrast_category: 'high',
            foreground_role: 'text',
            design_intent: 'Primary text',
            semantic_names: {
              simple: 'slate',
              descriptive: 'cool-slate-dark',
              emotional: 'calm-ink',
              technical: 'slate-neutral-dark',
              vibrancy: 'muted-slate',
            },
            category: 'text',
            temperature: 'cool',
            is_neutral: true,
            prominence_percentage: 42.5,
            extraction_metadata: { model: 'claude-sonnet', extractor: 'mock', source: 'unit' },
            histogram_significance: 0.54,
            saturation_level: 'low',
            lightness_level: 'dark',
            closest_web_safe: '#111111',
            delta_e_to_dominant: 1.23,
            tint_color: '#333333',
            shade_color: '#000000',
            tone_color: '#222222',
            harmony: 'analogous',
            hsl: 'hsl(0, 0%, 7%)',
            closest_css_named: 'black',
            wcag_contrast_on_white: 12.34,
            wcag_contrast_on_black: 1.12,
            wcag_aa_compliant_text: true,
            wcag_aaa_compliant_text: true,
            wcag_aa_compliant_normal: true,
            wcag_aaa_compliant_normal: false,
            colorblind_safe: true,
          },
        },
        'token/color/export/project/1/01': {
          $type: 'color',
          $value: { l: 0.72, c: 0.12, h: 45, alpha: 1, space: 'oklch' },
          attributes: {
            name: 'Warm Accent',
            hex: '#F2B24C',
            role: 'accent',
            confidence: 0.9,
            background_role: 'accent',
            contrast_category: 'medium',
            foreground_role: 'accent',
          },
        },
        'color.alias.primary': { $type: 'color', $value: '{color.text.primary}' },
      },
      spacing: {
        'spacing.base': {
          $type: 'dimension',
          $value: { value: 8, unit: 'px' },
          attributes: {
            confidence: 0.95,
            semantic_role: 'base',
            spacing_type: 'grid',
            grid_aligned: true,
            tailwind_class: 'space-2',
            prominence_percentage: 24.2,
            scale_position: 1,
            related_tokens: ['spacing.sm', 'spacing.md'],
            usage: ['gap', 'padding'],
            responsive_scales: { sm: 4, md: 8, lg: 12 },
          },
        },
        'spacing.sm': {
          $type: 'dimension',
          $value: { value: 4, unit: 'px' },
          multipleOf: 'spacing.base',
          multiplier: 0.5,
          attributes: {
            confidence: 0.9,
            semantic_role: 'compact',
            spacing_type: 'padding',
            grid_aligned: true,
            tailwind_class: 'space-1',
            prominence_percentage: 12.5,
            scale_position: 0,
            related_tokens: ['spacing.base'],
            usage: ['stack', 'inset'],
          },
        },
        'spacing.md': {
          $type: 'dimension',
          $value: { value: 16, unit: 'px' },
          multipleOf: 'spacing.base',
          multiplier: 2,
          attributes: {
            confidence: 0.88,
            semantic_role: 'spacious',
            spacing_type: 'margin',
            grid_aligned: false,
            tailwind_class: 'space-4',
            prominence_percentage: 8.8,
            scale_position: 2,
            related_tokens: ['spacing.base'],
            usage: ['section', 'layout'],
          },
        },
      },
      shadow: {
        'shadow.card': {
          $type: 'shadow',
          $value: [
            {
              x: { value: 0, unit: 'px' },
              y: { value: 4, unit: 'px' },
              blur: { value: 16, unit: 'px' },
              spread: { value: 0, unit: 'px' },
              color: '{color.text.primary}',
              inset: false,
              opacity: 0.2,
            },
            {
              x: { value: 0, unit: 'px' },
              y: { value: 1, unit: 'px' },
              blur: { value: 4, unit: 'px' },
              spread: { value: 0, unit: 'px' },
              color: 'rgba(0,0,0,0.12)',
              inset: false,
            },
          ],
          attributes: {
            name: 'shadow.card',
            shadow_type: 'drop',
            semantic_role: 'elevation',
            confidence: 0.92,
          },
        },
      },
      typography: {
        'typography.body': {
          $type: 'typography',
          $value: {
            fontFamily: ['Inter'],
            fontSize: { value: 16, unit: 'px' },
            lineHeight: { value: 24, unit: 'px' },
            fontWeight: 400,
            letterSpacing: { value: 0.02, unit: 'em' },
            casing: 'uppercase',
            color: '{color.text.primary}',
          },
          attributes: {
            semantic_role: 'body',
            confidence: 0.93,
            readability_score: 0.88,
            is_readable: true,
            prominence_percentage: 18.4,
            usage: ['body', 'article', 'longform'],
            extraction_metadata: { model: 'typography-v1', source: 'mock' },
          },
        },
      },
      layout: {},
      meta: {
        typography_recommendation: {
          style_attributes: {
            fontFamily: 'Inter',
            scale: 'minor-third',
            color_temperature: 'cool',
            visual_weight: 'medium',
            contrast_level: 'high',
            primary_style: 'modern',
            vlm_mood: 'calm',
            vlm_complexity: 'balanced',
          },
          confidence: 0.77,
        },
      },
    }

    return route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: json(response as any),
    })
  })

  // Metrics SSE (EventSource). Keep same-origin via VITE_API_BASE_URL in playwright config.
  await page.route('**/api/metrics/projects/*/stream', async (route) => {
    const sse =
      `data: ${JSON.stringify({ tier: 'tier_1', data: { color_count: 3, spacing_count: 3 } })}\n\n` +
      `data: ${JSON.stringify({ event: 'complete', total_time: 0.12 })}\n\n`
    return route.fulfill({
      status: 200,
      headers: {
        'content-type': 'text/event-stream',
        'cache-control': 'no-cache',
        connection: 'keep-alive',
      },
      body: sse,
    })
  })
}
