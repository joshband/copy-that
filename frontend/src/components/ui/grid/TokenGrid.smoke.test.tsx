import { render, screen } from '@testing-library/react'
import React from 'react'
import { vi } from 'vitest'
import TokenGrid from './TokenGrid'

// Mock stores
vi.mock('../../../store/tokenView', () => {
  return {
    useTokenViewState: () => ({
      tokens: [
        { id: '1', name: 'orange-500', semantic_names: 'molten-copper', usage: ['retro'] },
        { id: '2', name: 'blue-700', design_intent: 'calm marine', usage: ['ocean'] },
      ],
      tokenType: 'color',
      filters: {},
      searchTerm: 'molten',
      sortBy: 'name',
      viewMode: 'grid',
    }),
  }
})

// Registry mock
vi.mock('../../../config/tokenTypeRegistry', () => ({
  tokenTypeRegistry: {
    color: { filters: [] },
  },
}))

describe('TokenGrid semantic search', () => {
  it('filters by semantic/meaning fields', () => {
    render(<TokenGrid />)
    expect(screen.getByText(/molten-copper/)).toBeInTheDocument()
    expect(screen.queryByText(/blue-700/)).not.toBeInTheDocument()
  })
})
