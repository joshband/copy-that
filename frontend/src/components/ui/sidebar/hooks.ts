import { useState } from 'react'

export const useSidebarState = () => ({
  isOpen: false,
  onToggle: () => {},
})

export const useActiveTab = (initial: string) => {
  const [activeTab, setActiveTab] = useState(initial)
  return {
    activeTab,
    switchTab: (tab: string) => setActiveTab(tab),
  }
}

export const useCustomBackground = (initial: string) => {
  const [customBgColor, setBg] = useState(initial)
  return {
    customBgColor,
    updateBackground: (val: string) => setBg(val),
  }
}
