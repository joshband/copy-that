interface Props {
  isExpanded: boolean
}

export function TechSection({ isExpanded }: Props) {
  if (!isExpanded) return null

  return (
    <div className="section-content">
      <div className="tech-content">
        <div className="tech-item">
          <strong>Delta-E (CIEDE2000)</strong>
          <p>Perceptual color difference metric. Values: 0 (identical) - 100 (very different)</p>
        </div>
        <div className="tech-item">
          <strong>WCAG Contrast Ratio</strong>
          <p>How distinguishable two colors are. AA requires 4.5:1 for text, AAA requires 7:1</p>
        </div>
        <div className="tech-item">
          <strong>Color Spaces</strong>
          <p>RGB for display, HSL for design intent, Oklch for perceptual uniformity</p>
        </div>
        <div className="tech-item">
          <strong>Gamut Mapping</strong>
          <p>Ensures colors are displayable on sRGB screens</p>
        </div>
      </div>
    </div>
  )
}
