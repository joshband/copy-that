import { useState, useCallback, useMemo } from 'react'
import type { ActiveTab } from './types'

const hexToRgb = (hex: string) => {
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex)
  if (!result) return { r: 255, g: 255, b: 255 }
  return {
    r: parseInt(result[1], 16),
    g: parseInt(result[2], 16),
    b: parseInt(result[3], 16),
  }
}

const getLuminance = (rgb: { r: number; g: number; b: number }) => {
  const [r, g, b] = [rgb.r / 255, rgb.g / 255, rgb.b / 255].map((val) =>
    val <= 0.03928 ? val / 12.92 : Math.pow((val + 0.055) / 1.055, 2.4)
  )
  return 0.2126 * r + 0.7152 * g + 0.0722 * b
}

export const useActiveTab = (initialTab: ActiveTab = 'harmony') => {
  const [activeTab, setActiveTab] = useState<ActiveTab>(initialTab)

  const switchTab = useCallback((tab: ActiveTab) => {
    setActiveTab(tab)
  }, [])

  return { activeTab, switchTab }
}

export const useCustomBackground = (initialColor: string = '#ffffff') => {
  const [customBgColor, setCustomBgColor] = useState(initialColor)

  const updateBackground = useCallback((color: string) => {
    setCustomBgColor(color)
  }, [])

  return { customBgColor, updateBackground }
}

export const useContrastRatio = (foregroundColor: string, backgroundColor: string) => {
  return useMemo(() => {
    const getContrastRatio = (color1: string, color2: string) => {
      const l1 = getLuminance(hexToRgb(color1))
      const l2 = getLuminance(hexToRgb(color2))
      const lighter = Math.max(l1, l2)
      const darker = Math.min(l1, l2)
      return (lighter + 0.05) / (darker + 0.05)
    }

    const ratio = getContrastRatio(foregroundColor, backgroundColor)
    return {
      ratio,
      isAACompliant: ratio >= 4.5,
      isAAACompliant: ratio >= 7,
    }
  }, [foregroundColor, backgroundColor])
}
