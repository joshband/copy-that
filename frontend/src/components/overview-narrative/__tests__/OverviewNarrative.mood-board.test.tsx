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

describe('OverviewNarrative without mood board', () => {
  afterEach(() => {
    cleanup()
  })

  it('renders palette narrative without Labs or MoodBoard', () => {
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

    expect(screen.queryByTestId('overview-labs')).not.toBeInTheDocument()
    expect(screen.queryByTestId('mood-board-section')).not.toBeInTheDocument()
    expect(screen.getByTestId('overview-narrative')).toBeInTheDocument()
  })
})
