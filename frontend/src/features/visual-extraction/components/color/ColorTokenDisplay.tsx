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
        const attributes = raw?.attributes && typeof raw.attributes === 'object' ? (raw.attributes as any) : undefined
        const extensions = raw?.$extensions && typeof raw.$extensions === 'object' ? (raw.$extensions as any) : undefined

        const resolvedValue =
          c.isAlias && c.aliasTargetId ? (byId.get(String(c.aliasTargetId))?.raw as any)?.$value : raw?.$value
        const resolved = resolveW3CColorValue(resolvedValue)

        const name =
          raw?.name ??
          attributes?.name ??
          (typeof raw?.$description === 'string' ? raw.$description : undefined) ??
          String(c.id)
        const confidence =
          raw?.confidence ??
          attributes?.confidence ??
          (typeof extensions?.confidence === 'number' ? extensions.confidence : undefined) ??
          0.5

        const count =
          raw?.count ?? attributes?.count ?? (typeof extensions?.count === 'number' ? extensions.count : undefined)
        const background_role =
          raw?.background_role ??
          attributes?.background_role ??
          (typeof extensions?.background_role === 'string' ? extensions.background_role : undefined)
        const contrast_category =
          raw?.contrast_category ??
          attributes?.contrast_category ??
          (typeof extensions?.contrast_category === 'string' ? extensions.contrast_category : undefined)
        const foreground_role =
          raw?.foreground_role ??
          attributes?.foreground_role ??
          (typeof extensions?.foreground_role === 'string' ? extensions.foreground_role : undefined)
        const extraction_metadata =
          raw?.extraction_metadata ??
          attributes?.extraction_metadata ??
          (extensions?.extraction_metadata && typeof extensions.extraction_metadata === 'object'
            ? (extensions.extraction_metadata as any)
            : undefined)

        return {
          id: c.id,
          hex: resolved.hex,
          rgb: resolved.rgb,
          name,
          confidence,
          ...(count != null ? { count } : {}),
          ...(background_role ? { background_role } : {}),
          ...(contrast_category ? { contrast_category } : {}),
          ...(foreground_role ? { foreground_role } : {}),
          ...(extraction_metadata ? { extraction_metadata } : {}),
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
