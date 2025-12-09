interface WcagStandardsProps {
  contrast: number
  wcagLevels: {
    aaText: boolean
    aaaText: boolean
    aaNormal: boolean
    aaaNormal: boolean
  }
}

export function WcagStandards({ contrast, wcagLevels }: WcagStandardsProps) {
  return (
    <div className="wcag-standards">
      <div className={`standard ${wcagLevels.aaText ? 'pass' : 'fail'}`}>
        <span className="level">AA - Large Text</span>
        <span className="ratio">{wcagLevels.aaText ? '✓ Pass' : '✗ Fail'}</span>
        <p className="description">For body text larger than 18pt (or 14pt bold). Recommended minimum for readability.</p>
      </div>

      <div className={`standard ${wcagLevels.aaaText ? 'pass' : 'fail'}`}>
        <span className="level">AAA - Large Text</span>
        <span className="ratio">{wcagLevels.aaaText ? '✓ Pass' : '✗ Fail'}</span>
        <p className="description">Enhanced contrast for optimal readability. Recommended for critical content.</p>
      </div>

      <div className={`standard ${wcagLevels.aaNormal ? 'pass' : 'fail'}`}>
        <span className="level">AA - Normal Text</span>
        <span className="ratio">{wcagLevels.aaNormal ? '✓ Pass' : '✗ Fail'}</span>
        <p className="description">For regular body text (14-18pt). The most common use case.</p>
      </div>

      <div className={`standard ${wcagLevels.aaaNormal ? 'pass' : 'fail'}`}>
        <span className="level">AAA - Normal Text</span>
        <span className="ratio">{wcagLevels.aaaNormal ? '✓ Pass' : '✗ Fail'}</span>
        <p className="description">Enhanced contrast for normal-sized text. Ideal for accessibility.</p>
      </div>
    </div>
  )
}
