/**
 * ShadowTokenList
 *
 * Displays shadow tokens with visual previews and color linking capabilities
 * Phase 2: Color Linking implementation
 */

import React, { useEffect, useMemo } from 'react'
import { useShadowStore, apiShadowsToStore, type ColorTokenOption } from '../../../../../store/shadowStore'
import { useTokenGraphStore } from '../../../../../store/tokenGraphStore'
import { ShadowColorLink } from './ShadowColorLink'
import './ShadowTokenList.css'

// Support both API response format and W3C token format
interface ShadowTokenAPI {
  x_offset?: number
  y_offset?: number
  blur_radius?: number
  spread_radius?: number
  color_hex?: string
  opacity?: number
  name?: string
  shadow_type?: string
  semantic_role?: string
  confidence?: number
}

type ShadowValue = {
  color: string
  x: { value: number; unit: string }
  y: { value: number; unit: string }
  blur: { value: number; unit: string }
  spread: { value: number; unit: string }
}

interface ShadowTokenW3C {
  id?: string
  $value: ShadowValue
}

type ShadowToken = ShadowTokenAPI | ShadowTokenW3C

interface Props {
  shadows: ShadowToken[] | Record<string, ShadowToken> | null | undefined
  /** Optional: External color tokens for linking (if not using store) */
  colorTokens?: ColorTokenOption[]
  /** Optional: Enable/disable color linking UI */
  enableColorLinking?: boolean
  /** Optional: Read-only mode */
  readOnly?: boolean
}

