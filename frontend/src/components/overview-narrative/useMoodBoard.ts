import { useMemo } from 'react'
import type { ColorToken } from '../../types'
import type { MoodBoardVariant, MoodBoardTheme, VisualElement, AestheticReference } from './moodBoardTypes'
import { usePaletteAnalysis, useArtMovementClassification } from './hooks'
import type { TemperatureType, SaturationType, ArtMovement } from './types'

/**
 * Generates mood board variants based on extracted color tokens
 * Maps color characteristics to aesthetic themes, visual elements, and cultural references
 */
export function useMoodBoard(colors: ColorToken[]): MoodBoardVariant[] {
  const { temp, sat } = usePaletteAnalysis(colors)
  const movement = useArtMovementClassification(colors)

  return useMemo((): MoodBoardVariant[] => {
    const variants: MoodBoardVariant[] = []
    const dominantColors = colors.slice(0, 6).map(c => c.hex)

    // Variant 1: Primary aesthetic based on temperature + saturation
    const primaryTheme = generatePrimaryTheme(temp, sat, movement, colors)
    if (primaryTheme) {
      variants.push({
        id: 'primary',
        title: primaryTheme.name,
        subtitle: primaryTheme.description,
        theme: primaryTheme,
        dominantColors: dominantColors.slice(0, 3),
        vibe: primaryTheme.tags[0] || 'expressive'
      })
    }

    // Variant 2: Secondary aesthetic (complementary approach)
    const secondaryTheme = generateSecondaryTheme(temp, sat, movement, colors)
    if (secondaryTheme) {
      variants.push({
        id: 'secondary',
        title: secondaryTheme.name,
        subtitle: secondaryTheme.description,
        theme: secondaryTheme,
        dominantColors: dominantColors.slice(3, 6),
        vibe: secondaryTheme.tags[0] || 'balanced'
      })
    }

    return variants
  }, [colors, temp, sat, movement])
}

