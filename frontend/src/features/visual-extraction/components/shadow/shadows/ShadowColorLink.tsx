/**
 * ShadowColorLink
 *
 * Displays the color linking status for a shadow layer with inline editing
 * Shows whether a shadow is linked to a color token or using raw hex
 *
 * Phase 2: Color Linking implementation
 */

import React, { useState } from 'react'
import { ColorTokenPicker } from './ColorTokenPicker'
import type { ColorTokenOption } from '../../store/shadowStore'
import './ShadowColorLink.css'

interface Props {
  /** Shadow layer index (for multi-layer shadows) */
  layerIndex: number
  /** Currently linked color token ID (empty if not linked) */
  linkedColorId: string
  /** Original/current hex color value */
  currentHex: string
  /** Opacity value (0-1) */
  opacity: number
  /** Available color tokens for selection */
  availableColors: ColorTokenOption[]
  /** Callback when color is linked */
  onLinkColor: (colorId: string) => void
  /** Callback when color is unlinked */
  onUnlinkColor: () => void
  /** Optional: Show as compact mode */
  compact?: boolean
  /** Optional: Disable editing */
  readOnly?: boolean
}

export const ShadowColorLink: React.FC<Props> = ({
  layerIndex,
  linkedColorId,
  currentHex,
  opacity,
  availableColors,
  onLinkColor,
  onUnlinkColor,
  compact = false,
  readOnly = false,
}) => {
  const [isExpanded, setIsExpanded] = useState(false)

  // Find the linked color details
  const linkedColor = availableColors.find((c) => c.id === linkedColorId)
  const displayHex = linkedColor?.hex || currentHex
  const isLinked = Boolean(linkedColorId)

  // Format opacity for display
  const opacityPercent = Math.round(opacity * 100)

  if (compact) {
    return (
      <div className="shadow-color-link compact">
        <span
          className="color-swatch-mini"
          style={{ backgroundColor: displayHex }}
          title={isLinked ? `Linked: {${linkedColorId}}` : currentHex}
        />
        <span className="color-label-compact">
          {isLinked ? (
            <span className="linked-indicator" title={`Linked to ${linkedColorId}`}>
              {linkedColor?.name || linkedColorId}
            </span>
          ) : (
            <span className="hex-label">{currentHex}</span>
          )}
          {opacity < 1 && (
            <span className="opacity-indicator">@ {opacityPercent}%</span>
          )}
        </span>
        {isLinked && <span className="link-badge" title="Color token linked">&#128279;</span>}
      </div>
    )
  }

  return (
    <div className={`shadow-color-link ${isExpanded ? 'expanded' : ''}`}>
      {/* Header Row */}
      <div className="color-link-header">
        <div className="color-link-info">
          <span
            className="color-swatch"
            style={{ backgroundColor: displayHex }}
          />
          <div className="color-details">
            {isLinked ? (
              <>
                <span className="linked-token-name">
                  {linkedColor?.name || linkedColorId}
                </span>
                <span className="linked-token-ref">{`{${linkedColorId}}`}</span>
              </>
            ) : (
              <>
                <span className="raw-hex-value">{currentHex}</span>
                <span className="unlinked-hint">Not linked to token</span>
              </>
            )}
          </div>
        </div>

        {/* Status Badge */}
        <div className="color-link-status">
          {isLinked ? (
            <span className="status-badge linked">
              <span className="link-icon">&#128279;</span>
              Linked
            </span>
          ) : (
            <span className="status-badge unlinked">Raw Hex</span>
          )}
        </div>

        {/* Opacity Display */}
        {opacity < 1 && (
          <div className="opacity-display">
            <span className="opacity-label">Opacity:</span>
            <span className="opacity-value">{opacityPercent}%</span>
          </div>
        )}

        {/* Expand/Edit Button */}
        {!readOnly && (
          <button
            type="button"
            className="edit-link-btn"
            onClick={() => setIsExpanded(!isExpanded)}
            title={isExpanded ? 'Close editor' : 'Edit color link'}
          >
            {isExpanded ? '\u25B2 Close' : '\u270E Edit'}
          </button>
        )}
      </div>

      {/* Expanded Editor */}
      {isExpanded && !readOnly && (
        <div className="color-link-editor">
          <div className="editor-section">
            <label className="editor-label">
              {layerIndex > 0 ? `Layer ${layerIndex + 1} Color` : 'Shadow Color'}
            </label>
            <ColorTokenPicker
              selectedColorId={linkedColorId}
              availableColors={availableColors}
              currentHex={currentHex}
              onSelectColor={onLinkColor}
              onUnlink={onUnlinkColor}
            />
          </div>

          {/* Color Preview Comparison */}
          {isLinked && linkedColor && linkedColor.hex !== currentHex && (
            <div className="color-comparison">
              <div className="comparison-item">
                <span className="comparison-label">Original:</span>
                <span
                  className="comparison-swatch"
                  style={{ backgroundColor: currentHex }}
                />
                <span className="comparison-hex">{currentHex}</span>
              </div>
              <span className="comparison-arrow">\u2192</span>
              <div className="comparison-item">
                <span className="comparison-label">Linked:</span>
                <span
                  className="comparison-swatch"
                  style={{ backgroundColor: linkedColor.hex }}
                />
                <span className="comparison-hex">{linkedColor.hex}</span>
              </div>
            </div>
          )}

          {/* Tips */}
          <div className="editor-tips">
            <p className="tip">
              <strong>Tip:</strong> Linking to a color token ensures your shadow color updates
              automatically when the token changes.
            </p>
          </div>
        </div>
      )}
    </div>
  )
}

export default ShadowColorLink
