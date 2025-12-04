import type { ColorToken } from '../../types'

interface ColorSwatchesProps {
  colors: ColorToken[]
}

export function ColorSwatches({ colors }: ColorSwatchesProps) {
  if (colors.length === 0) return null

  const getSemanticLabel = (color: ColorToken): string => {
    const label =
      typeof color.semantic_names === 'string'
        ? color.semantic_names
        : typeof color.semantic_names === 'object' && color.semantic_names
          ? Object.values(color.semantic_names)[0]
          : null
    return String(label || color.hex)
  }

  return (
    <div className="color-palette-preview">
      <h4>Palette at a Glance</h4>
      <div className="color-swatches">
        {colors.slice(0, 10).map((color, idx) => {
          const label = getSemanticLabel(color)
          return (
            <div key={idx} className="swatch-item" title={label}>
              <div
                className="swatch"
                style={{
                  backgroundColor: color.hex,
                  border:
                    color.hex.toLowerCase() === '#ffffff' || color.hex.toLowerCase() === '#fff'
                      ? '1px solid #ddd'
                      : 'none'
                }}
              />
              <span className="swatch-label">
                {label.split('_')[0] || color.hex.slice(1, 4).toUpperCase()}
              </span>
            </div>
          )
        })}
        {colors.length > 10 && (
          <div className="swatch-item more">
            <div className="swatch">+{colors.length - 10}</div>
          </div>
        )}
      </div>
    </div>
  )
}
