/** Resolve aliases against the available graph; cycles and absent targets stay unavailable. */
export function resolveTypographyValue(value: unknown, tokens: Array<{ id: string; raw: { $value?: unknown } }>, seen = new Set<string>()): any {
  if (typeof value === 'string' && /^\{.+\}$/.test(value)) {
    const id = value.slice(1, -1)
    if (seen.has(id)) return undefined
    const token = tokens.find(t => t.id === id)
    return token ? resolveTypographyValue(token.raw.$value, tokens, new Set([...seen, id])) : undefined
  }
  if (Array.isArray(value)) return value.map(v => resolveTypographyValue(v, tokens, seen)).filter(v => v !== undefined)
  if (value && typeof value === 'object') return Object.fromEntries(Object.entries(value).map(([k, v]) => [k, resolveTypographyValue(v, tokens, seen)]))
  return value
}
