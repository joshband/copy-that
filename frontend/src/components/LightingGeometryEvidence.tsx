/**
 * Flag-gated P4 geometry evidence for lighting analyze responses.
 * Surfaces geometry_used, geometry_meta, and optional depth/normals thumbnails.
 */

import './LightingGeometryEvidence.css'

export interface LightingGeometryMeta {
  profile_requested?: string
  profile_resolved?: string
  device?: string
  depth_model?: string
  normals_source?: string
  warnings?: string[]
  [key: string]: unknown
}

export interface LightingGeometryImages {
  depth_png?: string
  normals_png?: string
}

export interface LightingGeometryEvidenceProps {
  geometryUsed?: boolean
  geometryMeta?: LightingGeometryMeta | null
  geometryImages?: LightingGeometryImages | null
}

function toDataUrl(pngBase64: string): string {
  if (pngBase64.startsWith('data:')) return pngBase64
  return `data:image/png;base64,${pngBase64}`
}

export function LightingGeometryEvidence({
  geometryUsed,
  geometryMeta,
  geometryImages,
}: LightingGeometryEvidenceProps) {
  if (geometryUsed !== true && !geometryMeta && !geometryImages) {
    return null
  }

  // Avoid empty shell when caller passes geometry_used=false with no payload
  if (
    geometryUsed !== true &&
    !geometryImages?.depth_png &&
    !geometryImages?.normals_png &&
    (!geometryMeta || Object.keys(geometryMeta).length === 0)
  ) {
    return null
  }

  const used = geometryUsed === true
  const metaEntries = geometryMeta
    ? [
        ['profile', geometryMeta.profile_resolved ?? geometryMeta.profile_requested],
        ['device', geometryMeta.device],
        ['depth model', geometryMeta.depth_model],
        ['normals', geometryMeta.normals_source],
      ].filter(([, value]) => value != null && String(value).length > 0)
    : []
  const warnings = Array.isArray(geometryMeta?.warnings)
    ? geometryMeta.warnings.filter((w): w is string => typeof w === 'string' && w.length > 0)
    : []

  return (
    <div
      className="geometry-evidence"
      data-testid="lighting-geometry-evidence"
      data-geometry-used={used ? 'true' : 'false'}
    >
      <h3>Geometry evidence</h3>
      <div className="geometry-status" data-testid="geometry-used-status">
        {used ? 'Real geometry extract applied' : 'Geometry not applied'}
      </div>

      {metaEntries.length > 0 && (
        <dl className="geometry-meta" data-testid="geometry-meta">
          {metaEntries.map(([label, value]) => (
            <div key={label} className="geometry-meta-row">
              <dt>{label}</dt>
              <dd>{String(value)}</dd>
            </div>
          ))}
        </dl>
      )}

      {warnings.length > 0 && (
        <ul className="geometry-warnings" data-testid="geometry-warnings">
          {warnings.map((warning) => (
            <li key={warning}>{warning}</li>
          ))}
        </ul>
      )}

      {(geometryImages?.depth_png || geometryImages?.normals_png) && (
        <div className="geometry-thumbnails" data-testid="geometry-thumbnails">
          {geometryImages.depth_png && (
            <figure className="geometry-thumb">
              <img
                src={toDataUrl(geometryImages.depth_png)}
                alt="Depth map preview"
                data-testid="geometry-depth-preview"
              />
              <figcaption>Depth</figcaption>
            </figure>
          )}
          {geometryImages.normals_png && (
            <figure className="geometry-thumb">
              <img
                src={toDataUrl(geometryImages.normals_png)}
                alt="Normals map preview"
                data-testid="geometry-normals-preview"
              />
              <figcaption>Normals</figcaption>
            </figure>
          )}
        </div>
      )}
    </div>
  )
}

export default LightingGeometryEvidence
