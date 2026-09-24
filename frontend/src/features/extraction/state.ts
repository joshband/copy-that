import { create } from 'zustand'
export type ExtractionPhase = 'idle' | 'running' | 'hydrating' | 'ready' | 'partial' | 'failed'
export type FamilyOutcome = 'pending' | 'running' | 'successful' | 'empty' | 'failed'
export function extractionPhase(running: boolean, terminal: boolean, loaded: boolean, loadError: boolean, outcomes: string[]): ExtractionPhase {
  if (running) return 'running'
  if (loadError) return 'failed'
  if (!terminal) return outcomes.includes('error') ? 'failed' : 'idle'
  if (!loaded) return 'hydrating'
  return outcomes.includes('error') ? 'partial' : 'ready'
}
export const useExtractionState = create<{
  phase: ExtractionPhase
  sourceId: string
  families: Record<string, FamilyOutcome>
}>(() => ({ phase: 'idle', sourceId: '', families: {} }))
export const phaseLabel: Record<ExtractionPhase, string> = {
  idle: 'Choose a source', running: 'Extracting tokens', hydrating: 'Loading results',
  ready: 'Ready', partial: 'Partial results', failed: 'Results need attention',
}
