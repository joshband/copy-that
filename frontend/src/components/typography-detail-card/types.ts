export interface TypographyTokenDetail {
  id: string
  fontFamily?: string
  fontSize?: string
  fontWeight?: number | string
  lineHeight?: number | string
  letterSpacing?: string
  textTransform?: string
  category?: string
  semanticRole?: string
  confidence?: number
  readabilityScore?: number
  isReadable?: boolean
  prominence?: number
  colorTemp?: string
  visualWeight?: string
  contrastLevel?: string
  primaryStyle?: string
  vlmMood?: string
  vlmComplexity?: string
  usage?: string[]
  extractionMetadata?: Record<string, any>
  raw?: any
}
