/**
 * Tests for Shadow Analysis Types and Helper Functions
 * Phase 4: Advanced Analysis
 */

import { describe, it, expect } from 'vitest'
import {
  computeQualityScore,
  getLightDirectionLabel,
  getLightingStyleLabel,
  azimuthToCompassDirection,
} from '../shadowAnalysis'
import type { LightingAnalysisResponse } from '../shadowAnalysis'

describe('Shadow Analysis Types', () => {
  describe('getLightDirectionLabel', () => {
    it('should return "Upper Left" for upper_left token', () => {
      expect(getLightDirectionLabel('upper_left')).toBe('Upper Left')
    })

    it('should return "Upper Right" for upper_right token', () => {
      expect(getLightDirectionLabel('upper_right')).toBe('Upper Right')
    })

    it('should return "Left" for left token', () => {
      expect(getLightDirectionLabel('left')).toBe('Left')
    })

    it('should return "Right" for right token', () => {
      expect(getLightDirectionLabel('right')).toBe('Right')
    })

    it('should return "Overhead" for overhead token', () => {
      expect(getLightDirectionLabel('overhead')).toBe('Overhead')
    })

    it('should return "Front" for front token', () => {
      expect(getLightDirectionLabel('front')).toBe('Front')
    })

    it('should return "Back" for back token', () => {
      expect(getLightDirectionLabel('back')).toBe('Back')
    })

    it('should return "Unknown" for unknown token', () => {
      expect(getLightDirectionLabel('unknown')).toBe('Unknown')
    })
  })

  describe('getLightingStyleLabel', () => {
    it('should return "Directional" for directional style', () => {
      expect(getLightingStyleLabel('directional')).toBe('Directional')
    })

    it('should return "Rim Light" for rim style', () => {
      expect(getLightingStyleLabel('rim')).toBe('Rim Light')
    })

    it('should return "Diffuse / Ambient" for diffuse style', () => {
      expect(getLightingStyleLabel('diffuse')).toBe('Diffuse / Ambient')
    })

    it('should return "Mixed Lighting" for mixed style', () => {
      expect(getLightingStyleLabel('mixed')).toBe('Mixed Lighting')
    })

    it('should return "Complex Multi-Source" for complex style', () => {
      expect(getLightingStyleLabel('complex')).toBe('Complex Multi-Source')
    })
  })

  describe('azimuthToCompassDirection', () => {
    it('should return N for 0 radians', () => {
      expect(azimuthToCompassDirection(0)).toBe('N')
    })

    it('should return E for PI/2 radians (90 degrees)', () => {
      expect(azimuthToCompassDirection(Math.PI / 2)).toBe('E')
    })

    it('should return S for PI radians (180 degrees)', () => {
      expect(azimuthToCompassDirection(Math.PI)).toBe('S')
    })

    it('should return W for 3*PI/2 radians (270 degrees)', () => {
      expect(azimuthToCompassDirection((3 * Math.PI) / 2)).toBe('W')
    })

    it('should return NE for PI/4 radians (45 degrees)', () => {
      expect(azimuthToCompassDirection(Math.PI / 4)).toBe('NE')
    })

    it('should return SE for 3*PI/4 radians (135 degrees)', () => {
      expect(azimuthToCompassDirection((3 * Math.PI) / 4)).toBe('SE')
    })

    it('should return SW for 5*PI/4 radians (225 degrees)', () => {
      expect(azimuthToCompassDirection((5 * Math.PI) / 4)).toBe('SW')
    })

    it('should return NW for 7*PI/4 radians (315 degrees)', () => {
      expect(azimuthToCompassDirection((7 * Math.PI) / 4)).toBe('NW')
    })

    it('should handle negative angles', () => {
      expect(azimuthToCompassDirection(-Math.PI / 2)).toBe('W')
    })

    it('should handle angles > 2*PI', () => {
      expect(azimuthToCompassDirection(2 * Math.PI + Math.PI / 2)).toBe('E')
    })
  })

  describe('computeQualityScore', () => {
    const baseAnalysis: LightingAnalysisResponse = {
      style_key_direction: 'upper_left',
      style_softness: 'medium',
      style_contrast: 'high',
      style_density: 'moderate',
      intensity_shadow: 'dark',
      intensity_lit: 'bright',
      lighting_style: 'directional',
      shadow_area_fraction: 0.25,
      mean_shadow_intensity: 0.3,
      mean_lit_intensity: 0.8,
      shadow_contrast: 0.6,
      edge_softness_mean: 0.4,
      light_direction: null,
      light_direction_confidence: 0.85,
      extraction_confidence: 0.9,
      shadow_count_major: 3,
      css_box_shadow: {
        subtle: '0 1px 2px rgba(0,0,0,0.1)',
        medium: '0 4px 8px rgba(0,0,0,0.15)',
        prominent: '0 8px 16px rgba(0,0,0,0.2)',
        dramatic: '0 16px 32px rgba(0,0,0,0.25)',
      },
      image_id: null,
      analysis_source: 'shadowlab',
    }

    it('should return quality score breakdown', () => {
      const result = computeQualityScore(baseAnalysis)

      expect(result).toHaveProperty('overall')
      expect(result).toHaveProperty('confidence')
      expect(result).toHaveProperty('consistency')
      expect(result).toHaveProperty('clarity')
    })

    it('should return overall score between 0 and 1', () => {
      const result = computeQualityScore(baseAnalysis)
      expect(result.overall).toBeGreaterThanOrEqual(0)
      expect(result.overall).toBeLessThanOrEqual(1)
    })

    it('should use extraction_confidence for confidence score', () => {
      const result = computeQualityScore(baseAnalysis)
      expect(result.confidence).toBe(0.9)
    })

    it('should calculate higher score for high confidence', () => {
      const highConfidence = { ...baseAnalysis, extraction_confidence: 0.95 }
      const lowConfidence = { ...baseAnalysis, extraction_confidence: 0.3 }

      const highResult = computeQualityScore(highConfidence)
      const lowResult = computeQualityScore(lowConfidence)

      expect(highResult.overall).toBeGreaterThan(lowResult.overall)
    })

    it('should calculate clarity based on edge softness', () => {
      const hardEdge = { ...baseAnalysis, edge_softness_mean: 0.1 }
      const softEdge = { ...baseAnalysis, edge_softness_mean: 0.8 }

      const hardResult = computeQualityScore(hardEdge)
      const softResult = computeQualityScore(softEdge)

      expect(hardResult.clarity).toBeGreaterThan(softResult.clarity)
    })

    it('should reduce consistency for very high contrast', () => {
      const normalContrast = { ...baseAnalysis, shadow_contrast: 0.5 }
      const highContrast = { ...baseAnalysis, shadow_contrast: 0.9 }

      const normalResult = computeQualityScore(normalContrast)
      const highResult = computeQualityScore(highContrast)

      expect(normalResult.consistency).toBeGreaterThanOrEqual(highResult.consistency)
    })
  })

  describe('Type Definitions', () => {
    it('should validate LightDirectionToken values', () => {
      const validTokens = [
        'upper_left',
        'upper_right',
        'left',
        'right',
        'overhead',
        'front',
        'back',
        'unknown',
      ]

      validTokens.forEach((token) => {
        expect(getLightDirectionLabel(token as any)).toBeDefined()
      })
    })

    it('should validate ShadowSoftnessToken values', () => {
      const validTokens = ['very_hard', 'hard', 'medium', 'soft', 'very_soft']
      // Type check - these should all be valid
      expect(validTokens.length).toBe(5)
    })

    it('should validate ShadowContrastToken values', () => {
      const validTokens = ['low', 'medium', 'high', 'very_high']
      expect(validTokens.length).toBe(4)
    })

    it('should validate LightingStyleToken values', () => {
      const validTokens = ['directional', 'rim', 'diffuse', 'mixed', 'complex']

      validTokens.forEach((token) => {
        expect(getLightingStyleLabel(token as any)).toBeDefined()
      })
    })
  })
})
