import { useMemo } from 'react'
import type { ColorToken } from '../../types'
import type {
  TemperatureType,
  SaturationType,
  ArtMovement,
  EmotionalTone,
  DesignEra
} from './types'

export function usePaletteAnalysis(colors: ColorToken[]) {
  return useMemo(() => {
    const analyzeTemperature = (): TemperatureType => {
      if (colors.length === 0) return 'balanced'
      const warmCount = colors.filter(c => c.temperature === 'warm').length
      const coolCount = colors.filter(c => c.temperature === 'cool').length
      const ratio = warmCount / (warmCount + coolCount || 1)
      if (ratio > 0.6) return 'warm'
      if (ratio < 0.4) return 'cool'
      return 'balanced'
    }

    const analyzeSaturation = (): SaturationType => {
      if (colors.length === 0) return 'medium'
      const highSat = colors.filter(c => c.saturation_level === 'high').length
      const lowSat = colors.filter(
        c => c.saturation_level === 'low' || c.saturation_level === 'desaturated'
      ).length
      const ratio = highSat / (highSat + lowSat || 1)
      if (ratio > 0.6) return 'vivid'
      if (ratio < 0.4) return 'muted'
      return 'balanced'
    }

    const temp = analyzeTemperature()
    const sat = analyzeSaturation()

    return { temp, sat }
  }, [colors])
}

export function useArtMovementClassification(colors: ColorToken[]) {
  const { temp, sat } = usePaletteAnalysis(colors)

  return useMemo((): ArtMovement => {
    const complexity = colors.length

    // Check most specific conditions first (temperature-specific vivid styles)
    if (sat === 'vivid' && temp === 'warm' && complexity >= 8) return 'Expressionism'
    if (sat === 'vivid' && temp === 'cool' && complexity >= 8) return 'Fauvism'
    // Then check general vivid conditions
    if (sat === 'vivid' && complexity >= 12) return 'Art Deco'
    if (sat === 'vivid' && temp === 'balanced') return 'Postmodernism'
    // Then muted conditions
    if (sat === 'muted' && complexity <= 4) return 'Minimalism'
    if (sat === 'muted' && temp === 'cool') return 'Swiss Modernism'
    if (temp === 'warm' && sat === 'muted') return 'Brutalism'
    // Then balanced conditions
    if (sat === 'balanced' && temp === 'balanced' && complexity >= 6) return 'Contemporary'
    // Finally simplicity-based conditions
    if (complexity <= 3) return 'Neo-Minimalism'
    return 'Modern Design'
  }, [temp, sat, colors.length])
}

export function useEmotionalTone(colors: ColorToken[]): EmotionalTone {
  const { temp, sat } = usePaletteAnalysis(colors)

  return useMemo((): EmotionalTone => {
    if (temp === 'warm' && sat === 'vivid') {
      return {
        emotion: 'energetic & passionate',
        description:
          'This palette radiates warmth and intensity. It commands attention and evokes excitement, creativity, and enthusiasm.'
      }
    }
    if (temp === 'cool' && sat === 'vivid') {
      return {
        emotion: 'calm & confident',
        description:
          'This palette conveys trust and serenity. The vibrant cool tones suggest innovation and forward-thinking without overwhelming.'
      }
    }
    if (sat === 'muted') {
      return {
        emotion: 'sophisticated & refined',
        description:
          'This palette whispers rather than shouts. Muted tones suggest maturity, elegance, and thoughtful restraint.'
      }
    }
    if (temp === 'balanced') {
      return {
        emotion: 'harmonious & accessible',
        description:
          'This palette achieves equilibrium. Balanced colors suggest inclusivity, versatility, and universal appeal.'
      }
    }
    return {
      emotion: 'expressive & dynamic',
      description: 'This palette tells a story through color harmony and intentional contrast.'
    }
  }, [temp, sat])
}

export function useDesignEra(colors: ColorToken[]): DesignEra {
  return useMemo((): DesignEra => {
    const complexity = colors.length

    if (complexity <= 2) return 'Monochromatic Focus'
    if (complexity <= 4) return 'Limited Palette Era'
    if (complexity <= 8) return 'Structured Harmony'
    if (complexity <= 12) return 'Rich Ecosystem'
    return 'Comprehensive System'
  }, [colors.length])
}

export function useNarrative(colors: ColorToken[]): string {
  const { temp } = usePaletteAnalysis(colors)

  return useMemo((): string => {
    if (temp === 'warm') {
      return `Your design language speaks in warm tones—inviting and approachable. This palette naturally encourages engagement and connection, making it ideal for experiences where warmth and approachability matter.`
    }
    if (temp === 'cool') {
      return `Your design language speaks in cool tones—calm and trustworthy. This palette naturally supports clarity and focus, making it ideal for experiences where reliability and professionalism matter.`
    }
    return `Your design language balances warmth and coolness. This versatile palette adapts to multiple contexts, supporting both energetic moments and calming ones with equal grace.`
  }, [temp])
}

export function useArtMovementDescription(movement: ArtMovement): string {
  const descriptions: Record<ArtMovement, string> = {
    'Expressionism': 'Expressionism—bold, emotional, and unafraid to make a statement.',
    'Fauvism': 'Fauvism—wild colors used in a liberated, intuitive way.',
    'Minimalism': 'Minimalism—intentional reduction to essential elements.',
    'Swiss Modernism': 'Swiss Modernism—clean, rational, and universally legible.',
    'Brutalism': 'Brutalism—raw, honest, and unapologetically bold.',
    'Art Deco': 'Art Deco—geometric precision meets visual luxury.',
    'Contemporary': 'Contemporary Design—balanced, accessible, forward-thinking.',
    'Neo-Minimalism': 'Neo-Minimalism—less is more, but with contemporary flair.',
    'Postmodernism': 'Postmodernism—thoughtful and intentional color strategy.',
    'Modern Design': 'Modern Design—thoughtful and intentional color strategy.'
  }
  return descriptions[movement]
}

export function useTemperatureDescription(temp: TemperatureType): string {
  const descriptions: Record<TemperatureType, string> = {
    'warm': 'Warm colors dominate your palette. They naturally draw attention and create a sense of immediacy and warmth.',
    'cool':
      'Cool colors define your palette. They suggest calm, trust, and create visual breathing room.',
    'balanced':
      'Your palette balances warm and cool equally. This versatility makes it adaptable to diverse contexts.'
  }
  return descriptions[temp]
}

export function useSaturationDescription(sat: SaturationType): string {
  const descriptions: Record<SaturationType, string> = {
    'vivid':
      'Vibrant and saturated colors create energy and visual impact. They demand attention and work well for primary actions and key moments.',
    'muted':
      'Muted, desaturated colors convey sophistication and calm. They provide visual rest and work beautifully for supporting elements.',
    'balanced':
      'Balanced saturation creates visual harmony. Neither too intense nor too subdued, these colors adapt naturally to their context.'
  }
  return descriptions[sat]
}
