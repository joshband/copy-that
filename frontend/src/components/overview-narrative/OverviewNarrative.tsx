import '../OverviewNarrative.css'
import type { OverviewNarrativeProps } from './types'
import { ColorSwatches } from './ColorSwatches'
import { MoodBoard } from './MoodBoard'
import { featureFlags } from '../../config/featureFlags'
import {
  usePaletteAnalysis,
  useEmotionalTone,
  useNarrative,
} from './hooks'

export function OverviewNarrative({
  colors,
  colorCount,
  aliasCount,
  spacingCount,
  multiplesCount,
  typographyCount,
  paletteSummary
}: OverviewNarrativeProps) {
  // Keep hooks for palette summary / mood; avoid unused-param lint on alias/multiples
  void aliasCount
  void multiplesCount
  const { temp, sat } = usePaletteAnalysis(colors)
  void temp
  void sat
  const emotional = useEmotionalTone(colors)
  const narrative = useNarrative(colors)
  const hasColors = colors.length > 0
  const hasAnyTokens = hasColors || spacingCount > 0 || typographyCount > 0

  // Upload lives in UploadPanel — avoid a second "Upload an image" empty state here.
  if (!hasAnyTokens) {
    return null
  }

  return (
    <div className="overview-narrative" data-testid="overview-narrative">
      {hasColors && <ColorSwatches colors={colors} />}

      <div className="narrative-story narrative-story--compact">
        <h3>Palette</h3>
        <p className="intro-text">
          {paletteSummary || narrative || `${colorCount} colors · ${emotional.emotion}`}
        </p>
      </div>

      {featureFlags.showMoodBoard && <MoodBoard colors={colors} />}
    </div>
  )
}
