export type TabType = 'white' | 'black' | 'custom'

export interface ColorRGB {
  r: number
  g: number
  b: number
}

export interface AccessibilityVisualizerProps {
  hex: string
  wcagContrastWhite?: number
  wcagContrastBlack?: number
  wcagAACompliantText?: boolean
  wcagAAACompliantText?: boolean
  wcagAACompliantNormal?: boolean
  wcagAAACompliantNormal?: boolean
  colorblindSafe?: boolean
}

export interface ContrastPanelProps {
  hex: string
  backgroundColor: string
  contrast: number
  wcagLevels: {
    aaText: boolean
    aaaText: boolean
    aaNormal: boolean
    aaaNormal: boolean
  }
  title: string
}
