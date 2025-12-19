import { memo, useMemo, useState } from 'react'
import { shallow } from 'zustand/shallow'
import ColorTokenDisplay from '../../features/visual-extraction/components/color/ColorTokenDisplay'
import ColorsTable from '../../features/visual-extraction/components/color/ColorsTable'
import ColorGraphPanel from '../../features/visual-extraction/components/color/ColorGraphPanel'
import ShadowTokenList from '../../features/visual-extraction/components/shadow/shadows/ShadowTokenList'
import ShadowInspector from '../../features/visual-extraction/components/shadow/ShadowInspector'
import ShadowAnalysisPanel from '../../features/visual-extraction/components/shadow/shadows/ShadowAnalysisPanel'
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
import { OverviewNarrative } from '../../components/overview-narrative'
import LightingAnalyzer from '../../components/LightingAnalyzer'
import RelationsTable from '../../components/RelationsTable'
import { TokenGraphDemo } from '../../shared'
import { DiagnosticsPanel } from '../../components/diagnostics-panel'
import { useTokenGraphStore } from '../../store/tokenGraphStore'
import type { ColorToken, LightingAnalysis } from '../../types'
import type { LightingAnalysisResponse } from '../../types/shadowAnalysis'

type Tab =
  | 'overview'
  | 'colors'
  | 'spacing'
  | 'typography'
  | 'shadows'
  | 'lighting'
  | 'export'
  | 'relations'
  | 'raw'

interface TokenExplorerProps {
  activeTab: Tab
  showDebug: boolean
  lighting?: LightingAnalysis | null
  onLightingAnalysis?: (analysis: LightingAnalysis | null) => void
}

