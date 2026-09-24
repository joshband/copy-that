import { useMemo, useState } from 'react'
import { shallow } from 'zustand/shallow'
import { useTokenGraphStore } from '../../../../store/tokenGraphStore'
import type { UiSpacingToken, UiTokenBase } from '../../../../store/tokenGraphStore'
import './LayoutTokenPanel.css'

interface LayoutPreviewState {
  columns: number
  gutter: number
  margin: number
  baseUnit?: number
}

interface ShapePreviewState {
  radius?: number
  border?: number
}

const toNumber = (value: unknown): number => {
  if (typeof value === 'number') return value
  if (typeof value === 'string') {
    const parsed = Number.parseFloat(value)
    return Number.isFinite(parsed) ? parsed : 0
  }
  if (value && typeof value === 'object' && 'value' in value && typeof (value as any).value === 'number') {
    return (value as any).value as number
  }
  return 0
}

const marginValue = (rawMargin: unknown): number => {
  if (rawMargin && typeof rawMargin === 'object') {
    const entries = Object.values(rawMargin as Record<string, unknown>)
    if (entries.length) {
      return Math.max(...entries.map(toNumber))
    }
  }
  return toNumber(rawMargin)
}

const extractSpacingValue = (token: UiSpacingToken): number => {
  const raw = token.raw as any
  if (raw?.$value && typeof raw.$value === 'object' && 'value' in raw.$value) {
    return toNumber(raw.$value.value)
  }
  if (raw?.$value != null) return toNumber(raw.$value)
  if (raw?.value && typeof raw.value === 'object' && 'value' in raw.value) return toNumber(raw.value.value)
  return 0
}

const roleFromToken = (token: UiTokenBase<unknown> | UiSpacingToken): string => {
  const raw = (token as any)?.raw ?? {}
  return (
    raw.role ||
    raw.$extensions?.role ||
    raw.attributes?.role ||
    (typeof token.id === 'string' && token.id.includes('gridColumns') ? 'grid_columns' : '') ||
    ''
  )
}

const buildLayoutPreview = (
  layoutTokens: UiTokenBase<unknown>[],
  spacingTokens: UiSpacingToken[],
): {
  grid: LayoutPreviewState | null
  shape: ShapePreviewState
  tokens: Array<{ id: string; role: string; value: number; baseUnit?: number; spacingReference?: string }>
  hasMeasured: boolean
} => {
  let columns: number | undefined
  let gutter: number | undefined
  let margin: number | undefined
  let baseUnit: number | undefined
  const shape: ShapePreviewState = {}

  const parsedTokens: Array<{ id: string; role: string; value: number; baseUnit?: number; spacingReference?: string }> = []

  layoutTokens.forEach((token) => {
    const raw = (token.raw as any) ?? {}
    const role = roleFromToken(token)
    const rawValue = raw.$value ?? raw.value ?? {}
    const tokenBase = typeof raw.base_unit === 'number' ? raw.base_unit : undefined
    const spacingReference = typeof raw.spacing_reference === 'string' ? raw.spacing_reference : undefined
    if (tokenBase != null) baseUnit = baseUnit ?? tokenBase

    if (role === 'gutter') {
      gutter = toNumber(rawValue.value ?? rawValue.gutter ?? rawValue)
      parsedTokens.push({ id: token.id, role, value: gutter, baseUnit: tokenBase, spacingReference })
    } else if (role === 'margin') {
      margin = marginValue(rawValue.margin ?? rawValue)
      parsedTokens.push({ id: token.id, role, value: margin, baseUnit: tokenBase, spacingReference })
    } else if (role === 'corner_radius') {
      shape.radius = toNumber(rawValue.radius ?? rawValue)
      parsedTokens.push({ id: token.id, role, value: shape.radius ?? 0, baseUnit: tokenBase, spacingReference })
    } else if (role === 'border_width') {
      const rawBorder = rawValue.border ?? rawValue
      const borderValue = rawBorder && typeof rawBorder === 'object' ? rawBorder.width ?? rawBorder : rawBorder
      shape.border = toNumber(borderValue)
      parsedTokens.push({ id: token.id, role, value: shape.border ?? 0, baseUnit: tokenBase, spacingReference })
    }
  })

  const gridColumnToken = spacingTokens.find((token) => roleFromToken(token) === 'grid_columns' || `${token.id}`.includes('gridColumns'))
  if (gridColumnToken) {
    const cols = extractSpacingValue(gridColumnToken)
    if (cols > 0) {
      columns = cols
      parsedTokens.push({ id: gridColumnToken.id, role: 'grid_columns', value: cols })
    }
  }

  const hasMeasured = parsedTokens.length > 0
  const grid =
    hasMeasured && (columns != null || gutter != null || margin != null)
      ? {
          columns: columns ?? 1,
          gutter: gutter ?? 0,
          margin: margin ?? 0,
          baseUnit,
        }
      : null

  return { grid, shape, tokens: parsedTokens, hasMeasured }
}

