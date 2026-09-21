/**
 * Tests for TokenSourceChip (synth vs extracted origin labels).
 */

import { describe, it, expect } from 'vitest'
import { render, within } from '@testing-library/react'
import { resolveTokenSource, TokenSourceChip } from '../TokenSourceChip'

describe('resolveTokenSource', () => {
  it('defaults to extracted when source is missing', () => {
    expect(resolveTokenSource({})).toBe('extracted')
    expect(resolveTokenSource(null)).toBe('extracted')
  })

  it('reads top-level and nested attributes.source', () => {
    expect(resolveTokenSource({ source: 'preset' })).toBe('preset')
    expect(resolveTokenSource({ attributes: { source: 'derived' } })).toBe('derived')
    expect(resolveTokenSource({ source: 'color-pair' })).toBe('color-pair')
    expect(resolveTokenSource({ source: 'synth' })).toBe('synth')
  })

  it('maps cv_fallback and measured:false to fallback', () => {
    expect(resolveTokenSource({ source: 'cv_fallback' })).toBe('fallback')
    expect(
      resolveTokenSource({ extraction_metadata: { source: 'cv_fallback', measured: false } }),
    ).toBe('fallback')
    expect(resolveTokenSource({ extraction_metadata: { measured: false } })).toBe('fallback')
  })
})

describe('TokenSourceChip', () => {
  it('renders Extracted for missing source', () => {
    const { container } = render(<TokenSourceChip raw={{ $type: 'duration', $value: 200 }} />)
    const chip = within(container).getByTestId('token-source-chip')
    expect(chip).toHaveAttribute('data-source', 'extracted')
    expect(chip).toHaveTextContent('Extracted')
  })

  it('renders Synth for source=synth', () => {
    const { container } = render(<TokenSourceChip raw={{ source: 'synth' }} />)
    expect(within(container).getByTestId('token-source-chip')).toHaveTextContent('Synth')
  })

  it('renders Fallback for cv_fallback', () => {
    const { container } = render(<TokenSourceChip raw={{ source: 'cv_fallback' }} />)
    expect(within(container).getByTestId('token-source-chip')).toHaveTextContent('Fallback')
  })
})
