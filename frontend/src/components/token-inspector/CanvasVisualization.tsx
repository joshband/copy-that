import { useRef } from 'react'
import type { SpacingExtractionResponse } from '../types'
import type { TokenRow, ColorMap } from './types'

interface Dimensions {
  naturalWidth: number
  naturalHeight: number
  clientWidth: number
  clientHeight: number
}

interface Props {
  overlaySrc: string | null
  tokens: TokenRow[]
  activeId: string | number | null
  colorMap: ColorMap
  fallbackColors: string[]
  dimensions: Dimensions
  metricById: Map<number, NonNullable<SpacingExtractionResponse['component_spacing_metrics']>[number]>
  onImgRef: (ref: HTMLImageElement | null) => void
  onCanvasRef: (ref: HTMLCanvasElement | null) => void
  onTokenHover: (id: string | number | null) => void
  onTokenClick: (id: string | number | null, isActive: boolean) => void
}

const getSelectedColor = (
  token: TokenRow,
  idx: number,
  metricById: Props['metricById'],
  colorMap: ColorMap,
  fallbackColors: string[],
): string => {
  const metric = metricById.get(typeof token.id === 'number' ? token.id : parseInt(token.id as string, 10))
  if (metric?.colors?.primary) {
    return metric.colors.primary
  }
  if (metric?.colors?.palette?.length) {
    return metric.colors.palette[0]
  }
  return colorMap[token.id] ?? fallbackColors[idx % fallbackColors.length] ?? '#888888'
}

export function CanvasVisualization({
  overlaySrc,
  tokens,
  activeId,
  colorMap,
  fallbackColors,
  dimensions,
  metricById,
  onImgRef,
  onCanvasRef,
  onTokenHover,
  onTokenClick,
}: Props) {
  const scaleBox = (box: [number, number, number, number]) => {
    const [x, y, w, h] = box
    const sx = dimensions.clientWidth / dimensions.naturalWidth
    const sy = dimensions.clientHeight / dimensions.naturalHeight
    return {
      left: x * sx,
      top: y * sy,
      width: Math.max(w * sx, 2),
      height: Math.max(h * sy, 2),
    }
  }

  const scalePolygon = (poly?: Array<[number, number]>) => {
    if (!poly?.length) return null
    const sx = dimensions.clientWidth / dimensions.naturalWidth
    const sy = dimensions.clientHeight / dimensions.naturalHeight
    return poly.map(([x, y]) => [x * sx, y * sy] as [number, number])
  }

  return (
    <div className="ti-overlay-card">
      {overlaySrc ? (
        <div className="overlay-stage">
          <img
            ref={onImgRef}
            className="overlay-base"
            src={overlaySrc}
            alt="Token overlay"
          />
          <svg
            className="overlay-svg"
            width={dimensions.clientWidth}
            height={dimensions.clientHeight}
            viewBox={`0 0 ${dimensions.clientWidth} ${dimensions.clientHeight}`}
          >
            {tokens.map((token, idx) => {
              const poly = scalePolygon(token.polygon)
              if (!poly) return null
              const color = getSelectedColor(token, idx, metricById, colorMap, fallbackColors)
              const isActive = activeId === token.id
              return (
                <polygon
                  key={`poly-${token.id}`}
                  points={poly.map((p) => p.join(',')).join(' ')}
                  className={`overlay-polygon${isActive ? ' is-active' : ''}`}
                  style={{ stroke: color }}
                  onMouseEnter={() => onTokenHover(token.id)}
                  onMouseLeave={() => onTokenHover((prev) => (prev === token.id ? null : prev) as any)}
                  onClick={() => onTokenClick(token.id, isActive)}
                />
              )
            })}
          </svg>
          {tokens.map((token, idx) => {
            const style = scaleBox(token.box)
            const color = getSelectedColor(token, idx, metricById, colorMap, fallbackColors)
            const isActive = activeId === token.id
            const metric = metricById.get(typeof token.id === 'number' ? token.id : parseInt(token.id as string, 10))
            const isLowConfidence = (metric?.padding_confidence ?? 1) < 0.35
            const label = token.text ? token.text.slice(0, 22) : `#${token.id}`
            return (
              <div
                key={`box-${token.id}`}
                className={`overlay-box${isActive ? ' is-active' : ''}${isLowConfidence ? ' is-low' : ''}`}
                style={{ ...style, borderColor: color, backgroundColor: `${color}22` }}
                onMouseEnter={() => onTokenHover(token.id)}
                onMouseLeave={() => onTokenHover((prev) => (prev === token.id ? null : prev) as any)}
                onClick={() => onTokenClick(token.id, isActive)}
                title={`${label} • ${token.type}`}
              >
                <span className="overlay-label">{label}</span>
              </div>
            )
          })}
        </div>
      ) : (
        <p className="muted">Upload an image to see overlay and tokens.</p>
      )}
      <canvas ref={onCanvasRef} className="ti-canvas" aria-hidden="true" />
    </div>
  )
}
