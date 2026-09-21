import React, { useMemo } from 'react'
import './PipelineStageIndicator.css'

export interface PipelineStage {
  id?: string
  phase: number
  name: string
  status: 'pending' | 'active' | 'complete' | 'failed'
  description?: string
  duration?: number
  /** 0–100 when a stage reports incremental progress */
  progress?: number
}

interface PipelineStageIndicatorProps {
  stages: PipelineStage[]
  compact?: boolean
  showTimings?: boolean
  /** Overall stream progress (0–100), used for the active stage when stage.progress is unset */
  streamProgress?: number
  title?: string
}

function stagePercent(
  stage: PipelineStage,
  streamProgress: number | undefined,
): number {
  if (stage.status === 'complete') return 100
  if (stage.status === 'failed') return 100
  if (stage.status === 'pending') return 0
  if (typeof stage.progress === 'number') {
    return Math.max(0, Math.min(100, Math.round(stage.progress)))
  }
  if (typeof streamProgress === 'number' && streamProgress > 0) {
    return Math.max(0, Math.min(99, Math.round(streamProgress)))
  }
  return 12
}

export const PipelineStageIndicator: React.FC<PipelineStageIndicatorProps> = ({
  stages,
  compact = false,
  showTimings = true,
  streamProgress,
  title = 'Extraction progress',
}) => {
  const overallPct = useMemo(() => {
    if (!stages.length) return 0
    const sum = stages.reduce((acc, stage) => acc + stagePercent(stage, streamProgress), 0)
    return Math.round(sum / stages.length)
  }, [stages, streamProgress])

  const iconFor = (status: PipelineStage['status']) => {
    if (status === 'complete') return '✓'
    if (status === 'failed') return '✕'
    if (status === 'active') return '●'
    return ''
  }

  if (compact) {
    return (
      <div
        className="pipeline-stage-indicator pipeline-stage-indicator--compact"
        role="status"
        aria-live="polite"
      >
        <div className="pipeline-stage-indicator__header">
          <p className="pipeline-stage-indicator__title">{title}</p>
          <span className="pipeline-stage-indicator__overall">{overallPct}%</span>
        </div>
        <div className="pipeline-stage-indicator__overall-bar" aria-hidden>
          <div
            className="pipeline-stage-indicator__overall-fill"
            style={{ width: `${overallPct}%` }}
          />
        </div>
        <ul className="pipeline-stage-list">
          {stages.map((stage) => (
            <li
              key={stage.id ?? stage.phase}
              className="pipeline-stage-row"
              data-status={stage.status}
              data-stage-phase={stage.phase}
              data-stage-status={stage.status}
              data-stage-name={stage.name}
              data-stage-id={stage.id ?? undefined}
            >
              <span className="pipeline-stage-row__icon" aria-hidden>
                {iconFor(stage.status)}
              </span>
              <span className="pipeline-stage-row__name">{stage.name}</span>
            </li>
          ))}
        </ul>
      </div>
    )
  }

  return (
    <div className="pipeline-stage-indicator" role="status" aria-live="polite">
      <div className="pipeline-stage-indicator__header">
        <p className="pipeline-stage-indicator__title">{title}</p>
        <span className="pipeline-stage-indicator__overall">{overallPct}%</span>
      </div>
      <div
        className="pipeline-stage-indicator__overall-bar"
        role="progressbar"
        aria-valuenow={overallPct}
        aria-valuemin={0}
        aria-valuemax={100}
        aria-label="Overall extraction progress"
      >
        <div
          className="pipeline-stage-indicator__overall-fill"
          style={{ width: `${overallPct}%` }}
        />
      </div>

      <ul className="pipeline-stage-list">
        {stages.map((stage) => {
          const pct = stagePercent(stage, streamProgress)
          return (
            <li
              key={stage.id ?? stage.phase}
              className="pipeline-stage-row"
              data-status={stage.status}
              data-stage-phase={stage.phase}
              data-stage-status={stage.status}
              data-stage-name={stage.name}
              data-stage-id={stage.id ?? undefined}
            >
              <span className="pipeline-stage-row__icon" aria-hidden>
                {iconFor(stage.status)}
              </span>
              <div className="pipeline-stage-row__copy">
                <p className="pipeline-stage-row__name">
                  Phase {stage.phase}: {stage.name}
                </p>
                {stage.description ? (
                  <p className="pipeline-stage-row__desc">{stage.description}</p>
                ) : null}
              </div>
              <span className="pipeline-stage-row__pct">
                {stage.status === 'failed'
                  ? 'Failed'
                  : showTimings && stage.duration
                    ? `${stage.duration.toFixed(1)}s`
                    : `${pct}%`}
              </span>
              <div className="pipeline-stage-row__bar" aria-hidden>
                <div
                  className="pipeline-stage-row__fill"
                  style={{ width: `${pct}%` }}
                />
              </div>
            </li>
          )
        })}
      </ul>
    </div>
  )
}

export default PipelineStageIndicator
