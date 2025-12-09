// Re-export ColorToken from main types (single source of truth)
import type { ColorToken } from '../../types'
export type { ColorToken }

export type ActiveTab = 'harmony' | 'accessibility' | 'picker' | 'variants'

export interface PlaygroundSidebarProps {
  selectedColor: ColorToken | null
  isOpen: boolean
  onToggle: () => void
}
