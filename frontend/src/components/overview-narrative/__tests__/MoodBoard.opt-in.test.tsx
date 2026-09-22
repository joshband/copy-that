import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, waitFor, fireEvent, cleanup } from '@testing-library/react'
import { MoodBoard, MOOD_BOARD_COST_HINT } from '../MoodBoard'
import type { ColorToken } from '../../../types'

const sampleColors: ColorToken[] = [
  {
    hex: '#FF5733',
    rgb: 'rgb(255, 87, 51)',
    name: 'Coral',
    confidence: 0.9,
    temperature: 'warm',
    saturation_level: 'high',
    hue_family: 'orange',
  },
]

const sampleVariant = {
  id: 'v1',
  title: 'Warm Board',
  subtitle: 'Test',
  vibe: 'warm',
  dominant_colors: ['#FF5733'],
  theme: {
    name: 'Warm',
    description: 'desc',
    tags: ['warm'],
    visual_elements: [],
    color_palette: ['#FF5733'],
    references: [],
    generated_images: [],
  },
}

function mockAsyncJobFlow(fetchMock: ReturnType<typeof vi.fn>, variants = [sampleVariant]) {
  let pollCount = 0
  fetchMock.mockImplementation(async (input: RequestInfo | URL) => {
    const url = String(input)
    if (url.includes('/mood-board/health')) {
      return {
        ok: true,
        status: 200,
        json: async () => ({
          status: 'healthy',
          text_provider: 'openai_compatible',
          text_configured: true,
          text_model: 'google/gemma-2-9b',
          image_provider: 'none',
          image_configured: false,
        }),
      }
    }
    if (url.includes('/mood-board/generate')) {
      return {
        ok: true,
        status: 202,
        json: async () => ({
          job_id: 42,
          status: 'queued',
          queue: 'mood-board',
          stream_url: '/api/v1/jobs/42/stream',
        }),
      }
    }
    if (url.includes('/jobs/42')) {
      pollCount += 1
      if (pollCount < 2) {
        return {
          ok: true,
          status: 200,
          json: async () => ({
            job_id: 42,
            status: 'running',
            progress: 0.2,
            message: 'generating_themes',
            error: null,
            result: null,
          }),
        }
      }
      return {
        ok: true,
        status: 200,
        json: async () => ({
          job_id: 42,
          status: 'completed',
          progress: 1,
          message: 'completed',
          error: null,
          result: {
            variants,
            generation_time_ms: 10,
            models_used: { content_generation: 'local', image_generation: 'none' },
            focus_type: 'material',
          },
        }),
      }
    }
    throw new Error(`Unexpected fetch: ${url}`)
  })
}

