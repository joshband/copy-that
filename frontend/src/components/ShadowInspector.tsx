import React from 'react'
import { useTokenGraphStore } from '../store/tokenGraphStore'
import { useTokenGraphStore as useColors } from '../store/tokenGraphStore'

const strip = (val: string) => (val.startsWith('{') && val.endsWith('}')) ? val.slice(1, -1) : val

export default function ShadowInspector() {
  const shadows = useTokenGraphStore((s) => s.shadows)
  const colors = useColors((s) => s.colors)
  if (!shadows.length) return null

  const findColorHex = (id: string) => {
    const hit = colors.find((c) => c.id === id)
    const val = (hit?.raw)?.$value
    return val?.hex ?? val ?? '#ccc'
  }

  return (
    <section className="panel">
      <h2>Shadow inspector</h2>
      <ul className="token-list">
        {shadows.map((sh) => {
          const layers = Array.isArray(sh.raw.$value) ? sh.raw.$value : [sh.raw.$value]
          return (
            <li key={sh.id}>
              <strong>{sh.id}</strong>
              <ol>
                {layers.map((layer, idx) => {
                  const colorRef = layer?.color && typeof layer.color === 'string' ? strip(layer.color) : undefined
                  const hex = colorRef ? findColorHex(colorRef) : undefined
                  const dim = (v: any) => (v && typeof v === 'object' && 'value' in v ? v.value : v)
                  return (
                    <li key={idx}>
                      offset ({dim(layer.x)}px, {dim(layer.y)}px), blur {dim(layer.blur)}px, spread {dim(layer.spread)}px, inset {String(layer.inset ?? false)}{' '}
                      {colorRef && (
                        <span>
                          color <code>{colorRef}</code> {hex && <span className="color-swatch" style={{ background: hex }} />}
                        </span>
                      )}
                    </li>
                  )
                })}
              </ol>
            </li>
          )
        })}
      </ul>
    </section>
  )
}
