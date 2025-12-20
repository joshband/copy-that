export interface SpacingToken {
  id: string
  name?: string
  value_px: number
  value_rem?: number
  confidence?: number
  role?: string
  [key: string]: unknown
}

export interface SpacingLibrary {
  tokens: SpacingToken[]
  statistics?: Record<string, unknown>
}
