import { useEffect, useState } from 'react'
import './App.css'
import AdvancedColorScienceDemo from './components/AdvancedColorScienceDemo'
import SpacingTokenShowcase from './components/SpacingTokenShowcase'

export default function App() {
  // Ensure global scroll isn’t disabled by other styles
  useEffect(() => {
    const originalBodyOverflow = document.body.style.overflowY
    const originalHtmlOverflow = document.documentElement.style.overflowY
    document.body.style.overflowY = 'auto'
    document.documentElement.style.overflowY = 'auto'
    return () => {
      document.body.style.overflowY = originalBodyOverflow
      document.documentElement.style.overflowY = originalHtmlOverflow
    }
  }, [])

  return <AdvancedColorScienceDemo />
}
