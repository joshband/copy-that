/**
 * P4 production flag policy: lighting stays default-off; mood board is a Mood tab.
 * See docs/planning/P4_GEOMETRY_GATES.md § Production flag policy.
 */

import { describe, it, expect } from 'vitest'
import { featureFlags, visibleAppTabs } from '../featureFlags'

describe('P4 geometry / lighting flag policy', () => {
  it('keeps lighting default-off; mood board unparked as Mood tab', () => {
    expect(featureFlags.showLightingTab).toBe(false)
    expect(featureFlags.showLightingAnalyzer).toBe(false)
    expect(featureFlags.showMoodBoard).toBe(true)
  })

  it('puts Mood on the default App nav; not lighting', () => {
    expect(visibleAppTabs()).not.toContain('lighting')
    expect(visibleAppTabs()).toEqual([
      'overview',
      'mood',
      'colors',
      'spacing',
      'typography',
      'shadows',
      'shape',
      'export',
    ])
  })
})
