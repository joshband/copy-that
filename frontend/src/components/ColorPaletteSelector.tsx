import { useState } from 'react'
import type { ColorToken } from '../types'
import './ColorPaletteSelector.css'

interface Props{
  colors?: ColorToken[]
  selectedIndex: number | null
  onSelectColor: (index: number) => void
}

export function ColorPaletteSelector({ colors = [], selectedIndex, onSelectColor }: Props) {
  const [copiedIndex, setCopiedIndex] = useState<number | null>(null)

  const handleSwatchClick = (index: number, hex: string) => {
    onSelectColor(index)
    navigator.clipboard.writeText(hex)
    setCopiedIndex(index)
    setTimeout(() => setCopiedIndex(null), 1500)
  }

  return (
    <>
      <h3 className="palette-title">Palette ({colors.length})</h3>
      <div className="palette-grid">
        {colors.map((color, index) => (
          <div
            key={index}
            className={`palette-swatch ${selectedIndex === index ? 'selected' : ''} ${copiedIndex === index ? 'copied' : ''}`}
            onClick={() => handleSwatchClick(index, color.hex)}
            title={`${color.name} - ${color.hex} (click to copy)`}
          >
            <div
              className="swatch-color"
              style={{ backgroundColor: color.hex }}
            >
              {copiedIndex === index && <span className="copy-indicator">✓</span>}
              {color.count != null && color.count > 1 && (
                <span className="swatch-count">{color.count}x</span>
              )}
            </div>
            <div className="swatch-info">
              <code className="swatch-hex">{color.hex}</code>
              <span className="swatch-confidence">{Math.round(color.confidence * 100)}%</span>
              {(color.background_role || color.contrast_category || color.foreground_role || (color as any)?.extraction_metadata?.accent || (color as any)?.extraction_metadata?.state_role) && (
                <div className="swatch-badges">
                  {color.background_role && (
                    <span className="badge bg">{color.background_role} bg</span>
                  )}
                  {color.contrast_category && (
                    <span className={`badge contrast ${color.contrast_category}`}>
                      {color.contrast_category} contrast
                    </span>
                  )}
                  {color.foreground_role && (
                    <span className="badge fg">text</span>
                  )}
                  {(color as any)?.extraction_metadata?.accent && (
                    <span className="badge accent">accent</span>
                  )}
                  {(color as any)?.extraction_metadata?.state_role && (
                    <span className="badge state">{(color as any).extraction_metadata.state_role}</span>
                  )}
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </>
  )
}
