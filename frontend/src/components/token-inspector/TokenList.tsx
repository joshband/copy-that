import type { SpacingExtractionResponse } from '../../types'
import type { TokenRow, ColorMap } from './types'

interface Props {
  tokens: TokenRow[]
  activeId: string | number | null
  colorMap: ColorMap
  fallbackColors: string[]
  metricById: Map<number, NonNullable<SpacingExtractionResponse['component_spacing_metrics']>[number]>
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

export function TokenList({
  tokens,
  activeId,
  colorMap,
  fallbackColors,
  metricById,
  onTokenHover,
  onTokenClick,
}: Props) {
  return (
    <div className="ti-table" role="table" aria-label="Extracted tokens">
      <div className="ti-row ti-head" role="row">
        <div>ID</div>
        <div>Type</div>
        <div>Position (x,y,w,h)</div>
        <div>Color</div>
        <div>Text</div>
      </div>
      <div className="ti-body">
        {tokens.map((token, idx) => {
          const color = getSelectedColor(token, idx, metricById, colorMap, fallbackColors)
          const isActive = activeId === token.id
          const metric = metricById.get(typeof token.id === 'number' ? token.id : parseInt(token.id as string, 10))
          const isLowConfidence = (metric?.padding_confidence ?? 1) < 0.35
          return (
            <div
              key={token.id}
              className={`ti-row${isActive ? ' is-active' : ''}${isLowConfidence ? ' is-low' : ''}`}
              role="row"
              onMouseEnter={() => onTokenHover(token.id)}
              onMouseLeave={() => onTokenHover(null)}
              onClick={() => onTokenClick(token.id, isActive)}
            >
              <div>#{token.id}</div>
              <div className="ti-type">
                {token.type}
                {token.elementType && token.elementType !== token.type
                  ? ` (${token.elementType})`
                  : ''}
              </div>
              <div className="ti-pos">
                {token.box[0]}, {token.box[1]}, {token.box[2]}, {token.box[3]}
              </div>
              <div className="ti-color">
                <span className="ti-swatch" style={{ background: color }} />
                <span>{color}</span>
                {metric?.colors?.secondary ? (
                  <span className="ti-swatch secondary" style={{ background: metric.colors.secondary }} />
                ) : null}
              </div>
              <div className="ti-text">{token.text ?? '—'}</div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
