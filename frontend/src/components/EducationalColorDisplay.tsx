import { useState } from 'react'
import { CompactColorGrid } from './CompactColorGrid'
import { ColorDetailsPanel } from './ColorDetailsPanel'
import { PlaygroundSidebar } from './PlaygroundSidebar'
import type { ColorToken } from '../types'
import './EducationalColorDisplay.css'

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
