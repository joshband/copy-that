/**
 * Color Science Hooks - Unit Tests
 *
 * Tests for useColorConversion and useContrastCalculation hooks
 * These are critical hooks for color analysis and accessibility.
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { renderHook } from '@testing-library/react'
import { useColorConversion, useContrastCalculation } from '../hooks'
import { ColorToken } from '../../types'

describe('useColorConversion', () => {
  let hook: ReturnType<typeof renderHook<ReturnType<typeof useColorConversion>, []>>

  beforeEach(() => {
    hook = renderHook(() => useColorConversion())
  })

  describe('hexToRgb', () => {
    it('should convert valid hex to rgb', () => {
      const rgb = hook.result.current.hexToRgb('#FF0000')
      expect(rgb).toBe('rgb(255, 0, 0)')
    })

    it('should convert hex without # prefix', () => {
      const rgb = hook.result.current.hexToRgb('00FF00')
      expect(rgb).toBe('rgb(0, 255, 0)')
    })

    it('should convert lowercase hex', () => {
      const rgb = hook.result.current.hexToRgb('#0000ff')
      expect(rgb).toBe('rgb(0, 0, 255)')
    })

    it('should handle white color', () => {
      const rgb = hook.result.current.hexToRgb('#FFFFFF')
      expect(rgb).toBe('rgb(255, 255, 255)')
    })

    it('should handle black color', () => {
      const rgb = hook.result.current.hexToRgb('#000000')
      expect(rgb).toBe('rgb(0, 0, 0)')
    })

    it('should return empty string for invalid hex', () => {
      expect(hook.result.current.hexToRgb('invalid')).toBe('')
      expect(hook.result.current.hexToRgb('#GG0000')).toBe('')
      expect(hook.result.current.hexToRgb('#12')).toBe('')
    })

    it('should handle various valid formats', () => {
      const testCases = [
        { input: '#FF6B6B', expected: 'rgb(255, 107, 107)' },
        { input: '#4ECDC4', expected: 'rgb(78, 205, 196)' },
        { input: '#95E1D3', expected: 'rgb(149, 225, 211)' },
      ]
      for (const { input, expected } of testCases) {
        expect(hook.result.current.hexToRgb(input)).toBe(expected)
      }
    })
  })

  describe('hexToHsl', () => {
    it('should convert red to hsl', () => {
      const hsl = hook.result.current.hexToHsl('#FF0000')
      expect(hsl).toBe('hsl(0, 100%, 50%)')
    })

    it('should convert green to hsl', () => {
      const hsl = hook.result.current.hexToHsl('#00FF00')
      expect(hsl).toBe('hsl(120, 100%, 50%)')
    })

    it('should convert blue to hsl', () => {
      const hsl = hook.result.current.hexToHsl('#0000FF')
      expect(hsl).toBe('hsl(240, 100%, 50%)')
    })

    it('should convert white to hsl', () => {
      const hsl = hook.result.current.hexToHsl('#FFFFFF')
      expect(hsl).toBe('hsl(0, 0%, 100%)')
    })

    it('should convert black to hsl', () => {
      const hsl = hook.result.current.hexToHsl('#000000')
      expect(hsl).toBe('hsl(0, 0%, 0%)')
    })

    it('should convert gray to hsl', () => {
      const hsl = hook.result.current.hexToHsl('#808080')
      expect(hsl).toBe('hsl(0, 0%, 50%)')
    })

    it('should return empty string for invalid hex', () => {
      expect(hook.result.current.hexToHsl('invalid')).toBe('')
    })

    it('should handle mixed saturation and lightness', () => {
      const hsl = hook.result.current.hexToHsl('#FF6B6B')
      expect(hsl).toMatch(/hsl\(\d+, \d+%, \d+%\)/)
    })
  })

  describe('hexToHsv', () => {
    it('should convert red to hsv', () => {
      const hsv = hook.result.current.hexToHsv('#FF0000')
      expect(hsv).toBe('hsv(0, 100%, 100%)')
    })

    it('should convert green to hsv', () => {
      const hsv = hook.result.current.hexToHsv('#00FF00')
      expect(hsv).toBe('hsv(120, 100%, 100%)')
    })

    it('should convert blue to hsv', () => {
      const hsv = hook.result.current.hexToHsv('#0000FF')
      expect(hsv).toBe('hsv(240, 100%, 100%)')
    })

    it('should convert white to hsv', () => {
      const hsv = hook.result.current.hexToHsv('#FFFFFF')
      expect(hsv).toBe('hsv(0, 0%, 100%)')
    })

    it('should convert black to hsv', () => {
      const hsv = hook.result.current.hexToHsv('#000000')
      expect(hsv).toBe('hsv(0, 0%, 0%)')
    })

    it('should return empty string for invalid hex', () => {
      expect(hook.result.current.hexToHsv('invalid')).toBe('')
    })
  })

  describe('getVibrancy', () => {
    it('should classify vibrant colors', () => {
      const vibrantColor: ColorToken = {
        hex: '#FF0000',
        hsl: 'hsl(0, 100%, 50%)',
      } as ColorToken
      expect(hook.result.current.getVibrancy(vibrantColor)).toBe('vibrant')
    })

    it('should classify muted colors', () => {
      const mutedColor: ColorToken = {
        hex: '#999999',
        hsl: 'hsl(0, 10%, 60%)',
      } as ColorToken
      expect(hook.result.current.getVibrancy(mutedColor)).toBe('muted')
    })

    it('should classify vibrant colors', () => {
      const vibrantColor: ColorToken = {
        hex: '#FF8800',
        hsl: 'hsl(30, 100%, 50%)',
      } as ColorToken
      expect(hook.result.current.getVibrancy(vibrantColor)).toBe('vibrant')
    })

    it('should return balanced for null color', () => {
      expect(hook.result.current.getVibrancy(null)).toBe('balanced')
    })

    it('should handle color without hsl', () => {
      const color: ColorToken = {
        hex: '#FF0000',
      } as ColorToken
      expect(hook.result.current.getVibrancy(color)).toBe('vibrant')
    })

    it('should handle invalid hsl format', () => {
      const color: ColorToken = {
        hex: '#FF0000',
        hsl: 'invalid-hsl',
      } as ColorToken
      expect(hook.result.current.getVibrancy(color)).toBe('balanced')
    })
  })

  describe('copyToClipboard', () => {
    it('should call navigator.clipboard.writeText', () => {
      const mockWriteText = vi.fn().mockResolvedValue(undefined)
      const originalClipboard = navigator.clipboard
      Object.defineProperty(navigator, 'clipboard', {
        value: { writeText: mockWriteText },
        configurable: true,
      })

      hook.result.current.copyToClipboard('test-text')

      expect(mockWriteText).toHaveBeenCalledWith('test-text')

      // Restore
      Object.defineProperty(navigator, 'clipboard', {
        value: originalClipboard,
        configurable: true,
      })
    })
  })
})

describe('useContrastCalculation', () => {
  let hook: ReturnType<typeof renderHook<ReturnType<typeof useContrastCalculation>, []>>

  beforeEach(() => {
    hook = renderHook(() => useContrastCalculation())
  })

  describe('getWCAGCompliance', () => {
    it('should identify WCAG compliance on white', () => {
      const color: ColorToken = {
        hex: '#000000',
        wcag_contrast_on_white: 21,
        wcag_contrast_on_black: 0,
      } as ColorToken

      const compliance = hook.result.current.getWCAGCompliance(color)
      expect(compliance).toEqual({
        hasOnWhiteContrast: true,
        hasOnBlackContrast: true,
        onWhitePasses: true,
        onBlackPasses: false,
      })
    })

    it('should identify WCAG compliance on black', () => {
      const color: ColorToken = {
        hex: '#FFFFFF',
        wcag_contrast_on_white: 0,
        wcag_contrast_on_black: 21,
      } as ColorToken

      const compliance = hook.result.current.getWCAGCompliance(color)
      expect(compliance).toEqual({
        hasOnWhiteContrast: true,
        hasOnBlackContrast: true,
        onWhitePasses: false,
        onBlackPasses: true,
      })
    })

    it('should handle insufficient contrast', () => {
      const color: ColorToken = {
        hex: '#FF8080',
        wcag_contrast_on_white: 2,
        wcag_contrast_on_black: 3,
      } as ColorToken

      const compliance = hook.result.current.getWCAGCompliance(color)
      expect(compliance).toEqual({
        hasOnWhiteContrast: true,
        hasOnBlackContrast: true,
        onWhitePasses: false,
        onBlackPasses: false,
      })
    })

    it('should handle missing contrast values', () => {
      const color: ColorToken = {
        hex: '#FF0000',
      } as ColorToken

      const compliance = hook.result.current.getWCAGCompliance(color)
      expect(compliance).toEqual({
        hasOnWhiteContrast: false,
        hasOnBlackContrast: false,
        onWhitePasses: false,
        onBlackPasses: false,
      })
    })
  })

  describe('getAccessibilityBadges', () => {
    it('should return AA badge for AA compliant text', () => {
      const color: ColorToken = {
        hex: '#000000',
        wcag_aa_compliant_text: true,
      } as ColorToken

      const badges = hook.result.current.getAccessibilityBadges(color)
      expect(badges).toContain('AA')
    })

    it('should return AAA badge for AAA compliant text', () => {
      const color: ColorToken = {
        hex: '#000000',
        wcag_aaa_compliant_text: true,
      } as ColorToken

      const badges = hook.result.current.getAccessibilityBadges(color)
      expect(badges).toContain('AAA')
    })

    it('should return colorblind safe badge', () => {
      const color: ColorToken = {
        hex: '#000000',
        colorblind_safe: true,
      } as ColorToken

      const badges = hook.result.current.getAccessibilityBadges(color)
      expect(badges).toContain('Colorblind Safe')
    })

    it('should return multiple badges', () => {
      const color: ColorToken = {
        hex: '#000000',
        wcag_aa_compliant_text: true,
        wcag_aaa_compliant_text: true,
        colorblind_safe: true,
      } as ColorToken

      const badges = hook.result.current.getAccessibilityBadges(color)
      expect(badges).toEqual(['AA', 'AAA', 'Colorblind Safe'])
    })

    it('should return empty array for no accessibility badges', () => {
      const color: ColorToken = {
        hex: '#000000',
      } as ColorToken

      const badges = hook.result.current.getAccessibilityBadges(color)
      expect(badges).toEqual([])
    })
  })
})
