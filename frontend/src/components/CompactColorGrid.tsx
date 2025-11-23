import { useState } from 'react'
import './CompactColorGrid.css'

interface ColorToken {
  id?: number
  hex: string
  rgb?: string
  name: string
  semantic_names?: Record<string, string> | null
  confidence: number
  temperature?: string
  saturation_level?: string
  lightness_level?: string
  category?: string
  count?: number
  prominence_percentage?: number
  tint_color?: string
  shade_color?: string
  tone_color?: string
}

interface Props {
  colors?: ColorToken[]
  selectedId?: number | null
  onSelectColor: (index: number) => void
}

export function CompactColorGrid({ colors = [], selectedId, onSelectColor }: Props) {
  const [copiedHex, setCopiedHex] = useState<string | null>(null)

  const getColorDisplayName = (color: ColorToken) => {
    // Use descriptive name from semantic_names if available
    if (color.semantic_names?.descriptive != null && color.semantic_names.descriptive !== '') {
      return color.semantic_names.descriptive
    }
    // Otherwise use the color name
    return color.name
  }

  const handleCopy = (hex: string, e: React.MouseEvent) => {
    e.stopPropagation()
    void navigator.clipboard.writeText(hex)
    setCopiedHex(hex)
    setTimeout(() => setCopiedHex(null), 2000)
  }

  return (
    <div className="compact-grid">
      <div className="grid-header">
        <h3>Palette ({colors.length})</h3>
        <p className="grid-subtitle">Click any color to explore details</p>
      </div>

      <div className="color-grid">
        {colors.map((color, index) => (
          <div
            key={color.id ?? index}
            className={`color-item ${selectedId === index ? 'selected' : ''}`}
            onClick={() => onSelectColor(index)}
          >
            {/* Swatch */}
            <div
              className="color-swatch"
              style={{ backgroundColor: color.hex }}
              title={color.hex}
            />

            {/* Inline Attributes */}
            <div className="color-info">
              <div className="color-name">{getColorDisplayName(color)}</div>
              <div className="color-hex">{color.hex}</div>
              <div className="color-confidence">{Math.round(color.confidence * 100)}%</div>

              {/* Context Tags */}
              <div className="color-tags">
                {color.temperature != null && color.temperature !== '' && (
                  <span className="tag temperature">{color.temperature}</span>
                )}
                {color.saturation_level != null && color.saturation_level !== '' && (
                  <span className="tag saturation">{color.saturation_level}</span>
                )}
              </div>

              {/* Copy Button */}
              <button
                className="copy-btn"
                onClick={(e) => handleCopy(color.hex, e)}
                title="Copy hex code"
              >
                {copiedHex === color.hex ? '✓' : '📋'}
              </button>
            </div>

            {/* Prominence Badge */}
            {color.count != null && color.count > 1 && (
              <div className="prominence-badge">{color.count}x</div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}
