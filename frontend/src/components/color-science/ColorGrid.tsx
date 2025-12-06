import React from 'react'
import { ColorToken, SpacingToken } from './types'

interface ColorGridProps {
  colors: ColorToken[]
  selectedColorIndex: number | null
  onSelectColor: (index: number) => void
  onCopyHex: (hex: string) => void
}

export function ColorGrid({ colors, selectedColorIndex, onSelectColor, onCopyHex }: ColorGridProps) {
  return (
    <section className="panel-card colors-section">
      <h2>Extracted Colors</h2>
      <div className="colors-grid">
        {colors.map((color, index) => (
          <div
            key={index}
            className={`color-card ${selectedColorIndex === index ? 'selected' : ''}`}
            onClick={() => onSelectColor(index)}
          >
            <div
              className="color-swatch"
              style={{ backgroundColor: color.hex }}
              onClick={(e) => {
                e.stopPropagation()
                onCopyHex(color.hex)
              }}
              title={`Click to copy ${color.hex}`}
            />
            <div className="color-info">
              <div className="color-name">{color.name}</div>
              <div className="color-hex mono">{color.hex}</div>
              <div className="color-tags">
                <span className="tag confidence">{Math.round(color.confidence * 100)}%</span>
                {color.harmony && <span className="tag harmony">{color.harmony}</span>}
                {color.temperature && <span className="tag temp">{color.temperature}</span>}
              </div>
            </div>
          </div>
        ))}
      </div>
    </section>
  )
}

interface SpacingGridProps {
  spacingTokens: SpacingToken[]
  spacingSummary: string
}

export function SpacingGrid({ spacingTokens, spacingSummary }: SpacingGridProps) {
  if (spacingTokens.length === 0) return null

  return (
    <section className="panel-card colors-section">
      <h2>Extracted Spacing Tokens</h2>
      <p className="palette-description">{spacingSummary}</p>
      <div className="colors-grid">
        {spacingTokens.map((t, idx) => (
          <div key={idx} className="color-card">
            <div className="color-info">
              <div className="color-name">{t.name}</div>
              <div className="color-hex mono">
                {t.value_px}px ({t.value_rem}rem)
              </div>
              <div className="color-tags">
                <span className="tag confidence">{Math.round(t.confidence * 100)}%</span>
                {t.semantic_role && <span className="tag temp">{t.semantic_role}</span>}
                {t.grid_aligned != null && (
                  <span className="tag {t.grid_aligned ? 'wcag-pass' : 'temp'}">
                    {t.grid_aligned ? 'Grid' : 'Off-grid'}
                  </span>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
    </section>
  )
}
