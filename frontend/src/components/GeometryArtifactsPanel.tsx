import { useCallback, useEffect, useState } from 'react'
import { API_BASE } from '../api/client'
import './GeometryArtifactsPanel.css'

type GeometryResponse = {
  meta: Record<string, unknown>
  images: Record<string, string>
}

type Props = {
  imageBase64?: string | null
}

type GeometryProfile = 'auto' | 'cpu_fast' | 'cpu_accurate' | 'gpu_full'

const PROFILE_LABELS: Record<GeometryProfile, string> = {
  auto: 'Auto',
  cpu_fast: 'CPU fast',
  cpu_accurate: 'CPU accurate',
  gpu_full: 'GPU full',
}

const LABELS: Record<string, string> = {
  depth_png: 'Depth map',
  normals_png: 'Normals map',
  normals_confidence_png: 'Normals confidence',
  normals_gradients_png: 'Normals gradients',
}

const toDataUrl = (value?: string | null) =>
  value ? `data:image/png;base64,${value}` : null

const metaValue = (value: unknown) =>
  typeof value === 'string' || typeof value === 'number' ? String(value) : null

export default function GeometryArtifactsPanel({ imageBase64 }: Props) {
  const [payload, setPayload] = useState<GeometryResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [profile, setProfile] = useState<GeometryProfile>('auto')

  useEffect(() => {
    const params = new URLSearchParams(window.location.search)
    const fromQuery =
      params.get('geometry_profile') ?? params.get('geometryProfile') ?? ''
    if (fromQuery && Object.prototype.hasOwnProperty.call(PROFILE_LABELS, fromQuery)) {
      setProfile(fromQuery as GeometryProfile)
    }
  }, [])

  useEffect(() => {
    const params = new URLSearchParams(window.location.search)
    params.set('geometry_profile', profile)
    const next = `${window.location.pathname}?${params.toString()}${window.location.hash}`
    window.history.replaceState({}, '', next)
  }, [profile])

  useEffect(() => {
    setPayload(null)
    setError(null)
  }, [imageBase64, profile])

  const handleExtract = useCallback(async () => {
    if (!imageBase64) {
      setError('Upload an image to extract geometry artifacts.')
      return
    }
    setLoading(true)
    setError(null)
    try {
      const response = await fetch(`${API_BASE}/geometry/extract`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ image_base64: imageBase64, profile }),
      })
      if (!response.ok) {
        const detail = await response.json().catch(() => ({}))
        const message =
          (detail && typeof detail.detail === 'string' && detail.detail) ||
          `HTTP ${response.status}: ${response.statusText}`
        throw new Error(message)
      }
      const data = (await response.json()) as GeometryResponse
      setPayload(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Geometry extraction failed')
    } finally {
      setLoading(false)
    }
  }, [imageBase64, profile])

  const meta = payload?.meta ?? {}
  const warnings = Array.isArray(meta.warnings) ? (meta.warnings as string[]) : []
  const metaItems = [
    { label: 'Profile', value: metaValue(meta.profile_resolved ?? meta.profile_requested) },
    { label: 'Depth model', value: metaValue(meta.depth_model) },
    { label: 'Normals source', value: metaValue(meta.normals_source) },
    { label: 'Device', value: metaValue(meta.device) },
  ].filter((item) => item.value)

  const images = payload?.images ? Object.entries(payload.images) : []

  return (
    <div className="geometry-panel">
      <div className="geometry-panel__header">
        <div>
          <p className="eyebrow">Geometry artifacts</p>
          <h3>Depth + normals previews</h3>
          <p className="muted">
            Generate depth and normals maps to validate shadow placement and lighting direction.
          </p>
        </div>
        <div className="geometry-panel__controls">
          <label className="geometry-panel__select">
            <span>Profile</span>
            <select
              value={profile}
              onChange={(event) => setProfile(event.target.value as GeometryProfile)}
              disabled={loading}
            >
              {Object.entries(PROFILE_LABELS).map(([value, label]) => (
                <option key={value} value={value}>
                  {label}
                </option>
              ))}
            </select>
          </label>
          <button
            type="button"
            className="ghost-btn geometry-panel__action"
            onClick={() => void handleExtract()}
            disabled={!imageBase64 || loading}
          >
            {loading ? 'Extracting...' : 'Extract geometry'}
          </button>
        </div>
      </div>

      {!imageBase64 && (
        <p className="muted standin geometry-panel__empty">
          Upload an image to enable geometry diagnostics.
        </p>
      )}
      {error && <p className="geometry-panel__error">{error}</p>}

      {metaItems.length > 0 && (
        <div className="geometry-panel__meta">
          {metaItems.map((item) => (
            <div key={item.label} className="geometry-panel__meta-item">
              <span className="geometry-panel__meta-label">{item.label}</span>
              <span className="geometry-panel__meta-value">{item.value}</span>
            </div>
          ))}
        </div>
      )}

      {warnings.length > 0 && (
        <div className="geometry-panel__warnings">
          {warnings.map((warning, idx) => (
            <span key={`${warning}-${idx}`} className="pill">
              {warning}
            </span>
          ))}
        </div>
      )}

      {images.length > 0 && (
        <div className="geometry-panel__grid">
          {images.map(([key, value]) => {
            const label = LABELS[key] ?? key.replace(/_/g, ' ')
            const src = toDataUrl(value)
            return (
              <figure key={key} className="geometry-panel__card">
                {src ? (
                  <img
                    src={src}
                    alt={`Geometry ${label}`}
                    className="geometry-panel__image"
                  />
                ) : (
                  <div className="geometry-panel__placeholder">No preview available</div>
                )}
                <figcaption className="geometry-panel__caption">{label}</figcaption>
              </figure>
            )
          })}
        </div>
      )}
    </div>
  )
}
