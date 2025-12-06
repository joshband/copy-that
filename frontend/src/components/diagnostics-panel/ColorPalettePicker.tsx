import type { PaletteEntry } from './types'

interface Props {
  palette: PaletteEntry[]
  selectedColor: string | null
  onColorSelect: (hex: string | null) => void
}

export function ColorPalettePicker({ palette, selectedColor, onColorSelect }: Props) {
  return (
    <div className="diagnostics-card">
      <div className="card-header">
        <h4>Color palette</h4>
        <span className="pill">coloraide</span>
      </div>
      <div className="palette-grid">
        {palette.map((entry) => (
          <button
            key={`${entry.hex}-${entry.label}`}
            className={`swatch${selectedColor === entry.hex ? ' is-active' : ''}`}
            style={{ background: entry.hex }}
            onClick={() => onColorSelect(selectedColor === entry.hex ? null : entry.hex)}
            title={`${entry.label} (${entry.hex})`}
          >
            <span className="swatch-hex">{entry.hex}</span>
            {entry.coverage != null && <span className="swatch-meta">{Math.round(entry.coverage)}%</span>}
          </button>
        ))}
        {!palette.length && <p className="muted">Palette not available yet.</p>}
      </div>
    </div>
  )
}
