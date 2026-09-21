/**
 * P4 production flag policy: lighting/mood stay default-off after G1–G4.
 * See docs/planning/P4_GEOMETRY_GATES.md § Production flag policy.
 */

import { describe, it, expect } from 'vitest'
import { featureFlags, visibleAppTabs } from '../featureFlags'

describe('P4 geometry / lighting flag policy', () => {
  it('keeps lighting and mood board defaults false', () => {
    expect(featureFlags.showLightingTab).toBe(false)
    expect(featureFlags.showLightingAnalyzer).toBe(false)
    expect(featureFlags.showMoodBoard).toBe(false)
  })

  it('does not put lighting on the default App nav', () => {
    expect(visibleAppTabs()).not.toContain('lighting')
    expect(visibleAppTabs()).toEqual([
      'overview',
      'colors',
      'spacing',
      'typography',
      'shadows',
      'shape',
      'export',
    ])
  })
})
