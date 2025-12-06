import { describe, it, expect } from 'vitest'
import type { StreamEvent, ImageMetadata, ExtractionState } from '../types'

describe('image-uploader types', () => {
  describe('StreamEvent', () => {
    it('should allow error field', () => {
      const event: StreamEvent = { error: 'Test error' }
      expect(event.error).toBe('Test error')
    })

    it('should allow phase and status fields', () => {
      const event: StreamEvent = { phase: 1, status: 'colors_extracted' }
      expect(event.phase).toBe(1)
      expect(event.status).toBe('colors_extracted')
    })

    it('should allow color progress fields', () => {
      const event: StreamEvent = {
        color_count: 10,
        progress: 0.5,
        colors: [
          {
            hex: '#FF0000',
            name: 'Red',
            confidence: 0.95,
            rgb: 'rgb(255, 0, 0)',
          },
        ],
      }
      expect(event.color_count).toBe(10)
      expect(event.progress).toBe(0.5)
      expect(event.colors).toHaveLength(1)
    })
  })

  describe('ImageMetadata', () => {
    it('should hold image file information', () => {
      const file = new File(['test'], 'test.jpg', { type: 'image/jpeg' })
      const metadata: ImageMetadata = {
        file,
        preview: 'data:image/jpeg;base64,...',
        base64: 'base64data',
        mediaType: 'image/jpeg',
      }
      expect(metadata.file).toBe(file)
      expect(metadata.preview).toContain('data:image')
      expect(metadata.mediaType).toBe('image/jpeg')
    })

    it('should allow null file and preview', () => {
      const metadata: ImageMetadata = {
        file: null,
        preview: null,
        base64: null,
        mediaType: 'image/jpeg',
      }
      expect(metadata.file).toBeNull()
      expect(metadata.preview).toBeNull()
    })
  })

  describe('ExtractionState', () => {
    it('should hold extraction results', () => {
      const state: ExtractionState = {
        colors: [
          {
            hex: '#FF0000',
            name: 'Red',
            confidence: 0.95,
            rgb: 'rgb(255, 0, 0)',
          },
        ],
        shadows: [{ id: 1, blur: 2, color: '#000000' }],
        backgrounds: ['#FFFFFF'],
        ramps: { primary: ['#FF0000', '#FF6666'] },
        debugOverlay: null,
        segmentation: null,
      }
      expect(state.colors).toHaveLength(1)
      expect(state.shadows).toHaveLength(1)
      expect(state.backgrounds).toHaveLength(1)
      expect(Object.keys(state.ramps)).toContain('primary')
    })

    it('should allow empty arrays and null values', () => {
      const state: ExtractionState = {
        colors: [],
        shadows: [],
        backgrounds: [],
        ramps: {},
        debugOverlay: null,
        segmentation: null,
      }
      expect(state.colors).toHaveLength(0)
      expect(Object.keys(state.ramps)).toHaveLength(0)
    })
  })
})
