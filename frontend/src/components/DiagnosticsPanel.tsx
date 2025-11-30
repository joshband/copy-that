import { useEffect, useMemo, useRef, useState } from 'react'
import './DiagnosticsPanel.css'
import type { ColorToken, SegmentedColor, SpacingExtractionResponse } from '../types'

type SpacingEntry = {
  value_px: number
  count: number
  orientation: 'horizontal' | 'vertical' | 'mixed'
}

type Props = {
  colors: ColorToken[]
  spacingResult?: SpacingExtractionResponse | null
  spacingOverlay?: string | null
  colorOverlay?: string | null
  segmentedPalette?: SegmentedColor[] | null
  showAlignment?: boolean
}

const FALLBACK_TOLERANCE = 2

const toDataUrl = (base64?: string | null) =>
  base64 ? `data:image/png;base64,${base64}` : null

const computeFallbackSpacings = (componentMetrics: SpacingExtractionResponse['component_spacing_metrics']) => {
  if (!componentMetrics?.length) return []
  const counts = new Map<number, number>()
  componentMetrics.forEach((metric) => {
    if (metric.neighbor_gap != null) {
      const rounded = Math.round(metric.neighbor_gap)
      counts.set(rounded, (counts.get(rounded) ?? 0) + 1)
    }
    if (metric.padding) {
      Object.values(metric.padding).forEach((val) => {
        const rounded = Math.round(val)
        counts.set(rounded, (counts.get(rounded) ?? 0) + 1)
      })
    }
  })
  return [...counts.entries()]
    .sort((a, b) => b[1] - a[1])
    .slice(0, 6)
    .map<SpacingEntry>(([value_px, count]) => ({
      value_px,
      count,
      orientation: 'mixed',
    }))
}

