import './ColorTokenDisplay.css'
import { ColorPaletteSelector } from './ColorPaletteSelector'
import { ColorDetailPanel } from './ColorDetailPanel'
import { useState } from 'react'

interface ColorToken {
  id?: number
  project_id?: number
  extraction_job_id?: number
  hex: string
  rgb: string
  hsl?: string
  hsv?: string
  name: string
  design_intent?: string
  semantic_names?: Record<string, string> | null
  category?: string
  confidence: number
  harmony?: string
  temperature?: string
  saturation_level?: string
  lightness_level?: string
  usage?: string | string[]
  count?: number
  prominence_percentage?: number
  wcag_contrast_on_white?: number
  wcag_contrast_on_black?: number
  wcag_aa_compliant_text?: boolean
  wcag_aaa_compliant_text?: boolean
  wcag_aa_compliant_normal?: boolean
  wcag_aaa_compliant_normal?: boolean
  colorblind_safe?: boolean
  tint_color?: string
  shade_color?: string
  tone_color?: string
  closest_web_safe?: string
  closest_css_named?: string
  delta_e_to_dominant?: number
  is_neutral?: boolean
  kmeans_cluster_id?: number
  sam_segmentation_mask?: string
  clip_embeddings?: number[]
  histogram_significance?: number
  created_at?: string
}

interface Props {
  colors: ColorToken[]
}

export default function ColorTokenDisplay({ colors }: Props) {
  const [selectedIndex, setSelectedIndex] = useState<number | null>(
    colors.length > 0 ? 0 : null
  )

  const selectedColor = selectedIndex !== null ? colors[selectedIndex] : null

  return (
    <div className="color-tokens layout-new">
      {/* Left: Palette Selector */}
      <aside className="palette-container">
        <ColorPaletteSelector
          colors={colors}
          selectedIndex={selectedIndex}
          onSelectColor={setSelectedIndex}
        />
      </aside>

      {/* Right: Detail Panel */}
      <main className="detail-container">
        <ColorDetailPanel color={selectedColor} />
      </main>
    </div>
  )
}
