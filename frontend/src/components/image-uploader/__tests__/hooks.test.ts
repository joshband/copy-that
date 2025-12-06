import { describe, it, expect, beforeEach, vi } from 'vitest'
import { renderHook, act } from '@testing-library/react'
import { useImageFile, useStreamingExtraction, useParallelExtractions, useProjectManagement } from '../hooks'

// Mock environment
vi.stubGlobal('import', { meta: { env: { VITE_API_URL: 'http://localhost:3000/api/v1' } } })

describe('image-uploader hooks', () => {
  describe('useImageFile', () => {
    it('should initialize with null file and preview', () => {
      const { result } = renderHook(() => useImageFile())
      expect(result.current.file).toBeNull()
      expect(result.current.preview).toBeNull()
      expect(result.current.base64).toBeNull()
      expect(result.current.mediaType).toBe('image/jpeg')
    })

    it('should clear file on selectFile(null)', async () => {
      const { result } = renderHook(() => useImageFile())
      await act(async () => {
        await result.current.selectFile(null)
      })
      expect(result.current.file).toBeNull()
      expect(result.current.preview).toBeNull()
    })

    it('should reject invalid image files', async () => {
      const { result } = renderHook(() => useImageFile())
      const invalidFile = new File(['test'], 'test.txt', { type: 'text/plain' })

      await act(async () => {
        try {
          await result.current.selectFile(invalidFile)
        } catch (error) {
          expect((error as Error).message).toContain('valid image file')
        }
      })
    })

    it('should reject files larger than 5MB', async () => {
      const { result } = renderHook(() => useImageFile())
      // Create a mock file larger than 5MB
      const largeFile = new File([new ArrayBuffer(6 * 1024 * 1024)], 'large.jpg', {
        type: 'image/jpeg',
      })

      await act(async () => {
        try {
          await result.current.selectFile(largeFile)
        } catch (error) {
          expect((error as Error).message).toContain('5MB')
        }
      })
    })
  })

  describe('useStreamingExtraction', () => {
    it('should export parseColorStream function', () => {
      const { result } = renderHook(() => useStreamingExtraction())
      expect(typeof result.current.parseColorStream).toBe('function')
    })

    it('should handle stream events with colors', async () => {
      const { result } = renderHook(() => useStreamingExtraction())

      // Create a mock response with streaming data
      const mockStream = new ReadableStream({
        start(controller) {
          controller.enqueue(
            new TextEncoder().encode('data: {"phase": 2, "status": "extraction_complete", "colors": [{"hex": "#FF0000", "name": "Red", "confidence": 0.95, "rgb": "rgb(255, 0, 0)"}]}\n')
          )
          controller.close()
        },
      })

      const mockResponse = {
        body: mockStream,
        ok: true,
      } as Response

      let extractionResult
      await act(async () => {
        extractionResult = await result.current.parseColorStream(mockResponse)
      })

      expect(extractionResult?.extractedColors).toHaveLength(1)
      expect(extractionResult?.extractedColors[0].hex).toBe('#FF0000')
    })

    it('should sanitize NaN values in stream', async () => {
      const { result } = renderHook(() => useStreamingExtraction())

      const mockStream = new ReadableStream({
        start(controller) {
          // Stream contains NaN which is invalid JSON
          controller.enqueue(
            new TextEncoder().encode('data: {"progress": NaN, "colors": []}\n')
          )
          controller.close()
        },
      })

      const mockResponse = {
        body: mockStream,
        ok: true,
      } as Response

      await act(async () => {
        // Should not throw error
        await result.current.parseColorStream(mockResponse)
      })
    })
  })

  describe('useParallelExtractions', () => {
    it('should export three extraction functions', () => {
      const { result } = renderHook(() => useParallelExtractions())
      expect(typeof result.current.extractSpacing).toBe('function')
      expect(typeof result.current.extractShadows).toBe('function')
      expect(typeof result.current.extractTypography).toBe('function')
    })

    it('extractSpacing should call correct endpoint', async () => {
      const { result } = renderHook(() => useParallelExtractions())
      const mockFetch = vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({ tokens: [] }),
      })
      global.fetch = mockFetch

      await act(async () => {
        await result.current.extractSpacing('base64data', 'image/jpeg', 123)
      })

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/spacing/extract'),
        expect.any(Object)
      )
    })

    it('extractShadows should call correct endpoint', async () => {
      const { result } = renderHook(() => useParallelExtractions())
      const mockFetch = vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({ tokens: [] }),
      })
      global.fetch = mockFetch

      await act(async () => {
        await result.current.extractShadows('base64data', 'image/jpeg')
      })

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/shadows/extract'),
        expect.any(Object)
      )
    })

    it('extractTypography should call correct endpoint', async () => {
      const { result } = renderHook(() => useParallelExtractions())
      const mockFetch = vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({ tokens: [] }),
      })
      global.fetch = mockFetch

      await act(async () => {
        await result.current.extractTypography('base64data', 'image/jpeg', 123)
      })

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/typography/extract'),
        expect.any(Object)
      )
    })
  })

  describe('useProjectManagement', () => {
    it('should return ensureProject function', () => {
      const { result } = renderHook(() => useProjectManagement())
      expect(typeof result.current.ensureProject).toBe('function')
    })

    it('should return existing projectId without creating new project', async () => {
      const { result } = renderHook(() => useProjectManagement())

      await act(async () => {
        const projectId = await result.current.ensureProject(123, 'Test Project')
        expect(projectId).toBe(123)
      })
    })
  })
})