describe('MoodBoard opt-in', () => {
  const fetchMock = vi.fn()
  const storage = new Map<string, string>()

  beforeEach(() => {
    fetchMock.mockReset()
    storage.clear()
    vi.stubGlobal('fetch', fetchMock)
    vi.stubGlobal('localStorage', {
      getItem: (key: string) => storage.get(key) ?? null,
      setItem: (key: string, value: string) => {
        storage.set(key, value)
      },
      removeItem: (key: string) => {
        storage.delete(key)
      },
    })
    fetchMock.mockImplementation(async (input: RequestInfo | URL) => {
      const url = String(input)
      if (url.includes('/mood-board/health')) {
        return {
          ok: true,
          status: 200,
          json: async () => ({
            status: 'healthy',
            text_configured: true,
            text_provider: 'anthropic',
            image_configured: false,
            image_provider: 'none',
          }),
        }
      }
      throw new Error(`Unexpected fetch: ${url}`)
    })
  })

  afterEach(() => {
    cleanup()
    vi.unstubAllGlobals()
  })

  it('shows cost banner and CTA without calling generate', async () => {
    render(<MoodBoard colors={sampleColors} />)

    expect(screen.getByTestId('mood-board-cost-banner')).toHaveTextContent(MOOD_BOARD_COST_HINT)
    expect(screen.getByTestId('mood-board-opt-in-button')).toHaveTextContent(/Generate themes/i)
    await waitFor(() => {
      expect(fetchMock.mock.calls.some((c) => String(c[0]).includes('/mood-board/health'))).toBe(
        true
      )
    })
    expect(fetchMock.mock.calls.some((c) => String(c[0]).includes('/mood-board/generate'))).toBe(
      false
    )
  })

  it('enqueues a themes-only job and polls until variants render', async () => {
    mockAsyncJobFlow(fetchMock)

    render(<MoodBoard colors={sampleColors} />)
    fireEvent.click(screen.getByTestId('mood-board-opt-in-button'))

    await waitFor(() => {
      expect(fetchMock.mock.calls.some((c) => String(c[0]).includes('/mood-board/generate'))).toBe(
        true
      )
    })
    const generateCall = fetchMock.mock.calls.find((c) =>
      String(c[0]).includes('/mood-board/generate')
    )
    const body = JSON.parse(String((generateCall?.[1] as RequestInit)?.body ?? '{}')) as {
      include_images?: boolean
      num_variants?: number
    }
    expect(body.include_images).toBe(false)
    expect(body.num_variants).toBe(2)

    expect(await screen.findByText('Warm Board', {}, { timeout: 5000 })).toBeInTheDocument()
    expect(screen.getByTestId('mood-board-themes-only')).toBeInTheDocument()
  })

  it('renders nothing without colors', () => {
    const { container } = render(<MoodBoard colors={[]} />)
    expect(container).toBeEmptyDOMElement()
  })

  it('surfaces Celery 503 as a clear error after opt-in', async () => {
    fetchMock.mockImplementation(async (input: RequestInfo | URL) => {
      const url = String(input)
      if (url.includes('/mood-board/health')) {
        return {
          ok: true,
          status: 200,
          json: async () => ({ status: 'healthy', text_configured: false, image_configured: false }),
        }
      }
      return {
        ok: false,
        status: 503,
        statusText: 'Service Unavailable',
        text: async () => 'unavailable',
      }
    })
    render(<MoodBoard colors={sampleColors} />)
    fireEvent.click(screen.getByTestId('mood-board-opt-in-button'))
    expect(await screen.findByText(/Celery worker not running/i)).toBeInTheDocument()
  })

  it('keeps CTA and skips generate when cache exists until opt-in', async () => {
    storage.set(
      'moodboard::material::themes::balanced',
      JSON.stringify([
        {
          id: 'v1',
          title: 'Cached Board',
          subtitle: 'from cache',
          vibe: 'cool',
          dominant_colors: ['#FF5733'],
          theme: {
            name: 'Cached',
            description: 'd',
            tags: [],
            visual_elements: [],
            color_palette: ['#FF5733'],
            references: [],
            generated_images: [],
          },
        },
      ])
    )
    render(<MoodBoard colors={sampleColors} />)
    expect(screen.getByTestId('mood-board-opt-in-button')).toBeInTheDocument()
    expect(screen.queryByText('Cached Board')).not.toBeInTheDocument()
    await waitFor(() => {
      expect(fetchMock.mock.calls.every((c) => String(c[0]).includes('/mood-board/health'))).toBe(
        true
      )
    })
  })

  it('hydrates cached variants after opt-in without generating', async () => {
    storage.set(
      'moodboard::material::themes::balanced',
      JSON.stringify([
        {
          id: 'v1',
          title: 'Cached Board',
          subtitle: 'from cache',
          vibe: 'cool',
          dominant_colors: ['#FF5733'],
          theme: {
            name: 'Cached',
            description: 'd',
            tags: [],
            visual_elements: [],
            color_palette: ['#FF5733'],
            references: [],
            generated_images: [],
          },
        },
      ])
    )
    render(<MoodBoard colors={sampleColors} />)
    fireEvent.click(screen.getByTestId('mood-board-opt-in-button'))
    expect(await screen.findByText('Cached Board')).toBeInTheDocument()
    expect(fetchMock.mock.calls.some((c) => String(c[0]).includes('/mood-board/generate'))).toBe(
      false
    )
  })

  it('surfaces failed job errors after polling', async () => {
    fetchMock.mockImplementation(async (input: RequestInfo | URL) => {
      const url = String(input)
      if (url.includes('/mood-board/health')) {
        return {
          ok: true,
          status: 200,
          json: async () => ({ status: 'healthy', text_configured: true, image_configured: false }),
        }
      }
      if (url.includes('/mood-board/generate')) {
        return {
          ok: true,
          status: 202,
          json: async () => ({
            job_id: 7,
            status: 'queued',
            queue: 'mood-board',
            stream_url: '/api/v1/jobs/7/stream',
          }),
        }
      }
      return {
        ok: true,
        status: 200,
        json: async () => ({
          job_id: 7,
          status: 'failed',
          progress: 0.2,
          message: 'failed',
          error: 'LM Studio unreachable',
          result: null,
        }),
      }
    })

    render(<MoodBoard colors={sampleColors} />)
    fireEvent.click(screen.getByTestId('mood-board-opt-in-button'))
    expect(await screen.findByText(/LM Studio unreachable/i)).toBeInTheDocument()
  })

  it('shows imagery progress copy when include-images is checked', async () => {
    fetchMock.mockImplementation(async (input: RequestInfo | URL) => {
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
            job_id: 99,
            status: 'queued',
            queue: 'mood-board',
            stream_url: '/api/v1/jobs/99/stream',
          }),
        }
      }
      return {
        ok: true,
        status: 200,
        json: async () => ({
          job_id: 99,
          status: 'running',
          progress: 0.5,
          message: 'rendering_images (1/1)',
          error: null,
          result: null,
        }),
      }
    })

    render(<MoodBoard colors={sampleColors} />)
    fireEvent.click(screen.getByTestId('mood-board-include-images'))
    fireEvent.click(screen.getByTestId('mood-board-opt-in-button'))

    expect(await screen.findByTestId('mood-board-progress-copy')).toHaveTextContent(/imagery/i)
    expect(screen.getByTestId('mood-board-progress-meta')).toHaveTextContent(/Elapsed/i)
    expect(screen.getByTestId('mood-board-progress-meta')).toHaveTextContent(/45 min/i)
    expect(screen.getByTestId('mood-board-cancel-button')).toBeInTheDocument()

    fireEvent.click(screen.getByTestId('mood-board-cancel-button'))
    expect(await screen.findByText(/Generation cancelled/i)).toBeInTheDocument()
  })
})
