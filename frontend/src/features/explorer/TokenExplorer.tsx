import { memo, useMemo, useState } from 'react'
import ColorTokenDisplay from '../../features/visual-extraction/components/color/ColorTokenDisplay'
import ColorsTable from '../../features/visual-extraction/components/color/ColorsTable'
import ColorGraphPanel from '../../features/visual-extraction/components/color/ColorGraphPanel'
import ShadowTokenList from '../../features/visual-extraction/components/shadow/shadows/ShadowTokenList'
import ShadowInspector from '../../features/visual-extraction/components/shadow/ShadowInspector'
import TypographyInspector from '../../features/visual-extraction/components/typography/TypographyInspector'
import { TypographyDetailCard } from '../../features/visual-extraction/components/typography/TypographyDetailCard'
import SpacingScalePanel from '../../features/visual-extraction/components/spacing/SpacingScalePanel'
import SpacingGraphList from '../../features/visual-extraction/components/spacing/SpacingGraphList'
import SpacingRuler from '../../features/visual-extraction/components/spacing/SpacingRuler'
import SpacingGapDemo from '../../features/visual-extraction/components/spacing/SpacingGapDemo'
import SpacingDetailCard from '../../features/visual-extraction/components/spacing/SpacingDetailCard'
import SpacingResponsivePreview from '../../features/visual-extraction/components/spacing/SpacingResponsivePreview'
import RelationsDebugPanel from '../../components/RelationsDebugPanel'
import TokenGraphPanel from '../../components/TokenGraphPanel'
import { TokenInspector } from '../../components/token-inspector'
import { useTokenGraphStore } from '../../store/tokenGraphStore'
import type { ColorToken } from '../../types'

type Tab =
  | 'overview'
  | 'colors'
  | 'spacing'
  | 'typography'
  | 'shadows'
  | 'lighting'
  | 'relations'
  | 'raw'

interface TokenExplorerProps {
  activeTab: Tab
  showDebug: boolean
}

export const TokenExplorer = memo(function TokenExplorer({ activeTab, showDebug }: TokenExplorerProps) {
  const legacyColors = useTokenGraphStore((s) => s.legacyColors())
  const legacySpacing = useTokenGraphStore((s) => s.legacySpacing())
  const typographyTokens = useTokenGraphStore((s) => s.typography)
  const graphColors = useMemo<ColorToken[]>(
    () =>
      legacyColors.map((c) => ({
        id: c.id,
        hex: c.hex,
        name: c.name ?? c.id,
        confidence: c.confidence ?? 0.5,
        rgb: '', // unused in most views
      })),
    [legacyColors],
  )

  const [showColorOverlay, setShowColorOverlay] = useState(false)
  const [showSpacingOverlay, setShowSpacingOverlay] = useState(false)
  const [showColorTable, setShowColorTable] = useState(false)

  const spacingTokensFallback =
    legacySpacing?.map((t) => ({
      id: t.name ?? `spacing-${t.value_px}`,
      name: t.name,
      value_px: t.value_px,
      value_rem: t.value_rem,
      multiplier: t.multiplier,
    })) ?? []

  if (activeTab === 'relations') {
    return (
      <section className="panel relations-panel">
        <RelationsDebugPanel />
      </section>
    )
  }

  if (activeTab === 'raw') {
    return (
      <section className="panel raw-panel">
        <TokenGraphPanel />
      </section>
    )
  }

  return (
    <>
      {activeTab === 'colors' && (
        <section className="panel colors-panel">
          <ColorTokenDisplay
            showOverlay={showColorOverlay}
            onToggleOverlay={() => setShowColorOverlay((s) => !s)}
            colors={graphColors}
            paletteSummary=""
            segmentedPalette={null}
            debugOverlay={null}
            showDebug={showDebug}
          />
          <ColorGraphPanel colors={graphColors} ramps={{}} segmentationResult={null} />
          <ColorsTable
            colors={graphColors}
            title="Extracted Colors"
            description="Colors from tokenGraphStore"
            showTable={showColorTable}
            onToggleTable={() => setShowColorTable((s) => !s)}
          />
        </section>
      )}

      {activeTab === 'spacing' && (
        <section className="panel spacing-panel">
          <SpacingScalePanel tokens={spacingTokensFallback} />
          <SpacingGraphList tokens={spacingTokensFallback} showOverlay={showSpacingOverlay} />
          <SpacingRuler tokens={spacingTokensFallback} />
          <SpacingGapDemo tokens={spacingTokensFallback} />
          <SpacingDetailCard tokens={spacingTokensFallback} />
          <SpacingResponsivePreview tokens={spacingTokensFallback} />
        </section>
      )}

      {activeTab === 'typography' && (
        <section className="panel typography-panel">
          <TypographyInspector typographyTokens={typographyTokens} />
          <TypographyDetailCard typographyTokens={typographyTokens} />
        </section>
      )}

      {activeTab === 'shadows' && (
        <section className="panel shadows-panel">
          <ShadowTokenList shadows={[]} />
          <ShadowInspector shadows={[]} />
        </section>
      )}

      {activeTab === 'overview' && (
        <section className="panel overview-panel">
          <TokenInspector componentMeta={null} />
          <TokenGraphPanel />
        </section>
      )}
    </>
  )
})
