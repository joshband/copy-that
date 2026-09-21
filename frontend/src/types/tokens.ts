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
  fontStyle?: string
  letterSpacing?: string | { em: number } | { value: number; unit: string }
  casing?: string
  textAlign?: string
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

export interface W3COpacityToken extends W3CBaseToken {
  $type: 'number' | string
  $value: number
}

export interface W3CGradientToken extends W3CBaseToken {
  $type: 'gradient' | string
  $value: {
    type?: string
    angle?: number
    stops?: Array<{ position?: number; color?: string }>
  }
}

export interface W3CDurationToken extends W3CBaseToken {
  $type: 'duration' | string
  $value: { value: number; unit: string } | number | string
}

export interface W3CCubicBezierToken extends W3CBaseToken {
  $type: 'cubicBezier' | string
  $value: number[]
}

export interface W3CFontFamilyToken extends W3CBaseToken {
  $type: 'fontFamily' | string
  $value: string | string[]
}

export interface W3CFontWeightToken extends W3CBaseToken {
  $type: 'fontWeight' | string
  $value: number | string
}

export interface W3CStrokeStyleToken extends W3CBaseToken {
  $type: 'strokeStyle' | string
  $value: string | Record<string, unknown>
}

export interface W3CBorderToken extends W3CBaseToken {
  $type: 'border' | string
  $value: {
    color?: string
    width?: W3CDimensionValue | number
    style?: string
  }
}

export interface W3CTransitionToken extends W3CBaseToken {
  $type: 'transition' | string
  $value: {
    duration?: unknown
    delay?: unknown
    timingFunction?: unknown
  }
}

export interface W3CNumberToken extends W3CBaseToken {
  $type: 'number' | string
  $value: number
}

export interface W3CDimensionToken extends W3CBaseToken {
  $type: 'dimension' | string
  $value: W3CDimensionValue | number
}

export interface W3CDesignTokenResponse {
  color?: Record<TokenId, W3CColorToken>
  spacing?: Record<TokenId, W3CSpacingToken>
  shadow?: Record<TokenId, W3CShadowToken>
  typography?: Record<TokenId, WCTypographyToken>
  layout?: Record<TokenId, W3CLayoutToken>
  opacity?: Record<TokenId, W3COpacityToken>
  gradient?: Record<TokenId, W3CGradientToken>
  duration?: Record<TokenId, W3CDurationToken>
  cubicBezier?: Record<TokenId, W3CCubicBezierToken>
  fontFamily?: Record<TokenId, W3CFontFamilyToken>
  fontWeight?: Record<TokenId, W3CFontWeightToken>
  strokeStyle?: Record<TokenId, W3CStrokeStyleToken>
  border?: Record<TokenId, W3CBorderToken>
  transition?: Record<TokenId, W3CTransitionToken>
  number?: Record<TokenId, W3CNumberToken>
  dimension?: Record<TokenId, W3CDimensionToken>
  meta?: {
    typography_recommendation?: {
      style_attributes?: Record<string, string | number>
      confidence?: number | null
    }
  }
  [key: string]: unknown
}
