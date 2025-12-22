import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import ScienceArtifactsPanel from '../../features/visual-extraction/components/color/ScienceArtifactsPanel'

describe('ScienceArtifactsPanel', () => {
  it('renders science images and json summaries', () => {
    const artifacts = {
      images: [
        {
          type: 'oklch-scatter',
          mime: 'image/png',
          base64: 'ZmFrZQ==',
          stage: 'science',
          description: 'OKLCH scatter',
        },
      ],
      json: [
        {
          type: 'delta-e-matrix',
          payload: { matrix: [[0, 1], [1, 0]] },
          stage: 'science',
        },
      ],
    }

    render(<ScienceArtifactsPanel artifacts={artifacts} />)

    expect(screen.getByText('Science artifacts')).toBeInTheDocument()
    expect(screen.getByText('Palette analytics')).toBeInTheDocument()
    expect(screen.getByText('Oklch Scatter')).toBeInTheDocument()
    expect(screen.getByText('Delta E Matrix')).toBeInTheDocument()
  })

  it('renders nothing without artifacts', () => {
    const { container } = render(<ScienceArtifactsPanel artifacts={null} />)
    expect(container).toBeEmptyDOMElement()
  })
})
