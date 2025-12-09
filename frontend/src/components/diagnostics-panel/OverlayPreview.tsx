import { useRef } from 'react'
import type { SpacingExtractionResponse } from '../../types'

interface MatchingBox {
  metric: NonNullable<SpacingExtractionResponse['component_spacing_metrics']>[number]
  idx: number
}

interface AlignmentLine {
  orientation: 'vertical' | 'horizontal'
  style: { left?: number; top?: number }
}

interface Props {
  overlaySrc: string | null
  fastsamTokens: SpacingExtractionResponse['fastsam_tokens'] | undefined
  matchingBoxes: MatchingBox[]
  alignmentLines: AlignmentLine[]
  dimensions: {
    naturalWidth: number
    naturalHeight: number
    clientWidth: number
    clientHeight: number
  }
  showSegments: boolean
  showAlignmentLines: boolean
  selectedSpacing: number | null
  selectedComponent: number | null
  onSegmentsToggle: () => void
  scalePolygon: (poly?: Array<[number, number]>) => Array<[number, number]> | null
  renderBox: (box: [number, number, number, number]) => { left: number; top: number; width: number; height: number } | null
}

export function OverlayPreview({
  overlaySrc,
  fastsamTokens,
  matchingBoxes,
  alignmentLines,
  dimensions,
  showSegments,
  showAlignmentLines,
  selectedSpacing,
  selectedComponent,
  onSegmentsToggle,
  scalePolygon,
  renderBox,
}: Props) {
  const overlayImgRef = useRef<HTMLImageElement | null>(null)

  return (
    <div className="diagnostics-card overlay-card">
      <div className="card-header">
        <h4>Overlay preview</h4>
        <span className="pill">{overlaySrc ? 'interactive' : 'awaiting image'}</span>
      </div>
      {fastsamTokens?.length ? (
        <div className="alignment-row">
          <label className="switch">
            <input
              type="checkbox"
              checked={showSegments}
              onChange={onSegmentsToggle}
            />
            <span className="slider" />
          </label>
          <span className="alignment-values">
            {showSegments ? 'Hide FastSAM segments' : 'Show FastSAM segments'} ({fastsamTokens.length})
          </span>
        </div>
      ) : null}
      {overlaySrc ? (
        <div className="overlay-stage">
          <img
            ref={overlayImgRef}
            src={overlaySrc}
            alt="Diagnostics overlay"
            className="overlay-base"
          />
          {showSegments && (
            <svg
              className="overlay-svg"
              width={dimensions.clientWidth}
              height={dimensions.clientHeight}
              viewBox={`0 0 ${dimensions.clientWidth} ${dimensions.clientHeight}`}
            >
              {fastsamTokens?.map((token) => {
                const scaled = scalePolygon(token.polygon)
                if (!scaled) return null
                return (
                  <polygon
                    key={`seg-${token.id}`}
                    points={scaled.map((p) => p.join(',')).join(' ')}
                    className="overlay-polygon"
                  />
                )
              })}
            </svg>
          )}
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
  )
}
