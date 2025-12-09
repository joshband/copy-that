/**
 * Shadow Visual Adapter
 *
 * Adapter for rendering shadow tokens in generic UI components
 * Handles W3C Design Token format for shadow composites
 *
 * Responsibilities:
 * - Extract shadow layers from W3C $value
 * - Render shadow preview box
 * - Display shadow metadata (offset, blur, spread, color)
 * - Provide detail tabs for shadow inspector
 */

import React from 'react'
import type { TokenVisualAdapter, TabDefinition } from '../../../shared/adapters'
import type { UiShadowToken } from '../../../store/tokenGraphStore'

/**
 * Extract shadow layers from W3C token $value
 */
function extractShadowLayers(token: UiShadowToken): Array<{
  x: number
  y: number
  blur: number
  spread: number
  color: string
  inset?: boolean
}> {
  const value = token.raw.$value

  // Normalize to array (W3C allows single layer or array)
  const layers = Array.isArray(value) ? value : [value]

  return layers.map((layer) => {
    if (!layer || typeof layer !== 'object') {
      return { x: 0, y: 0, blur: 0, spread: 0, color: '#000000' }
    }

    const obj = layer as Record<string, unknown>

    // Extract dimensions (can be objects or numbers)
    const extractDimension = (key: string): number => {
      const val = obj[key]
      if (typeof val === 'number') return val
      if (val && typeof val === 'object' && 'value' in val && typeof val.value === 'number') {
        return val.value
      }
      return 0
    }

    return {
      x: extractDimension('x') || extractDimension('offsetX'),
      y: extractDimension('y') || extractDimension('offsetY'),
      blur: extractDimension('blur') || extractDimension('blurRadius'),
      spread: extractDimension('spread') || extractDimension('spreadRadius'),
      color: typeof obj['color'] === 'string' ? obj['color'] : '#000000',
      inset: typeof obj['inset'] === 'boolean' ? obj['inset'] : undefined,
    }
  })
}

/**
 * Generate CSS box-shadow string from layers
 */
function generateBoxShadow(layers: Array<{ x: number; y: number; blur: number; spread: number; color: string; inset?: boolean }>): string {
  return layers
    .map((layer) => {
      const inset = layer.inset ? 'inset ' : ''
      return `${inset}${layer.x}px ${layer.y}px ${layer.blur}px ${layer.spread}px ${layer.color}`
    })
    .join(', ')
}

/**
 * Extract display name from token
 */
function getShadowName(token: UiShadowToken): string {
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
 * Shadow Visual Adapter
 * Implements TokenVisualAdapter interface for shadow tokens
 */
export const ShadowVisualAdapter: TokenVisualAdapter<UiShadowToken> = {
  category: 'shadow',

  renderSwatch: (token: UiShadowToken) => {
    const layers = extractShadowLayers(token)
    const boxShadow = generateBoxShadow(layers)

    return (
      <div
        className="shadow-swatch"
        style={{
          width: '48px',
          height: '32px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
        <div
          style={{
            width: '32px',
            height: '20px',
            backgroundColor: '#ffffff',
            borderRadius: '4px',
            boxShadow,
          }}
        />
      </div>
    )
  },

  renderMetadata: (token: UiShadowToken) => {
    const layers = extractShadowLayers(token)
    const firstLayer = layers[0]

    return (
      <div className="shadow-metadata" style={{ fontSize: '0.85rem', color: '#666' }}>
        <div style={{ marginBottom: '0.25rem' }}>
          <strong>Layers:</strong> {layers.length}
        </div>
        {firstLayer && (
          <>
            <div style={{ fontSize: '0.75rem', fontFamily: 'monospace' }}>
              x: {firstLayer.x}px, y: {firstLayer.y}px
            </div>
            <div style={{ fontSize: '0.75rem', fontFamily: 'monospace' }}>
              blur: {firstLayer.blur}px, spread: {firstLayer.spread}px
            </div>
            <div style={{ fontSize: '0.75rem' }}>
              <strong>Color:</strong> {firstLayer.color}
            </div>
            {firstLayer.inset && (
              <div style={{ fontSize: '0.75rem', color: '#0066FF' }}>inset</div>
            )}
          </>
        )}
        {token.referencedColorIds && token.referencedColorIds.length > 0 && (
          <div style={{ fontSize: '0.75rem', color: '#0066FF', marginTop: '0.25rem' }}>
            → {token.referencedColorIds.length} color refs
          </div>
        )}
      </div>
    )
  },

  getDetailTabs: (_token: UiShadowToken): TabDefinition[] => {
    // TODO: Import actual tab components when available
    return []
  },

  getDisplayName: (token: UiShadowToken): string => {
    return getShadowName(token)
  },

  getDisplayValue: (token: UiShadowToken): string => {
    const layers = extractShadowLayers(token)
    const first = layers[0]
    if (!first) return 'none'
    return `${first.x}px ${first.y}px ${first.blur}px`
  },

  canEdit: (_token: UiShadowToken): boolean => {
    return true
  },
}

/**
 * Auto-register adapter on module load
 */
import { registerAdapter } from '../../../shared/adapters'
registerAdapter(ShadowVisualAdapter)
