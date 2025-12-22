import { useMemo } from 'react'
import './ShadowArtifactsPanel.css'
import type { ArtifactBundle, ArtifactImage } from '../../../../types'

interface Props {
  artifacts?: ArtifactBundle | null
}

const formatLabel = (value: string) =>
  value
    .split('_')
    .map((part) => (part ? part[0].toUpperCase() + part.slice(1) : part))
    .join(' ')

const toDataUrl = (image: ArtifactImage) =>
  `data:${image.mime ?? 'image/png'};base64,${image.base64}`

export default function ShadowArtifactsPanel({ artifacts }: Props) {
  const images = useMemo(() => {
    if (!artifacts?.images?.length) return []
    return artifacts.images
  }, [artifacts])

  if (!images.length) {
    return null
  }

  return (
    <div className="shadow-artifacts">
      <div className="shadow-artifacts__header">
        <div>
          <p className="shadow-artifacts__kicker">Shadow artifacts</p>
          <h3>Mask + lighting previews</h3>
          <p className="shadow-artifacts__subtitle">
            Review shadowlab masks and illumination layers to validate the extracted shadow stack.
          </p>
        </div>
        <div className="shadow-artifacts__counts">
          <span>{images.length} images</span>
        </div>
      </div>

      <div className="shadow-artifacts__grid">
        {images.map((item, index) => (
          <figure className="shadow-artifacts__card" key={`${item.type}-${index}`}>
            <img
              src={toDataUrl(item)}
              alt={`Shadow artifact ${formatLabel(item.type)}`}
              className="shadow-artifacts__image"
              loading="lazy"
            />
            <figcaption className="shadow-artifacts__caption">
              <span className="shadow-artifacts__type">{formatLabel(item.type)}</span>
              {item.description ? ` · ${item.description}` : ''}
            </figcaption>
          </figure>
        ))}
      </div>
    </div>
  )
}
