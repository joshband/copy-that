import { describe, it, expect } from 'vitest'
import { extractionPhase } from './state'
describe('extraction outcomes', () => {
  it('keeps failed families partial after hydration', () => {
    expect(extractionPhase(false, true, true, false, ['complete', 'error'])).toBe('partial')
  })
  it('does not call a graph load failure ready', () => {
    expect(extractionPhase(false, true, false, true, ['complete'])).toBe('failed')
  })
  it('treats successful empty results as ready', () => {
    expect(extractionPhase(false, true, true, false, ['complete'])).toBe('ready')
  })
  it('waits for graph hydration after stages settle', () => {
    expect(extractionPhase(false, true, false, false, ['complete'])).toBe('hydrating')
  })
})
