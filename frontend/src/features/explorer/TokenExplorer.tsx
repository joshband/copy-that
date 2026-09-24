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
import LayoutTokenPanel from '../../features/visual-extraction/components/layout/LayoutTokenPanel'
import RelationsDebugPanel from '../../components/RelationsDebugPanel'
import TokenGraphPanel from '../../components/TokenGraphPanel'
import { OverviewNarrative } from '../../components/overview-narrative'
import { MoodBoard } from '../../components/overview-narrative/MoodBoard'
import { OverviewCard, OverviewStatGrid } from '../../components/overview'
import LightingAnalyzer from '../../components/LightingAnalyzer'
import RelationsTable from '../../components/RelationsTable'
import { TokenGraphDemo } from '../../shared'
import { DiagnosticsPanel } from '../../components/diagnostics-panel'
import { ProjectTokenExport } from '../../components/ProjectTokenExport'
import { TokenSourceChip } from '../../components/TokenSourceChip'
import ScienceArtifactsPanel from '../../features/visual-extraction/components/color/ScienceArtifactsPanel'
import GeometryArtifactsPanel from '../../components/GeometryArtifactsPanel'
import ShadowArtifactsPanel from '../../features/visual-extraction/components/shadow/ShadowArtifactsPanel'
import ShadowDiagnosticsPanel from '../../features/visual-extraction/components/shadow/ShadowDiagnosticsPanel'
import { useTokenGraphStore } from '../../store/tokenGraphStore'
import { featureFlags, type AppTab } from '../../config/featureFlags'
import type {
  ArtifactBundle,
  ColorRampMap,
  ColorToken,
  LightingAnalysis,
  SegmentedColor,
  SpacingExtractionResponse,
} from '../../types'
import type { LightingAnalysisResponse } from '../../types/shadowAnalysis'
import './TokenExplorer.css'

