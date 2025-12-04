export type SectionType = 'pipeline' | 'theory' | 'naming' | 'tech' | 'resources'

export interface LearningSidebarProps {
  isOpen: boolean
  onToggle: () => void
}
