import React from 'react'
import { useTokenGraphStore } from '../../../../store/tokenGraphStore'

interface FontFamilyToken {
  name: string
  confidence: number
  weights: Set<number | string>
  sizes: Set<string>
  usage: number
}

/**
 * Font Family Showcase
 * Shows all unique font families with their variations and usage
 */
export default function FontFamilyShowcase() {
  const typography = useTokenGraphStore((s: any) => s.typography)

  // Extract unique font families and their properties
  const fontFamilies = new Map<string, FontFamilyToken>()

  typography.forEach((t: any) => {
    const val = t.raw?.$value || {}
    const fontFamily = Array.isArray(val.fontFamily) ? val.fontFamily[0] : val.fontFamily
    const fontFamilyName = typeof fontFamily === 'string' ? fontFamily : undefined

    if (!fontFamilyName) return

    if (!fontFamilies.has(fontFamilyName)) {
      fontFamilies.set(fontFamilyName, {
        name: fontFamilyName,
        confidence: t.confidence || 0.8,
        weights: new Set(),
        sizes: new Set(),
        usage: 0,
      })
    }

    const family = fontFamilies.get(fontFamilyName)!
    if (val.fontWeight) family.weights.add(val.fontWeight)
    if (val.fontSize) family.sizes.add(typeof val.fontSize === 'string' ? val.fontSize : `${val.fontSize.value}${val.fontSize.unit || 'px'}`)
    family.usage += 1
  })

  if (fontFamilies.size === 0) {
    return null
  }

  const sortedFamilies = Array.from(fontFamilies.values()).sort((a, b) => b.usage - a.usage)

  return (
    <div className="font-family-showcase">
      <div className="font-showcase-title">Font Families</div>
      <p className="font-showcase-subtitle">All unique fonts in the system</p>

      <div className="font-family-grid">
        {sortedFamilies.map((family) => (
          <div key={family.name} className="font-family-card">
            {/* Family Name */}
            <div className="font-family-header">
              <div className="font-family-name">{family.name}</div>
              <div className="font-family-badge">{family.usage} styles</div>
            </div>

            {/* Preview */}
            <div
              className="font-family-preview"
              style={{
                fontFamily: family.name,
              }}
            >
              The quick brown fox
            </div>

            {/* Details */}
            <div className="font-family-details">
              {/* Weights */}
              {family.weights.size > 0 && (
                <div className="detail-row">
                  <span className="detail-label">Weights</span>
                  <div className="font-weights">
                    {Array.from(family.weights)
                      .sort((a, b) => {
                        const aNum = typeof a === 'number' ? a : parseInt(String(a))
                        const bNum = typeof b === 'number' ? b : parseInt(String(b))
                        return aNum - bNum
                      })
                      .map((w, i) => (
                        <span key={i} className="weight-tag">
                          {w}
                        </span>
                      ))}
                  </div>
                </div>
              )}

              {/* Sizes */}
              {family.sizes.size > 0 && (
                <div className="detail-row">
                  <span className="detail-label">Sizes</span>
                  <div className="font-sizes">
                    {Array.from(family.sizes)
                      .sort()
                      .slice(0, 3)
                      .map((s, i) => (
                        <span key={i} className="size-tag">
                          {s}
                        </span>
                      ))}
                    {family.sizes.size > 3 && <span className="size-tag">+{family.sizes.size - 3}</span>}
                  </div>
                </div>
              )}

              {/* Confidence */}
              <div className="detail-row">
                <span className="detail-label">Confidence</span>
                <div className="font-confidence" style={{ '--font-confidence': family.confidence } as React.CSSProperties}>
                  {Math.round(family.confidence * 100)}%
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
