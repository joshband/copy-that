import type { ColorToken, SpacingToken } from '../color-science'
import {
  ColorDetailsPanel,
  ColorGrid,
  SpacingGrid,
  StatsPanel,
  useColorConversion,
} from '../color-science'
import type { ExtractionPanelProps } from './types'

/**
 * Displays extraction results: colors, spacing, and details
 */
export function ExtractionPanel({
  isExtracting,
  error,
  colors,
  spacingTokens,
  selectedColorIndex,
  extractorUsed,
  paletteDescription,
  spacingSummary,
  onSelectColor,
}: ExtractionPanelProps) {
  const { copyToClipboard } = useColorConversion()
  const selectedColor = selectedColorIndex !== null ? colors[selectedColorIndex] : null

  return (
    <main className="center-panel">
      {error && <div className="error-message">{error}</div>}

      {colors.length === 0 && !isExtracting && (
        <div className="empty-state">
          <p>Upload an image to extract and analyze colors</p>
        </div>
      )}

      {isExtracting && (
        <div className="loading-state">
          <div className="spinner" />
          <p>Processing through pipeline...</p>
        </div>
      )}

      {colors.length > 0 && (
        <>
          <StatsPanel colors={colors} extractorUsed={extractorUsed} paletteDescription={paletteDescription} />
          <ColorGrid
            colors={colors}
            selectedColorIndex={selectedColorIndex}
            onSelectColor={onSelectColor}
            onCopyHex={copyToClipboard}
          />
          <SpacingGrid spacingTokens={spacingTokens} spacingSummary={spacingSummary} />
        </>
      )}

      <aside className="right-panel">
        <ColorDetailsPanel selectedColor={selectedColor} paletteDescription={paletteDescription} />
      </aside>
    </main>
  )
}
