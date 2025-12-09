/**
 * Typography Visual Adapter
 *
 * Adapter for rendering typography tokens in generic UI components
 * Handles W3C Design Token format for typography composites
 *
 * Responsibilities:
 * - Extract typography properties from W3C $value
 * - Render font preview with actual typeface
 * - Display typography metadata (family, size, weight, line-height)
 * - Provide detail tabs for typography inspector
 */

import React from 'react'
import type { TokenVisualAdapter, TabDefinition } from '../../../shared/adapters'
import type { UiTypographyToken } from '../../../store/tokenGraphStore'

/**
 * Extract font family from W3C token $value
 */
function extractFontFamily(token: UiTypographyToken): string {
  const value = token.raw.$value as Record<string, unknown> | undefined

  if (!value || typeof value !== 'object') {
    return 'sans-serif'
  }

  const fontFamily = value['fontFamily']

  // Array format: ['Arial', 'sans-serif']
  if (Array.isArray(fontFamily) && fontFamily.length > 0) {
    return fontFamily
      .filter((f) => typeof f === 'string')
      .join(', ')
  }

  // String format: 'Arial, sans-serif'
  if (typeof fontFamily === 'string') {
    return fontFamily
  }

  return 'sans-serif'
}

/**
 * Extract font size in pixels
 */
function extractFontSize(token: UiTypographyToken): number {
  const value = token.raw.$value as Record<string, unknown> | undefined

  if (!value || typeof value !== 'object') {
    return 16
  }

  const fontSize = value['fontSize']

  // Number format (pixels)
  if (typeof fontSize === 'number') {
    return fontSize
  }

  // String format: '16px', '1rem'
  if (typeof fontSize === 'string') {
    const match = fontSize.match(/^([\d.]+)(px|rem|em)?$/)
    if (match) {
      const numValue = parseFloat(match[1])
      const unit = match[2] || 'px'

      if (unit === 'rem' || unit === 'em') {
        return numValue * 16
      }
      return numValue
    }
  }

  // Object format: { value: 16, unit: 'px' }
  if (fontSize && typeof fontSize === 'object' && 'value' in fontSize) {
    const obj = fontSize as Record<string, unknown>
    if (typeof obj['value'] === 'number') {
      const unit = typeof obj['unit'] === 'string' ? obj['unit'] : 'px'
      if (unit === 'rem' || unit === 'em') {
        return obj['value'] * 16
      }
      return obj['value']
    }
  }

  return 16
}

/**
 * Extract font weight
 */
function extractFontWeight(token: UiTypographyToken): number {
  const value = token.raw.$value as Record<string, unknown> | undefined

  if (!value || typeof value !== 'object') {
    return 400
  }

  const fontWeight = value['fontWeight']

  if (typeof fontWeight === 'number') {
    return fontWeight
  }

  if (typeof fontWeight === 'string') {
    const weights: Record<string, number> = {
      thin: 100,
      extralight: 200,
      light: 300,
      normal: 400,
      medium: 500,
      semibold: 600,
      bold: 700,
      extrabold: 800,
      black: 900,
    }
    return weights[fontWeight.toLowerCase()] || 400
  }

  return 400
}

/**
 * Extract display name from token
 */
function getTypographyName(token: UiTypographyToken): string {
  if (token.raw.$description && typeof token.raw.$description === 'string') {
    return token.raw.$description
  }

  const formatted = token.id
    .split('.')
    .pop()
    ?.replace(/-/g, ' ')
    .replace(/\b\w/g, (l) => l.toUpperCase())

  return formatted || token.id
}

/**
 * Extract metadata from token
 */
function getMetadata(token: UiTypographyToken): {
  lineHeight?: string
  letterSpacing?: string
  referencedColorId?: string
  fontFamilyTokenId?: string
  fontSizeTokenId?: string
} {
  const value = token.raw.$value as Record<string, unknown> | undefined

  return {
    lineHeight: value && typeof value['lineHeight'] === 'string' ? value['lineHeight'] : undefined,
    letterSpacing: value && typeof value['letterSpacing'] === 'string' ? value['letterSpacing'] : undefined,
    referencedColorId: token.referencedColorId,
    fontFamilyTokenId: token.fontFamilyTokenId,
    fontSizeTokenId: token.fontSizeTokenId,
  }
}

/**
 * Typography Visual Adapter
 * Implements TokenVisualAdapter interface for typography tokens
 */
export const TypographyVisualAdapter: TokenVisualAdapter<UiTypographyToken> = {
  category: 'typography',

  renderSwatch: (token: UiTypographyToken) => {
    const fontFamily = extractFontFamily(token)
    const fontSize = extractFontSize(token)
    const fontWeight = extractFontWeight(token)

    return (
      <div
        className="typography-swatch"
        style={{
          fontFamily,
          fontSize: `${Math.min(fontSize, 24)}px`, // Cap at 24px for swatch
          fontWeight,
          padding: '4px 8px',
          border: '1px solid rgba(0,0,0,0.1)',
          borderRadius: '4px',
          background: 'white',
          lineHeight: 1.2,
          whiteSpace: 'nowrap',
          overflow: 'hidden',
          textOverflow: 'ellipsis',
          maxWidth: '120px',
        }}
        title={`${fontFamily} ${fontSize}px`}
      >
        Aa
      </div>
    )
  },

  renderMetadata: (token: UiTypographyToken) => {
    const fontFamily = extractFontFamily(token)
    const fontSize = extractFontSize(token)
    const fontWeight = extractFontWeight(token)
    const metadata = getMetadata(token)

    return (
      <div className="typography-metadata" style={{ fontSize: '0.85rem', color: '#666' }}>
        <div style={{ marginBottom: '0.25rem' }}>
          <strong>Font:</strong> {fontFamily}
        </div>
        <div>
          <strong>Size:</strong> {fontSize}px
        </div>
        <div>
          <strong>Weight:</strong> {fontWeight}
        </div>
        {metadata.lineHeight && (
          <div>
            <strong>Line Height:</strong> {metadata.lineHeight}
          </div>
        )}
        {metadata.letterSpacing && (
          <div>
            <strong>Letter Spacing:</strong> {metadata.letterSpacing}
          </div>
        )}
        {metadata.referencedColorId && (
          <div style={{ fontSize: '0.75rem', color: '#0066FF' }}>
            → Color: {metadata.referencedColorId}
          </div>
        )}
      </div>
    )
  },

  getDetailTabs: (_token: UiTypographyToken): TabDefinition[] => {
    // TODO: Import actual tab components when available
    return []
  },

  getDisplayName: (token: UiTypographyToken): string => {
    return getTypographyName(token)
  },

  getDisplayValue: (token: UiTypographyToken): string => {
    const fontSize = extractFontSize(token)
    const fontWeight = extractFontWeight(token)
    return `${fontSize}px / ${fontWeight}`
  },

  canEdit: (_token: UiTypographyToken): boolean => {
    return true
  },
}

/**
 * Auto-register adapter on module load
 */
import { registerAdapter } from '../../../shared/adapters'
registerAdapter(TypographyVisualAdapter)
