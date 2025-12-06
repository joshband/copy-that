import { useState, useRef, useEffect } from 'react'
import type { Props } from './types'
import { FilterBar } from './FilterBar'
import { TokenList } from './TokenList'
import { CanvasVisualization } from './CanvasVisualization'
import {
  useTokens,
  useMetricById,
  useFallbackColors,
  useCanvasColorSampling,
  useFilteredTokens,
} from './hooks'

const toDataUrl = (b64?: string | null) => (b64 ? `data:image/png;base64,${b64}` : null)

export default function TokenInspector({
  spacingResult,
  overlayBase64,
  colors,
  segmentedPalette,
  showOverlay = true,
}: Props) {
  const [activeId, setActiveId] = useState<number | string | null>(null)
  const [filter, setFilter] = useState('')
  const imgRef = useRef<HTMLImageElement | null>(null)

  const tokens = useTokens(spacingResult)
  const metricById = useMetricById(spacingResult)
  const fallbackColors = useFallbackColors(colors, segmentedPalette)
  const overlaySrc = showOverlay ? toDataUrl(overlayBase64 ?? spacingResult?.debug_overlay ?? null) : null
  const { canvasRef, colorMap } = useCanvasColorSampling(overlaySrc, tokens)
  const filteredTokens = useFilteredTokens(tokens, filter)

  // Track overlay dimensions for scaling
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

  const downloadJson = () => {
    const getColor = (token: typeof filteredTokens[0], idx: number): string => {
      const metric = metricById.get(typeof token.id === 'number' ? token.id : parseInt(token.id as string, 10))
      if (metric?.colors?.primary) {
        return metric.colors.primary
      }
      if (metric?.colors?.palette?.length) {
        return metric.colors.palette[0]
      }
      return colorMap[token.id] ?? fallbackColors[idx % fallbackColors.length] ?? '#888888'
    }

    const payload = filteredTokens.map((t, idx) => ({
      id: t.id,
      type: t.type,
      box: t.box,
      polygon: t.polygon,
      text: t.text,
      source: t.source,
      color: getColor(t, idx),
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
      <FilterBar
        filter={filter}
        filteredCount={filteredTokens.length}
        totalCount={tokens.length}
        onFilterChange={setFilter}
        onDownloadJson={downloadJson}
      />

      <div className="ti-grid">
        <TokenList
          tokens={filteredTokens}
          activeId={activeId}
          colorMap={colorMap}
          fallbackColors={fallbackColors}
          metricById={metricById}
          onTokenHover={(id) => setActiveId(id)}
          onTokenClick={(id, isActive) => setActiveId(isActive ? null : id)}
        />

        <CanvasVisualization
          overlaySrc={overlaySrc}
          tokens={filteredTokens}
          activeId={activeId}
          colorMap={colorMap}
          fallbackColors={fallbackColors}
          dimensions={dims}
          metricById={metricById}
          onImgRef={(ref) => {
            imgRef.current = ref
          }}
          onCanvasRef={(ref) => {
            canvasRef.current = ref
          }}
          onTokenHover={(id) => setActiveId(id)}
          onTokenClick={(id, isActive) => setActiveId(isActive ? null : id)}
        />
      </div>
    </div>
  )
}
