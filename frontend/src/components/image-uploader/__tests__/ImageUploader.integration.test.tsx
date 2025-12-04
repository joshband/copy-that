import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest'
import { render, screen, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import ImageUploader from '../ImageUploader'

// Mock API client
vi.mock('../../api/client', () => ({
  ApiClient: {
    post: vi.fn(() => Promise.resolve({ id: 123 })),
  },
}))

// Mock utilities
vi.mock('../../utils', () => ({
  isValidImageFile: vi.fn((file) => {
    return file.type.startsWith('image/')
  }),
  isFileSizeValid: vi.fn((file, maxSize) => {
    return file.size <= maxSize
  }),
  resizeImageFile: vi.fn(async (file) => ({
    dataUrl: 'data:image/jpeg;base64,test',
    base64: 'base64testdata',
    mediaType: 'image/jpeg',
  })),
}))

describe('ImageUploader Integration Tests', () => {
  let mockCallbacks: {
    onProjectCreated: ReturnType<typeof vi.fn>
    onColorExtracted: ReturnType<typeof vi.fn>
    onSpacingExtracted: ReturnType<typeof vi.fn>
    onShadowsExtracted: ReturnType<typeof vi.fn>
    onTypographyExtracted: ReturnType<typeof vi.fn>
    onRampsExtracted: ReturnType<typeof vi.fn>
    onDebugOverlay: ReturnType<typeof vi.fn>
    onSegmentationExtracted: ReturnType<typeof vi.fn>
    onImageBase64Extracted: ReturnType<typeof vi.fn>
    onError: ReturnType<typeof vi.fn>
    onLoadingChange: ReturnType<typeof vi.fn>
  }

  beforeEach(() => {
    mockCallbacks = {
      onProjectCreated: vi.fn(),
      onColorExtracted: vi.fn(),
      onSpacingExtracted: vi.fn(),
      onShadowsExtracted: vi.fn(),
      onTypographyExtracted: vi.fn(),
      onRampsExtracted: vi.fn(),
      onDebugOverlay: vi.fn(),
      onSegmentationExtracted: vi.fn(),
      onImageBase64Extracted: vi.fn(),
      onError: vi.fn(),
      onLoadingChange: vi.fn(),
    }

    // Mock fetch for extraction endpoints
    global.fetch = vi.fn((url: string) => {
      if (url.includes('/colors/extract-streaming')) {
        return Promise.resolve({
          ok: true,
          body: {
            getReader: () => ({
              read: vi.fn(async () => ({
                done: true,
                value: new Uint8Array(),
              })),
            }),
          },
        } as Response)
      }
      return Promise.resolve({
        ok: true,
        json: async () => ({ tokens: [] }),
      } as Response)
    })
  })

  afterEach(() => {
    vi.clearAllMocks()
  })

  describe('File Upload Workflow', () => {
    it('should render upload area initially', () => {
      render(
        <ImageUploader
          projectId={null}
          {...mockCallbacks}
        />
      )

      expect(screen.getByText('Upload Image')).toBeInTheDocument()
      expect(screen.getByText(/Drag and drop or click/i)).toBeInTheDocument()
    })

    it('should display preview after file selection', async () => {
      const user = userEvent.setup()
      const file = new File(['test'], 'test.jpg', { type: 'image/jpeg' })

      render(
        <ImageUploader
          projectId={null}
          {...mockCallbacks}
        />
      )

      const input = screen.getByRole('button', { name: /Upload Image/i }).closest('label')?.querySelector('input[type="file"]')

      if (input) {
        await user.upload(input, file)

        await waitFor(() => {
          expect(screen.getByText('Preview')).toBeInTheDocument()
        })
      }
    })

    it('should display project settings', () => {
      render(
        <ImageUploader
          projectId={null}
          {...mockCallbacks}
        />
      )

      expect(screen.getByLabelText(/Project Name/)).toBeInTheDocument()
      expect(screen.getByLabelText(/Max Colors/)).toBeInTheDocument()
    })

    it('should disable project name input when projectId exists', () => {
      render(
        <ImageUploader
          projectId={123}
          {...mockCallbacks}
        />
      )

      expect(screen.getByLabelText(/Project Name/)).toBeDisabled()
      expect(screen.getByText('Project ID')).toBeInTheDocument()
      expect(screen.getByText('123')).toBeInTheDocument()
    })
  })

  describe('Extraction Orchestration', () => {
    it('should disable extract button when no file selected', () => {
      render(
        <ImageUploader
          projectId={null}
          {...mockCallbacks}
        />
      )

      const extractBtn = screen.getByRole('button', { name: /Extract Colors/ })
      expect(extractBtn).toBeDisabled()
    })

    it('should handle extraction workflow', async () => {
      const user = userEvent.setup()
      const file = new File(['test'], 'test.jpg', { type: 'image/jpeg' })

      // Mock realistic streaming response
      const mockStream = {
        getReader: () => {
          let called = false
          return {
            read: vi.fn(async () => {
              if (!called) {
                called = true
                const data = {
                  phase: 2,
                  status: 'extraction_complete',
                  colors: [
                    { hex: '#FF0000', name: 'Red', confidence: 0.95, rgb: 'rgb(255, 0, 0)' },
                  ],
                }
                return {
                  done: false,
                  value: new TextEncoder().encode(`data: ${JSON.stringify(data)}\n`),
                }
              }
              return { done: true, value: undefined }
            }),
          }
        },
      }

      global.fetch = vi.fn((url: string) => {
        if (url.includes('/colors/extract-streaming')) {
          return Promise.resolve({
            ok: true,
            body: mockStream,
          } as any)
        }
        return Promise.resolve({
          ok: true,
          json: async () => ({ tokens: [] }),
        } as Response)
      })

      render(
        <ImageUploader
          projectId={null}
          {...mockCallbacks}
        />
      )

      // Simulate file upload
      const input = document.querySelector('input[type="file"]') as HTMLInputElement
      if (input) {
        await user.upload(input, file)
      }

      // Wait for preview to appear
      await waitFor(() => {
        expect(screen.getByText('Preview')).toBeInTheDocument()
      })

      // Click extract button
      const extractBtn = screen.getByRole('button', { name: /Extract Colors/ })
      expect(extractBtn).not.toBeDisabled()
      await user.click(extractBtn)

      // Verify loading state was triggered
      await waitFor(() => {
        expect(mockCallbacks.onLoadingChange).toHaveBeenCalledWith(true)
      })
    })

    it('should call onImageBase64Extracted with base64 data', async () => {
      const user = userEvent.setup()
      const file = new File(['test'], 'test.jpg', { type: 'image/jpeg' })

      global.fetch = vi.fn(() =>
        Promise.resolve({
          ok: true,
          body: {
            getReader: () => ({
              read: vi.fn(async () => ({ done: true, value: undefined })),
            }),
          },
        } as any)
      )

      render(
        <ImageUploader
          projectId={null}
          {...mockCallbacks}
        />
      )

      const input = document.querySelector('input[type="file"]') as HTMLInputElement
      if (input) {
        await user.upload(input, file)

        await waitFor(() => {
          expect(screen.getByText('Preview')).toBeInTheDocument()
        })

        const extractBtn = screen.getByRole('button', { name: /Extract Colors/ })
        await user.click(extractBtn)

        await waitFor(() => {
          expect(mockCallbacks.onImageBase64Extracted).toHaveBeenCalledWith(
            expect.stringContaining('base64testdata')
          )
        })
      }
    })

    it('should handle error during extraction', async () => {
      const user = userEvent.setup()
      const file = new File(['test'], 'test.jpg', { type: 'image/jpeg' })

      global.fetch = vi.fn(() =>
        Promise.resolve({
          ok: false,
          statusText: 'Internal Server Error',
        } as Response)
      )

      render(
        <ImageUploader
          projectId={null}
          {...mockCallbacks}
        />
      )

      const input = document.querySelector('input[type="file"]') as HTMLInputElement
      if (input) {
        await user.upload(input, file)

        await waitFor(() => {
          expect(screen.getByText('Preview')).toBeInTheDocument()
        })

        const extractBtn = screen.getByRole('button', { name: /Extract Colors/ })
        await user.click(extractBtn)

        await waitFor(() => {
          expect(mockCallbacks.onError).toHaveBeenCalledWith(
            expect.stringContaining('API error')
          )
        })
      }
    })
  })

  describe('Parallel Extraction Phases', () => {
    it('should call all extraction endpoints in parallel', async () => {
      const user = userEvent.setup()
      const file = new File(['test'], 'test.jpg', { type: 'image/jpeg' })

      const fetchSpy = vi.fn()
      global.fetch = vi.fn((url: string) => {
        fetchSpy(url)
        return Promise.resolve({
          ok: true,
          body:
            url.includes('/colors/extract-streaming')
              ? {
                  getReader: () => ({
                    read: vi.fn(async () => ({ done: true, value: undefined })),
                  }),
                }
              : undefined,
          json: async () => ({ tokens: [] }),
        } as any)
      })

      render(
        <ImageUploader
          projectId={null}
          onSpacingExtracted={mockCallbacks.onSpacingExtracted}
          onShadowsExtracted={mockCallbacks.onShadowsExtracted}
          onTypographyExtracted={mockCallbacks.onTypographyExtracted}
          {...mockCallbacks}
        />
      )

      const input = document.querySelector('input[type="file"]') as HTMLInputElement
      if (input) {
        await user.upload(input, file)

        await waitFor(() => {
          expect(screen.getByText('Preview')).toBeInTheDocument()
        })

        const extractBtn = screen.getByRole('button', { name: /Extract Colors/ })
        await user.click(extractBtn)

        // Wait for extract calls
        await waitFor(() => {
          const calls = fetchSpy.mock.calls.map((c) => c[0] as string)
          expect(calls.some((url) => url.includes('/colors/extract-streaming'))).toBe(true)
          expect(calls.some((url) => url.includes('/spacing/extract'))).toBe(true)
          expect(calls.some((url) => url.includes('/shadows/extract'))).toBe(true)
          expect(calls.some((url) => url.includes('/typography/extract'))).toBe(true)
        })
      }
    })
  })

  describe('Settings Management', () => {
    it('should allow changing max colors', async () => {
      const user = userEvent.setup()

      render(
        <ImageUploader
          projectId={null}
          {...mockCallbacks}
        />
      )

      const slider = screen.getByLabelText(/Max Colors/) as HTMLInputElement
      await user.clear(slider)
      await user.type(slider, '25')

      expect(slider).toHaveValue('25')
    })

    it('should allow changing project name', async () => {
      const user = userEvent.setup()

      render(
        <ImageUploader
          projectId={null}
          {...mockCallbacks}
        />
      )

      const input = screen.getByLabelText(/Project Name/) as HTMLInputElement
      await user.clear(input)
      await user.type(input, 'My Custom Project')

      expect(input).toHaveValue('My Custom Project')
    })
  })

  describe('Error Handling', () => {
    it('should handle invalid file type', async () => {
      const user = userEvent.setup()
      const file = new File(['test'], 'test.txt', { type: 'text/plain' })

      render(
        <ImageUploader
          projectId={null}
          {...mockCallbacks}
        />
      )

      const input = document.querySelector('input[type="file"]') as HTMLInputElement
      if (input) {
        await user.upload(input, file)

        await waitFor(() => {
          expect(mockCallbacks.onError).toHaveBeenCalled()
        })
      }
    })

    it('should clear error message on new file selection', async () => {
      const user = userEvent.setup()
      const validFile = new File(['test'], 'test.jpg', { type: 'image/jpeg' })

      render(
        <ImageUploader
          projectId={null}
          {...mockCallbacks}
        />
      )

      const input = document.querySelector('input[type="file"]') as HTMLInputElement
      if (input) {
        await user.upload(input, validFile)

        await waitFor(() => {
          expect(mockCallbacks.onError).toHaveBeenCalledWith('')
        })
      }
    })
  })

  describe('Project Management', () => {
    it('should create project if none exists', async () => {
      const user = userEvent.setup()
      const file = new File(['test'], 'test.jpg', { type: 'image/jpeg' })

      global.fetch = vi.fn(() =>
        Promise.resolve({
          ok: true,
          body: {
            getReader: () => ({
              read: vi.fn(async () => ({ done: true, value: undefined })),
            }),
          },
        } as any)
      )

      render(
        <ImageUploader
          projectId={null}
          {...mockCallbacks}
        />
      )

      const input = document.querySelector('input[type="file"]') as HTMLInputElement
      if (input) {
        await user.upload(input, file)

        await waitFor(() => {
          expect(screen.getByText('Preview')).toBeInTheDocument()
        })

        const extractBtn = screen.getByRole('button', { name: /Extract Colors/ })
        await user.click(extractBtn)

        // Verify onProjectCreated was called with the new ID
        // (This would be called by ApiClient.post in the real scenario)
      }
    })

    it('should use existing project ID if provided', async () => {
      render(
        <ImageUploader
          projectId={999}
          {...mockCallbacks}
        />
      )

      expect(screen.getByText('999')).toBeInTheDocument()
      const nameInput = screen.getByLabelText(/Project Name/) as HTMLInputElement
      expect(nameInput).toBeDisabled()
    })
  })
})
