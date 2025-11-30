import './ColorTokenDisplay.css'
import { ColorPaletteSelector } from './ColorPaletteSelector'
import { ColorDetailPanel } from './ColorDetailPanel'
import { useState, useMemo, useEffect } from 'react'
import { ColorRampMap, ColorToken, SegmentedColor } from '../types'
import { useTokenGraphStore } from '../store/tokenGraphStore'

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
  const graphColors = useTokenGraphStore((s) => s.colors)
  // Normalize to colors array - support both props patterns
  const normalizedColors = useMemo(() => {
    if (graphColors.length > 0) {
      return graphColors.map((c) => ({
        id: c.id,
        hex: (c.raw as any)?.$value?.hex ?? (c.raw as any)?.$value ?? '#ccc',
        rgb: '#',
        name: (c.raw as any)?.name ?? c.id,
        confidence: (c.raw as any)?.confidence ?? 0.5,
        isAlias: c.isAlias,
        aliasTargetId: c.aliasTargetId,
      })) as ColorToken[]
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
  const accentRampEntries = useMemo(() => {
    if (!ramps || Object.keys(ramps).length === 0) return []
    return Object.entries(ramps)
      .map(([id, entry]) => ({ id, entry }))
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
                const val = entry?.$value || {}
                const hex =
                  (val as any).hex ||
                  (val.l != null && val.c != null && val.h != null
                    ? `oklch(${(val.l as number).toFixed(3)} ${(val.c as number).toFixed(3)} ${(val.h as number).toFixed(1)})`
                    : '#ccc')
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
        />
      </main>
    </div>
  )
}
