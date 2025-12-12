import { useEffect, useState } from 'react'
import type { ColorToken } from '../../types'

interface MoodBoardProps {
  colors: ColorToken[]
}

interface VisualElement {
  type: string
  description: string
  prominence: string
}

interface AestheticReference {
  movement: string
  artist?: string
  period?: string
  characteristics: string[]
}

interface GeneratedImage {
  url: string
  prompt: string
  revised_prompt?: string
}

interface MoodBoardTheme {
  name: string
  description: string
  tags: string[]
  visual_elements: VisualElement[]
  color_palette: string[]
  references: AestheticReference[]
  generated_images: GeneratedImage[]
}

interface MoodBoardVariant {
  id: string
  title: string
  subtitle: string
  theme: MoodBoardTheme
  dominant_colors: string[]
  vibe: string
}

interface MoodBoardResponse {
  variants: MoodBoardVariant[]
  generation_time_ms: number
  models_used: {
    content_generation: string
    image_generation: string
  }
}

export function MoodBoard({ colors }: MoodBoardProps) {
  const [moodBoards, setMoodBoards] = useState<MoodBoardVariant[] | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [focusType, setFocusType] = useState<'material' | 'typography'>('material')

  useEffect(() => {
    if (colors.length === 0) return

    const fetchMoodBoards = async () => {
      setLoading(true)
      setError(null)

      try {
        // Prepare color data for API
        const colorInput = colors.slice(0, 10).map(c => ({
          hex: c.hex,
          name: c.name,
          temperature: c.temperature,
          saturation_level: c.saturation_level,
          hue_family: c.hue_family
        }))

        const response = await fetch('http://localhost:8000/api/v1/mood-board/generate', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            colors: colorInput,
            num_variants: 2,
            include_images: true,
            num_images_per_variant: 4,
            focus_type: focusType
          })
        })

        if (!response.ok) {
          throw new Error(`Failed to generate mood boards: ${response.statusText}`)
        }

        const data: MoodBoardResponse = await response.json()
        setMoodBoards(data.variants)
      } catch (err) {
        console.error('Error fetching mood boards:', err)
        setError(err instanceof Error ? err.message : 'Failed to load mood boards')
      } finally {
        setLoading(false)
      }
    }

    fetchMoodBoards()
  }, [colors, focusType])

  if (colors.length === 0) return null

  return (
    <div className="mood-board-section">
      <h3>AI-Curated Mood Boards</h3>

      {/* Focus Type Selector */}
      <div className="mood-board-focus-selector">
        <label>Board Focus:</label>
        <div className="focus-buttons">
          <button
            className={`focus-button ${focusType === 'material' ? 'active' : ''}`}
            onClick={() => setFocusType('material')}
          >
            Material & Texture
          </button>
          <button
            className={`focus-button ${focusType === 'typography' ? 'active' : ''}`}
            onClick={() => setFocusType('typography')}
          >
            Typography & Grid
          </button>
        </div>
      </div>

      <p className="mood-board-intro">
        {focusType === 'material'
          ? 'Explore physical materials, textures, and tactile qualities that embody your palette.'
          : 'Discover typographic systems, grid structures, and graphic language inspired by your colors.'}
      </p>

      {loading && (
        <div className="mood-board-loading">
          <div className="loading-spinner"></div>
          <p>Generating mood boards with Claude + DALL-E...</p>
        </div>
      )}

      {error && (
        <div className="mood-board-error">
          <p>❌ {error}</p>
          <p className="error-note">
            Note: Mood board generation requires ANTHROPIC_API_KEY and OPENAI_API_KEY environment variables.
          </p>
        </div>
      )}

      {moodBoards && moodBoards.length > 0 && (
        <div className="mood-board-variants">
          {moodBoards.map((variant, index) => (
            <MoodBoardVariant key={variant.id} variant={variant} index={index} />
          ))}
        </div>
      )}
    </div>
  )
}

interface MoodBoardVariantProps {
  variant: MoodBoardVariant
  index: number
}

function MoodBoardVariant({ variant, index }: MoodBoardVariantProps) {
  return (
    <div className="mood-board-variant">
      <div className="mood-board-header">
        <span className="mood-board-label">Board {index + 1}</span>
        <h4 className="mood-board-title">{variant.title}</h4>
        <p className="mood-board-subtitle">{variant.subtitle}</p>
        <span className="mood-board-vibe">Vibe: {variant.vibe}</span>
      </div>

      {/* Color swatches at top */}
      <div className="mood-board-colors">
        {variant.dominant_colors.map((color, i) => (
          <div key={i} className="mood-board-color-swatch" style={{ backgroundColor: color }} title={color} />
        ))}
      </div>

      {/* Tags/characteristics */}
      <div className="mood-board-tags">
        {variant.theme.tags.map((tag, i) => (
          <span key={i} className="mood-board-tag">
            {tag}
          </span>
        ))}
      </div>

      {/* AI-generated images */}
      {variant.theme.generated_images && variant.theme.generated_images.length > 0 && (
        <div className="mood-board-visual-grid">
          {variant.theme.generated_images.map((image, i) => (
            <div key={i} className="mood-board-image">
              <img src={image.url} alt={`${variant.title} inspiration ${i + 1}`} loading="lazy" />
            </div>
          ))}
        </div>
      )}

      {/* Visual elements description */}
      <div className="mood-board-elements">
        <h5>Visual Language</h5>
        <ul>
          {variant.theme.visual_elements.slice(0, 4).map((element, i) => (
            <li key={i} className={`element-${element.prominence}`}>
              <strong>{element.type}:</strong> {element.description}
            </li>
          ))}
        </ul>
      </div>

      {/* Aesthetic references */}
      <div className="mood-board-references">
        <h5>Cultural References</h5>
        {variant.theme.references.map((ref, i) => (
          <div key={i} className="mood-board-reference">
            <strong>{ref.movement}</strong>
            {ref.artist && <span className="reference-artist"> — {ref.artist}</span>}
            {ref.period && <span className="reference-period"> ({ref.period})</span>}
            <div className="reference-characteristics">
              {ref.characteristics.slice(0, 3).map((char, j) => (
                <span key={j} className="characteristic-tag">
                  {char}
                </span>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
