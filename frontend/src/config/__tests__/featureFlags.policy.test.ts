/**
 * P4 flag policy: lighting and geometry surfaces are on; mood board is a Mood tab.
 * Explicit product choice on 2026-09-24, not an accidental default-on of heavy CV.
 */

import { describe, it, expect } from 'vitest'
import { featureFlags, visibleAppTabs } from '../featureFlags'

describe('P4 geometry / lighting flag policy', () => {
  it('shows lighting and geometry surfaces; mood board stays a Mood tab', () => {
    expect(featureFlags.showLightingTab).toBe(true)
    expect(featureFlags.showLightingAnalyzer).toBe(true)
    expect(featureFlags.showMoodBoard).toBe(true)
  })

  it('puts Mood and Lighting on the default App nav', () => {
    // Mood stays after Shape. Overview's next tab is Colors,
    // which the shell keyboard contract (ArrowRight) relies on.
    // Lighting follows Mood so End still lands on Export.
    expect(visibleAppTabs()).toEqual([
      'overview',
      'colors',
      'spacing',
      'typography',
      'shadows',
      'shape',
      'mood',
      'lighting',
      'export',
    ])
  })
})
