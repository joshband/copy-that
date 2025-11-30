import { useEffect, useMemo, useRef, useState } from 'react'
import './TokenInspector.css'
import type { ColorToken, SegmentedColor, SpacingExtractionResponse } from '../types'

type TokenRow = {
  id: number
  type: string
  box: [number, number, number, number]
  color?: string
  text?: string
}

type Props = {
  spacingResult?: SpacingExtractionResponse | null
  overlayBase64?: string | null
  colors: ColorToken[]
  segmentedPalette?: SegmentedColor[] | null
}

const toDataUrl = (b64?: string | null) => (b64 ? `data:image/png;base64,${b64}` : null)

const deriveType = (metric: NonNullable<SpacingExtractionResponse['component_spacing_metrics']>[number]) => {
  if (metric.padding && Object.values(metric.padding).some((v) => (v ?? 0) > 8)) {
    return 'container'
  }
  if (metric.neighbor_gap && metric.neighbor_gap > 0) {
    return 'element'
  }
  return 'node'
}

export default function TokenInspector({ spacingResult, overlayBase64, colors, segmentedPalette }: Props) {
  const [activeId, setActiveId] = useState<number | null>(null)
  const [filter, setFilter] = useState('')
  const [colorMap, setColorMap] = useState<Record<number, string>>({})
  const imgRef = useRef<HTMLImageElement | null>(null)
  const canvasRef = useRef<HTMLCanvasElement | null>(null)
  const overlaySrc = toDataUrl(overlayBase64 ?? spacingResult?.debug_overlay ?? null)

  const tokens: TokenRow[] = useMemo(() => {
    const metrics = spacingResult?.component_spacing_metrics ?? []
    return metrics
      .map((m, idx) => ({ metric: m, idx }))
      .filter(({ metric }) => Array.isArray(metric.box) && metric.box.length === 4)
      .map(({ metric, idx }) => ({
        id: metric.index ?? idx,
        type: deriveType(metric),
        box: metric.box as [number, number, number, number],
        text: undefined,
      }))
  }, [spacingResult?.component_spacing_metrics])

  const metricById = useMemo(() => {
    const metrics = spacingResult?.component_spacing_metrics ?? []
    const map = new Map<number, (typeof metrics)[number]>()
    metrics.forEach((m, idx) => {
      map.set(m.index ?? idx, m)
    })
    return map
  }, [spacingResult?.component_spacing_metrics])

  // Sample colors from overlay image (center of each box) if available; fallback to palette or color list.
  useEffect(() => {
    if (!overlaySrc || !tokens.length) {
      setColorMap({})
      return
    }
    const img = new Image()
    img.crossOrigin = 'anonymous'
    img.src = overlaySrc
    img.onload = () => {
      const canvas = canvasRef.current
      if (!canvas) return
      canvas.width = img.naturalWidth
      canvas.height = img.naturalHeight
      const ctx = canvas.getContext('2d')
      if (!ctx) return
      ctx.drawImage(img, 0, 0)
      const next: Record<number, string> = {}
      tokens.forEach((token) => {
        const [x, y, w, h] = token.box
        const cx = Math.min(Math.max(Math.round(x + w / 2), 0), img.naturalWidth - 1)
        const cy = Math.min(Math.max(Math.round(y + h / 2), 0), img.naturalHeight - 1)
        const data = ctx.getImageData(cx, cy, 1, 1).data
        const hex = `#${[data[0], data[1], data[2]].map((v) => v.toString(16).padStart(2, '0')).join('')}`
        next[token.id] = hex
      })
      setColorMap(next)
    }
  }, [overlaySrc, tokens])

  // Fallback palette colors if overlay sampling not available
  const fallbackColors = useMemo(() => {
    if (segmentedPalette?.length) {
      return segmentedPalette.map((s) => s.hex)
    }
    return colors.map((c) => c.hex)
  }, [colors, segmentedPalette])

  const filteredTokens = useMemo(() => {
    const term = filter.trim().toLowerCase()
    if (!term) return tokens
    return tokens.filter((t) => t.type.toLowerCase().includes(term) || String(t.id).includes(term))
  }, [filter, tokens])

  const selectedColor = (token: TokenRow, idx: number) =>
    colorMap[token.id] ?? fallbackColors[idx % fallbackColors.length] ?? '#888888'

  // For overlay positioning
  const [dims, setDims] = useState({ naturalWidth: 1, naturalHeight: 1, clientWidth: 1, clientHeight: 1 })
  useEffect(() => {
    const img = imgRef.current
    if (!img) return
    const update = () =>
      setDims({
        naturalWidth: img.naturalWidth || 1,
        naturalHeight: img.naturalHeight || 1,
        clientWidth: img.clientWidth || 1,
        clientHeight: img.clientHeight || 1,
      })
    update()
    window.addEventListener('resize', update)
    return () => window.removeEventListener('resize', update)
  }, [overlaySrc])

  const scaleBox = (box: [number, number, number, number]) => {
    const [x, y, w, h] = box
    const sx = dims.clientWidth / dims.naturalWidth
    const sy = dims.clientHeight / dims.naturalHeight
    return {
      left: x * sx,
      top: y * sy,
      width: Math.max(w * sx, 2),
      height: Math.max(h * sy, 2),
    }
  }

  const downloadJson = () => {
    const payload = filteredTokens.map((t, idx) => ({
      id: t.id,
      type: t.type,
      box: t.box,
      color: selectedColor(t, idx),
    }))
    const blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = 'tokens.json'
    link.click()
    URL.revokeObjectURL(url)
  }

  if (!tokens.length) {
    return null
  }

  return (
    <div className="token-inspector">
      <div className="ti-header">
        <div>
          <p className="eyebrow">Token Inspector</p>
          <h3>Review extracted elements</h3>
          <p className="diagnostics-subtitle">
            Hover rows to highlight on the overlay. Click to persist selection. Filter by type to focus a subset.
          </p>
        </div>
        <div className="ti-actions">
          <input
            type="text"
            placeholder="Filter by type or id…"
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
          />
          <button className="ghost-btn" onClick={downloadJson}>
            Download JSON
          </button>
        </div>
      </div>

      <div className="ti-grid">
        <div className="ti-table" role="table" aria-label="Extracted tokens">
          <div className="ti-row ti-head" role="row">
            <div>ID</div>
            <div>Type</div>
            <div>Position (x,y,w,h)</div>
            <div>Color</div>
            <div>Text</div>
          </div>
          <div className="ti-body">
            {filteredTokens.map((token, idx) => {
              const color = selectedColor(token, idx)
              const isActive = activeId === token.id
              const metric = metricById.get(token.id)
              const isLowConfidence = (metric?.padding_confidence ?? 1) < 0.35
              return (
                <div
                  key={token.id}
                  className={`ti-row${isActive ? ' is-active' : ''}${isLowConfidence ? ' is-low' : ''}`}
                  role="row"
                  onMouseEnter={() => setActiveId(token.id)}
                  onMouseLeave={() => setActiveId((prev) => (prev === token.id ? null : prev))}
                  onClick={() => setActiveId(isActive ? null : token.id)}
                >
                  <div>#{token.id}</div>
                  <div className="ti-type">{token.type}</div>
                  <div className="ti-pos">
                    {token.box[0]}, {token.box[1]}, {token.box[2]}, {token.box[3]}
                  </div>
                  <div className="ti-color">
                    <span className="ti-swatch" style={{ background: color }} />
                    <span>{color}</span>
                  </div>
                  <div className="ti-text">{token.text ?? '—'}</div>
                </div>
              )
            })}
          </div>
        </div>

        <div className="ti-overlay-card">
          {overlaySrc ? (
            <div className="overlay-stage">
              <img
                ref={imgRef}
                className="overlay-base"
                src={overlaySrc}
                alt="Token overlay"
              />
              {filteredTokens.map((token, idx) => {
                const style = scaleBox(token.box)
                const color = selectedColor(token, idx)
                const isActive = activeId === token.id
                const metric = metricById.get(token.id)
                const isLowConfidence = (metric?.padding_confidence ?? 1) < 0.35
                return (
                  <div
                    key={`box-${token.id}`}
                    className={`overlay-box${isActive ? ' is-active' : ''}${isLowConfidence ? ' is-low' : ''}`}
                    style={{ ...style, borderColor: color, backgroundColor: `${color}22` }}
                    onMouseEnter={() => setActiveId(token.id)}
                    onMouseLeave={() => setActiveId((prev) => (prev === token.id ? null : prev))}
                    onClick={() => setActiveId(isActive ? null : token.id)}
                    title={`#${token.id} • ${token.type}`}
                  >
                    <span className="overlay-label">#{token.id}</span>
                  </div>
                )
              })}
            </div>
          ) : (
            <p className="muted">Upload an image to see overlay and tokens.</p>
          )}
        </div>
      </div>
      <canvas ref={canvasRef} className="ti-canvas" aria-hidden="true" />
    </div>
  )
}
