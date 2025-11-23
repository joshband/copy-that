import { describe, it, expect } from 'vitest'
import { z } from 'zod'

// Import schemas (will be implemented after tests)
import {
  ColorTokenSchema,
  ProjectSchema,
  ExtractionResponseSchema,
  parseColorToken,
  parseColorTokens,
  parseExtractionResponse,
} from '../schemas'

describe('ColorTokenSchema', () => {
  it('validates a minimal valid color token', () => {
    const validToken = {
      hex: '#FF5733',
      rgb: 'rgb(255, 87, 51)',
      name: 'Coral Red',
      confidence: 0.95,
    }

    const result = ColorTokenSchema.safeParse(validToken)
    expect(result.success).toBe(true)
    if (result.success) {
      expect(result.data.hex).toBe('#FF5733')
      expect(result.data.name).toBe('Coral Red')
      expect(result.data.confidence).toBe(0.95)
    }
  })

  it('validates a complete color token with all optional fields', () => {
    const completeToken = {
      id: 1,
      project_id: 1,
      hex: '#FF5733',
      rgb: 'rgb(255, 87, 51)',
      hsl: 'hsl(10, 100%, 60%)',
      name: 'Coral Red',
      confidence: 0.95,
      harmony: 'triadic',
      temperature: 'warm',
      saturation_level: 'high',
      lightness_level: 'medium',
      count: 5,
      prominence_percentage: 25.5,
      wcag_contrast_on_white: 3.5,
      wcag_contrast_on_black: 12.1,
      wcag_aa_compliant_text: true,
      wcag_aaa_compliant_text: false,
      colorblind_safe: true,
      tint_color: '#FF8A6B',
      shade_color: '#CC4529',
      tone_color: '#E06B4F',
      closest_web_safe: '#FF6633',
      is_neutral: false,
    }

    const result = ColorTokenSchema.safeParse(completeToken)
    expect(result.success).toBe(true)
  })

  it('rejects token missing required hex field', () => {
    const invalidToken = {
      rgb: 'rgb(255, 87, 51)',
      name: 'Coral Red',
      confidence: 0.95,
    }

    const result = ColorTokenSchema.safeParse(invalidToken)
    expect(result.success).toBe(false)
  })

  it('rejects token missing required name field', () => {
    const invalidToken = {
      hex: '#FF5733',
      rgb: 'rgb(255, 87, 51)',
      confidence: 0.95,
    }

    const result = ColorTokenSchema.safeParse(invalidToken)
    expect(result.success).toBe(false)
  })

  it('rejects token with confidence out of range (> 1)', () => {
    const invalidToken = {
      hex: '#FF5733',
      rgb: 'rgb(255, 87, 51)',
      name: 'Coral Red',
      confidence: 1.5,
    }

    const result = ColorTokenSchema.safeParse(invalidToken)
    expect(result.success).toBe(false)
  })

  it('rejects token with confidence out of range (< 0)', () => {
    const invalidToken = {
      hex: '#FF5733',
      rgb: 'rgb(255, 87, 51)',
      name: 'Coral Red',
      confidence: -0.1,
    }

    const result = ColorTokenSchema.safeParse(invalidToken)
    expect(result.success).toBe(false)
  })

  it('provides default for missing optional rgb field', () => {
    const tokenWithoutRgb = {
      hex: '#FF5733',
      name: 'Coral Red',
      confidence: 0.95,
    }

    const result = ColorTokenSchema.safeParse(tokenWithoutRgb)
    expect(result.success).toBe(true)
    if (result.success) {
      expect(result.data.rgb).toBe('')
    }
  })
})

describe('ProjectSchema', () => {
  it('validates a valid project', () => {
    const validProject = {
      id: 1,
      name: 'My Design Project',
      description: 'Color palette for website',
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-02T00:00:00Z',
    }

    const result = ProjectSchema.safeParse(validProject)
    expect(result.success).toBe(true)
  })

  it('rejects project missing required id', () => {
    const invalidProject = {
      name: 'My Project',
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-02T00:00:00Z',
    }

    const result = ProjectSchema.safeParse(invalidProject)
    expect(result.success).toBe(false)
  })
})

describe('ExtractionResponseSchema', () => {
  it('validates a successful extraction response', () => {
    const validResponse = {
      success: true,
      colors: [
        {
          hex: '#FF5733',
          rgb: 'rgb(255, 87, 51)',
          name: 'Coral Red',
          confidence: 0.95,
        },
        {
          hex: '#33FF57',
          rgb: 'rgb(51, 255, 87)',
          name: 'Neon Green',
          confidence: 0.88,
        },
      ],
      job_id: 'job-123',
    }

    const result = ExtractionResponseSchema.safeParse(validResponse)
    expect(result.success).toBe(true)
    if (result.success) {
      expect(result.data.colors).toHaveLength(2)
    }
  })

  it('validates response with empty colors array', () => {
    const emptyResponse = {
      success: true,
      colors: [],
    }

    const result = ExtractionResponseSchema.safeParse(emptyResponse)
    expect(result.success).toBe(true)
  })

  it('rejects response with invalid color in array', () => {
    const invalidResponse = {
      success: true,
      colors: [
        {
          hex: '#FF5733',
          name: 'Valid',
          confidence: 0.95,
        },
        {
          // Missing required fields
          hex: '#000000',
        },
      ],
    }

    const result = ExtractionResponseSchema.safeParse(invalidResponse)
    expect(result.success).toBe(false)
  })
})

describe('parseColorToken helper', () => {
  it('returns parsed token for valid input', () => {
    const validToken = {
      hex: '#FF5733',
      rgb: 'rgb(255, 87, 51)',
      name: 'Coral Red',
      confidence: 0.95,
    }

    const result = parseColorToken(validToken)
    expect(result.hex).toBe('#FF5733')
  })

  it('throws ZodError for invalid input', () => {
    const invalidToken = { hex: '#FF5733' }
    expect(() => parseColorToken(invalidToken)).toThrow(z.ZodError)
  })
})

describe('parseColorTokens helper', () => {
  it('returns parsed array for valid input', () => {
    const validTokens = [
      { hex: '#FF5733', rgb: 'rgb(255, 87, 51)', name: 'Red', confidence: 0.9 },
      { hex: '#33FF57', rgb: 'rgb(51, 255, 87)', name: 'Green', confidence: 0.8 },
    ]

    const result = parseColorTokens(validTokens)
    expect(result).toHaveLength(2)
  })

  it('returns empty array for undefined input', () => {
    const result = parseColorTokens(undefined)
    expect(result).toEqual([])
  })

  it('returns empty array for null input', () => {
    const result = parseColorTokens(null)
    expect(result).toEqual([])
  })
})

describe('parseExtractionResponse helper', () => {
  it('returns parsed response with valid colors', () => {
    const validResponse = {
      success: true,
      colors: [
        { hex: '#FF5733', rgb: 'rgb(255, 87, 51)', name: 'Red', confidence: 0.9 },
      ],
    }

    const result = parseExtractionResponse(validResponse)
    expect(result.success).toBe(true)
    expect(result.colors).toHaveLength(1)
  })
})
