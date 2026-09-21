import { ContrastPanel } from './ContrastPanel'
import { calculateContrast } from './utils'

interface CustomBackgroundTabProps {
  hex: string
  customBackground: string
  onCustomBackgroundChange: (color: string) => void
}

export function CustomBackgroundTab({
  hex,
  customBackground,
  onCustomBackgroundChange,
}: CustomBackgroundTabProps) {
  const customContrast = calculateContrast(hex, customBackground)

  return (
    <>
      <div className="custom-input">
        <label htmlFor="bg-color">Choose a background color:</label>
        <input
          id="bg-color"
          type="color"
          value={customBackground}
          onChange={(e) => onCustomBackgroundChange(e.target.value)}
        />
        <span className="hex-display">{customBackground}</span>
      </div>

      <ContrastPanel
        hex={hex}
        backgroundColor={customBackground}
        contrast={customContrast}
        wcagLevels={{
          aaText: customContrast >= 3,
          aaaText: customContrast >= 4.5,
          aaNormal: customContrast >= 4.5,
          aaaNormal: customContrast >= 7,
        }}
        title="Custom Background"
      />
    </>
  )
}
