/**
 * Format a 0–1 confidence as a percentage string.
 * Returns null when value is missing/invalid so callers omit invented %s.
 */
export function formatConfidence(value?: number | null): string | null {
  if (typeof value !== 'number' || Number.isNaN(value)) return null
  if (value < 0 || value > 1) return null
  return `${Math.round(value * 100)}%`
}

/** Display helper: confidence label or em dash when unknown. */
export function formatConfidenceOrDash(value?: number | null): string {
  return formatConfidence(value) ?? '—'
}
