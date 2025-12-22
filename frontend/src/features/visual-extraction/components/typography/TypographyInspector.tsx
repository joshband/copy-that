import React from 'react'
import { useTokenGraphStore } from '../../../../store/tokenGraphStore'

const strip = (val: string) => (val.startsWith('{') && val.endsWith('}')) ? val.slice(1, -1) : val
const formatStyleValue = (value: unknown) => {
  if (Array.isArray(value)) return value.map((item) => String(item)).join(', ')
  if (value && typeof value === 'object') return JSON.stringify(value)
  return String(value)
}

const parseMetadata = (value: unknown): Record<string, unknown> | null => {
  if (!value) return null
  if (typeof value === 'string') {
    try {
      const parsed = JSON.parse(value)
      return parsed && typeof parsed === 'object' && !Array.isArray(parsed)
        ? (parsed as Record<string, unknown>)
        : null
    } catch {
      return null
    }
  }
  if (typeof value === 'object' && !Array.isArray(value)) {
    return value as Record<string, unknown>
  }
  return null
}

export default function TypographyInspector() {
  const typography = useTokenGraphStore((s) => s.typography)
  const colors = useTokenGraphStore((s) => s.colors)
  const recommendation = useTokenGraphStore((s) => s.typographyRecommendation)
  // Destructure recommendation to avoid repetitive optional chaining and to set defaults.
  const { confidence, styleAttributes } = recommendation ?? {}
  const styleEntries =
    styleAttributes && typeof styleAttributes === 'object'
      ? Object.entries(styleAttributes).filter(([, value]) => value != null && value !== '')
      : []
  if (!typography.length) return null

  const findColorHex = (id: string) => {
    const hit = colors.find((c) => c.id === id)
    const val = (hit?.raw)?.$value
    return (val as any)?.hex ?? val ?? '#ccc'
  }

  return (
    <section className="panel">
      <h2>Typography inspector</h2>
      {recommendation && (
        <div className="meta-row">
          <span className="badge">
            Confidence:{' '}
            <span
              className={
                typeof confidence === 'number' && !Number.isNaN(confidence) ? '' : 'standin'
              }
            >
              {typeof confidence === 'number' && !Number.isNaN(confidence) ? confidence.toFixed(2) : '—'}
            </span>
          </span>
          {styleEntries.length > 0 && (
            <div className="style-attrs">
              <span className="style-attrs-label">Style attributes</span>
              {styleEntries.map(([key, value]) => (
                <div key={key} className="style-attr">
                  <span className="style-attr-key">{key}</span>
                  <code className="style-attr-value">{formatStyleValue(value)}</code>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
      <ul className="token-list">
        {typography.map((t) => {
          const raw = t.raw as any
          const val = raw.$value
          const fontFamilyRaw = Array.isArray(val?.fontFamily) ? val.fontFamily[0] : val?.fontFamily
          const fontFamily = typeof fontFamilyRaw === 'string' ? strip(fontFamilyRaw) : undefined
          const fontSize = val?.fontSize
          const fontSizePx =
            fontSize && typeof fontSize === 'object' && 'value' in fontSize
              ? (fontSize).value
              : fontSize && typeof fontSize === 'object' && 'px' in fontSize
                ? fontSize.px
                : undefined
          const fontSizeUnit =
            fontSize && typeof fontSize === 'object' && 'unit' in fontSize
              ? (fontSize).unit
              : 'px'
          const lineHeight = val?.lineHeight
          const lineHeightPx =
            lineHeight && typeof lineHeight === 'object' && 'value' in lineHeight
              ? (lineHeight as any).value
              : lineHeight && typeof lineHeight === 'object' && 'px' in lineHeight
                ? (lineHeight as any).px
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
          const fontStyle = val?.fontStyle ?? '—'
          const fontFamilyDisplay = fontFamily ?? '—'
          const fontSizeDisplay =
            fontSizePx != null
              ? `${fontSizePx}${fontSizeUnit}`
              : typeof fontSize === 'string'
                ? fontSize
                : '—'
          const lineHeightDisplay =
            lineHeightPx != null
              ? `${lineHeightPx}${typeof lineHeight === 'object' && 'unit' in (lineHeight ?? {}) ? (lineHeight).unit ?? '' : 'px'}`
              : typeof lineHeight === 'number'
                ? String(lineHeight)
              : typeof lineHeight === 'string'
                ? lineHeight
                : '—'
          const letterSpacingDisplay = letterSpacingText ?? '—'
          const textAlign = val?.textAlign ?? '—'
          const extractionMeta = parseMetadata(raw?.extraction_metadata ?? raw?.attributes?.extraction_metadata)
          const baselineOverlay =
            extractionMeta && typeof extractionMeta.baseline_overlay === 'string'
              ? extractionMeta.baseline_overlay
              : null
        return (
          <li key={t.id}>
            <strong>{t.id}</strong>
            <div>
              Font:{' '}
              <span className={fontFamily ? '' : 'standin'}>{fontFamilyDisplay}</span>
            </div>
            <div>
              Size:{' '}
              <span className={fontSizeDisplay === '—' ? 'standin' : ''}>{fontSizeDisplay}</span>
            </div>
            <div>
              Line height:{' '}
              <span className={lineHeightDisplay === '—' ? 'standin' : ''}>{lineHeightDisplay}</span>
            </div>
            <div>
              Weight: <span className={fontWeight === '—' ? 'standin' : ''}>{fontWeight}</span>
            </div>
            <div>
              Style: <span className={fontStyle === '—' ? 'standin' : ''}>{fontStyle}</span>
            </div>
            <div>
              Letter spacing:{' '}
              <span className={letterSpacingDisplay === '—' ? 'standin' : ''}>{letterSpacingDisplay}</span>
            </div>
            <div>
              Casing: <span className={casing === '—' ? 'standin' : ''}>{casing}</span>
            </div>
            <div>
              Align: <span className={textAlign === '—' ? 'standin' : ''}>{textAlign}</span>
            </div>
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
                  fontWeight: fontWeight,
                  fontStyle: fontStyle === '—' ? undefined : fontStyle,
                  lineHeight: lineHeightPx != null ? `${lineHeightPx}px` : undefined,
                  letterSpacing:
                    letterSpacing && typeof letterSpacingText === 'string' ? letterSpacingText : undefined,
                  textTransform: casing === 'uppercase' ? 'uppercase' : undefined,
                  textAlign: textAlign === '—' ? undefined : textAlign,
                  color: colorHex,
                }}
              >
                The quick brown fox jumps over the lazy dog.
              </div>
              {baselineOverlay && (
                <div style={{ marginTop: '0.75rem' }}>
                  <span className="badge">Baseline overlay</span>
                  <img
                    src={`data:image/png;base64,${baselineOverlay}`}
                    alt="Typography baseline overlay"
                    style={{
                      display: 'block',
                      maxWidth: '100%',
                      marginTop: '0.5rem',
                      borderRadius: '8px',
                      border: '1px solid rgba(0, 0, 0, 0.08)',
                    }}
                  />
                </div>
              )}
            </li>
          )
        })}
      </ul>
    </section>
  )
}
