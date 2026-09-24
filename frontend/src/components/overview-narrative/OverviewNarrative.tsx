import '../OverviewNarrative.css'
import type { OverviewNarrativeProps } from './types'
import { ColorSwatches } from './ColorSwatches'
export function OverviewNarrative({ colors, colorCount, spacingCount, typographyCount, paletteSummary }: OverviewNarrativeProps) {
  if (!colors.length && !spacingCount && !typographyCount) return null
  return <div className="overview-narrative" data-testid="overview-narrative">
    {colors.length > 0 && <ColorSwatches colors={colors} />}
    <p>{colorCount} color tokens, {spacingCount} spacing values, and {typographyCount} type styles are available. Inspect each family to review its values and origin.</p>
    {paletteSummary && <details><summary>Palette interpretation</summary><p>{paletteSummary}</p></details>}
  </div>
}
