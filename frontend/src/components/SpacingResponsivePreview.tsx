import React, { useState } from 'react'
import { useTokenGraphStore } from '../store/tokenGraphStore'

interface ResponsiveBreakpoint {
  name: string
  key: string
  width: number
}

const BREAKPOINTS: ResponsiveBreakpoint[] = [
  { name: 'Mobile', key: 'sm', width: 375 },
  { name: 'Tablet', key: 'md', width: 768 },
  { name: 'Desktop', key: 'lg', width: 1024 },
]

/**
 * Responsive Spacing Preview
 * Shows how spacing adapts across breakpoints and devices
 */
export default function SpacingResponsivePreview({ fallback }: { fallback?: any[] }) {
  const spacing = useTokenGraphStore((s: any) => s.spacing)
  const [activeBreakpoint, setActiveBreakpoint] = useState<string>('md')

  const tokens = (spacing.length ? spacing : fallback || [])
    .map((s: any) => {
      const val = s.raw?.$value || { value: s.value_px }
      const px = typeof val === 'object' && val ? val.value : s.value_px
      const rem = typeof px === 'number' ? px / 16 : 0
      return {
        id: s.id || s.name || `spacing-${px}`,
        px,
        rem,
        responsive_scales: s.responsive_scales,
      }
    })
    .sort((a, b) => a.px - b.px)

  // Check if any token has responsive data
  const hasResponsiveData = tokens.some(t => t.responsive_scales && Object.keys(t.responsive_scales).length > 0)

  if (!tokens.length || !hasResponsiveData) {
    return null
  }

  return (
    <div className="spacing-responsive-section">
      <div className="responsive-header">
        <div className="responsive-title">Responsive Scales</div>
        <p className="responsive-subtitle">Spacing values adapt across breakpoints</p>
      </div>

      {/* Breakpoint Selector */}
      <div className="breakpoint-selector">
        {BREAKPOINTS.map((bp) => (
          <button
            key={bp.key}
            className={`breakpoint-btn ${activeBreakpoint === bp.key ? 'active' : ''}`}
            onClick={() => setActiveBreakpoint(bp.key)}
          >
            <div className="bp-name">{bp.name}</div>
            <div className="bp-width">{bp.width}px</div>
          </button>
        ))}
      </div>

      {/* Responsive Preview */}
      <div className="responsive-preview">
        <div className="preview-frame" style={{ maxWidth: BREAKPOINTS.find(b => b.key === activeBreakpoint)?.width }}>
          <div className="preview-label">
            {BREAKPOINTS.find(b => b.key === activeBreakpoint)?.name} View
          </div>

          {/* Sample component with responsive spacing */}
          <div className="responsive-demo">
            {tokens.map((token) => {
              const responsiveValue = token.responsive_scales?.[activeBreakpoint] || token.px
              return (
                <div
                  key={token.id}
                  className="responsive-demo-item"
                  style={{ '--responsive-spacing': `${responsiveValue}px` } as React.CSSProperties}
                >
                  <div className="demo-label">{token.id}</div>
                  <div className="demo-value">
                    {responsiveValue}px {responsiveValue !== token.px && <span className="changed">↔</span>}
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      </div>

      {/* Responsive Table */}
      <div className="responsive-table-section">
        <div className="table-title">Breakpoint Mapping</div>
        <div className="responsive-table-container">
          <table className="responsive-table">
            <thead>
              <tr>
                <th>Token</th>
                <th>Base</th>
                {BREAKPOINTS.map((bp) => (
                  <th key={bp.key}>{bp.name}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {tokens
                .filter(t => t.responsive_scales && Object.keys(t.responsive_scales).length > 0)
                .map((token) => (
                  <tr key={token.id}>
                    <td className="token-name">{token.id}</td>
                    <td className="token-base">{token.px}px</td>
                    {BREAKPOINTS.map((bp) => {
                      const value = token.responsive_scales?.[bp.key] ?? token.px
                      const changed = value !== token.px
                      return (
                        <td key={bp.key} className={changed ? 'changed' : ''}>
                          {value}px
                        </td>
                      )
                    })}
                  </tr>
                ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
