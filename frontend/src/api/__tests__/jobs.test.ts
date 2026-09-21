import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { pollJobUntilDone } from '../jobs'

describe('pollJobUntilDone', () => {
  const fetchMock = vi.fn()

  beforeEach(() => {
    fetchMock.mockReset()
    vi.stubGlobal('fetch', fetchMock)
  })

  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it('polls until completed and returns the terminal job', async () => {
    fetchMock
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          job_id: 1,
          status: 'running',
          progress: 0.2,
          message: 'generating_themes',
          result: null,
        }),
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          job_id: 1,
          status: 'completed',
          progress: 1,
          message: 'completed',
          result: { variants: [] },
        }),
      })

    const updates: string[] = []
    const job = await pollJobUntilDone(1, {
      intervalMs: 1,
      onUpdate: j => updates.push(j.status),
    })

    expect(job.status).toBe('completed')
    expect(updates).toEqual(['running', 'completed'])
    expect(fetchMock).toHaveBeenCalledTimes(2)
  })

  it('stops on failed without throwing', async () => {
    fetchMock.mockResolvedValue({
      ok: true,
      json: async () => ({
        job_id: 2,
        status: 'failed',
        progress: 0.1,
        error: 'boom',
        result: null,
      }),
    })

    const job = await pollJobUntilDone(2, { intervalMs: 1 })
    expect(job.status).toBe('failed')
    expect(job.error).toBe('boom')
  })

  it('throws JobPollTimeoutError when maxWaitMs elapses', async () => {
    fetchMock.mockResolvedValue({
      ok: true,
      json: async () => ({
        job_id: 3,
        status: 'running',
        progress: 0.2,
        message: 'rendering_images',
        result: null,
      }),
    })

    const { JobPollTimeoutError } = await import('../jobs')
    await expect(
      pollJobUntilDone(3, { intervalMs: 5, maxWaitMs: 20 })
    ).rejects.toBeInstanceOf(JobPollTimeoutError)
  })
})
