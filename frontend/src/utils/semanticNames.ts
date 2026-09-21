export function formatSemanticValue(value: unknown): string {
  if (value == null) return ''

  if (typeof value === 'string' || typeof value === 'number' || typeof value === 'boolean') {
    return String(value)
  }

  if (Array.isArray(value)) {
    const flattened = value
      .map((item) => formatSemanticValue(item))
      .filter((item) => item !== '')
    return flattened.join(', ')
  }

  if (typeof value === 'object') {
    const record = value as Record<string, unknown>
    const candidateKeys = ['name', 'label', 'title', 'value', 'display']

    for (const key of candidateKeys) {
      const candidate = record[key]
      if (typeof candidate === 'string' && candidate.trim() !== '') {
        return candidate
      }
    }

    const nested = Object.values(record)
      .map((item) => formatSemanticValue(item))
      .filter((item) => item !== '')

    if (nested.length > 0) {
      return nested.join(', ')
    }

    try {
      return JSON.stringify(value)
    } catch {
      return String(value)
    }
  }

  return String(value)
}

export function pickPreferredSemanticName(
  semanticNames: Record<string, unknown> | string | null | undefined,
  preferences: string[] = ['descriptive', 'simple', 'emotional', 'technical', 'vibrancy']
): string | undefined {
  if (!semanticNames) return undefined

  if (typeof semanticNames === 'string') {
    return semanticNames
  }

  for (const key of preferences) {
    const value = semanticNames[key]
    const formatted = formatSemanticValue(value)
    if (formatted.trim() !== '') {
      return formatted
    }
  }

  const firstValue = Object.values(semanticNames)[0]
  const formatted = formatSemanticValue(firstValue)
  return formatted.trim() === '' ? undefined : formatted
}
