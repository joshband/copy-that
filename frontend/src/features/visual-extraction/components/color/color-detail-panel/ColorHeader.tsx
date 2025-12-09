import { copyToClipboard } from '../../../../../utils/clipboard'
import type { ColorToken } from './types'

interface Props {
  color: ColorToken
  isAlias?: boolean
  aliasTargetId?: string
}

export function ColorHeader({ color, isAlias, aliasTargetId }: Props) {
  const featureNotes: string[] = []
  if (color.background_role) {
    featureNotes.push(`${color.background_role} background`)
  }
  if (color.contrast_category && color.contrast_category !== 'background') {
    featureNotes.push(`Contrast tagging (${color.contrast_category})`)
  }
  if (color.count != null && color.count > 1) {
    featureNotes.push(`OKLCH merged (${color.count} hits)`)
  }

  return (
    <div className="detail-header">
      <div className="header-top">
        <div className="color-display">
          <h2 className="color-name">{color.name}</h2>
          <div
            className="color-swatch-large"
            style={{ backgroundColor: color.hex }}
          />
          <div className="swatch-info-below">
            <code
              className="hex-clickable"
              onClick={() => void copyToClipboard(color.hex)}
              title="Click to copy"
            >
              {color.hex}
            </code>
            <span className="confidence-badge">
              {Math.round(color.confidence * 100)}% confidence
            </span>
          </div>
        </div>
        <div className="quick-codes-sidebar">
          <div
            className="code-item"
            onClick={() => void copyToClipboard(color.rgb)}
            title="Click to copy"
          >
            <span className="code-label">RGB</span>
            <code>{color.rgb}</code>
          </div>
          {color.hsl != null && color.hsl !== '' && (
            <div
              className="code-item"
              onClick={() => void copyToClipboard(color.hsl ?? '')}
              title="Click to copy"
            >
              <span className="code-label">HSL</span>
              <code>{color.hsl}</code>
            </div>
          )}
          {color.closest_css_named != null && color.closest_css_named !== '' && (
            <div
              className="code-item"
              onClick={() => void copyToClipboard(color.closest_css_named ?? '')}
              title="Click to copy"
            >
              <span className="code-label">CSS</span>
              <code>{color.closest_css_named}</code>
            </div>
          )}
        </div>
        <div className="header-info">
          {featureNotes.length > 0 && (
            <div className="feature-note">
              <span className="feature-note-title">New features</span>
              <div className="feature-note-items">
                {featureNotes.map((item) => (
                  <span key={item} className="feature-tag">
                    {item}
                  </span>
                ))}
              </div>
            </div>
          )}
          <div className="badge-row">
            {isAlias && aliasTargetId && (
              <span className="alias-badge">
                Alias of <code>{aliasTargetId}</code>
              </span>
            )}
            {color.background_role && (
              <span className={`background-badge ${color.background_role}`}>
                {color.background_role} background
              </span>
            )}
            {color.contrast_category && color.contrast_category !== 'background' && (
              <span className={`contrast-badge ${color.contrast_category}`}>
                Contrast: {color.contrast_category}
              </span>
            )}
            {color.count != null && color.count > 1 && (
              <span className="merge-badge">OKLCH merged</span>
            )}
          </div>
        </div>
        {color.count != null && color.count > 1 && (
          <div className="count-info">
            <span className="count-value">{color.count}x</span>
            <span className="count-label">in image</span>
          </div>
        )}
      </div>
    </div>
  )
}