function generatePrimaryTheme(
  temp: TemperatureType,
  sat: SaturationType,
  movement: ArtMovement,
  colors: ColorToken[]
): MoodBoardTheme {
  // Retro-Futurism theme (warm + vivid + blues/golds like the user's example)
  if (temp === 'warm' && sat === 'vivid') {
    const hasBlues = colors.some(c => c.hue_family === 'blue' || c.hue_family === 'cyan')
    const hasGolds = colors.some(c =>
      c.hue_family === 'yellow' || c.hue_family === 'orange' || c.name?.toLowerCase().includes('gold')
    )

    if (hasBlues && hasGolds) {
      return {
        name: 'Retro-Futurism',
        description: 'Playful & tactile control objects meet Yves Klein blue',
        tags: ['retro-futurism', 'tactile', 'analog', 'mid-century', 'optimistic'],
        visualElements: [
          { type: 'object', description: 'Analog radios and oscilloscope screens', prominence: 'primary' },
          { type: 'shape', description: 'Resin-like controls and rounded knobs', prominence: 'primary' },
          { type: 'texture', description: 'Glossy surfaces with depth', prominence: 'secondary' },
          { type: 'composition', description: 'Mid-century geometric shapes', prominence: 'accent' }
        ],
        colorPalette: colors.slice(0, 5).map(c => c.hex),
        references: [
          {
            movement: 'International Klein Blue (IKB)',
            artist: 'Yves Klein',
            period: '1960s',
            characteristics: ['ultramarine blue', 'pure pigment', 'immaterial sensibility']
          },
          {
            movement: 'Retro-Futurism',
            period: '1950s-1970s',
            characteristics: ['optimistic technology', 'playful controls', 'tactile interfaces']
          }
        ]
      }
    }
  }

  // Vaporwave/Synth-wave theme (cool + vivid)
  if (temp === 'cool' && sat === 'vivid') {
    return {
      name: 'Synth-Wave Dreams',
      description: 'Electric blues meet neon warmth in digital landscapes',
      tags: ['vaporwave', 'synth-wave', 'digital', 'nostalgic', 'neon'],
      visualElements: [
        { type: 'composition', description: 'Grid landscapes with neon horizons', prominence: 'primary' },
        { type: 'pattern', description: 'Geometric grids and digital patterns', prominence: 'primary' },
        { type: 'texture', description: 'Glowing neon and metallic surfaces', prominence: 'secondary' },
        { type: 'shape', description: 'Circular sun/moon motifs', prominence: 'accent' }
      ],
      colorPalette: colors.slice(0, 5).map(c => c.hex),
      references: [
        {
          movement: 'Vaporwave Aesthetic',
          period: '2010s',
          characteristics: ['nostalgic digital', 'neon colors', 'retro technology']
        },
        {
          movement: 'Synth-wave',
          period: '1980s revival',
          characteristics: ['sunset gradients', 'grid landscapes', 'neon typography']
        }
      ]
    }
  }

  // Painterly/Expressionist theme (warm + any saturation with artistic qualities)
  if (temp === 'warm' && movement === 'Expressionism') {
    return {
      name: 'Painterly Expressionism',
      description: 'Van Gogh swirls meet emotional color fields',
      tags: ['painterly', 'expressive', 'emotional', 'artistic', 'textured'],
      visualElements: [
        { type: 'texture', description: 'Thick brushstrokes and swirling paint', prominence: 'primary' },
        { type: 'pattern', description: 'Van Gogh-inspired spiral motifs', prominence: 'primary' },
        { type: 'composition', description: 'Dynamic, kinetic movement', prominence: 'secondary' },
        { type: 'texture', description: 'Impasto textures and visible marks', prominence: 'accent' }
      ],
      colorPalette: colors.slice(0, 5).map(c => c.hex),
      references: [
        {
          movement: 'Post-Impressionism',
          artist: 'Vincent van Gogh',
          period: '1880s-1890s',
          characteristics: ['swirling brushwork', 'emotional color', 'visible texture']
        },
        {
          movement: 'Expressionism',
          period: 'Early 20th century',
          characteristics: ['emotional intensity', 'bold color', 'subjective vision']
        }
      ]
    }
  }

  // Bauhaus/Modernist theme (balanced + any)
  if (temp === 'balanced' || sat === 'balanced') {
    return {
      name: 'Bauhaus Geometry',
      description: 'Modernist circles meet structured color fields',
      tags: ['bauhaus', 'geometric', 'modernist', 'systematic', 'functional'],
      visualElements: [
        { type: 'shape', description: 'Primary shapes: circles, squares, triangles', prominence: 'primary' },
        { type: 'composition', description: 'Grid-based layouts', prominence: 'primary' },
        { type: 'pattern', description: 'Geometric patterns and repetition', prominence: 'secondary' },
        { type: 'texture', description: 'Flat color fields', prominence: 'accent' }
      ],
      colorPalette: colors.slice(0, 5).map(c => c.hex),
      references: [
        {
          movement: 'Bauhaus',
          period: '1919-1933',
          characteristics: ['form follows function', 'primary colors', 'geometric shapes']
        },
        {
          movement: 'De Stijl',
          artist: 'Piet Mondrian',
          period: '1917-1931',
          characteristics: ['primary colors', 'straight lines', 'asymmetric balance']
        }
      ]
    }
  }

  // Art Nouveau/Decorative theme (muted + warm)
  if (sat === 'muted' && temp === 'warm') {
    return {
      name: 'Art Nouveau Elegance',
      description: 'Klimt-inspired ornamental warmth',
      tags: ['art-nouveau', 'decorative', 'organic', 'ornamental', 'golden'],
      visualElements: [
        { type: 'pattern', description: 'Klimt-style spiral and organic patterns', prominence: 'primary' },
        { type: 'texture', description: 'Golden and metallic textures', prominence: 'primary' },
        { type: 'shape', description: 'Flowing, organic forms', prominence: 'secondary' },
        { type: 'composition', description: 'Decorative layering', prominence: 'accent' }
      ],
      colorPalette: colors.slice(0, 5).map(c => c.hex),
      references: [
        {
          movement: 'Art Nouveau',
          artist: 'Gustav Klimt',
          period: '1890s-1910s',
          characteristics: ['golden patterns', 'organic forms', 'decorative richness']
        },
        {
          movement: 'Vienna Secession',
          period: 'Early 1900s',
          characteristics: ['ornamental design', 'geometric-organic fusion', 'luxury materials']
        }
      ]
    }
  }

  // Default: Modern minimalism
  return {
    name: 'Modern Minimalism',
    description: 'Clean, contemporary design language',
    tags: ['modern', 'minimal', 'clean', 'contemporary', 'refined'],
    visualElements: [
      { type: 'shape', description: 'Simple geometric forms', prominence: 'primary' },
      { type: 'composition', description: 'Negative space as design element', prominence: 'primary' },
      { type: 'texture', description: 'Subtle material textures', prominence: 'secondary' }
    ],
    colorPalette: colors.slice(0, 5).map(c => c.hex),
    references: [
      {
        movement: 'Minimalism',
        period: '1960s-present',
        characteristics: ['reduction', 'essential elements', 'clarity']
      }
    ]
  }
}

