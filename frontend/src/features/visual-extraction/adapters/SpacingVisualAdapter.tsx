/**
 * Spacing Visual Adapter
 *
 * Adapter for rendering spacing tokens in generic UI components
 * Handles W3C Design Token format for spacing/dimensions
 *
 * Responsibilities:
 * - Extract spacing value from W3C $value
 * - Render spacing ruler visualization
 * - Display spacing metadata (px, rem, semantic role)
 * - Provide detail tabs for spacing inspector
 */

import React from 'react'
import type { TokenVisualAdapter, TabDefinition } from '../../../shared/adapters'
import type { UiSpacingToken } from '../../../store/tokenGraphStore'

/**
 * Extract spacing value in pixels from W3C token $value
 */
function extractSpacingPx(token: UiSpacingToken): number {
  const value = token.raw.$value

  if (!value || typeof value !== 'object') {
    return 0
  }

  // W3C format: { value: number, unit: string }
  if ('value' in value && typeof value.value === 'number') {
    const unit = 'unit' in value && typeof value.unit === 'string' ? value.unit : 'px'

    // Convert to pixels based on unit
    switch (unit) {
      case 'px':
        return value.value
      case 'rem':
        return value.value * 16 // Assume 16px base
      case 'em':
        return value.value * 16
      default:
        return value.value
    }
  }

  return 0
}

/**
 * Extract spacing value with unit
 */
function extractSpacingDisplay(token: UiSpacingToken): string {
  const value = token.raw.$value

  if (!value || typeof value !== 'object') {
    return '0px'
  }

  if ('value' in value && typeof value.value === 'number') {
    const unit = 'unit' in value && typeof value.unit === 'string' ? value.unit : 'px'
    return `${value.value}${unit}`
  }

  return '0px'
}

/**
 * Extract display name from token
 */
function getSpacingName(token: UiSpacingToken): string {
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
function getMetadata(token: UiSpacingToken): {
  semanticRole?: string
  spacingType?: string
  multiplier?: number
  baseId?: string
  confidence?: number
} {
  const extensions = token.raw.$extensions as Record<string, unknown> | undefined

  return {
    semanticRole: extensions && typeof extensions['semantic_role'] === 'string' ? extensions['semantic_role'] : undefined,
    spacingType: extensions && typeof extensions['spacing_type'] === 'string' ? extensions['spacing_type'] : undefined,
    multiplier: token.multiplier,
    baseId: token.baseId,
    confidence: extensions && typeof extensions['confidence'] === 'number' ? extensions['confidence'] : undefined,
  }
}

/**
 * Spacing Visual Adapter
 * Implements TokenVisualAdapter interface for spacing tokens
 */
export const SpacingVisualAdapter: TokenVisualAdapter<UiSpacingToken> = {
  category: 'spacing',

  renderSwatch: (token: UiSpacingToken) => {
    const px = extractSpacingPx(token)
    const maxWidth = 100 // Max width for visualization

    return (
      <div
        className="spacing-swatch"
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '4px',
          width: '100%',
        }}
      >
        {/* Ruler visualization */}
        <div
          style={{
            height: '16px',
            width: `${Math.min(px, maxWidth)}px`,
            background: 'linear-gradient(90deg, #3b82f6 0%, #60a5fa 100%)',
            borderRadius: '2px',
            border: '1px solid rgba(59, 130, 246, 0.3)',
            position: 'relative',
          }}
        >
          {/* Tick marks for scale */}
          <div
            style={{
              position: 'absolute',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              background: 'repeating-linear-gradient(90deg, rgba(255,255,255,0.2) 0px, rgba(255,255,255,0.2) 1px, transparent 1px, transparent 4px)',
            }}
          />
        </div>
        {/* Value label */}
        <span
          style={{
            fontSize: '0.7rem',
            fontFamily: 'monospace',
            color: '#3b82f6',
            fontWeight: 600,
          }}
        >
          {px > maxWidth ? `${px}px` : ''}
        </span>
      </div>
    )
  },

  renderMetadata: (token: UiSpacingToken) => {
    const display = extractSpacingDisplay(token)
    const px = extractSpacingPx(token)
    const rem = (px / 16).toFixed(2)
    const metadata = getMetadata(token)

    return (
      <div className="spacing-metadata" style={{ fontSize: '0.85rem', color: '#666' }}>
        <div style={{ fontFamily: 'monospace', marginBottom: '0.25rem', fontSize: '0.9rem', fontWeight: 600 }}>
          {display} ({rem}rem)
        </div>
        {metadata.semanticRole && (
          <div>
            <strong>Role:</strong> {metadata.semanticRole}
          </div>
        )}
        {metadata.spacingType && (
          <div>
            <strong>Type:</strong> {metadata.spacingType}
          </div>
        )}
        {metadata.multiplier && metadata.baseId && (
          <div>
            <strong>Scale:</strong> {metadata.multiplier}× {metadata.baseId}
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

  getDetailTabs: (_token: UiSpacingToken): TabDefinition[] => {
    // TODO: Import actual tab components when available
    return []

    // Future implementation:
    // return [
    //   { name: 'scale', label: 'Scale', component: SpacingScaleTab },
    //   { name: 'relationships', label: 'Relationships', component: SpacingRelationshipsTab },
    //   { name: 'grid', label: 'Grid', component: SpacingGridTab },
    // ]
  },

  getDisplayName: (token: UiSpacingToken): string => {
    return getSpacingName(token)
  },

  getDisplayValue: (token: UiSpacingToken): string => {
    return extractSpacingDisplay(token)
  },

  canEdit: (_token: UiSpacingToken): boolean => {
    return true
  },
}

/**
 * Auto-register adapter on module load
 */
import { registerAdapter } from '../../../shared/adapters'
registerAdapter(SpacingVisualAdapter)
