/**
 * Pipeline stage types and constants for multi-modal token extraction
 */

export type StageName =
  | 'colors'
  | 'spacing'
  | 'typography'
  | 'shadows'
  | 'analysis'
  | 'save'

export type StageStatus = 'pending' | 'running' | 'complete' | 'error'

export interface PipelineStage {
  id: StageName
  label: string
  description?: string
  status: StageStatus
  progress?: number // 0-100 for stages that support incremental progress
  startTime?: number
  endTime?: number
}

export interface ExtractorStatus {
  colors: StageStatus
  spacing: StageStatus
  typography: StageStatus
  shadows: StageStatus
}

/**
 * Default pipeline stage definitions
 */
export const DEFAULT_STAGES: Record<StageName, Omit<PipelineStage, 'status'>> = {
  colors: {
    id: 'colors',
    label: 'Color Extraction',
    description: 'Extracting colors from image',
  },
  spacing: {
    id: 'spacing',
    label: 'Spacing Analysis',
    description: 'Analyzing spacing and layout',
  },
  typography: {
    id: 'typography',
    label: 'Typography Detection',
    description: 'Detecting typography information',
  },
  shadows: {
    id: 'shadows',
    label: 'Shadow Detection',
    description: 'Detecting shadows and depth',
  },
  analysis: {
    id: 'analysis',
    label: 'Token Analysis',
    description: 'Analyzing extracted tokens',
  },
  save: {
    id: 'save',
    label: 'Saving Results',
    description: 'Saving to database',
  },
}

/**
 * Initial state for all pipeline stages
 */
export const createInitialStages = (): PipelineStage[] => {
  return Object.entries(DEFAULT_STAGES).map(([, stage]) => ({
    ...stage,
    status: 'pending' as const,
  }))
}

/**
 * Helper to update a stage in the stages array
 */
export const updateStage = (
  stages: PipelineStage[],
  stageName: StageName,
  updates: Partial<PipelineStage>
): PipelineStage[] => {
  return stages.map((stage) =>
    stage.id === stageName ? { ...stage, ...updates } : stage
  )
}
