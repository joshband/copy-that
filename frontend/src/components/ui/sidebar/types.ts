export interface PlaygroundSidebarProps {
  selectedColor?: any
  isOpen?: boolean
  onToggle?: () => void
}

export interface UIProps extends PlaygroundSidebarProps {}

export type SectionType = string
export interface LearningSidebarProps {
  isOpen?: boolean
  onToggle?: () => void
}