export const TokenExplorer = memo(function TokenExplorer({
  activeTab,
  showDebug,
  lighting,
  onLightingAnalysis,
}: TokenExplorerProps) {
  const { colors, spacing, shadows, typography: typographyTokens } = useTokenGraphStore(
    (s) => ({
      colors: s.colors,
      spacing: s.spacing,
      shadows: s.shadows,
      typography: s.typography,
    }),
    shallow,
  )
  const legacyColorsSelector = useTokenGraphStore((s) => s.legacyColors, shallow)
  const legacySpacingSelector = useTokenGraphStore((s) => s.legacySpacing, shallow)
  const legacyColorExtrasSelector = useTokenGraphStore((s) => s.legacyColorExtras, shallow)

  const legacyColors = useMemo(() => legacyColorsSelector(), [legacyColorsSelector])
  const legacySpacing = useMemo(() => legacySpacingSelector(), [legacySpacingSelector])
  const colorExtras = useMemo(() => legacyColorExtrasSelector(), [legacyColorExtrasSelector])

  const [showColorOverlay, setShowColorOverlay] = useState(false)

  const graphColors = useMemo<ColorToken[]>(
    () =>
      legacyColors.map((c) => ({
        id: c.id,
        hex: c.hex,
        name: c.name ?? c.id,
        confidence: c.confidence ?? 0.5,
        rgb: 'rgb(0, 0, 0)',
      })),
    [legacyColors],
  )

  const fallbackColors = useMemo(
    () =>
      graphColors.map((c) => ({
        id: String(c.id ?? c.hex),
        hex: c.hex,
        name: c.name,
      })),
    [graphColors],
  )

  const spacingTokensFallback = useMemo(
    () =>
      legacySpacing?.map((t) => ({
        id: t.name ?? `spacing-${t.value_px}`,
        name: t.name,
        value_px: t.value_px,
        value_rem: t.value_rem,
        multiplier: t.multiplier,
      })) ?? [],
    [legacySpacing],
  )
  const spacingWarnings = spacingTokensFallback.length ? [] : ['No spacing tokens yet']

  const aliasCount = useMemo(() => {
    if (colors?.length) {
      return colors.filter((c) => c.isAlias).length
    }
    return graphColors.filter((c) => colorExtras?.[String(c.id)]?.isAlias).length
  }, [colors, graphColors, colorExtras])

  const shadowTokens = useMemo(
    () => shadows.map((s) => ({ id: s.id, ...(s.raw as any) })),
    [shadows],
  )

  const lightingPanelData = useMemo<LightingAnalysisResponse | null>(() => {
    if (!lighting) return null
    return {
      ...lighting,
      light_direction: null,
      analysis_source: 'client',
    } as unknown as LightingAnalysisResponse
  }, [lighting])

  const stats = useMemo(
    () => ({
      colorCount: graphColors.length,
      spacingCount: spacingTokensFallback.length,
      typographyCount: typographyTokens.length,
      shadowCount: shadows.length,
      aliasCount,
    }),
    [graphColors.length, spacingTokensFallback.length, typographyTokens.length, shadows.length, aliasCount],
  )

  if (activeTab === 'relations') {
    return (
      <section className="panel relations-panel">
        <RelationsTable />
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

  if (activeTab === 'lighting') {
    return (
      <section className="panel lighting-panel">
        {lightingPanelData ? (
          <ShadowAnalysisPanel analysis={lightingPanelData} />
        ) : (
          <div className="empty-state">
            <p>No lighting analysis available yet.</p>
            <p>Trigger analysis from the overview tab to populate this view.</p>
          </div>
        )}
      </section>
    )
  }

  if (activeTab === 'export') {
    return (
      <section className="panel export-panel">
        <div className="overview-grid">
          <div className="overview-card">
            <h3>Token snapshot</h3>
            <ul>
              <li>
                {stats.colorCount} colors ({aliasCount} aliases)
              </li>
              <li>{stats.spacingCount} spacing tokens</li>
              <li>{stats.typographyCount} typography tokens</li>
              <li>{stats.shadowCount} shadow tokens</li>
            </ul>
            <p className="caption">
              Internal graph uses DTCG/W3C shape. Public /api/v1 exports continue to use the flattened helper.
            </p>
          </div>
          <div className="overview-card">
            <h3>Export guidance</h3>
            <p>
              Use the flattened export helper for existing clients; keep W3C graph data for new generators.
              Verify request schemas before exposing /design-tokens/export/generator.
            </p>
            <p className="caption">
              Routes stay stable; this panel surfaces the graph currently in tokenGraphStore.
            </p>
          </div>
          <div className="overview-card">
            <TokenGraphPanel />
          </div>
        </div>
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
            segmentedPalette={undefined}
            debugOverlay={undefined}
            showDebug={showDebug}
          />
          <ColorGraphPanel />
          <ColorsTable fallback={fallbackColors} />
        </section>
      )}

      {activeTab === 'spacing' && (
        <section className="panel spacing-panel">
          <SpacingScalePanel />
          <SpacingGraphList />
          <SpacingRuler fallback={spacingTokensFallback} />
          <SpacingGapDemo fallback={spacingTokensFallback} />
          <SpacingDetailCard fallback={spacingTokensFallback} />
          <SpacingResponsivePreview fallback={spacingTokensFallback} />
          {spacingWarnings.length > 0 && <div className="warning-banner">{spacingWarnings.join(' ')}</div>}
        </section>
      )}

      {activeTab === 'typography' && (
        <section className="panel typography-panel">
          <TypographyInspector />
          <TypographyDetailCard />
        </section>
      )}

      {activeTab === 'shadows' && (
        <section className="panel shadows-panel">
          <ShadowTokenList shadows={shadowTokens} />
          <ShadowInspector />
        </section>
      )}

      {activeTab === 'overview' && (
        <section className="panel overview-panel">
          <div className="overview-grid">
            <div className="overview-card">
              <h3>Snapshot</h3>
              <p>
                {stats.colorCount} colors ({aliasCount} aliases)
              </p>
              <p>
                {stats.spacingCount} spacing · {stats.typographyCount} typography · {stats.shadowCount} shadows
              </p>
            </div>
            <div className="overview-card">
              <OverviewNarrative
                colors={graphColors}
                colorCount={stats.colorCount}
                aliasCount={aliasCount}
                spacingCount={stats.spacingCount}
                multiplesCount={spacingTokensFallback.filter((t) => t.multiplier != null).length}
                typographyCount={stats.typographyCount}
                paletteSummary={null}
              />
            </div>
            <div className="overview-card">
              <LightingAnalyzer imageBase64={undefined} onAnalysisComplete={onLightingAnalysis ?? (() => {})} />
            </div>
            <div className="overview-card">
              <TokenGraphDemo />
            </div>
            <div className="overview-card">
              <DiagnosticsPanel
                colors={graphColors}
                spacingResult={null}
                spacingOverlay={null}
                colorOverlay={null}
                segmentedPalette={null}
                showAlignment={false}
                showPayload={false}
              />
            </div>
          </div>
        </section>
      )}
    </>
  )
})
