import { useState } from 'react'
import { CompactColorGrid } from './CompactColorGrid'
import { ColorDetailsPanel } from './ColorDetailsPanel'
import { PlaygroundSidebar } from './PlaygroundSidebar'
import './EducationalColorDisplay.css'

interface ColorToken {
  id?: number
  hex: string
  rgb?: string
  hsl?: string
  name: string
  semantic_names?: Record<string, string> | null
  confidence: number
  temperature?: string
  saturation_level?: string
  lightness_level?: string
  category?: string
  count?: number
  prominence_percentage?: number
  tint_color?: string
  shade_color?: string
  tone_color?: string
  wcag_contrast_on_white?: number
  wcag_contrast_on_black?: number
  wcag_aa_compliant_text?: boolean
  wcag_aaa_compliant_text?: boolean
  colorblind_safe?: boolean
}

interface Props {
  colors?: ColorToken[]
}

export default function EducationalColorDisplay({ colors = [] }: Props) {
  const [selectedColorIndex, setSelectedColorIndex] = useState<number | null>(
    colors.length > 0 ? 0 : null
  )

  const selectedColor = selectedColorIndex !== null && colors.length > 0 ? colors[selectedColorIndex] : null

  return (
    <div className="educational-display">
      {/* Left: Compact Grid (Focal) */}
      <main className="grid-column">
        <CompactColorGrid
          colors={colors}
          selectedId={selectedColorIndex}
          onSelectColor={(index) => setSelectedColorIndex(index)}
        />
      </main>

      {/* Right: Color Details + Playground */}
      <aside className="details-column">
        {/* Color Details */}
        <div className="details-section">
          <ColorDetailsPanel color={selectedColor} />
        </div>

        {/* Playground */}
        <div className="playground-section">
          <PlaygroundSidebar selectedColor={selectedColor} isOpen={true} onToggle={() => {}} />
        </div>
      </aside>
    </div>
  )
}
