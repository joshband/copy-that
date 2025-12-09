import type { ColorToken } from '../../../types/index'
import { useContrastRatio } from '../hooks'

interface Props {
  selectedColor: ColorToken
  customBgColor: string
  onBackgroundChange: (color: string) => void
}

export function AccessibilityTab({
  selectedColor,
  customBgColor,
  onBackgroundChange,
}: Props) {
  const { ratio, isAACompliant, isAAACompliant } = useContrastRatio(
    selectedColor.hex,
    customBgColor
  )

  return (
    <div className="accessibility-content">
      <h4>WCAG Accessibility</h4>

      {/* Static Contrast */}
      <div className="contrast-section">
        <div className="contrast-item">
          <span className="label">On White:</span>
          <div className="contrast-value">
            {selectedColor.wcag_contrast_on_white?.toFixed(2) || 'N/A'}:1
          </div>
          {selectedColor.wcag_aa_compliant_text && (
            <span className="badge aa">AA ✓</span>
          )}
          {selectedColor.wcag_aaa_compliant_text && (
            <span className="badge aaa">AAA ✓</span>
          )}
        </div>
      </div>

      {/* Custom Background */}
      <div className="custom-bg-section">
        <label>Test on background:</label>
        <input
          type="color"
          value={customBgColor}
          onChange={(e) => onBackgroundChange(e.target.value)}
          className="color-input"
        />
        <div className="preview" style={{ backgroundColor: customBgColor }}>
          <span style={{ color: selectedColor.hex }}>Sample Text</span>
        </div>
        <div className="custom-contrast">
          <span>Contrast: {ratio.toFixed(2)}:1</span>
          {isAAACompliant && <span className="badge aaa">AAA ✓</span>}
          {isAACompliant && !isAAACompliant && <span className="badge aa">AA ✓</span>}
          {!isAACompliant && <span className="badge fail">⚠️ Low</span>}
        </div>
      </div>

      {/* Info */}
      <div className="a11y-info">
        <p>
          <strong>AA:</strong> Normal text needs 4.5:1 contrast
        </p>
        <p>
          <strong>AAA:</strong> Enhanced contrast needs 7:1
        </p>
      </div>
    </div>
  )
}
