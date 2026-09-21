interface Props {
  isExpanded: boolean
}

export function NamingSection({ isExpanded }: Props) {
  if (!isExpanded) return null

  return (
    <div className="section-content">
      <div className="naming-content">
        <p className="naming-intro">
          Each color gets 5 semantic names for different contexts:
        </p>
        <ul className="naming-list">
          <li>
            <span className="naming-type">Simple</span>
            <span className="naming-example">red, blue, green</span>
          </li>
          <li>
            <span className="naming-type">Descriptive</span>
            <span className="naming-example">warm red, sky blue</span>
          </li>
          <li>
            <span className="naming-type">Emotional</span>
            <span className="naming-example">passionate, serene</span>
          </li>
          <li>
            <span className="naming-type">Technical</span>
            <span className="naming-example">#FF5733</span>
          </li>
          <li>
            <span className="naming-type">Vibrancy</span>
            <span className="naming-example">vivid, muted, desaturated</span>
          </li>
        </ul>
      </div>
    </div>
  )
}
