import './ColorPaletteSelector.css'

interface ColorToken {
  hex: string
  name: string
  confidence: number
  count?: number
}

interface Props {
  colors?: ColorToken[]
  selectedIndex: number | null
  onSelectColor: (index: number) => void
}

export function ColorPaletteSelector({ colors = [], selectedIndex, onSelectColor }: Props) {
  return (
    <div className="palette-selector">
      <h3 className="palette-title">Palette ({colors.length})</h3>
      <div className="palette-grid">
        {colors.map((color, index) => (
          <div
            key={index}
            className={`palette-swatch ${selectedIndex === index ? 'selected' : ''}`}
            onClick={() => onSelectColor(index)}
            title={`${color.name} - ${color.hex}`}
          >
            <div
              className="swatch-color"
              style={{ backgroundColor: color.hex }}
            >
              {color.count != null && color.count > 1 && (
                <span className="swatch-count">{color.count}x</span>
              )}
            </div>
            <div className="swatch-info">
              <code className="swatch-hex">{color.hex}</code>
              <span className="swatch-confidence">{Math.round(color.confidence * 100)}%</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
