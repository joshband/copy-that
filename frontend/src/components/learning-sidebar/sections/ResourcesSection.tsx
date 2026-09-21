interface Props {
  isExpanded: boolean
}

export function ResourcesSection({ isExpanded }: Props) {
  if (!isExpanded) return null

  return (
    <div className="section-content">
      <div className="resources-content">
        <a href="#" className="resource-link">
          Color Theory Basics
        </a>
        <a href="#" className="resource-link">
          WCAG Accessibility Guide
        </a>
        <a href="#" className="resource-link">
          Design Tokens Specification
        </a>
        <a href="#" className="resource-link">
          Color Science Deep Dive
        </a>
      </div>
    </div>
  )
}
