import { memo, useMemo, useState, type ReactNode, type SyntheticEvent } from 'react'
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
import type { ColorRampMap, ColorToken, LightingAnalysis, SegmentedColor, SpacingExtractionResponse } from '../../types'
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
  imageBase64?: string | null
  ramps?: ColorRampMap
  segmentedPalette?: SegmentedColor[] | null
  paletteSummary?: string | null
  spacingResult?: SpacingExtractionResponse | null
  debugOverlay?: string | null
}

interface SpacingSectionProps {
  title: string
  subtitle: string
  children: ReactNode
  defaultOpen?: boolean
}

function SpacingSection({ title, subtitle, children, defaultOpen = false }: SpacingSectionProps) {
  const [isOpen, setIsOpen] = useState(defaultOpen)
  const handleToggle = (event: SyntheticEvent<HTMLDetailsElement>) => {
    setIsOpen(event.currentTarget.open)
  }

  return (
    <details className="spacing-section" open={isOpen} onToggle={handleToggle}>
      <summary>
        <div className="spacing-section-summary">
          <span className="spacing-section-title">{title}</span>
          <span className="spacing-section-subtitle">{subtitle}</span>
        </div>
      </summary>
      <div className="spacing-section-body">{children}</div>
    </details>
  )
}

export const TokenExplorer = memo(function TokenExplorer({
  activeTab,
  showDebug,
  lighting,
  onLightingAnalysis,
  imageBase64,
  ramps,
  segmentedPalette,
  paletteSummary,
  spacingResult,
  debugOverlay,
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

  const legacyColors = useMemo(() => legacyColorsSelector(), [legacyColorsSelector, colors])
  const legacySpacing = useMemo(() => legacySpacingSelector(), [legacySpacingSelector, spacing])
  const colorExtras = useMemo(() => legacyColorExtrasSelector(), [legacyColorExtrasSelector, colors])

  const graphColors = useMemo<ColorToken[]>(
    () =>
      legacyColors.map((c) => ({
        id: c.id,
        hex: c.hex,
        name: c.name ?? c.id,
        confidence: c.confidence ?? 0.5,
        rgb: c.rgb ?? 'rgb(0, 0, 0)',
        temperature: c.temperature,
        saturation_level: c.saturation_level,
        lightness_level: c.lightness_level,
        harmony: c.harmony,
        semantic_names: c.semantic_names,
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
        confidence: t.confidence,
        semantic_role: t.semantic_role,
        spacing_type: t.spacing_type,
        grid_aligned: t.grid_aligned,
        tailwind_class: t.tailwind_class,
        prominence_percentage: t.prominence_percentage,
        scale_position: t.scale_position,
        related_tokens: t.related_tokens,
        usage: t.usage,
        responsive_scales: t.responsive_scales,
      })) ?? [],
    [legacySpacing],
  )

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
  const hasSpacingTokens = spacing.length > 0 || spacingTokensFallback.length > 0
  const hasSpacingGraph = spacing.length > 0
  const hasResponsiveScales = useMemo(() => {
    const hasFromGraph = spacing.some((token) => {
      const rawRecord = token.raw && typeof token.raw === 'object' ? (token.raw as Record<string, unknown>) : undefined
      if (!rawRecord) return false
      const attributes =
        rawRecord.attributes && typeof rawRecord.attributes === 'object'
          ? (rawRecord.attributes as Record<string, unknown>)
          : undefined
      const extensions =
        rawRecord.$extensions && typeof rawRecord.$extensions === 'object'
          ? (rawRecord.$extensions as Record<string, unknown>)
          : undefined
      const responsive = rawRecord.responsive_scales ?? attributes?.responsive_scales ?? extensions?.responsive_scales
      return Boolean(
        responsive &&
          typeof responsive === 'object' &&
          Object.keys(responsive as Record<string, unknown>).length > 0,
      )
    })
    const hasFromFallback = spacingTokensFallback.some(
      (token) => token.responsive_scales && Object.keys(token.responsive_scales).length > 0,
    )
    return hasFromGraph || hasFromFallback
  }, [spacing, spacingTokensFallback])
  const spacingWarnings = hasSpacingTokens ? [] : ['No spacing tokens yet']

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
        <TokenGraphPanel spacingResult={spacingResult} />
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
            <p className="standin">No lighting analysis available yet.</p>
            <p className="standin">Trigger analysis from the overview tab to populate this view.</p>
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
            <TokenGraphPanel spacingResult={spacingResult} />
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
            colors={graphColors}
            ramps={ramps}
            segmentedPalette={segmentedPalette ?? undefined}
            debugOverlay={debugOverlay ?? undefined}
            showDebugOverlay
          />
          <ColorGraphPanel />
          <ColorsTable fallback={fallbackColors} />
        </section>
      )}

      {activeTab === 'spacing' && (
        <section className="panel spacing-panel">
          {hasSpacingTokens && (
            <>
              <div className="spacing-section-grid">
                {hasSpacingGraph && (
                  <div className="spacing-card">
                    <SpacingScalePanel />
                  </div>
                )}
                <div className="spacing-card">
                  <SpacingRuler fallback={spacingTokensFallback} />
                  <SpacingGapDemo fallback={spacingTokensFallback} />
                </div>
              </div>

              <SpacingSection
                title="Token metadata"
                subtitle="Semantic roles, usage, and derived scale info"
                defaultOpen
              >
                <SpacingDetailCard fallback={spacingTokensFallback} />
              </SpacingSection>

              {hasResponsiveScales && (
                <SpacingSection
                  title="Responsive scaling"
                  subtitle="Breakpoint overrides and previews"
                  defaultOpen
                >
                  <SpacingResponsivePreview fallback={spacingTokensFallback} />
                </SpacingSection>
              )}
            </>
          )}
          {spacingWarnings.length > 0 && (
            <div className="warning-banner">
              <span className="standin">{spacingWarnings.join(' ')}</span>
            </div>
          )}
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
                paletteSummary={paletteSummary ?? null}
              />
            </div>
            <div className="overview-card">
              <LightingAnalyzer
                imageBase64={imageBase64 ?? undefined}
                onAnalysisComplete={onLightingAnalysis ?? (() => {})}
              />
            </div>
            <div className="overview-card">
              <TokenGraphDemo />
            </div>
            <div className="overview-card">
              <DiagnosticsPanel
                colors={graphColors}
                spacingResult={spacingResult}
                spacingOverlay={spacingResult?.debug_overlay ?? null}
                colorOverlay={debugOverlay ?? null}
                segmentedPalette={segmentedPalette ?? null}
                showAlignment={showDebug}
                showPayload={showDebug}
              />
            </div>
          </div>
        </section>
      )}
    </>
  )
})

export default TokenExplorer