export function LayoutTokenPanel({ showDebug = false }: { showDebug?: boolean }) {
  const { layout, spacing, legacySpacing } = useTokenGraphStore(
    (s) => ({ layout: s.layout, spacing: s.spacing, legacySpacing: s.legacySpacing }),
    shallow,
  )

  const legacySpacingTokens = useMemo(() => legacySpacing(), [legacySpacing])
  const { grid, shape, tokens, hasMeasured } = useMemo(
    () => buildLayoutPreview(layout, spacing),
    [layout, spacing],
  )

  const [showGridLines, setShowGridLines] = useState(true)
  const [showSpacingEdges, setShowSpacingEdges] = useState(true)
  const [showShapeHighlights, setShowShapeHighlights] = useState(true)

  const spacingAlignment = useMemo(() => {
    if (!legacySpacingTokens.length) return { alignedRate: null, groups: 0 }
    const aligned = legacySpacingTokens.filter((t) => t.grid_aligned === true).length
    const groups = new Set(
      legacySpacingTokens
        .map((t) => t.semantic_role)
        .filter((v): v is string => Boolean(v)),
    ).size
    return { alignedRate: aligned / legacySpacingTokens.length, groups }
  }, [legacySpacingTokens])

  const gridConfidence =
    spacingAlignment.alignedRate != null
      ? Math.round(spacingAlignment.alignedRate * 100)
      : null

  if (!hasMeasured || !grid) {
    return (
      <div className="layout-panel">
        <div className="empty-state">
          <h3 className="standin">No layout tokens yet</h3>
          <p className="standin">
            Grid inference appears here when layout values are available.
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="layout-panel">
      <header className="layout-panel__header">
        <div>
          <p className="eyebrow">Layout tokens</p>
          <h3>Grid, border, and radius</h3>
          <p className="muted">
            Illustrative grid from inferred layout values. This is not an overlay of source coordinates.
          </p>
        </div>
        <div className="layout-panel__toggles">
          <label className="toggle">
            <input type="checkbox" checked={showGridLines} onChange={() => setShowGridLines((v) => !v)} />
            <span>Grid lines</span>
          </label>
          <label className="toggle">
            <input type="checkbox" checked={showSpacingEdges} onChange={() => setShowSpacingEdges((v) => !v)} />
            <span>Spacing edges</span>
          </label>
          <label className="toggle">
            <input type="checkbox" checked={showShapeHighlights} onChange={() => setShowShapeHighlights((v) => !v)} />
            <span>Border & radius</span>
          </label>
        </div>
      </header>

      <div className="layout-viewport" aria-label="Grid preview" data-testid="layout-viewport">
        <div className="layout-viewport__surface" style={{ paddingInline: `${grid.margin}px` }}>
          <div
            className={`layout-columns ${showGridLines ? 'layout-columns--visible' : ''}`}
            style={{
              gridTemplateColumns: `repeat(${grid.columns}, minmax(0, 1fr))`,
              gap: `${grid.gutter}px`,
            }}
            title={`Grid: ${grid.columns} columns • gutter ${grid.gutter}px • margin ${grid.margin}px`}
          >
            {Array.from({ length: grid.columns }).map((_, idx) => (
              <div key={idx} className="layout-column" />
            ))}
          </div>

          {showSpacingEdges && (
            <div className="layout-guides" aria-label="Spacing guides">
              <div className="layout-guide layout-guide--margin" style={{ left: 0 }}>
                Margin {grid.margin}px
              </div>
              <div className="layout-guide layout-guide--margin" style={{ right: 0 }}>
                Margin {grid.margin}px
              </div>
              <div className="layout-guide layout-guide--gutter">Gutter {grid.gutter}px</div>
            </div>
          )}

          {showShapeHighlights && (shape.border != null || shape.radius != null) && (
            <div
              className="layout-shape-preview"
              style={{
                borderWidth: `${shape.border ?? 0}px`,
                borderRadius: `${shape.radius ?? 0}px`,
              }}
              title={`Border ${shape.border ?? 0}px · Radius ${shape.radius ?? 0}px`}
            >
              <div className="layout-shape-preview__label">Border & radius highlight</div>
              <div className="layout-shape-preview__meta">
                {shape.border != null ? `${shape.border}px border` : 'Border token missing'} ·{' '}
                {shape.radius != null ? `${shape.radius}px radius` : 'Radius token missing'}
              </div>
            </div>
          )}
        </div>
      </div>

      <div className="layout-why">
        {showDebug && (
          <div>
            <p className="eyebrow">Why these values</p>
            <h4>Estimated from spacing alignment</h4>
            <ul className="layout-why__list">
              <li title="Share of spacing tokens marked grid-aligned">
                <strong>{gridConfidence != null ? `${gridConfidence}%` : '—'}</strong> spacing
                tokens grid-aligned
              </li>
              <li title="Alignment groups derived from semantic spacing roles">
                <strong>{spacingAlignment.groups || '—'}</strong> alignment groups observed
              </li>
              <li title="Base unit emitted with gutter/margin tokens when available">
                <strong>{grid.baseUnit ?? '—'}</strong> px base unit anchor
              </li>
            </ul>
          </div>
        )}
        <div>
          <p className="eyebrow">Inspector</p>
          <div className="layout-token-table" role="list">
            {tokens.length === 0 ? (
              <p className="muted standin">No layout tokens yet.</p>
            ) : (
              tokens.map((token) => {
              const label = token.role.replace('_', ' ')
              const tooltip = [
                `${label}: ${token.value}px`,
                token.baseUnit ? `Base ${token.baseUnit}px` : null,
                token.spacingReference ? `Derived from ${token.spacingReference}` : null,
              ]
                .filter(Boolean)
                .join(' · ')
              return (
                <div className="layout-token-row" key={token.id} role="listitem" title={tooltip}>
                  <div className="layout-token-row__label">{label}</div>
                  <div className="layout-token-row__value">{token.value}px</div>
                  <div className="layout-token-row__meta">
                    {token.baseUnit ? <span>Base {token.baseUnit}px</span> : <span>Measured</span>}
                    {token.spacingReference && <span className="muted">ref {token.spacingReference}</span>}
                  </div>
                </div>
              )
            })
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default LayoutTokenPanel
