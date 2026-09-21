import { useState, useCallback } from 'react'
import type { SectionType } from './types'

export const useSectionExpansion = (initialSection: SectionType = 'pipeline') => {
  const [expandedSection, setExpandedSection] = useState<SectionType | null>(initialSection)

  const toggleSection = useCallback((section: SectionType) => {
    setExpandedSection((prev) => (prev === section ? null : section))
  }, [])

  return { expandedSection, toggleSection }
}
