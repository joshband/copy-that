import React from 'react'

type ShadowValue = {
  color: string
  x: { value: number; unit: string }
  y: { value: number; unit: string }
  blur: { value: number; unit: string }
  spread: { value: number; unit: string }
}

interface ShadowToken {
  id?: string
  $value: ShadowValue
}

interface Props {
  shadows: ShadowToken[] | Record<string, ShadowToken> | null | undefined
}

const ShadowTokenList: React.FC<Props> = ({ shadows }) => {
  const list: ShadowToken[] = Array.isArray(shadows)
    ? shadows
    : shadows && typeof shadows === 'object'
      ? Object.values(shadows)
      : []

  if (!list || list.length === 0) {
    return <div className="empty-state">No shadows extracted yet.</div>
  }

  return (
    <div className="shadow-list">
      {list.map((shadow, idx) => (
        <div key={shadow.id ?? idx} className="shadow-card">
          <div className="shadow-swatch" />
          <div className="shadow-info">
            <div className="shadow-title">{shadow.id ?? `shadow.${idx + 1}`}</div>
            <div className="shadow-props">
              <span>Color: {shadow.$value.color}</span>
              <span>
                Offset: {shadow.$value.x.value}{shadow.$value.x.unit},{' '}
                {shadow.$value.y.value}{shadow.$value.y.unit}
              </span>
              <span>
                Blur: {shadow.$value.blur.value}
                {shadow.$value.blur.unit} | Spread: {shadow.$value.spread.value}
                {shadow.$value.spread.unit}
              </span>
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}

export default ShadowTokenList
