/**
 * Durable job status helpers (Celery-backed `/api/v1/jobs/{id}`).
 */

import { API_BASE } from './client'

export interface JobStatusResponse {
  job_id: number
  status: string
  progress: number
  queue?: string | null
  message?: string | null
  error?: string | null
  result?: Record<string, unknown> | null
}

export interface PollJobOptions {
  /** Poll interval in ms (default 750, matches backend SSE cadence). */
  intervalMs?: number
  /**
   * Max wall-clock wait before giving up (ms).
   * Omit or pass `Infinity` to poll until terminal status (or abort).
   */
  maxWaitMs?: number
  signal?: AbortSignal
  onUpdate?: (job: JobStatusResponse) => void
}

export class JobPollTimeoutError extends Error {
  readonly jobId: number
  readonly maxWaitMs: number

  constructor(jobId: number, maxWaitMs: number) {
    super(
      `Job ${jobId} still running after ${Math.round(maxWaitMs / 60000)} minutes. ` +
        'Local mood-board image generation can take a long time — retry or check the Celery worker.'
    )
    this.name = 'JobPollTimeoutError'
    this.jobId = jobId
    this.maxWaitMs = maxWaitMs
  }
}

const TERMINAL = new Set(['completed', 'failed'])

function sleep(ms: number, signal?: AbortSignal): Promise<void> {
  return new Promise((resolve, reject) => {
    if (signal?.aborted) {
      reject(new DOMException('Aborted', 'AbortError'))
      return
    }
    const timer = setTimeout(resolve, ms)
    const onAbort = () => {
      clearTimeout(timer)
      reject(new DOMException('Aborted', 'AbortError'))
    }
    signal?.addEventListener('abort', onAbort, { once: true })
  })
}

export async function fetchJob(
  jobId: number,
  signal?: AbortSignal
): Promise<JobStatusResponse> {
  const response = await fetch(`${API_BASE}/jobs/${jobId}`, { signal })
  if (!response.ok) {
    const text = await response.text().catch(() => '')
    throw new Error(
      `Failed to fetch job ${jobId} (${response.status}): ${response.statusText || text || 'Unknown error'}`
    )
  }
  return (await response.json()) as JobStatusResponse
}

/**
 * Poll job status until completed or failed.
 * Prefer this over inventing sync generate endpoints — Celery jobs are SoT.
 */
export async function pollJobUntilDone(
  jobId: number,
  options: PollJobOptions = {}
): Promise<JobStatusResponse> {
  const intervalMs = options.intervalMs ?? 750
  const maxWaitMs = options.maxWaitMs
  const { signal, onUpdate } = options
  const startedAt = Date.now()

  for (;;) {
    if (signal?.aborted) {
      throw new DOMException('Aborted', 'AbortError')
    }

    if (
      typeof maxWaitMs === 'number' &&
      Number.isFinite(maxWaitMs) &&
      Date.now() - startedAt > maxWaitMs
    ) {
      throw new JobPollTimeoutError(jobId, maxWaitMs)
    }

    const job = await fetchJob(jobId, signal)
    onUpdate?.(job)

    if (TERMINAL.has(job.status)) {
      return job
    }

    await sleep(intervalMs, signal)
  }
}
