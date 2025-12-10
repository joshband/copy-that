import type { SectionType } from './types'

interface Props {
  section: SectionType
  icon: string
  title: string
  isExpanded: boolean
  onToggle: (section: SectionType) => void
}

export function SectionHeader({ section, icon, title, isExpanded, onToggle }: Props) {
  return (
    <button
      className="section-header"
      onClick={() => onToggle(section)}
    >
      <span className="section-icon">{icon}</span>
      <span>{title}</span>
      <span className="section-toggle">
        {isExpanded ? '▼' : '▶'}
      </span>
    </button>
  )
}
