/**
 * Tests for flag-gated lighting geometry evidence UI (P4 G1).
 */

import { describe, it, expect } from 'vitest'
import { render, within } from '@testing-library/react'
import { LightingGeometryEvidence } from '../LightingGeometryEvidence'

describe('LightingGeometryEvidence', () => {
  it('renders nothing when geometry fields are absent', () => {
    const { container } = render(<LightingGeometryEvidence />)
    expect(container).toBeEmptyDOMElement()
  })

  it('shows real-geometry status, meta, and depth/normals thumbnails', () => {
    const { container } = render(
      <LightingGeometryEvidence
        geometryUsed={true}
        geometryMeta={{
          profile_resolved: 'cpu_fast',
          device: 'cpu',
          depth_model: 'depth-anything/Depth-Anything-V2-Small-hf',
          normals_source: 'depth_gradient',
        }}
        geometryImages={{
          depth_png: 'AAAA',
          normals_png: 'BBBB',
        }}
      />,
    )

    const root = within(container)
    expect(root.getByTestId('lighting-geometry-evidence')).toHaveAttribute(
      'data-geometry-used',
      'true',
    )
    expect(root.getByTestId('geometry-used-status')).toHaveTextContent(
      'Real geometry extract applied',
    )
    expect(root.getByTestId('geometry-meta')).toHaveTextContent('cpu_fast')
    expect(root.getByTestId('geometry-meta')).toHaveTextContent('depth_gradient')

    const depth = root.getByTestId('geometry-depth-preview')
    const normals = root.getByTestId('geometry-normals-preview')
    expect(depth).toHaveAttribute('src', 'data:image/png;base64,AAAA')
    expect(normals).toHaveAttribute('src', 'data:image/png;base64,BBBB')
  })

  it('shows not-applied status when geometry_used is false', () => {
    const { container } = render(
      <LightingGeometryEvidence
        geometryUsed={false}
        geometryMeta={{ error: 'missing deps' }}
      />,
    )
    expect(within(container).getByTestId('geometry-used-status')).toHaveTextContent(
      'Geometry not applied',
    )
  })

  it('surfaces MPS / profile warnings from geometry_meta', () => {
    const { container } = render(
      <LightingGeometryEvidence
        geometryUsed={true}
        geometryMeta={{
          profile_resolved: 'gpu_full',
          device: 'mps',
          normals_source: 'depth_gradient',
          warnings: ['gpu_non_cuda_depth_only', 'marigold_requires_cuda_depth_gradient'],
        }}
      />,
    )

    const warnings = within(container).getByTestId('geometry-warnings')
    expect(warnings).toHaveTextContent('gpu_non_cuda_depth_only')
    expect(warnings).toHaveTextContent('marigold_requires_cuda_depth_gradient')
  })
})
