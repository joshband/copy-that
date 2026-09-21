import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, cleanup } from '@testing-library/react'
import type { ColorToken } from '../../../types'
import { OverviewNarrative } from '../OverviewNarrative'

const sampleColors: ColorToken[] = [
  {
    hex: '#3366FF',
    rgb: 'rgb(51, 102, 255)',
    name: 'Blue',
    confidence: 0.8,
  },
]

const { mockFeatureFlags } = vi.hoisted(() => ({
  mockFeatureFlags: {
    showMoodBoard: false,
    showLightingTab: false,
    showLightingAnalyzer: false,
    showRelationsTab: false,
    showRawTab: false,
    showTokenGraphDemo: false,
  },
}))

vi.mock('../../../config/featureFlags', () => ({
  featureFlags: mockFeatureFlags,
}))

describe('OverviewNarrative mood board gate', () => {
  afterEach(() => {
    cleanup()
  })

  beforeEach(() => {
    mockFeatureFlags.showMoodBoard = false
  })

  it('does not mount MoodBoard when showMoodBoard is false', () => {
    mockFeatureFlags.showMoodBoard = false
    render(
      <OverviewNarrative
        colors={sampleColors}
        colorCount={1}
        aliasCount={0}
        spacingCount={0}
        multiplesCount={0}
        typographyCount={0}
      />
    )

    expect(screen.queryByTestId('mood-board-section')).not.toBeInTheDocument()
    expect(screen.getByTestId('overview-narrative')).toBeInTheDocument()
  })

  it('mounts MoodBoard when showMoodBoard is true', () => {
    mockFeatureFlags.showMoodBoard = true
    render(
      <OverviewNarrative
        colors={sampleColors}
        colorCount={1}
        aliasCount={0}
        spacingCount={0}
        multiplesCount={0}
        typographyCount={0}
      />
    )
    expect(screen.getByTestId('mood-board-section')).toBeInTheDocument()
    expect(screen.getByTestId('mood-board-opt-in-button')).toBeInTheDocument()
  })
})