export default function DiagnosticsPanel({
  colors,
  spacingResult,
  spacingOverlay,
  colorOverlay,
  segmentedPalette,
  showAlignment = true,
}: Props) {
  const [selectedSpacing, setSelectedSpacing] = useState<number | null>(null)
  const [selectedComponent, setSelectedComponent] = useState<number | null>(null)
  const [selectedColor, setSelectedColor] = useState<string | null>(null)
  const [showAlignmentLines, setShowAlignmentLines] = useState(false)

  const componentMetrics = spacingResult?.component_spacing_metrics ?? []
  const commonSpacings: SpacingEntry[] = useMemo(() => {
    if (spacingResult?.common_spacings?.length) {
      return spacingResult.common_spacings
    }
    return computeFallbackSpacings(componentMetrics)
  }, [componentMetrics, spacingResult?.common_spacings])

  const palette = useMemo(() => {
    if (segmentedPalette?.length) {
      return segmentedPalette
        .slice(0, 10)
        .map((seg, idx) => ({ hex: seg.hex, coverage: seg.coverage, label: `Segment ${idx + 1}` }))
    }
    return colors.slice(0, 10).map((c, idx) => ({
      hex: c.hex,
      coverage: c.prominence_percentage ?? 0,
      label: c.name ?? `Color ${idx + 1}`,
    }))
  }, [colors, segmentedPalette])

  const overlaySrc = toDataUrl(spacingOverlay ?? spacingResult?.debug_overlay) ?? toDataUrl(colorOverlay)
  const overlayImgRef = useRef<HTMLImageElement | null>(null)
  const [dimensions, setDimensions] = useState({
    naturalWidth: 0,
    naturalHeight: 0,
    clientWidth: 0,
    clientHeight: 0,
  })

  useEffect(() => {
    const img = overlayImgRef.current
    if (!img) return undefined
    const update = () =>
      setDimensions({
        naturalWidth: img.naturalWidth || 1,
        naturalHeight: img.naturalHeight || 1,
        clientWidth: img.clientWidth || 1,
        clientHeight: img.clientHeight || 1,
      })
    update()
    window.addEventListener('resize', update)
    return () => window.removeEventListener('resize', update)
  }, [overlaySrc])

  const matchingBoxes = useMemo(() => {
    if (!componentMetrics.length) return []
    const byGap = selectedSpacing != null
      ? componentMetrics
          .map((metric, idx) => ({ metric, idx }))
          .filter(
            ({ metric }) =>
              metric.neighbor_gap != null &&
              Math.abs(Math.round(metric.neighbor_gap) - (selectedSpacing ?? 0)) <= FALLBACK_TOLERANCE,
          )
      : []
    const bySelection =
      selectedComponent != null
        ? componentMetrics
            .map((metric, idx) => ({ metric, idx }))
            .filter(({ idx }) => idx === selectedComponent)
        : []
    const combined = [...byGap, ...bySelection]
    const unique = new Map<number, { metric: (typeof componentMetrics)[number]; idx: number }>()
    combined.forEach((entry) => {
      if (!unique.has(entry.idx)) unique.set(entry.idx, entry)
    })
    return [...unique.values()]
  }, [componentMetrics, selectedComponent, selectedSpacing])

  const renderBox = (box: [number, number, number, number]) => {
    if (!dimensions.naturalWidth || !dimensions.naturalHeight) return null
    const [x, y, w, h] = box
    const scaleX = dimensions.clientWidth / dimensions.naturalWidth
    const scaleY = dimensions.clientHeight / dimensions.naturalHeight
    return {
      left: x * scaleX,
      top: y * scaleY,
      width: Math.max(w * scaleX, 2),
      height: Math.max(h * scaleY, 2),
    }
  }

  const alignmentLines = useMemo(() => {
    if (!spacingResult?.alignment || !dimensions.naturalWidth || !dimensions.naturalHeight) return []
    const sx = dimensions.clientWidth / dimensions.naturalWidth
    const sy = dimensions.clientHeight / dimensions.naturalHeight
    const lines: Array<{ orientation: 'vertical' | 'horizontal'; pos: number }> = []
    const addLines = (vals: number[] | undefined, orientation: 'vertical' | 'horizontal') => {
      if (!vals) return
      vals.forEach((v) => lines.push({ orientation, pos: v }))
    }
    addLines(spacingResult.alignment.left as number[] | undefined, 'vertical')
    addLines(spacingResult.alignment.center_x as number[] | undefined, 'vertical')
    addLines(spacingResult.alignment.right as number[] | undefined, 'vertical')
    addLines(spacingResult.alignment.top as number[] | undefined, 'horizontal')
    addLines(spacingResult.alignment.center_y as number[] | undefined, 'horizontal')
    addLines(spacingResult.alignment.bottom as number[] | undefined, 'horizontal')
    return lines.map((line) => {
      if (line.orientation === 'vertical') {
        return {
          orientation: 'vertical' as const,
          style: { left: line.pos * sx },
        }
      }
      return {
        orientation: 'horizontal' as const,
        style: { top: line.pos * sy },
      }
    })
  }, [dimensions.clientHeight, dimensions.clientWidth, dimensions.naturalHeight, dimensions.naturalWidth, spacingResult?.alignment])

  const payloadInfo = useMemo(() => {
    const items: Array<{ label: string; value: string }> = []
    items.push({ label: 'components', value: String(componentMetrics.length || 0) })
    items.push({ label: 'common spacings', value: String(commonSpacings.length || 0) })
    if (spacingResult?.alignment) {
      const totalLines = Object.values(spacingResult.alignment).reduce(
        (sum, vals) => sum + ((vals as number[] | undefined)?.length ?? 0),
        0,
      )
      items.push({ label: 'alignment lines', value: `${totalLines} lines` })
    }
    if (spacingResult?.gap_clusters) {
      const gx = spacingResult.gap_clusters.x?.join(', ') || '—'
      const gy = spacingResult.gap_clusters.y?.join(', ') || '—'
      items.push({ label: 'gap clusters', value: `x: ${gx} | y: ${gy}` })
    }
    items.push({
      label: 'debug overlay',
      value: spacingResult?.debug_overlay ? 'yes' : 'no',
    })
    items.push({
      label: 'warnings',
      value: spacingResult?.warnings?.length ? spacingResult.warnings.join(' | ') : 'none',
    })
    return items
  }, [commonSpacings.length, componentMetrics.length, spacingResult?.alignment, spacingResult?.debug_overlay, spacingResult?.gap_clusters, spacingResult?.warnings])

  return (
    <div className="diagnostics">
      <div className="diagnostics-header">
        <div>
          <p className="eyebrow">Diagnostics</p>
          <h3>Spacing & color QA</h3>
          <p className="diagnostics-subtitle">
            Inspect common gaps and the extracted palette. Click a spacing value to highlight
            matching regions; click a component or swatch to focus details.
          </p>
        </div>
      </div>

      <div className="diagnostics-grid">
        <div className="diagnostics-card">
          <div className="card-header">
            <h4>Spacing diagnostics</h4>
            <span className="pill">adjacency</span>
          </div>
          {showAlignment && spacingResult?.alignment && (
            <div className="alignment-summary">
              <div className="alignment-row">
                <span className="pill light">vertical lines</span>
                <span className="alignment-values">
                  {['left', 'center_x', 'right']
                    .map((key) => ({
                      key,
                      vals: spacingResult.alignment?.[key] as number[] | undefined,
                    }))
                    .filter((item) => item.vals?.length)
                    .map((item) => `${item.key}: ${item.vals?.join(', ')}`)
                    .join(' • ')}
                </span>
              </div>
              <div className="alignment-row">
                <span className="pill light">horizontal lines</span>
                <span className="alignment-values">
                  {['top', 'center_y', 'bottom']
                    .map((key) => ({
                      key,
                      vals: spacingResult.alignment?.[key] as number[] | undefined,
                    }))
                    .filter((item) => item.vals?.length)
                    .map((item) => `${item.key}: ${item.vals?.join(', ')}`)
                    .join(' • ')}
                </span>
              </div>
              <div className="alignment-row">
                <label className="switch">
                  <input
                    type="checkbox"
                    checked={showAlignmentLines}
                    onChange={() => setShowAlignmentLines((s) => !s)}
                  />
                  <span className="slider" />
                </label>
                <span className="alignment-values">
                  {showAlignmentLines ? 'Hide alignment overlay' : 'Show alignment overlay'}
                </span>
              </div>
              {spacingResult.gap_clusters && (
                <div className="alignment-row">
                  <span className="pill light">gap clusters</span>
                  <span className="alignment-values">
                    x: {(spacingResult.gap_clusters.x || []).join(', ') || '—'} | y:{' '}
                    {(spacingResult.gap_clusters.y || []).join(', ') || '—'}
                  </span>
                </div>
              )}
            </div>
          )}
          <div className="payload-summary">
            <div className="card-header small">
              <h4>API payload</h4>
              <span className="pill light">debug</span>
            </div>
            <ul className="payload-list">
              {payloadInfo.map((item) => (
                <li key={item.label}>
                  <span className="payload-label">{item.label}</span>
                  <span className="payload-value">{item.value}</span>
                </li>
              ))}
            </ul>
          </div>
          <div className="spacing-chip-row">
            {commonSpacings.length ? (
              commonSpacings.map((entry) => (
                <button
                  key={entry.value_px}
                  className={`spacing-chip${selectedSpacing === entry.value_px ? ' is-active' : ''}`}
                  onClick={() => setSelectedSpacing(selectedSpacing === entry.value_px ? null : entry.value_px)}
                >
                  <span className="chip-value">{entry.value_px}px</span>
                  <span className="chip-meta">
                    {entry.orientation} • {entry.count}×
                  </span>
                </button>
              ))
            ) : (
              <p className="muted">No spacing diagnostics available yet.</p>
            )}
          </div>

          {componentMetrics.length ? (
            <div className="component-scroll">
              {componentMetrics.slice(0, 8).map((metric, idx) => (
                <button
                  key={metric.index ?? idx}
                  className={`component-row${selectedComponent === idx ? ' is-active' : ''}`}
                  onClick={() => setSelectedComponent(selectedComponent === idx ? null : idx)}
                >
                  <div>
                    <div className="row-title">Component #{(metric.index ?? idx) + 1}</div>
                    <div className="row-subtitle">
                      Padding {metric.padding ? `${metric.padding.top}/${metric.padding.right}/${metric.padding.bottom}/${metric.padding.left}px` : '—'}
                    </div>
                  </div>
                  <div className="row-metrics">
                    {metric.neighbor_gap != null && <span>{Math.round(metric.neighbor_gap)}px gap</span>}
                    <span className="pill light">{(metric.padding_confidence ?? 0).toFixed(2)}c</span>
                  </div>
                </button>
              ))}
            </div>
          ) : (
            <p className="muted">Run spacing extraction to see component metrics.</p>
          )}
        </div>

        <div className="diagnostics-card">
          <div className="card-header">
            <h4>Color palette</h4>
            <span className="pill">coloraide</span>
          </div>
          <div className="palette-grid">
            {palette.map((entry) => (
              <button
                key={`${entry.hex}-${entry.label}`}
                className={`swatch${selectedColor === entry.hex ? ' is-active' : ''}`}
                style={{ background: entry.hex }}
                onClick={() => setSelectedColor(selectedColor === entry.hex ? null : entry.hex)}
                title={`${entry.label} (${entry.hex})`}
              >
                <span className="swatch-hex">{entry.hex}</span>
                {entry.coverage != null && <span className="swatch-meta">{Math.round(entry.coverage)}%</span>}
              </button>
            ))}
            {!palette.length && <p className="muted">Palette not available yet.</p>}
          </div>
        </div>

        <div className="diagnostics-card overlay-card">
          <div className="card-header">
            <h4>Overlay preview</h4>
            <span className="pill">{overlaySrc ? 'interactive' : 'awaiting image'}</span>
          </div>
          {overlaySrc ? (
            <div className="overlay-stage">
              <img
                ref={overlayImgRef}
                src={overlaySrc}
                alt="Diagnostics overlay"
                className="overlay-base"
              />
              {matchingBoxes.map(({ metric, idx }) => {
                const style = metric.box ? renderBox(metric.box) : null
                if (!style) return null
                return (
                  <div
                    key={`box-${idx}`}
                    className="overlay-box"
                    style={style}
                  >
                    <span className="overlay-label">
                      {selectedSpacing ? `${selectedSpacing}px` : `#${(metric.index ?? idx) + 1}`}
                    </span>
                  </div>
                )
              })}
              {showAlignmentLines &&
                alignmentLines.map((line, idx) => (
                  <div
                    key={`line-${line.orientation}-${idx}`}
                    className={`overlay-line ${line.orientation}`}
                    style={line.style}
                  />
                ))}
            </div>
          ) : (
            <p className="muted">Upload an image to view overlay guides.</p>
          )}
        </div>
      </div>
    </div>
  )
}
