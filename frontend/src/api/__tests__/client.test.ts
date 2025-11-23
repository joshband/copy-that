import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { ApiClient } from '../client'

// Mock fetch globally
const mockFetch = vi.fn()
;(globalThis as unknown as { fetch: typeof mockFetch }).fetch = mockFetch

describe('ApiClient', () => {
  beforeEach(() => {
    mockFetch.mockReset()
  })

  afterEach(() => {
    vi.clearAllMocks()
  })

  describe('request', () => {
    it('makes GET request and returns parsed data', async () => {
      const mockData = { id: 1, name: 'Test' }
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockData),
      })

      const result = await ApiClient.get('/test')
      expect(result).toEqual(mockData)
      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/test'),
        expect.objectContaining({ method: 'GET' })
      )
    })

    it('makes POST request with JSON body', async () => {
      const mockData = { success: true }
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockData),
      })

      const body = { name: 'Test Project' }
      await ApiClient.post('/projects', body)

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/projects'),
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify(body),
        })
      )
    })

    it('throws ApiError on non-ok response', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 404,
        statusText: 'Not Found',
        json: () => Promise.resolve({ detail: 'Resource not found' }),
      })

      await expect(ApiClient.get('/nonexistent')).rejects.toEqual({
        detail: 'Resource not found',
      })
    })

    it('handles network errors gracefully', async () => {
      mockFetch.mockRejectedValueOnce(new Error('Network error'))

      await expect(ApiClient.get('/test')).rejects.toThrow('Network error')
    })
  })

  describe('getColors with validation', () => {
    it('returns validated color tokens from API', async () => {
      const validColors = [
        {
          hex: '#FF5733',
          rgb: 'rgb(255, 87, 51)',
          name: 'Coral Red',
          confidence: 0.95,
        },
      ]

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(validColors),
      })

      const result = await ApiClient.getColors(1)
      expect(result).toHaveLength(1)
      expect(result[0].hex).toBe('#FF5733')
    })

    it('throws validation error for invalid color data', async () => {
      const invalidColors = [
        {
          hex: '#FF5733',
          // Missing required 'name' and 'confidence'
        },
      ]

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(invalidColors),
      })

      await expect(ApiClient.getColors(1)).rejects.toThrow()
    })

    it('returns empty array when API returns empty', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve([]),
      })

      const result = await ApiClient.getColors(1)
      expect(result).toEqual([])
    })
  })

  describe('createProject with validation', () => {
    it('returns validated project from API', async () => {
      const validProject = {
        id: 1,
        name: 'Test Project',
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      }

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(validProject),
      })

      const result = await ApiClient.createProject('Test Project', 'Description')
      expect(result.id).toBe(1)
      expect(result.name).toBe('Test Project')
    })
  })

  describe('extractColors with validation', () => {
    it('returns validated extraction response', async () => {
      const validResponse = {
        success: true,
        colors: [
          {
            hex: '#FF5733',
            rgb: 'rgb(255, 87, 51)',
            name: 'Coral Red',
            confidence: 0.95,
          },
        ],
        job_id: 'job-123',
      }

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(validResponse),
      })

      const result = await ApiClient.extractColors(1, 'base64data', 10)
      expect(result.success).toBe(true)
      expect(result.colors).toHaveLength(1)
    })

    it('validates color tokens in extraction response', async () => {
      const invalidResponse = {
        success: true,
        colors: [
          {
            hex: '#FF5733',
            // Invalid: confidence out of range
            name: 'Bad Color',
            confidence: 1.5,
          },
        ],
      }

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(invalidResponse),
      })

      await expect(ApiClient.extractColors(1, 'base64data', 10)).rejects.toThrow()
    })
  })
})
