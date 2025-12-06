export type ActiveTab = 'harmony' | 'accessibility' | 'picker' | 'variants'

export interface ColorToken {
  hex: string
  name: string
  semantic_names?: Record<string, unknown> | null
  tint_color?: string
  shade_color?: string
  tone_color?: string
  wcag_contrast_on_white?: number
  wcag_aa_compliant_text?: boolean
  wcag_aaa_compliant_text?: boolean
  colorblind_safe?: boolean
}

export interface PlaygroundSidebarProps {
  selectedColor: ColorToken | null
  isOpen: boolean
  onToggle: () => void
}
