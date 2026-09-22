/** API / cache shapes for mood board variants (snake_case matches backend JSON). */

export interface VisualElement {
  type: string
  description: string
  prominence: string
}

export interface AestheticReference {
  movement: string
  artist?: string
  period?: string
  characteristics: string[]
}

export interface GeneratedImage {
  url: string
  prompt: string
  revised_prompt?: string
  provider?: string
  selection?: {
    provider?: string
    policy?: string
    scores?: Record<string, number>
    fallback_from?: string | null
  }
}

export interface MoodBoardTheme {
  name: string
  description: string
  tags: string[]
  visual_elements: VisualElement[]
  color_palette: string[]
  references: AestheticReference[]
  generated_images?: GeneratedImage[]
}

export interface MoodBoardVariant {
  id: string
  title: string
  subtitle: string
  theme: MoodBoardTheme
  dominant_colors: string[]
  vibe: string
}

/** Client-side heuristic theme shape (camelCase) used by useMoodBoard. */
export interface HeuristicMoodBoardTheme {
  name: string
  description: string
  tags: string[]
  visualElements: VisualElement[]
  colorPalette: string[]
  references: AestheticReference[]
}

export interface HeuristicMoodBoardVariant {
  id: string
  title: string
  subtitle: string
  theme: HeuristicMoodBoardTheme
  dominantColors: string[]
  vibe: string
}
