import type { DiagnosticsTabProps } from '../types'

export function DiagnosticsTab({ overlay }: DiagnosticsTabProps) {
  if (!overlay) {
    return (
      <div className="diagnostics-content">
        <div className="empty-state">
          <p className="standin">No diagnostics overlay available for this color</p>
        </div>
      </div>
    )
  }

  return (
    <div className="diagnostics-content">
      <p className="diagnostics-hint">
        Superpixel boundaries plus background/text picks for quick QA.
      </p>
      <div className="diagnostics-frame">
        <img
          src={`data:image/png;base64,${overlay}`}
          alt="Color extraction diagnostics overlay"
          className="diagnostics-image"
        />
      </div>
    </div>
  )
}
