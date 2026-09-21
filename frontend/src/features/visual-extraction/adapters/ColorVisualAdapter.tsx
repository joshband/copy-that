/**
 * Color Visual Adapter
 *
 * Adapter for rendering color tokens in generic UI components
 * Handles W3C Design Token format for colors
 *
 * Responsibilities:
 * - Extract hex color from W3C $value (supports multiple formats)
 * - Render color swatches
 * - Display color metadata (harmony, temperature, saturation)
 * - Provide detail tabs for color inspector
 */

import React from 'react'
import type { TokenVisualAdapter, TabDefinition } from '../../../shared/adapters'
import type { UiColorToken } from '../../../store/tokenGraphStore'

/**
 * Extract hex color from W3C token $value
 * Supports multiple formats:
 * - Direct hex string: { $value: "#2563eb" }
 * - Object with hex: { $value: { hex: "#2563eb" } }
 * - OKLCH object: { $value: { l: 0.5, c: 0.1, h: 250 } }
 */
function extractHex(token: UiColorToken): string {
  const value = token.raw.$value

  // Direct hex string
  if (typeof value === 'string' && value.startsWith('#')) {
    return value
  }

  // Object with hex property
  if (value && typeof value === 'object' && 'hex' in value && typeof value.hex === 'string') {
    return value.hex
  }

  // OKLCH format (convert to hex - placeholder for now)
  if (value && typeof value === 'object' && 'l' in value && 'c' in value && 'h' in value) {
    // TODO: Implement OKLCH → Hex conversion
    // For now, return a placeholder
    return '#888888'
  }

  // Fallback
  return '#CCCCCC'
}

/**
 * Extract display name from token
 * Uses token ID or $description
 */
function getColorName(token: UiColorToken): string {
  // Check for $description
  if (token.raw.$description && typeof token.raw.$description === 'string') {
    return token.raw.$description
  }

  // Use token ID, format nicely
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
function getMetadata(token: UiColorToken): {
  harmony?: string
  temperature?: string
  saturation?: string
  lightness?: string
  confidence?: number
} {
  const extensions = token.raw.$extensions as Record<string, unknown> | undefined

  if (!extensions || typeof extensions !== 'object') {
    return {}
  }

  return {
    harmony: typeof extensions['harmony'] === 'string' ? extensions['harmony'] : undefined,
    temperature: typeof extensions['temperature'] === 'string' ? extensions['temperature'] : undefined,
    saturation: typeof extensions['saturation_level'] === 'string' ? extensions['saturation_level'] : undefined,
    lightness: typeof extensions['lightness_level'] === 'string' ? extensions['lightness_level'] : undefined,
    confidence: typeof extensions['confidence'] === 'number' ? extensions['confidence'] : undefined,
  }
}

/**
 * Color Visual Adapter
 * Implements TokenVisualAdapter interface for color tokens
 */
export const ColorVisualAdapter: TokenVisualAdapter<UiColorToken> = {
  category: 'color',

  renderSwatch: (token: UiColorToken) => {
    const hex = extractHex(token)

    return (
      <div
        className="color-swatch"
        style={{
          width: '32px',
          height: '32px',
          borderRadius: '4px',
          backgroundColor: hex,
          border: '1px solid rgba(0,0,0,0.1)',
          boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
        }}
        title={hex}
      />
    )
  },

  renderMetadata: (token: UiColorToken) => {
    const hex = extractHex(token)
    const metadata = getMetadata(token)

    return (
      <div className="color-metadata" style={{ fontSize: '0.85rem', color: '#666' }}>
        <div style={{ fontFamily: 'monospace', marginBottom: '0.25rem' }}>{hex}</div>
        {metadata.harmony && (
          <div>
            <strong>Harmony:</strong> {metadata.harmony}
          </div>
        )}
        {metadata.temperature && (
          <div>
            <strong>Temperature:</strong> {metadata.temperature}
          </div>
        )}
        {metadata.saturation && (
          <div>
            <strong>Saturation:</strong> {metadata.saturation}
          </div>
        )}
        {metadata.confidence !== undefined && (
          <div>
            <strong>Confidence:</strong> {(metadata.confidence * 100).toFixed(0)}%
          </div>
        )}
      </div>
    )
  },

  getDetailTabs: (_token: UiColorToken): TabDefinition[] => {
    // Import tabs dynamically to avoid circular dependencies
    const { OverviewTab } = require('../components/color/color-detail-panel/tabs/OverviewTab')
    const { HarmonyTab } = require('../components/color/color-detail-panel/tabs/HarmonyTab')
    const { AccessibilityTab } = require('../components/color/color-detail-panel/tabs/AccessibilityTab')
    const { PropertiesTab } = require('../components/color/color-detail-panel/tabs/PropertiesTab')
    const { DiagnosticsTab } = require('../components/color/color-detail-panel/tabs/DiagnosticsTab')

    return [
      { name: 'overview', label: 'Overview', component: OverviewTab },
      { name: 'harmony', label: 'Harmony', component: HarmonyTab },
      { name: 'accessibility', label: 'Accessibility', component: AccessibilityTab },
      { name: 'properties', label: 'Properties', component: PropertiesTab },
      { name: 'diagnostics', label: 'Diagnostics', component: DiagnosticsTab },
    ]
  },

  getDisplayName: (token: UiColorToken): string => {
    return getColorName(token)
  },

  getDisplayValue: (token: UiColorToken): string => {
    return extractHex(token)
  },

  canEdit: (_token: UiColorToken): boolean => {
    // Colors can be edited (future feature)
    return true
  },
}

/**
 * Auto-register adapter on module load
 * This ensures the adapter is available when the visual-extraction feature is imported
 */
import { registerAdapter } from '../../../shared/adapters'
registerAdapter(ColorVisualAdapter)
