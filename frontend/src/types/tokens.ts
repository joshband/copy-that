export type TokenId = string

// Base W3C design token shape
export interface W3CBaseToken {
  $type: string
  $value: unknown
  [key: string]: unknown
}

// Color tokens (supports OKLCH dict or hex strings)
export interface W3CColorValue {
  l?: number
  c?: number
  h?: number
  alpha?: number
  space?: string
  hex?: string
}

export interface W3CColorToken extends W3CBaseToken {
  $type: 'color'
  $value: W3CColorValue | string
}

// Dimension tokens (spacing/layout)
export interface W3CDimensionValue {
  value: number
  unit: string
}

export interface W3CSpacingToken extends W3CBaseToken {
  $type: 'dimension'
  $value: W3CDimensionValue
}

// Shadow composites
export interface W3CShadowLayer {
  x: W3CDimensionValue | number
  y: W3CDimensionValue | number
  blur: W3CDimensionValue | number
  spread: W3CDimensionValue | number
  color: string
  inset?: boolean
  [key: string]: unknown
}

export interface W3CShadowToken extends W3CBaseToken {
  $type: 'shadow'
  $value: W3CShadowLayer[] | W3CShadowLayer
}

// Typography composites
export interface W3CTypographyValue {
  fontFamily?: string | string[]
  fontSize?: string | W3CDimensionValue | { token: string }
  fontSizeToken?: string
  lineHeight?: string | W3CDimensionValue
  fontWeight?: string | number
  letterSpacing?: string | { em: number } | { value: number; unit: string }
  casing?: string
  color?: string
  [key: string]: unknown
}

export interface WCTypographyToken extends W3CBaseToken {
  $type: 'typography'
  $value: W3CTypographyValue
}

// Layout tokens (grid/gutter/etc.)
export interface W3CLayoutToken extends W3CBaseToken {
  $type: string
}

export interface W3CDesignTokenResponse {
  color?: Record<TokenId, W3CColorToken>
  spacing?: Record<TokenId, W3CSpacingToken>
  shadow?: Record<TokenId, W3CShadowToken>
  typography?: Record<TokenId, WCTypographyToken>
  layout?: Record<TokenId, W3CLayoutToken>
  meta?: {
    typography_recommendation?: {
      style_attributes?: Record<string, unknown>
      confidence?: number
    }
  }
  [key: string]: unknown
}