interface TokenExplorerProps {
  activeTab: AppTab
  projectId?: number | null
  showDebug: boolean
  lighting?: LightingAnalysis | null
  onLightingAnalysis?: (analysis: LightingAnalysis | null) => void
  imageBase64?: string | null
  ramps?: ColorRampMap
  segmentedPalette?: SegmentedColor[] | null
  paletteSummary?: string | null
  spacingResult?: SpacingExtractionResponse | null
  debugOverlay?: string | null
  scienceArtifacts?: ArtifactBundle | null
  shadowArtifacts?: ArtifactBundle | null
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
  projectId = null,
  showDebug,
  lighting,
  onLightingAnalysis,
  imageBase64,
  ramps,
  segmentedPalette,
  paletteSummary,
  spacingResult,
  debugOverlay,
  scienceArtifacts,
  shadowArtifacts,
}: TokenExplorerProps) {
  const {
    colors,
    spacing,
    shadows,
    typography: typographyTokens,
    layout,
    opacity,
    gradient,
    duration,
    cubicBezier,
    fontFamily,
    fontWeight,
    strokeStyle,
    border,
    transition,
    number: numberTokens,
    dimension,
  } = useTokenGraphStore(
    (s) => ({
      colors: s.colors,
      spacing: s.spacing,
      shadows: s.shadows,
      typography: s.typography,
      layout: s.layout,
      opacity: s.opacity,
      gradient: s.gradient,
      duration: s.duration,
      cubicBezier: s.cubicBezier,
      fontFamily: s.fontFamily,
      fontWeight: s.fontWeight,
      strokeStyle: s.strokeStyle,
      border: s.border,
      transition: s.transition,
      number: s.number,
      dimension: s.dimension,
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
        confidence: c.confidence,
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
      layoutCount: layout.length,
      opacityCount: opacity.length,
      gradientCount: gradient.length,
      durationCount: duration.length,
      easingCount: cubicBezier.length,
      aliasCount,
    }),
    [
      graphColors.length,
      spacingTokensFallback.length,
      typographyTokens.length,
      shadows.length,
      layout.length,
      opacity.length,
      gradient.length,
      duration.length,
      cubicBezier.length,
      aliasCount,
    ],
  )
  const hasSpacingTokens = spacing.length > 0 || spacingTokensFallback.length > 0
  const hasSpacingGraph = spacing.length > 0
  const spacingIsFallback =
    Boolean(
      spacingResult?.spacing_confidence_breakdown &&
        typeof spacingResult.spacing_confidence_breakdown.fallback === 'number' &&
        spacingResult.spacing_confidence_breakdown.fallback >= 1,
    ) || (spacingResult?.warnings ?? []).some((w) => /fallback/i.test(w))
  const spacingConfPct =
    typeof spacingResult?.extraction_confidence === 'number'
      ? Math.round(spacingResult.extraction_confidence * 100)
      : null
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
  const spacingWarnings = hasSpacingTokens
    ? [
        ...(spacingResult?.warnings ?? []),
        ...(spacingIsFallback
          ? ['Spacing used an unmeasured 4pt preset — verify against the layout.']
          : []),
      ]
    : ['No spacing tokens yet']

  if (featureFlags.showRelationsTab && activeTab === 'relations') {
    return (
      <section className="panel relations-panel">
        <RelationsTable />
        <RelationsDebugPanel />
      </section>
    )
  }

  if (featureFlags.showRawTab && activeTab === 'raw') {
    return (
      <section className="panel raw-panel">
        <TokenGraphPanel spacingResult={spacingResult} />
      </section>
    )
  }

  if (featureFlags.showLightingTab && activeTab === 'lighting') {
    return (
      <section className="panel lighting-panel">
        {lightingPanelData ? (
          <ShadowAnalysisPanel analysis={lightingPanelData} />
        ) : (
          <div className="empty-state">
            <p className="standin">No lighting analysis available yet.</p>
            <p className="standin">Lighting is parked for MVP; enable featureFlags.showLightingTab to use this view.</p>
          </div>
        )}
        <GeometryArtifactsPanel imageBase64={imageBase64 ?? undefined} />
      </section>
    )
  }

  if (featureFlags.showMoodBoard && activeTab === 'mood') {
    return (
      <section className="panel mood-panel" data-testid="mood-tab-panel">
        {graphColors.length > 0 ? (
          <MoodBoard colors={graphColors} sourceImageBase64={imageBase64 ?? null} />
        ) : (
          <div className="empty-state" data-testid="mood-tab-empty">
            <p className="standin">Extract a palette first, then generate mood boards here.</p>
          </div>
        )}
      </section>
    )
  }

  if (activeTab === 'export') {
    return (
      <section className="panel export-panel">
        <ProjectTokenExport
          projectId={projectId}
          colorCount={stats.colorCount}
          spacingCount={stats.spacingCount}
          typographyCount={stats.typographyCount}
          shadowCount={stats.shadowCount}
          gradientCount={stats.gradientCount}
        />
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
            showDebugOverlay={showDebug}
          />
          {showDebug && <ScienceArtifactsPanel artifacts={scienceArtifacts ?? null} />}
          {showDebug && (
            <details className="colors-advanced">
              <summary>Advanced color views</summary>
              <ColorGraphPanel />
              <ColorsTable fallback={fallbackColors} />
            </details>
          )}
        </section>
      )}

      {activeTab === 'spacing' && (
        <section className="panel spacing-panel">
          {hasSpacingTokens ? (
            <>
              <div className="spacing-card spacing-card--visual">
                <SpacingRuler
                  fallback={spacingTokensFallback}
                  extraction={spacingResult}
                />
                <SpacingGapDemo fallback={spacingTokensFallback} />
              </div>

              <SpacingSection
                title="Token metadata"
                subtitle="Semantic roles, usage, and derived scale info"
                defaultOpen={false}
              >
                <SpacingDetailCard fallback={spacingTokensFallback} />
              </SpacingSection>

              {hasResponsiveScales && (
                <SpacingSection
                  title="Responsive scaling"
                  subtitle="Breakpoint overrides and previews"
                  defaultOpen={false}
                >
                  <SpacingResponsivePreview fallback={spacingTokensFallback} />
                </SpacingSection>
              )}

              {showDebug && hasSpacingGraph && (
                <SpacingSection
                  title="Graph paths"
                  subtitle="Full token ids from the graph"
                  defaultOpen={false}
                >
                  <SpacingScalePanel extraction={spacingResult} />
                </SpacingSection>
              )}
            </>
          ) : (
            <SpacingRuler fallback={[]} extraction={spacingResult} />
          )}
          {hasSpacingTokens && spacingWarnings.length > 0 && (
            <div className="warning-banner">
              <span className="standin">{spacingWarnings.join(' ')}</span>
            </div>
          )}
        </section>
      )}

      {activeTab === 'typography' && (
        <section className="panel typography-panel">
          {typographyTokens.length > 0 ? (
            <>
              <TypographyInspector showDebug={showDebug} />
              {showDebug && <TypographyDetailCard />}
            </>
          ) : (
            <div className="empty-state">
              <h3 className="standin">No type styles detected</h3>
              <p className="standin">Extract an image to see typography tokens here.</p>
            </div>
          )}
        </section>
      )}

      {activeTab === 'shadows' && (
        <section className="panel shadows-panel">
          {showDebug && <ShadowArtifactsPanel artifacts={shadowArtifacts ?? null} />}
          {showDebug && <ShadowDiagnosticsPanel artifacts={shadowArtifacts ?? null} />}
          <ShadowTokenList shadows={shadowTokens} enableColorLinking={false} readOnly />
          {showDebug && <ShadowInspector />}
          {showDebug && opacity.length > 0 && (
            <div className="opacity-tokens" style={{ marginTop: '1.25rem' }}>
              <h3>Opacity tokens</h3>
              <p className="standin">Derived from unique shadow opacities.</p>
              <ul style={{ listStyle: 'none', padding: 0, margin: '0.75rem 0 0' }}>
                {opacity.map((token) => (
                  <li
                    key={token.id}
                    style={{
                      display: 'flex',
                      justifyContent: 'space-between',
                      gap: '1rem',
                      padding: '0.35rem 0',
                      borderBottom: '1px solid rgba(0,0,0,0.08)',
                    }}
                  >
                    <code>{token.id}</code>
                    <span>{token.value}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </section>
      )}

      {activeTab === 'shape' && (
        <section className="panel shape-panel">
          <LayoutTokenPanel showDebug={showDebug} />
          {showDebug && (gradient.length > 0 || duration.length > 0 || cubicBezier.length > 0) && (
            <div className="shape-addon motion-tokens">
              <h3>Motion</h3>
              <p className="standin">Gradients, durations, and easing from the extract.</p>
              {gradient.length > 0 && (
                <ul className="shape-token-list">
                  {gradient.map((token) => {
                    const stops = token.raw.$value?.stops ?? []
                    const label = stops
                      .map((s) => s.color)
                      .filter(Boolean)
                      .join(' → ')
                    return (
                      <li key={token.id} className="shape-token-row">
                        <code>{token.id}</code>
                        <span className="shape-token-row__meta">
                          <TokenSourceChip raw={token.raw as Record<string, unknown>} />
                          <span>{label || 'gradient'}</span>
                        </span>
                      </li>
                    )
                  })}
                </ul>
              )}
              {duration.length > 0 && (
                <ul className="shape-token-list">
                  {duration.map((token) => {
                    const val = token.raw.$value
                    const text =
                      typeof val === 'object' && val && 'value' in val
                        ? `${val.value}${val.unit ?? 'ms'}`
                        : String(val ?? '')
                    return (
                      <li key={token.id} className="shape-token-row">
                        <code>{token.id}</code>
                        <span className="shape-token-row__meta">
                          <TokenSourceChip raw={token.raw as Record<string, unknown>} />
                          <span>{text}</span>
                        </span>
                      </li>
                    )
                  })}
                </ul>
              )}
              {cubicBezier.length > 0 && (
                <ul className="shape-token-list">
                  {cubicBezier.map((token) => (
                    <li key={token.id} className="shape-token-row">
                      <code>{token.id}</code>
                      <span className="shape-token-row__meta">
                        <TokenSourceChip raw={token.raw as Record<string, unknown>} />
                        <span>
                          {Array.isArray(token.raw.$value)
                            ? token.raw.$value.join(', ')
                            : 'easing'}
                        </span>
                      </span>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          )}
          {showDebug &&
            (fontFamily.length > 0 ||
              fontWeight.length > 0 ||
              strokeStyle.length > 0 ||
              border.length > 0 ||
              transition.length > 0 ||
              dimension.length > 0 ||
              numberTokens.length > 0) && (
            <div className="shape-addon coverage-tokens">
              <h3>Derived types</h3>
              <p className="standin">Atomic tokens for export coverage.</p>
              <div className="shape-token-list">
                {[
                  ...fontFamily.map((t) => ({ id: t.id, label: String(t.raw.$value ?? ''), raw: t.raw })),
                  ...fontWeight.map((t) => ({ id: t.id, label: String(t.raw.$value ?? ''), raw: t.raw })),
                  ...strokeStyle.map((t) => ({ id: t.id, label: String(t.raw.$value ?? ''), raw: t.raw })),
                  ...border.map((t) => ({ id: t.id, label: 'border', raw: t.raw })),
                  ...transition.map((t) => ({ id: t.id, label: 'transition', raw: t.raw })),
                  ...dimension.map((t) => {
                    const v = t.raw.$value
                    const label =
                      typeof v === 'object' && v && 'value' in v
                        ? `${(v as { value: number; unit?: string }).value}${(v as { unit?: string }).unit ?? 'px'}`
                        : String(v ?? '')
                    return { id: t.id, label, raw: t.raw }
                  }),
                  ...numberTokens.map((t) => ({ id: t.id, label: String(t.raw.$value ?? ''), raw: t.raw })),
                ].map((row) => (
                  <div key={row.id} className="shape-token-row">
                    <code>{row.id}</code>
                    <span className="shape-token-row__meta">
                      <TokenSourceChip raw={row.raw as Record<string, unknown>} />
                      <span>{row.label}</span>
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </section>
      )}

      {activeTab === 'overview' && (
        <section className="panel overview-panel">
          {stats.colorCount > 0 ||
          stats.spacingCount > 0 ||
          stats.typographyCount > 0 ||
          stats.shadowCount > 0 ||
          showDebug ? (
            <div className="overview-grid">
              {(stats.colorCount > 0 ||
                stats.spacingCount > 0 ||
                stats.typographyCount > 0 ||
                stats.shadowCount > 0) && (
                <OverviewCard title="Snapshot" subtitle="Token families from this extract">
                  <OverviewStatGrid
                    stats={[
                      {
                        label: 'Colors',
                        value: `${stats.colorCount}`,
                        hint: aliasCount ? `${aliasCount} aliases` : undefined,
                      },
                      {
                        label: 'Spacing',
                        value: `${stats.spacingCount}`,
                        hint:
                          spacingConfPct != null
                            ? `${spacingConfPct}%${spacingIsFallback ? ' fallback' : ''}`
                            : undefined,
                      },
                      { label: 'Typography', value: `${stats.typographyCount}` },
                      { label: 'Shadows', value: `${stats.shadowCount}` },
                      { label: 'Shape', value: `${stats.layoutCount}` },
                      {
                        label: 'Other',
                        value: `${stats.opacityCount + stats.gradientCount + stats.durationCount}`,
                        hint: 'opacity · gradient · duration',
                      },
                    ]}
                  />
                </OverviewCard>
              )}
              {(stats.colorCount > 0 || stats.spacingCount > 0 || stats.typographyCount > 0) && (
                <OverviewCard title="Palette">
                  <OverviewNarrative
                    colors={graphColors}
                    colorCount={stats.colorCount}
                    aliasCount={aliasCount}
                    spacingCount={stats.spacingCount}
                    multiplesCount={spacingTokensFallback.filter((t) => t.multiplier != null).length}
                    typographyCount={stats.typographyCount}
                    paletteSummary={paletteSummary ?? null}
                  />
                </OverviewCard>
              )}
              {featureFlags.showLightingAnalyzer && (
                <OverviewCard title="Lighting">
                  <LightingAnalyzer
                    imageBase64={imageBase64 ?? undefined}
                    onAnalysisComplete={onLightingAnalysis ?? (() => {})}
                  />
                </OverviewCard>
              )}
              {featureFlags.showTokenGraphDemo && (
                <OverviewCard title="Token graph">
                  <TokenGraphDemo />
                </OverviewCard>
              )}
              {showDebug && (
                <OverviewCard title="Diagnostics">
                  <DiagnosticsPanel
                    colors={graphColors}
                    spacingResult={spacingResult}
                    spacingOverlay={spacingResult?.debug_overlay ?? null}
                    colorOverlay={debugOverlay ?? null}
                    segmentedPalette={segmentedPalette ?? null}
                    showAlignment={showDebug}
                    showPayload={showDebug}
                  />
                </OverviewCard>
              )}
            </div>
          ) : (
            <div className="overview-empty-cue standin">
              <p>Extract to explore colors, spacing, type, and shadows.</p>
            </div>
          )}
        </section>
      )}
    </>
  )
})

export default TokenExplorer