function generateSecondaryTheme(
  temp: TemperatureType,
  sat: SaturationType,
  movement: ArtMovement,
  colors: ColorToken[]
): MoodBoardTheme | null {
  // Generate a complementary/contrasting theme

  // If primary is warm + vivid, make secondary cool + structured
  if (temp === 'warm' && sat === 'vivid') {
    return {
      name: 'Industrial Warmth',
      description: 'Analog hardware meets warm minimalism',
      tags: ['industrial', 'analog', 'hardware', 'tactile', 'warm-minimal'],
      visualElements: [
        { type: 'object', description: 'Vintage audio equipment', prominence: 'primary' },
        { type: 'texture', description: 'Metal and wood surfaces', prominence: 'secondary' },
        { type: 'shape', description: 'Knobs, dials, and interfaces', prominence: 'accent' }
      ],
      colorPalette: colors.slice(0, 5).map(c => c.hex),
      references: [
        {
          movement: 'Industrial Design',
          period: '1960s-1980s',
          characteristics: ['functional beauty', 'exposed mechanics', 'tactile controls']
        }
      ]
    }
  }

  // If primary is cool + vivid, make secondary warm + painterly
  if (temp === 'cool' && sat === 'vivid') {
    return {
      name: 'Dynamic Texture',
      description: 'Painterly movement with digital precision',
      tags: ['dynamic', 'textured', 'painterly', 'kinetic', 'expressive'],
      visualElements: [
        { type: 'texture', description: 'Swirling brushwork', prominence: 'primary' },
        { type: 'pattern', description: 'Organic flow patterns', prominence: 'secondary' },
        { type: 'composition', description: 'Asymmetric balance', prominence: 'accent' }
      ],
      colorPalette: colors.slice(0, 5).map(c => c.hex),
      references: [
        {
          movement: 'Abstract Expressionism',
          period: '1940s-1960s',
          characteristics: ['gestural brushwork', 'spontaneous creation', 'emotional intensity']
        }
      ]
    }
  }

  // If primary is balanced, make secondary more expressive
  if (temp === 'balanced' && sat === 'balanced') {
    return {
      name: 'Expressive Geometry',
      description: 'Structured forms with playful energy',
      tags: ['geometric', 'playful', 'structured', 'modern', 'expressive'],
      visualElements: [
        { type: 'shape', description: 'Dynamic geometric shapes', prominence: 'primary' },
        { type: 'composition', description: 'Playful arrangements', prominence: 'secondary' },
        { type: 'pattern', description: 'Rhythmic repetition', prominence: 'accent' }
      ],
      colorPalette: colors.slice(0, 5).map(c => c.hex),
      references: [
        {
          movement: 'Constructivism',
          period: '1920s-1930s',
          characteristics: ['geometric forms', 'dynamic composition', 'modern energy']
        }
      ]
    }
  }

  return null
}
