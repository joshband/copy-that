import './ScienceArtifactsPanel.css'
import { useMemo } from 'react'
import type { ArtifactBundle, ArtifactImage, ArtifactJson } from '../../../../types'

interface Props {
  artifacts?: ArtifactBundle | null
}

const formatLabel = (value: string) =>
  value
    .split('-')
    .map((part) => (part ? part[0].toUpperCase() + part.slice(1) : part))
    .join(' ')

const toDataUrl = (image: ArtifactImage) =>
  `data:${image.mime ?? 'image/png'};base64,${image.base64}`

export default function ScienceArtifactsPanel({ artifacts }: Props) {
  const { images, json } = useMemo(() => {
    if (!artifacts) {
      return { images: [] as ArtifactImage[], json: [] as ArtifactJson[] }
    }
    const images = (artifacts.images ?? []).filter((item) => item.stage === 'science')
    const json = (artifacts.json ?? []).filter((item) => item.stage === 'science')
    return { images, json }
  }, [artifacts])

  if (images.length === 0 && json.length === 0) {
    return null
  }

  return (
    <div className="science-artifacts">
      <div className="science-artifacts-header">
        <div>
          <p className="science-artifacts-kicker">Science artifacts</p>
          <h3>Palette analytics</h3>
          <p className="science-artifacts-subtitle">
            Palette-level visuals and metrics derived from OKLCH, Delta-E, and WCAG contrast.
          </p>
        </div>
        <div className="science-artifacts-counts">
          <span>{images.length} images</span>
          <span>{json.length} data</span>
        </div>
      </div>

      {images.length > 0 && (
        <div className="science-artifacts-grid">
          {images.map((item, index) => (
            <figure className="science-artifact-card" key={`${item.type}-${index}`}>
              <img
                src={toDataUrl(item)}
                alt={item.description ?? item.type}
                className="science-artifact-image"
                loading="lazy"
              />
              <figcaption className="science-artifact-caption">
                <span className="science-artifact-type">{formatLabel(item.type)}</span>
                {item.description ? ` · ${item.description}` : ''}
              </figcaption>
            </figure>
          ))}
        </div>
      )}

      {json.length > 0 && (
        <div className="science-artifacts-json">
          {json.map((item, index) => (
            <details className="science-artifact-json-card" key={`${item.type}-${index}`}>
              <summary>{formatLabel(item.type)}</summary>
              <pre>{JSON.stringify(item.payload, null, 2)}</pre>
            </details>
          ))}
        </div>
      )}
    </div>
  )
}
