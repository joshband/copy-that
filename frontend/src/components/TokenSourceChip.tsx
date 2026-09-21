/**
 * Token origin chip — maps export attributes.source to a short label.
 * Missing source ≈ extracted from the image (not synth/preset/derived).
 */

import './TokenSourceChip.css'

export type TokenSourceKind =
  | 'extracted'
  | 'derived'
  | 'synth'
  | 'preset'
  | 'fallback'
  | 'color-pair'
  | 'shadow'
  | 'cv'
  | 'ai'
  | 'other'

const LABELS: Record<TokenSourceKind, string> = {
  extracted: 'Extracted',
  derived: 'Derived',
  synth: 'Synth',
  preset: 'Preset',
  fallback: 'Fallback',
  'color-pair': 'From colors',
  shadow: 'From shadows',
  cv: 'CV',
  ai: 'AI',
  other: 'Other',
}

function readMeasuredFlag(raw?: Record<string, unknown> | null): boolean | undefined {
  if (!raw || typeof raw !== 'object') return undefined
  const attrs =
    raw.attributes && typeof raw.attributes === 'object'
      ? (raw.attributes as Record<string, unknown>)
      : undefined
  const meta =
    (raw.extraction_metadata as Record<string, unknown> | undefined) ??
    (attrs?.extraction_metadata as Record<string, unknown> | undefined)
  if (meta && typeof meta.measured === 'boolean') return meta.measured
  return undefined
}

export function resolveTokenSource(raw?: Record<string, unknown> | null): TokenSourceKind {
  if (!raw || typeof raw !== 'object') return 'extracted'
  const attrs =
    raw.attributes && typeof raw.attributes === 'object'
      ? (raw.attributes as Record<string, unknown>)
      : undefined
  const ext =
    raw.$extensions && typeof raw.$extensions === 'object'
      ? (raw.$extensions as Record<string, unknown>)
      : undefined
  const meta =
    (raw.extraction_metadata as Record<string, unknown> | undefined) ??
    (attrs?.extraction_metadata as Record<string, unknown> | undefined)
  const source = raw.source ?? attrs?.source ?? ext?.source ?? meta?.source
  if (typeof source === 'string' && source.trim()) {
    const normalized = source.trim().toLowerCase()
    if (normalized === 'cv_fallback' || normalized.endsWith('_fallback')) return 'fallback'
    if (normalized in LABELS) return normalized as TokenSourceKind
    if (normalized === 'color_pair') return 'color-pair'
    if (normalized.startsWith('cv')) return 'cv'
    return 'other'
  }
  if (readMeasuredFlag(raw) === false) return 'fallback'
  return 'extracted'
}

export interface TokenSourceChipProps {
  source?: TokenSourceKind | string | null
  raw?: Record<string, unknown> | null
  className?: string
}

export function TokenSourceChip({ source, raw, className }: TokenSourceChipProps) {
  const kind: TokenSourceKind =
    typeof source === 'string' && source in LABELS
      ? (source as TokenSourceKind)
      : resolveTokenSource(raw)

  return (
    <span
      className={`token-source-chip token-source-chip--${kind}${className ? ` ${className}` : ''}`}
      data-testid="token-source-chip"
      data-source={kind}
      title={`Token origin: ${LABELS[kind]}`}
    >
      {LABELS[kind]}
    </span>
  )
}

export default TokenSourceChip
