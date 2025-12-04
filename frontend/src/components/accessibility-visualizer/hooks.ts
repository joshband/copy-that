import { useState } from 'react'
import { calculateContrast } from './utils'
import type { TabType } from './types'

export function useTabState() {
  const [activeTab, setActiveTab] = useState<TabType>('white')
  return { activeTab, setActiveTab }
}

export function useCustomBackground() {
  const [customBackground, setCustomBackground] = useState('#ffffff')
  return { customBackground, setCustomBackground }
}

export function useContrastCalculations(
  hex: string,
  wcagContrastWhite?: number,
  wcagContrastBlack?: number
) {
  const { customBackground } = useCustomBackground()
  const customContrast = calculateContrast(hex, customBackground)

  return {
    whiteContrast: wcagContrastWhite,
    blackContrast: wcagContrastBlack,
    customContrast,
  }
}
