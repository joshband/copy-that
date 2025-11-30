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
          const fontFamilyRaw = Array.isArray(val?.fontFamily) ? val.fontFamily[0] : val?.fontFamily
          const fontFamily = typeof fontFamilyRaw === 'string' ? strip(fontFamilyRaw) : undefined
          const fontSize = val?.fontSize
          const fontSizePx =
            fontSize && typeof fontSize === 'object' && 'value' in fontSize
              ? (fontSize as any).value
              : fontSize && typeof fontSize === 'object' && 'px' in fontSize
                ? fontSize.px
                : undefined
          const fontSizeUnit =
            fontSize && typeof fontSize === 'object' && 'unit' in fontSize
              ? (fontSize as any).unit
              : 'px'
          const lineHeight = val?.lineHeight
          const lineHeightPx =
            lineHeight && typeof lineHeight === 'object' && 'value' in lineHeight
              ? (lineHeight as any).value
              : lineHeight && typeof lineHeight === 'object' && 'px' in lineHeight
                ? lineHeight.px
                : undefined
          const colorRef = val?.color && typeof val.color === 'string' ? strip(val.color) : undefined
          const colorHex = colorRef ? findColorHex(colorRef) : undefined
          const letterSpacing = val?.letterSpacing
          const letterSpacingText =
            letterSpacing && typeof letterSpacing === 'object' && 'value' in letterSpacing
              ? `${letterSpacing.value}${letterSpacing.unit ?? ''}`
              : letterSpacing && typeof letterSpacing === 'object' && 'em' in letterSpacing
                ? `${letterSpacing.em}em`
                : letterSpacing ?? undefined
          const casing = val?.casing ?? '—'
          const fontWeight = val?.fontWeight ?? '—'
          return (
            <li key={t.id}>
              <strong>{t.id}</strong>
              <div>Font: {fontFamily ?? '—'}</div>
              <div>
                Size:{' '}
                {fontSizePx != null
                  ? `${fontSizePx}${fontSizeUnit}`
                  : typeof fontSize === 'string'
                    ? fontSize
                    : '—'}
              </div>
              <div>
                Line height:{' '}
                {lineHeightPx != null
                  ? `${lineHeightPx}${typeof lineHeight === 'object' && 'unit' in (lineHeight ?? {}) ? (lineHeight as any).unit ?? '' : 'px'}`
                  : typeof lineHeight === 'string'
                    ? lineHeight
                    : '—'}
              </div>
              <div>Weight: {fontWeight}</div>
              <div>Letter spacing: {letterSpacingText ?? '—'}</div>
              <div>Casing: {casing}</div>
              {colorRef && (
                <div className="color-row">
                  Color: <code>{colorRef}</code>{' '}
                  {colorHex && <span className="color-swatch" style={{ background: colorHex }} />}
                </div>
              )}
              <div
                className="typography-sample"
                style={{
                  fontFamily,
                  fontSize: fontSizePx != null ? `${fontSizePx}${fontSizeUnit}` : undefined,
                  fontWeight: fontWeight as any,
                  lineHeight: lineHeightPx != null ? `${lineHeightPx}px` : undefined,
                  letterSpacing:
                    letterSpacing && typeof letterSpacingText === 'string' ? letterSpacingText : undefined,
                  textTransform: casing === 'uppercase' ? 'uppercase' : undefined,
                  color: colorHex,
                }}
              >
                The quick brown fox jumps over the lazy dog.
              </div>
            </li>
          )
        })}
      </ul>
    </section>
  )
}
