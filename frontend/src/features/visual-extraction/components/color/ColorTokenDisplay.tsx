import './ColorTokenDisplay.css'
import { ColorPaletteSelector } from './ColorPaletteSelector'
import { ColorDetailPanel } from './color-detail-panel'
import { useState, useMemo, useEffect } from 'react'
import { ColorRampMap, ColorRampEntry, ColorToken, SegmentedColor } from '../../../../types/index'
import { useTokenGraphStore } from '../../../../store/tokenGraphStore'
import { resolveW3CColorValue } from '../../../../utils/w3cColor'

interface Props {
  colors?: ColorToken[]
  // Support single token prop from TokenCard/registry pattern
  token?: Partial<ColorToken>
  ramps?: ColorRampMap
  debugOverlay?: string
  segmentedPalette?: SegmentedColor[]
  showDebugOverlay?: boolean
}

export default function ColorTokenDisplay({
  colors,
  token,
  ramps,
  debugOverlay,
  segmentedPalette,
  showDebugOverlay = false,
}: Props) {
  const graphColors = useTokenGraphStore((s: any) => s.colors)
  // Normalize to colors array - support both props patterns
  const normalizedColors = useMemo(() => {
    if (graphColors.length > 0) {
      const byId = new Map<string, any>(graphColors.map((c: any) => [String(c.id), c]))

      return graphColors.map((c: any) => {
        const raw = c.raw as any
        const rawRecord = raw && typeof raw === 'object' ? (raw as Record<string, unknown>) : {}
        const attributes =
          rawRecord.attributes && typeof rawRecord.attributes === 'object'
            ? (rawRecord.attributes as Record<string, unknown>)
            : undefined
        const extensions =
          rawRecord.$extensions && typeof rawRecord.$extensions === 'object'
            ? (rawRecord.$extensions as Record<string, unknown>)
            : undefined
        const getMeta = (key: string) => rawRecord[key] ?? attributes?.[key] ?? extensions?.[key]

        const resolvedValue =
          c.isAlias && c.aliasTargetId ? (byId.get(String(c.aliasTargetId))?.raw as any)?.$value : raw?.$value
        const resolved = resolveW3CColorValue(resolvedValue)

        const name =
          rawRecord.name ??
          attributes?.name ??
          (typeof rawRecord.$description === 'string' ? rawRecord.$description : undefined) ??
          String(c.id)
        const confidenceValue = getMeta('confidence')
        const confidence = typeof confidenceValue === 'number' ? confidenceValue : 0.5

        const countValue = getMeta('count')
        const count = typeof countValue === 'number' ? countValue : undefined
        const background_role = getMeta('background_role')
        const contrast_category = getMeta('contrast_category')
        const foreground_role = getMeta('foreground_role')
        const extraction_metadata = getMeta('extraction_metadata')
        const extractionMetadata =
          extraction_metadata && typeof extraction_metadata === 'object' ? extraction_metadata : undefined
        const design_intent = getMeta('design_intent')
        const semantic_names = getMeta('semantic_names')
        const category = getMeta('category')
        const temperature = getMeta('temperature')
        const is_neutral = getMeta('is_neutral')
        const prominence_percentage = getMeta('prominence_percentage')
        const histogram_significance = getMeta('histogram_significance')
        const hsl = getMeta('hsl')
        const closest_css_named = getMeta('closest_css_named')
        const saturation_level = getMeta('saturation_level')
        const lightness_level = getMeta('lightness_level')
        const closest_web_safe = getMeta('closest_web_safe')
        const delta_e_to_dominant = getMeta('delta_e_to_dominant')
        const tint_color = getMeta('tint_color')
        const shade_color = getMeta('shade_color')
        const tone_color = getMeta('tone_color')
        const harmony = getMeta('harmony')
        const wcag_contrast_on_white = getMeta('wcag_contrast_on_white')
        const wcag_contrast_on_black = getMeta('wcag_contrast_on_black')
        const wcag_aa_compliant_text = getMeta('wcag_aa_compliant_text')
        const wcag_aaa_compliant_text = getMeta('wcag_aaa_compliant_text')
        const wcag_aa_compliant_normal = getMeta('wcag_aa_compliant_normal')
        const wcag_aaa_compliant_normal = getMeta('wcag_aaa_compliant_normal')
        const colorblind_safe = getMeta('colorblind_safe')

        return {
          id: c.id,
          hex: resolved.hex,
          rgb: resolved.rgb,
          name,
          confidence,
          ...(count != null ? { count } : {}),
          ...(background_role !== undefined ? { background_role } : {}),
          ...(contrast_category !== undefined ? { contrast_category } : {}),
          ...(foreground_role !== undefined ? { foreground_role } : {}),
          ...(extractionMetadata !== undefined ? { extraction_metadata: extractionMetadata } : {}),
          ...(design_intent !== undefined ? { design_intent } : {}),
          ...(semantic_names !== undefined ? { semantic_names } : {}),
          ...(category !== undefined ? { category } : {}),
          ...(temperature !== undefined ? { temperature } : {}),
          ...(is_neutral !== undefined ? { is_neutral } : {}),
          ...(prominence_percentage !== undefined ? { prominence_percentage } : {}),
          ...(histogram_significance !== undefined ? { histogram_significance } : {}),
          ...(hsl !== undefined ? { hsl } : {}),
          ...(closest_css_named !== undefined ? { closest_css_named } : {}),
          ...(saturation_level !== undefined ? { saturation_level } : {}),
          ...(lightness_level !== undefined ? { lightness_level } : {}),
          ...(closest_web_safe !== undefined ? { closest_web_safe } : {}),
          ...(delta_e_to_dominant !== undefined ? { delta_e_to_dominant } : {}),
          ...(tint_color !== undefined ? { tint_color } : {}),
          ...(shade_color !== undefined ? { shade_color } : {}),
          ...(tone_color !== undefined ? { tone_color } : {}),
          ...(harmony !== undefined ? { harmony } : {}),
          ...(wcag_contrast_on_white !== undefined ? { wcag_contrast_on_white } : {}),
          ...(wcag_contrast_on_black !== undefined ? { wcag_contrast_on_black } : {}),
          ...(wcag_aa_compliant_text !== undefined ? { wcag_aa_compliant_text } : {}),
          ...(wcag_aaa_compliant_text !== undefined ? { wcag_aaa_compliant_text } : {}),
          ...(wcag_aa_compliant_normal !== undefined ? { wcag_aa_compliant_normal } : {}),
          ...(wcag_aaa_compliant_normal !== undefined ? { wcag_aaa_compliant_normal } : {}),
          ...(colorblind_safe !== undefined ? { colorblind_safe } : {}),
        } as unknown as ColorToken
      })
    }
    if (colors && colors.length > 0) {
      return colors
    }
    if (token) {
      return [token as ColorToken]
    }
    return []
  }, [colors, token, graphColors])

  const [selectedIndex, setSelectedIndex] = useState<number | null>(
    normalizedColors.length > 0 ? 0 : null
  )

  // Update selectedIndex when colors change
  useEffect(() => {
    if (normalizedColors.length > 0 && selectedIndex === null) {
      setSelectedIndex(0)
    } else if (normalizedColors.length === 0) {
      setSelectedIndex(null)
    } else if (selectedIndex !== null && selectedIndex >= normalizedColors.length) {
      setSelectedIndex(normalizedColors.length - 1)
    }
  }, [normalizedColors.length, selectedIndex])

  const selectedColor =
    selectedIndex !== null && normalizedColors.length > 0
      ? normalizedColors[selectedIndex]
      : null
  const selectedGraphMeta =
    selectedColor && graphColors.find((g: any) => g.id === selectedColor.id)
  const accentRampEntries = useMemo(() => {
    if (!ramps || Object.keys(ramps).length === 0) return []
    return Object.entries(ramps)
      .map(([id, entry]): { id: string; entry: ColorRampEntry } => ({ id, entry: entry as ColorRampEntry }))
      .sort((a, b) => {
        const ai = parseInt(a.id.split('.').pop() || '0', 10)
        const bi = parseInt(b.id.split('.').pop() || '0', 10)
        return ai - bi
      })
  }, [ramps])

  return (
    <div className="color-tokens layout-new">
      {/* Left: Palette Selector */}
      <aside className="palette-container">
        <ColorPaletteSelector
          colors={normalizedColors}
          selectedIndex={selectedIndex}
          onSelectColor={setSelectedIndex}
        />
        {segmentedPalette && segmentedPalette.length > 0 && (
          <div className="ramp-section">
            <div className="ramp-header">
              <div className="ramp-title">Segmented coverage</div>
              <div className="ramp-subtitle">Top clusters from CV segmentation</div>
            </div>
            <div className="segmentation-list">
              {segmentedPalette.slice(0, 6).map((seg) => (
                <div className="segmentation-row" key={`${seg.hex}-${seg.coverage}`}>
                  <div className="segmentation-swatch" style={{ background: seg.hex }} />
                  <div className="segmentation-meta">
                    <div className="segmentation-hex">{seg.hex}</div>
                    <div className="segmentation-bar">
                      <div
                        className="segmentation-fill"
                        style={{ width: `${Math.min(seg.coverage, 100)}%` }}
                      />
                    </div>
                    <div className="segmentation-coverage">{seg.coverage}%</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
        {accentRampEntries.length > 0 && (
          <div className="ramp-section">
            <div className="ramp-header">
              <div className="ramp-title">Accent ramp</div>
              <div className="ramp-subtitle">Light → dark state variants</div>
            </div>
            <div className="ramp-chips">
              {accentRampEntries.map(({ id, entry }) => {
                const resolved = resolveW3CColorValue(entry?.$value)
                const hex = resolved.alpha < 1 ? resolved.rgb : resolved.hex
                return (
                  <div className="ramp-chip" key={id}>
                    <div className="ramp-swatch" style={{ background: hex }} />
                    <span className="ramp-label">{id.split('.').pop()}</span>
                  </div>
                )
              })}
            </div>
          </div>
        )}
      </aside>

      {/* Right: Detail Panel */}
      <main className="detail-container">
        <ColorDetailPanel
          color={selectedColor}
          debugOverlay={showDebugOverlay ? debugOverlay : undefined}
          isAlias={selectedGraphMeta?.isAlias}
          aliasTargetId={selectedGraphMeta?.aliasTargetId}
        />
      </main>
    </div>
  )
}
