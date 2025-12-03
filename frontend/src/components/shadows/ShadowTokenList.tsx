import React from 'react'
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
}

const ShadowTokenList: React.FC<Props> = ({ shadows }) => {
  const list: ShadowToken[] = Array.isArray(shadows)
    ? shadows
    : shadows && typeof shadows === 'object'
      ? Object.values(shadows)
      : []

  console.log('ShadowTokenList rendered with shadows:', shadows, 'list:', list)

  if (!list || list.length === 0) {
    console.log('ShadowTokenList: No shadows, showing empty state')
    return <div className="empty-state">No shadows extracted yet.</div>
  }

  console.log('ShadowTokenList: Rendering', list.length, 'shadow tokens')

  const getShadowStyle = (shadow: ShadowToken): string => {
    const api = shadow as ShadowTokenAPI
    if (api.x_offset !== undefined) {
      const x = api.x_offset || 0
      const y = api.y_offset || 0
      const blur = api.blur_radius || 0
      const spread = api.spread_radius || 0
      const color = api.color_hex || '#000000'
      const opacity = (api.opacity ?? 1).toFixed(2)
      return `${x}px ${y}px ${blur}px ${spread}px ${color}${opacity !== '1' ? Math.round(parseFloat(opacity) * 100) : ''}`
    }
    return 'none'
  }

  const getShadowLabel = (shadow: ShadowToken, idx: number): string => {
    const api = shadow as ShadowTokenAPI
    return api.name || `shadow.${idx + 1}`
  }

  const getShadowInfo = (shadow: ShadowToken): { type: string; role: string; confidence: string } => {
    const api = shadow as ShadowTokenAPI
    return {
      type: api.shadow_type || 'drop',
      role: api.semantic_role || 'medium',
      confidence: (api.confidence ? (api.confidence * 100).toFixed(0) : '0') + '%',
    }
  }

  return (
    <div className="shadow-list">
      {list.map((shadow, idx) => {
        const info = getShadowInfo(shadow)
        const label = getShadowLabel(shadow, idx)
        const style = getShadowStyle(shadow)
        const api = shadow as ShadowTokenAPI

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
                  <span className="prop-value">{info.type}</span>
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
                      className="color-swatch"
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
                  <span className="prop-value">{info.confidence}</span>
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
