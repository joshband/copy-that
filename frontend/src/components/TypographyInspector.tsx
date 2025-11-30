import React from 'react'
import { useTokenGraphStore } from '../store/tokenGraphStore'

const strip = (val: string) => (val.startsWith('{') && val.endsWith('}')) ? val.slice(1, -1) : val

export default function TypographyInspector() {
  const typography = useTokenGraphStore((s) => s.typography)
  const colors = useTokenGraphStore((s) => s.colors)
  if (!typography.length) return null

  const findColorHex = (id: string) => {
    const hit = colors.find((c) => c.id === id)
    const val = (hit?.raw as any)?.$value as any
    return val?.hex ?? val ?? '#ccc'
  }

  return (
    <section className="panel">
      <h2>Typography inspector</h2>
      <ul className="token-list">
        {typography.map((t) => {
          const val = t.raw.$value as any
          const fontFamily = typeof val?.fontFamily === 'string' ? strip(val.fontFamily) : undefined
          const fontSize = val?.fontSize
          const fontSizePx = fontSize && typeof fontSize === 'object' && 'px' in fontSize ? fontSize.px : undefined
          const lineHeight = val?.lineHeight
          const lineHeightPx = lineHeight && typeof lineHeight === 'object' && 'px' in lineHeight ? lineHeight.px : undefined
          const colorRef = val?.color && typeof val.color === 'string' ? strip(val.color) : undefined
          const colorHex = colorRef ? findColorHex(colorRef) : undefined
          return (
            <li key={t.id}>
              <strong>{t.id}</strong>
              <div>Font: {fontFamily ?? '—'}</div>
              <div>Size: {fontSizePx != null ? `${fontSizePx}px` : typeof fontSize === 'string' ? fontSize : '—'}</div>
              <div>Line height: {lineHeightPx != null ? `${lineHeightPx}px` : typeof lineHeight === 'string' ? lineHeight : '—'}</div>
              <div>Weight: {val?.fontWeight ?? '—'}</div>
              {colorRef && (
                <div>
                  Color: <code>{colorRef}</code> {colorHex && <span className="color-swatch" style={{ background: colorHex }} />}
                </div>
              )}
            </li>
          )
        })}
      </ul>
    </section>
  )
}
