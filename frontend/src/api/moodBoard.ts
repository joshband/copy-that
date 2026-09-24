/**
 * Mood board generate + job wait (async Celery flow).
 */

import { API_BASE } from './client'
import { pollJobUntilDone, type JobStatusResponse, type PollJobOptions } from './jobs'
import type { MoodBoardVariant } from '../components/overview-narrative/moodBoardTypes'

/**
 * Local mflux image gens often take 5+ minutes per image; Midjourney-pair smoke
 * with 4 images ran ~18 minutes. Keep the UI waiting long enough for solo-pool
 * Celery jobs (see soft_time_limit on generate_mood_board_job).
 */
export const MOOD_BOARD_POLL_MAX_WAIT_MS = 45 * 60 * 1000

export interface MoodBoardColorInput {
  hex: string
  name?: string | null
  temperature?: string | null
  saturation_level?: string | null
  hue_family?: string | null
}

export interface MoodBoardImageSlot {
  focus_type: 'material' | 'typography'
}

export interface MoodBoardGenerateRequest {
  colors: MoodBoardColorInput[]
  num_variants?: number
  include_images?: boolean
  num_images_per_variant?: number
  focus_type?: 'material' | 'typography' | 'mixed'
  image_slots?: MoodBoardImageSlot[]
  policy?: 'balanced' | 'fast' | 'cheap' | 'private' | 'quality'
  allow_cloud?: boolean
  max_latency_ms?: number
}

export interface MoodBoardJobHandle {
  job_id: number
  status: string
  queue?: string | null
  stream_url: string
}

export interface MoodBoardResult {
  variants: MoodBoardVariant[]
  generation_time_ms?: number
  models_used?: Record<string, string>
  focus_type?: string
}

export class MoodBoardUnavailableError extends Error {
  readonly status: number

  constructor(message: string, status: number) {
    super(message)
    this.name = 'MoodBoardUnavailableError'
    this.status = status
  }
}

export interface MoodBoardBackendHealth {
  id: string
  kind: string
  available: boolean
  reason?: string | null
  estimated_latency_ms?: number
  cost_per_image_usd?: number
  quality?: number
}

export interface MoodBoardHealth {
  status: string
  text_provider?: string
  text_configured?: boolean
  text_model?: string | null
  image_provider?: string
  image_configured?: boolean
  image_model?: string | null
  anthropic_configured?: boolean
  openai_configured?: boolean
  backends?: MoodBoardBackendHealth[]
  recommended_policy?: string
  default_policy?: string
}

/** Provider / config hints for the Mood tab UI. */
export async function fetchMoodBoardHealth(signal?: AbortSignal): Promise<MoodBoardHealth> {
  const response = await fetch(`${API_BASE}/mood-board/health`, { signal })
  if (!response.ok) {
    throw new Error(`Mood board health check failed (${response.status})`)
  }
  return (await response.json()) as MoodBoardHealth
}

export async function enqueueMoodBoard(
  body: MoodBoardGenerateRequest,
  signal?: AbortSignal
): Promise<MoodBoardJobHandle> {
  const response = await fetch(`${API_BASE}/mood-board/generate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
    signal,
  })

  if (!response.ok) {
    const text = await response.text().catch(() => '')
    if (response.status === 503) {
      throw new MoodBoardUnavailableError(
        'Mood board generation unavailable (Celery worker not running).',
        503
      )
    }
    throw new Error(
      `Failed to generate mood boards (${response.status}): ${response.statusText || text || 'Unknown error'}`
    )
  }

  return (await response.json()) as MoodBoardJobHandle
}

function parseResult(job: JobStatusResponse): MoodBoardResult {
  const raw = job.result
  if (!raw || typeof raw !== 'object') {
    throw new Error('Mood board job completed without a result payload.')
  }
  const typed = raw as unknown as MoodBoardResult
  if (!Array.isArray(typed.variants)) {
    throw new Error('Mood board job result missing variants.')
  }
  return {
    variants: typed.variants,
    generation_time_ms: typed.generation_time_ms,
    models_used: typed.models_used,
    focus_type: typed.focus_type,
  }
}

export interface GenerateMoodBoardOptions extends PollJobOptions {
  signal?: AbortSignal
}

/**
 * Enqueue mood board generation and poll until the job completes or fails.
 */
export async function generateMoodBoard(
  body: MoodBoardGenerateRequest,
  options: GenerateMoodBoardOptions = {}
): Promise<MoodBoardResult> {
  const { signal, onUpdate, intervalMs, maxWaitMs = MOOD_BOARD_POLL_MAX_WAIT_MS } = options
  const handle = await enqueueMoodBoard(body, signal)
  onUpdate?.({
    job_id: handle.job_id,
    status: handle.status,
    progress: 0,
    queue: handle.queue,
    message: 'enqueued',
    error: null,
    result: null,
  })

  const job = await pollJobUntilDone(handle.job_id, {
    signal,
    onUpdate,
    intervalMs,
    maxWaitMs,
  })

  if (job.status === 'failed') {
    throw new Error(job.error || job.message || 'Mood board generation failed.')
  }

  return parseResult(job)
}
