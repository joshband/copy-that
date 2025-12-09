import { ColorToken } from '../../../../types/index'
import './ColorPrimaryPreview.css'

interface Props {
  token: Partial<ColorToken>
}

/**
 * Minimal primary preview for color tokens.
 * Shows a single swatch with a subtle glow and optional accent chip.
 */
export function ColorPrimaryPreview({ token }: Props) {
  const hex = token.hex ?? '#cccccc'
  const name = token.name ?? 'Color'

  return (
    <div className="color-primary-preview">
      <div className="color-primary-swatch" style={{ backgroundColor: hex }}>
        <div className="color-primary-glow" />
      </div>
      <div className="color-primary-meta">
        <span className="color-primary-name">{name}</span>
        <code className="color-primary-hex">{hex}</code>
      </div>
    </div>
  )
}
