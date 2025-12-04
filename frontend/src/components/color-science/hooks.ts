import { ColorToken } from './types'

export function useColorConversion() {
  // Convert HEX to RGB
  const hexToRgb = (hex: string): string => {
    const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex)
    if (!result) return ''
    const r = parseInt(result[1], 16)
    const g = parseInt(result[2], 16)
    const b = parseInt(result[3], 16)
    return `rgb(${r}, ${g}, ${b})`
  }

  // Convert HEX to HSL
  const hexToHsl = (hex: string): string => {
    const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex)
    if (!result) return ''
    let r = parseInt(result[1], 16) / 255
    let g = parseInt(result[2], 16) / 255
    let b = parseInt(result[3], 16) / 255

    const max = Math.max(r, g, b)
    const min = Math.min(r, g, b)
    let h = 0
    let s = 0
    const l = (max + min) / 2

    if (max !== min) {
      const d = max - min
      s = l > 0.5 ? d / (2 - max - min) : d / (max + min)

      switch (max) {
        case r:
          h = ((g - b) / d + (g < b ? 6 : 0)) / 6
          break
        case g:
          h = ((b - r) / d + 2) / 6
          break
        case b:
          h = ((r - g) / d + 4) / 6
          break
      }
    }

    return `hsl(${Math.round(h * 360)}, ${Math.round(s * 100)}%, ${Math.round(l * 100)}%)`
  }

  // Convert HEX to HSV
  const hexToHsv = (hex: string): string => {
    const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex)
    if (!result) return ''
    let r = parseInt(result[1], 16) / 255
    let g = parseInt(result[2], 16) / 255
    let b = parseInt(result[3], 16) / 255

    const max = Math.max(r, g, b)
    const min = Math.min(r, g, b)
    const d = max - min
    let h = 0
    const s = max === 0 ? 0 : d / max
    const v = max

    if (max !== min) {
      switch (max) {
        case r:
          h = ((g - b) / d + (g < b ? 6 : 0)) / 6
          break
        case g:
          h = ((b - r) / d + 2) / 6
          break
        case b:
          h = ((r - g) / d + 4) / 6
          break
      }
    }

    return `hsv(${Math.round(h * 360)}, ${Math.round(s * 100)}%, ${Math.round(v * 100)}%)`
  }

  const getVibrancy = (color: ColorToken | null) => {
    const hslValue = color?.hsl || (color?.hex ? hexToHsl(color.hex) : '')
    if (!hslValue) return 'balanced'
    const match = hslValue.match(/hsl\(([^,]+),\s*([^%]+)%?,\s*([^%]+)%?\)/i)
    if (!match) return 'balanced'
    const saturation = parseFloat(match[2]) / 100
    const lightness = parseFloat(match[3]) / 100
    if (saturation >= 0.65 && lightness >= 0.45 && lightness <= 0.75) return 'vibrant'
    if (saturation <= 0.25) return 'muted'
    return 'balanced'
  }

  const copyToClipboard = (text: string) => {
    void navigator.clipboard.writeText(text)
  }

  return { getVibrancy, copyToClipboard, hexToRgb, hexToHsl, hexToHsv }
}

export function useContrastCalculation() {
  const getWCAGCompliance = (color: ColorToken) => {
    const hasOnWhiteContrast = color.wcag_contrast_on_white != null
    const hasOnBlackContrast = color.wcag_contrast_on_black != null

    return {
      hasOnWhiteContrast,
      hasOnBlackContrast,
      onWhitePasses: hasOnWhiteContrast && color.wcag_contrast_on_white >= 4.5,
      onBlackPasses: hasOnBlackContrast && color.wcag_contrast_on_black >= 4.5,
    }
  }

  const getAccessibilityBadges = (color: ColorToken) => {
    const badges = []
    if (color.wcag_aa_compliant_text) badges.push('AA')
    if (color.wcag_aaa_compliant_text) badges.push('AAA')
    if (color.colorblind_safe) badges.push('Colorblind Safe')
    return badges
  }

  return { getWCAGCompliance, getAccessibilityBadges }
}