const ShadowTokenList: React.FC<Props> = ({
  shadows,
  colorTokens,
  enableColorLinking = true,
  readOnly = false,
}) => {
  // Zustand stores
  const {
    shadows: storeShadows,
    availableColors,
    setShadows,
    setAvailableColors,
    linkColorToShadow,
    unlinkColorFromShadow,
  } = useShadowStore()

  const { colors: graphColors } = useTokenGraphStore()

  // Convert graph colors to color options format
  const graphColorOptions = useMemo<ColorTokenOption[]>(() => {
    return graphColors.map((c) => {
      const raw = c.raw as any
      const val = raw?.$value
      const hex =
        (typeof val === 'object' && val?.hex) ||
        raw?.hex ||
        raw?.attributes?.hex ||
        '#cccccc'
      return {
        id: c.id,
        hex,
        name: raw?.name ?? raw?.attributes?.name,
      }
    })
  }, [graphColors])

  // Use provided color tokens or fallback to graph colors
  const effectiveColors = colorTokens || graphColorOptions

  // Sync shadows to store when props change
  useEffect(() => {
    if (shadows) {
      const list = Array.isArray(shadows)
        ? shadows
        : Object.entries(shadows).map(([id, token]) => ({ ...token, id }))

      const converted = apiShadowsToStore(
        list as any,
        effectiveColors
      )
      setShadows(converted)
    }
  }, [shadows, effectiveColors, setShadows])

  // Sync available colors to store
  useEffect(() => {
    if (effectiveColors.length > 0) {
      setAvailableColors(effectiveColors)
    }
  }, [effectiveColors, setAvailableColors])

  // Use store shadows if populated, otherwise convert from props
  const displayShadows = storeShadows.length > 0 ? storeShadows : []

  // Fallback to direct list if store is empty
  const list: ShadowToken[] = Array.isArray(shadows)
    ? shadows
    : shadows && typeof shadows === 'object'
      ? Object.values(shadows)
      : []

  if (displayShadows.length === 0 && list.length === 0) {
    return <div className="empty-state">No shadows extracted yet.</div>
  }

  // Helper to get shadow style for preview
  const getShadowStyle = (shadow: any): string => {
    // Try store shadow format
    if (shadow.raw?.$value) {
      const value = shadow.raw.$value
      const layer = Array.isArray(value) ? value[0] : value
      if (layer) {
        const x = typeof layer.x === 'object' ? layer.x.value : layer.x || 0
        const y = typeof layer.y === 'object' ? layer.y.value : layer.y || 0
        const blur = typeof layer.blur === 'object' ? layer.blur.value : layer.blur || 0
        const spread = typeof layer.spread === 'object' ? layer.spread.value : layer.spread || 0
        // Resolve color - use linked color hex or extract from value
        let color = shadow.originalColors?.[0] || '#000000'
        if (shadow.linkedColorIds?.[0]) {
          const linkedColor = effectiveColors.find((c) => c.id === shadow.linkedColorIds[0])
          if (linkedColor) {
            color = linkedColor.hex
          }
        }
        return `${x}px ${y}px ${blur}px ${spread}px ${color}`
      }
    }

    // Fallback to API format
    const api = shadow as ShadowTokenAPI
    if (api.x_offset !== undefined) {
      const x = api.x_offset || 0
      const y = api.y_offset || 0
      const blur = api.blur_radius || 0
      const spread = api.spread_radius || 0
      const color = api.color_hex || '#000000'
      const opacity = api.opacity ?? 1
      // Apply opacity to color
      const colorWithOpacity = opacity < 1
        ? `${color}${Math.round(opacity * 255).toString(16).padStart(2, '0')}`
        : color
      return `${x}px ${y}px ${blur}px ${spread}px ${colorWithOpacity}`
    }
    return 'none'
  }

  // Render store shadows with color linking
  if (displayShadows.length > 0) {
    return (
      <div className="shadow-list">
        {displayShadows.map((shadow, idx) => {
          const style = getShadowStyle(shadow)
          const colorHex = shadow.originalColors[0] || '#000000'
          const linkedColorId = shadow.linkedColorIds[0] || ''

          // Get opacity from raw value
          const rawValue = shadow.raw.$value
          const layer = Array.isArray(rawValue) ? rawValue[0] : rawValue
          const opacity = (layer as any)?.opacity ?? 1

          // Extract dimension values
          const x = typeof layer?.x === 'object' ? layer.x.value : layer?.x || 0
          const y = typeof layer?.y === 'object' ? layer.y.value : layer?.y || 0
          const blur = typeof layer?.blur === 'object' ? layer.blur.value : layer?.blur || 0
          const spread = typeof layer?.spread === 'object' ? layer.spread.value : layer?.spread || 0

          return (
            <div key={shadow.id} className="shadow-card">
              {/* Visual preview */}
              <div className="shadow-preview-container">
                <div
                  className="shadow-preview-box"
                  style={{
                    boxShadow: style,
                    width: '100px',
                    height: '60px',
                    backgroundColor: '#f5f5f5',
                    borderRadius: '4px',
                  }}
                />
              </div>

              {/* Info */}
              <div className="shadow-info">
                <div className="shadow-title">{shadow.name || shadow.id}</div>
                <div className="shadow-props">
                  {shadow.shadowType && (
                    <div className="prop-row">
                      <span className="prop-label">Type:</span>
                      <span className="prop-value">{shadow.shadowType}</span>
                    </div>
                  )}
                  <div className="prop-row">
                    <span className="prop-label">Offset:</span>
                    <span className="prop-value">{x}px, {y}px</span>
                  </div>
                  <div className="prop-row">
                    <span className="prop-label">Blur:</span>
                    <span className="prop-value">{blur}px</span>
                  </div>
                  {spread !== 0 && (
                    <div className="prop-row">
                      <span className="prop-label">Spread:</span>
                      <span className="prop-value">{spread}px</span>
                    </div>
                  )}

                  {/* Color Linking Section */}
                  {enableColorLinking ? (
                    <div className="color-link-section">
                      <ShadowColorLink
                        layerIndex={0}
                        linkedColorId={linkedColorId}
                        currentHex={colorHex}
                        opacity={opacity}
                        availableColors={availableColors}
                        onLinkColor={(colorId) => linkColorToShadow(shadow.id, 0, colorId)}
                        onUnlinkColor={() => unlinkColorFromShadow(shadow.id, 0)}
                        readOnly={readOnly}
                      />
                    </div>
                  ) : (
                    <div className="prop-row">
                      <span className="prop-label">Color:</span>
                      <span className="prop-value">
                        <span
                          className="color-swatch-inline"
                          style={{
                            display: 'inline-block',
                            width: '16px',
                            height: '16px',
                            backgroundColor: colorHex,
                            borderRadius: '2px',
                            border: '1px solid #ccc',
                            marginRight: '4px',
                          }}
                        />
                        {linkedColorId ? (
                          <span className="linked-color-ref">{`{${linkedColorId}}`}</span>
                        ) : (
                          colorHex
                        )}
                        {opacity < 1 && ` @ ${Math.round(opacity * 100)}%`}
                      </span>
                    </div>
                  )}

                  {shadow.confidence !== undefined && (
                    <div className="prop-row">
                      <span className="prop-label">Confidence:</span>
                      <span className="prop-value">
                        {Math.round((shadow.confidence || 0) * 100)}%
                      </span>
                    </div>
                  )}

                  {shadow.semanticRole && (
                    <div className="prop-row">
                      <span className="prop-label">Role:</span>
                      <span className="prop-value semantic-role-badge">
                        {shadow.semanticRole}
                      </span>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )
        })}
      </div>
    )
  }

  // Fallback: Render without store (legacy mode)
  return (
    <div className="shadow-list">
      {list.map((shadow, idx) => {
        const api = shadow as ShadowTokenAPI
        const label = api.name || `shadow.${idx + 1}`
        const style = getShadowStyle(shadow)

        return (
          <div key={label} className="shadow-card">
            {/* Visual preview */}
            <div className="shadow-preview-container">
              <div
                className="shadow-preview-box"
                style={{
                  boxShadow: style,
                  width: '100px',
                  height: '60px',
                  backgroundColor: '#f5f5f5',
                  borderRadius: '4px',
                }}
              />
            </div>

            {/* Info */}
            <div className="shadow-info">
              <div className="shadow-title">{label}</div>
              <div className="shadow-props">
                <div className="prop-row">
                  <span className="prop-label">Type:</span>
                  <span className="prop-value">{api.shadow_type || 'drop'}</span>
                </div>
                <div className="prop-row">
                  <span className="prop-label">Offset:</span>
                  <span className="prop-value">
                    {api.x_offset || 0}px, {api.y_offset || 0}px
                  </span>
                </div>
                <div className="prop-row">
                  <span className="prop-label">Blur:</span>
                  <span className="prop-value">{api.blur_radius || 0}px</span>
                </div>
                {(api.spread_radius || 0) !== 0 && (
                  <div className="prop-row">
                    <span className="prop-label">Spread:</span>
                    <span className="prop-value">{api.spread_radius || 0}px</span>
                  </div>
                )}
                <div className="prop-row">
                  <span className="prop-label">Color:</span>
                  <span className="prop-value">
                    <span
                      className="color-swatch-inline"
                      style={{
                        display: 'inline-block',
                        width: '16px',
                        height: '16px',
                        backgroundColor: api.color_hex || '#000000',
                        borderRadius: '2px',
                        border: '1px solid #ccc',
                        marginRight: '4px',
                      }}
                    />
                    {api.color_hex} @ {((api.opacity ?? 1) * 100).toFixed(0)}%
                  </span>
                </div>
                <div className="prop-row">
                  <span className="prop-label">Confidence:</span>
                  <span className="prop-value">
                    {(api.confidence ? (api.confidence * 100).toFixed(0) : '0')}%
                  </span>
                </div>
              </div>
            </div>
          </div>
        )
      })}
    </div>
  )
}

export default ShadowTokenList
