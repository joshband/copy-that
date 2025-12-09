import type { ColorRGB } from './types'

export function parseHex(hex: string): ColorRGB {
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex)
  return result
    ? {
        r: parseInt(result[1], 16),
        g: parseInt(result[2], 16),
        b: parseInt(result[3], 16),
      }
    : { r: 0, g: 0, b: 0 }
}

export function getLuminance(color: string): number {
  const { r, g, b } = parseHex(color)
  const [rs, gs, bs] = [r, g, b].map((x) => {
    x = x / 255
    return x <= 0.03928 ? x / 12.92 : Math.pow((x + 0.055) / 1.055, 2.4)
  })
  return 0.2126 * rs + 0.7152 * gs + 0.0722 * bs
}

export function calculateContrast(color1: string, color2: string): number {
  const lum1 = getLuminance(color1)
  const lum2 = getLuminance(color2)
  const lighter = Math.max(lum1, lum2)
  const darker = Math.min(lum1, lum2)
  return (lighter + 0.05) / (darker + 0.05)
}

export function getWcagLevelText(ratio: number): string {
  if (ratio >= 7) return 'AAA'
  if (ratio >= 4.5) return 'AA'
  return 'Fail'
}

export function getWcagLevelNormal(ratio: number): string {
  if (ratio >= 4.5) return 'AAA'
  if (ratio >= 3) return 'AA'
  return 'Fail'
}
