import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, cleanup, fireEvent, waitFor } from '@testing-library/react'
import { MoodBoard } from '../MoodBoard'
import type { ColorToken } from '../../../types'

const sampleColors: ColorToken[] = [
  {
    hex: '#FF5733',
    rgb: 'rgb(255, 87, 51)',
    name: 'Coral',
    confidence: 0.9,
  },
]

const compositionVariant = {
  id: 'v1',
  title: 'Composition Board',
  subtitle: 'stack',
  vibe: 'warm',
  dominant_colors: ['#FF5733'],
  theme: {
    name: 'Composition',
    description: 'd',
    tags: ['material'],
    visual_elements: [],
    color_palette: ['#FF5733'],
    references: [],
    generated_images: [
      {
        url: 'https://example.com/mat1.png',
        prompt: 'm1',
        provider: 'flux_fast',
        focus_type: 'material' as const,
        role: 'material' as const,
        selection: { provider: 'flux_fast', policy: 'fast' },
      },
      {
        url: 'https://example.com/mat2.png',
        prompt: 'm2',
        provider: 'flux_fast',
        focus_type: 'ui' as const,
        role: 'ui' as const,
        selection: { provider: 'flux_fast', policy: 'fast' },
      },
      {
        url: 'https://example.com/type.png',
        prompt: 't1',
        provider: 'flux_fast',
        focus_type: 'typography' as const,
        role: 'typography' as const,
        selection: { provider: 'flux_fast', policy: 'fast' },
      },
    ],
  },
}

describe('MoodBoard composition slots', () => {
  const storage = new Map<string, string>()

  beforeEach(() => {
    storage.clear()
    vi.stubGlobal('localStorage', {
      getItem: (key: string) => storage.get(key) ?? null,
      setItem: (key: string, value: string) => {
        storage.set(key, value)
      },
      removeItem: (key: string) => {
        storage.delete(key)
      },
      clear: () => storage.clear(),
    })
  })

  afterEach(() => {
    cleanup()
    vi.unstubAllGlobals()
  })

  it('renders Material ×2 → Source → Typography order with source preview', async () => {
    let pollCount = 0
    const fetchMock = vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input)
      if (url.includes('/mood-board/health')) {
        return {
          ok: true,
          status: 200,
          json: async () => ({ status: 'healthy', text_configured: true, image_configured: true }),
        }
      }
      if (url.includes('/mood-board/generate')) {
        return {
          ok: true,
          status: 202,
          json: async () => ({
            job_id: 11,
            status: 'queued',
            queue: 'mood-board',
            stream_url: '/api/v1/jobs/11/stream',
          }),
        }
      }
      pollCount += 1
      if (pollCount < 2) {
        return {
          ok: true,
          status: 200,
          json: async () => ({
            job_id: 11,
            status: 'running',
            progress: 0.5,
            message: 'rendering_images',
            error: null,
            result: null,
          }),
        }
      }
      return {
        ok: true,
        status: 200,
        json: async () => ({
          job_id: 11,
          status: 'completed',
          progress: 1,
          message: 'completed',
          error: null,
          result: {
            variants: [compositionVariant],
            focus_type: 'mixed',
            models_used: { image_generation: 'flux_fast' },
          },
        }),
      }
    })
    vi.stubGlobal('fetch', fetchMock)

    render(
      <MoodBoard
        colors={sampleColors}
        sourceImageBase64="data:image/png;base64,aaa"
      />
    )
    fireEvent.click(screen.getByTestId('mood-board-include-images'))
    fireEvent.click(screen.getByTestId('mood-board-opt-in-button'))

    await waitFor(
      () => {
        expect(screen.getByTestId('mood-board-composition-grid')).toBeInTheDocument()
      },
      { timeout: 8000 }
    )

    const generateCall = fetchMock.mock.calls.find((c) =>
      String(c[0]).includes('/mood-board/generate')
    )
    const body = JSON.parse(String((generateCall?.[1] as RequestInit)?.body ?? '{}')) as {
      focus_type?: string
      image_slots?: { focus_type: string }[]
      num_images_per_variant?: number
    }
    expect(body.focus_type).toBe('mixed')
    expect(body.image_slots).toEqual([
      { focus_type: 'material' },
      { focus_type: 'ui' },
      { focus_type: 'typography' },
    ])
    expect(body.num_images_per_variant).toBe(3)

    const grid = screen.getByTestId('mood-board-composition-grid')
    const labels = Array.from(grid.querySelectorAll('.mood-board-slot-label')).map(
      (el) => el.textContent
    )
    expect(labels).toEqual([
      'Materials & finishes',
      'UI elements',
      'Source',
      'Typography & grid',
    ])
    expect(screen.getByTestId('mood-board-source-slot').querySelector('img')).toHaveAttribute(
      'src',
      'data:image/png;base64,aaa'
    )
  })
})
