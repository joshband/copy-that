import './ColorTokenDisplay.css'
import { ColorPaletteSelector } from './ColorPaletteSelector'
import { ColorDetailPanel } from './ColorDetailPanel'
import { useState } from 'react'
import { ColorToken } from '../types'

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
