import type { SpacingExtractionResponse } from '../types'
import type { SpacingEntry } from './types'

interface Props {
  commonSpacings: SpacingEntry[]
  componentMetrics: SpacingExtractionResponse['component_spacing_metrics'] | undefined
  spacingResult: SpacingExtractionResponse | undefined | null
  selectedSpacing: number | null
  selectedComponent: number | null
  showPayload: boolean
  payloadInfo: Array<{ label: string; value: string }>
  onSpacingSelect: (value: number | null) => void
  onComponentSelect: (index: number | null) => void
}

export function SpacingDiagnostics({
  commonSpacings,
  componentMetrics,
  spacingResult,
  selectedSpacing,
  selectedComponent,
  showPayload,
  payloadInfo,
  onSpacingSelect,
  onComponentSelect,
}: Props) {
  return (
    <div className="diagnostics-card">
      <div className="card-header">
        <h4>Spacing diagnostics</h4>
        <span className="pill">adjacency</span>
      </div>

      {spacingResult?.alignment && (
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

      {showPayload && (
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
      )}

      <div className="spacing-chip-row">
        {commonSpacings.length ? (
          commonSpacings.map((entry) => (
            <button
              key={entry.value_px}
              className={`spacing-chip${selectedSpacing === entry.value_px ? ' is-active' : ''}`}
              onClick={() => onSpacingSelect(selectedSpacing === entry.value_px ? null : entry.value_px)}
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

      {componentMetrics?.length ? (
        <div className="component-scroll">
          {componentMetrics.slice(0, 8).map((metric, idx) => (
            <button
              key={metric.index ?? idx}
              className={`component-row${selectedComponent === idx ? ' is-active' : ''}`}
              onClick={() => onComponentSelect(selectedComponent === idx ? null : idx)}
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
  )
}
