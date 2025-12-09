import type { DiagnosticsTabProps } from '../types'

export function DiagnosticsTab({ overlay }: DiagnosticsTabProps) {
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
