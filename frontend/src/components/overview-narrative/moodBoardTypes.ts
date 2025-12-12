export interface MoodBoardTheme {
  name: string
  description: string
  tags: string[]
  visualElements: VisualElement[]
  colorPalette: string[]
  references: AestheticReference[]
}

export interface VisualElement {
  type: 'texture' | 'shape' | 'pattern' | 'object' | 'composition'
  description: string
  prominence: 'primary' | 'secondary' | 'accent'
}

export interface AestheticReference {
  movement: string
  artist?: string
  period?: string
  characteristics: string[]
}

export interface MoodBoardVariant {
  id: string
  title: string
  subtitle: string
  theme: MoodBoardTheme
  dominantColors: string[]
  vibe: string
}
