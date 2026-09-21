import { WcagStandards } from './WcagStandards'

interface ContrastPanelProps {
  hex: string
  backgroundColor: string
  contrast: number
  wcagLevels: {
    aaText: boolean
    aaaText: boolean
    aaNormal: boolean
    aaaNormal: boolean
  }
  title: string
  isDarkBg?: boolean
}

export function ContrastPanel({
  hex,
  backgroundColor,
  contrast,
  wcagLevels,
  title,
  isDarkBg,
}: ContrastPanelProps) {
  return (
    <div className="contrast-panel">
      <div className="preview-area">
        <div
          style={{
            backgroundColor,
            padding: '40px',
            borderRadius: '8px',
            border: '2px solid #e2e8f0',
          }}
        >
          <p style={{ color: hex, margin: 0, fontSize: '18px', fontWeight: '500' }}>
            {isDarkBg ? 'This text is displayed on black' : 'This text is displayed on white'}
          </p>
          <p style={{ color: hex, margin: '8px 0 0 0', fontSize: '14px' }}>
            The contrast ratio is {contrast.toFixed(2)}:1
          </p>
        </div>
      </div>

      <div className="wcag-info">
        <h4>{title} - Contrast Ratio: {contrast.toFixed(2)}:1</h4>

        <WcagStandards contrast={contrast} wcagLevels={wcagLevels} />

        <div className="wcag-explanation">
          <h5>{isDarkBg ? 'Dark background considerations' : 'What do these standards mean?'}</h5>
          <ul>
            {isDarkBg ? (
              <>
                <li>Dark backgrounds require lighter text for readability.</li>
                <li>Light colors often achieve higher contrast on dark backgrounds.</li>
                <li>Be mindful of eye strain—too much contrast can also be uncomfortable.</li>
              </>
            ) : (
              <>
                <li>
                  <strong>AA (4.5:1 for normal, 3:1 for large):</strong> Minimum legal requirement in many jurisdictions.
                  Meets WCAG 2.0 AA level.
                </li>
                <li>
                  <strong>AAA (7:1 for normal, 4.5:1 for large):</strong> Enhanced contrast. Recommended for maximum
                  accessibility.
                </li>
                <li>
                  <strong>Large text:</strong> 18pt+ or 14pt+ bold fonts. Less demanding requirements.
                </li>
              </>
            )}
          </ul>
        </div>
      </div>
    </div>
  )
}
