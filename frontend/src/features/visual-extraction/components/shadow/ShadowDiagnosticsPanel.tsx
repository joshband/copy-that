import { useMemo, useState } from 'react'
import './ShadowDiagnosticsPanel.css'
import type { ArtifactBundle, ArtifactJson } from '../../../../types'

interface Props {
  artifacts?: ArtifactBundle | null
}

const formatLabel = (value: string) =>
  value
    .split('_')
    .map((part) => (part ? part[0].toUpperCase() + part.slice(1) : part))
    .join(' ')

const formatPercent = (value: number) =>
  Number.isFinite(value) ? `${Math.round(value * 100)}%` : '—'

const LARGE_JSON_BYTES = 12_000

const bytesForText = (text: string) => {
  if (typeof TextEncoder !== 'undefined') {
    return new TextEncoder().encode(text).length
  }
  return text.length
}

const formatBytes = (bytes: number) => {
  if (bytes < 1024) return `${bytes} B`
  const kb = bytes / 1024
  if (kb < 1024) return `${kb.toFixed(1)} KB`
  const mb = kb / 1024
  return `${mb.toFixed(1)} MB`
}

export default function ShadowDiagnosticsPanel({ artifacts }: Props) {
  const json = useMemo(() => {
    if (!artifacts?.json?.length) return [] as ArtifactJson[]
    return artifacts.json
  }, [artifacts])
  const [copiedKey, setCopiedKey] = useState<string | null>(null)

  if (!json.length) {
    return null
  }

  const pipeline = json.find((item) => item.type === 'pipeline_results')?.payload as any
  const tokens = json.find((item) => item.type === 'shadow_tokens')?.payload as any

  const stageCount = Array.isArray(pipeline?.stages) ? pipeline.stages.length : null
  const artifactCount = Array.isArray(pipeline?.artifacts_list) ? pipeline.artifacts_list.length : null
  const durationMs = typeof pipeline?.total_duration_ms === 'number' ? Math.round(pipeline.total_duration_ms) : null
  const layerCount = Array.isArray(pipeline?.visual_layers) ? pipeline.visual_layers.length : null

  const shadowMetrics = tokens?.shadow_tokens ?? tokens?.shadowTokens ?? null

  const coverage = typeof shadowMetrics?.coverage === 'number' ? shadowMetrics.coverage : null
  const meanStrength =
    typeof shadowMetrics?.mean_strength === 'number' ? shadowMetrics.mean_strength : null
  const edgeSoftness =
    typeof shadowMetrics?.edge_softness_mean === 'number' ? shadowMetrics.edge_softness_mean : null
  const physics =
    typeof shadowMetrics?.physics_consistency === 'number'
      ? shadowMetrics.physics_consistency
      : null

  const entries = useMemo(
    () =>
      json.map((item, index) => {
        const payloadText = JSON.stringify(item.payload, null, 2)
        const sizeBytes = bytesForText(payloadText)
        return {
          key: `${item.type}-${index}`,
          item,
          payloadText,
          sizeBytes,
          sizeLabel: formatBytes(sizeBytes),
          isLarge: sizeBytes > LARGE_JSON_BYTES,
        }
      }),
    [json],
  )

  const handleCopy = async (payloadText: string, key: string) => {
    try {
      if (navigator?.clipboard?.writeText) {
        await navigator.clipboard.writeText(payloadText)
      } else {
        const textarea = document.createElement('textarea')
        textarea.value = payloadText
        textarea.style.position = 'fixed'
        textarea.style.opacity = '0'
        document.body.appendChild(textarea)
        textarea.focus()
        textarea.select()
        document.execCommand('copy')
        document.body.removeChild(textarea)
      }
      setCopiedKey(key)
      window.setTimeout(() => setCopiedKey(null), 2000)
    } catch {
      setCopiedKey(null)
    }
  }

  return (
    <div className="shadow-diagnostics">
      <div className="shadow-diagnostics__header">
        <div>
          <p className="shadow-diagnostics__kicker">Raw diagnostics</p>
          <h3>ShadowLab JSON signals</h3>
          <p className="shadow-diagnostics__subtitle">
            Scan pipeline stats and token metrics before exporting shadows.
          </p>
        </div>
      </div>

      {(stageCount != null || artifactCount != null || durationMs != null || layerCount != null) && (
        <div className="shadow-diagnostics__summary">
          {stageCount != null && (
            <div className="shadow-diagnostics__summary-item">
              <span>Stages</span>
              <strong>{stageCount}</strong>
            </div>
          )}
          {artifactCount != null && (
            <div className="shadow-diagnostics__summary-item">
              <span>Artifacts</span>
              <strong>{artifactCount}</strong>
            </div>
          )}
          {layerCount != null && (
            <div className="shadow-diagnostics__summary-item">
              <span>Layers</span>
              <strong>{layerCount}</strong>
            </div>
          )}
          {durationMs != null && (
            <div className="shadow-diagnostics__summary-item">
              <span>Runtime</span>
              <strong>{durationMs}ms</strong>
            </div>
          )}
        </div>
      )}

      {(coverage != null || meanStrength != null || edgeSoftness != null || physics != null) && (
        <div className="shadow-diagnostics__metrics">
          {coverage != null && (
            <div className="shadow-diagnostics__metric">
              <span>Coverage</span>
              <strong>{formatPercent(coverage)}</strong>
            </div>
          )}
          {meanStrength != null && (
            <div className="shadow-diagnostics__metric">
              <span>Mean strength</span>
              <strong>{formatPercent(meanStrength)}</strong>
            </div>
          )}
          {edgeSoftness != null && (
            <div className="shadow-diagnostics__metric">
              <span>Edge softness</span>
              <strong>{formatPercent(edgeSoftness)}</strong>
            </div>
          )}
          {physics != null && (
            <div className="shadow-diagnostics__metric">
              <span>Physics consistency</span>
              <strong>{formatPercent(physics)}</strong>
            </div>
          )}
        </div>
      )}

      <div className="shadow-diagnostics__json">
        {entries.map((entry) => (
          <details
            className="shadow-diagnostics__json-card"
            key={entry.key}
            open={!entry.isLarge}
          >
            <summary className="shadow-diagnostics__json-summary">
              <span className="shadow-diagnostics__json-title">
                {formatLabel(entry.item.type)}
              </span>
              <span className="shadow-diagnostics__json-meta">
                <span className="shadow-diagnostics__json-size">{entry.sizeLabel}</span>
                {entry.isLarge && (
                  <span className="shadow-diagnostics__json-collapsed">collapsed</span>
                )}
              </span>
              <button
                type="button"
                className="shadow-diagnostics__copy-btn"
                onClick={(event) => {
                  event.preventDefault()
                  event.stopPropagation()
                  void handleCopy(entry.payloadText, entry.key)
                }}
              >
                Copy JSON
              </button>
              {copiedKey === entry.key && (
                <span className="shadow-diagnostics__copy-status">Copied</span>
              )}
            </summary>
            <pre>{entry.payloadText}</pre>
          </details>
        ))}
      </div>
    </div>
  )
}
