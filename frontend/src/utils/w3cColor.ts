import type { W3CColorValue } from '../types'

export type ResolvedColorStrings = {
  hex: string
  rgb: string
  alpha: number
}

const FALLBACK: ResolvedColorStrings = {
  hex: '#CCCCCC',
  rgb: 'rgb(204, 204, 204)',
  alpha: 1,
}

function clamp01(value: number): number {
  if (Number.isNaN(value)) return 0
  if (value < 0) return 0
  if (value > 1) return 1
  return value
}

function linearToSrgbChannel(value: number): number {
  const clamped = clamp01(value)
  if (clamped <= 0.0031308) return 12.92 * clamped
  return 1.055 * Math.pow(clamped, 1 / 2.4) - 0.055
}

function byteToHex(value: number): string {
  return value.toString(16).padStart(2, '0').toUpperCase()
}

function srgbToHex(r: number, g: number, b: number): string {
  return `#${byteToHex(r)}${byteToHex(g)}${byteToHex(b)}`
}

function normalizeHexString(input: string): { hex: string; alpha: number } | null {
  const raw = input.trim()
  if (!raw.startsWith('#')) return null

  const hex = raw.slice(1)
  if (/^[0-9a-fA-F]{3}$/.test(hex)) {
    const expanded = hex
      .split('')
      .map((c) => c + c)
      .join('')
      .toUpperCase()
    return { hex: `#${expanded}`, alpha: 1 }
  }

  if (/^[0-9a-fA-F]{6}$/.test(hex)) {
    return { hex: `#${hex.toUpperCase()}`, alpha: 1 }
  }

  if (/^[0-9a-fA-F]{8}$/.test(hex)) {
    const rgb = hex.slice(0, 6).toUpperCase()
    const alphaByte = parseInt(hex.slice(6, 8), 16)
    const alpha = clamp01(alphaByte / 255)
    return { hex: `#${rgb}`, alpha }
  }

  return null
}

function hexToRgbBytes(hex: string): { r: number; g: number; b: number } | null {
  const normalized = normalizeHexString(hex)
  if (!normalized) return null
  const rgb = normalized.hex.slice(1)
  const value = parseInt(rgb, 16)
  const r = (value >> 16) & 255
  const g = (value >> 8) & 255
  const b = value & 255
  return { r, g, b }
}

function normalizeOklch(value: W3CColorValue): { l: number; c: number; h: number; alpha: number } | null {
  const lRaw = typeof value.l === 'number' ? value.l : undefined
  const cRaw = typeof value.c === 'number' ? value.c : undefined
  const hRaw = typeof value.h === 'number' ? value.h : undefined
  if (lRaw == null || cRaw == null || hRaw == null) return null

  const l = clamp01(lRaw > 1 ? lRaw / 100 : lRaw)
  const c = Number.isFinite(cRaw) ? cRaw : 0
  const h = Number.isFinite(hRaw) ? hRaw : 0

  const alphaRaw = typeof value.alpha === 'number' ? value.alpha : 1
  const alpha = clamp01(alphaRaw > 1 ? alphaRaw / 100 : alphaRaw)

  return { l, c, h, alpha }
}

function oklchToSrgbBytes(l: number, c: number, h: number): { r: number; g: number; b: number } | null {
  if (!Number.isFinite(l) || !Number.isFinite(c) || !Number.isFinite(h)) return null

  const hRad = (h * Math.PI) / 180
  const a = c * Math.cos(hRad)
  const b = c * Math.sin(hRad)

  // OKLab -> linear sRGB (Björn Ottosson)
  const l_ = l + 0.3963377774 * a + 0.2158037573 * b
  const m_ = l - 0.1055613458 * a - 0.0638541728 * b
  const s_ = l - 0.0894841775 * a - 1.291485548 * b

  const l3 = l_ * l_ * l_
  const m3 = m_ * m_ * m_
  const s3 = s_ * s_ * s_

  const rLin = 4.0767416621 * l3 - 3.3077115913 * m3 + 0.2309699292 * s3
  const gLin = -1.2684380046 * l3 + 2.6097574011 * m3 - 0.3413193965 * s3
  const bLin = -0.0041960863 * l3 - 0.7034186147 * m3 + 1.707614701 * s3

  const r = Math.round(clamp01(linearToSrgbChannel(rLin)) * 255)
  const g = Math.round(clamp01(linearToSrgbChannel(gLin)) * 255)
  const bOut = Math.round(clamp01(linearToSrgbChannel(bLin)) * 255)

  return { r, g, b: bOut }
}

export function resolveW3CColorValue(value: unknown): ResolvedColorStrings {
  if (typeof value === 'string') {
    // Alias reference like "{color.primary}" is not a color.
    if (value.startsWith('{') && value.endsWith('}')) return FALLBACK

    const normalized = normalizeHexString(value)
    if (normalized) {
      const rgb = hexToRgbBytes(normalized.hex)
      if (!rgb) return FALLBACK
      return {
        hex: normalized.hex,
        rgb:
          normalized.alpha < 1
            ? `rgba(${rgb.r}, ${rgb.g}, ${rgb.b}, ${normalized.alpha.toFixed(3).replace(/0+$/, '').replace(/\.$/, '')})`
            : `rgb(${rgb.r}, ${rgb.g}, ${rgb.b})`,
        alpha: normalized.alpha,
      }
    }

    if (value.trim().startsWith('rgb(') || value.trim().startsWith('rgba(')) {
      return { ...FALLBACK, rgb: value.trim() }
    }

    return FALLBACK
  }

  if (value && typeof value === 'object') {
    const record = value as Record<string, unknown>
    const hexCandidate = typeof record.hex === 'string' ? record.hex : undefined
    if (hexCandidate) {
      const normalized = normalizeHexString(hexCandidate)
      if (normalized) {
        const rgb = hexToRgbBytes(normalized.hex)
        if (!rgb) return FALLBACK
        return {
          hex: normalized.hex,
          rgb:
            normalized.alpha < 1
              ? `rgba(${rgb.r}, ${rgb.g}, ${rgb.b}, ${normalized.alpha.toFixed(3).replace(/0+$/, '').replace(/\.$/, '')})`
              : `rgb(${rgb.r}, ${rgb.g}, ${rgb.b})`,
          alpha: normalized.alpha,
        }
      }
    }

    const oklch = normalizeOklch(record as W3CColorValue)
    if (oklch) {
      const rgb = oklchToSrgbBytes(oklch.l, oklch.c, oklch.h)
      if (!rgb) return FALLBACK
      const hex = srgbToHex(rgb.r, rgb.g, rgb.b)
      return {
        hex,
        rgb:
          oklch.alpha < 1
            ? `rgba(${rgb.r}, ${rgb.g}, ${rgb.b}, ${oklch.alpha.toFixed(3).replace(/0+$/, '').replace(/\.$/, '')})`
            : `rgb(${rgb.r}, ${rgb.g}, ${rgb.b})`,
        alpha: oklch.alpha,
      }
    }
  }

  return FALLBACK
}
