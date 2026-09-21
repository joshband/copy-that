import React from 'react'
import { PipelineStage } from './types'

interface PipelineVisualizationProps {
  stages: PipelineStage[]
}

export function PipelineVisualization({ stages }: PipelineVisualizationProps) {
  return (
    <section className="panel-card pipeline-section">
      <h2>Pipeline Stages</h2>
      <div className="pipeline-stages">
        {stages.map((stage, index) => (
          <div key={stage.id} className={`pipeline-stage ${stage.status}`}>
            <div className="stage-number">{index + 1}</div>
            <div className="stage-info">
              <div className="stage-name">{stage.name}</div>
              <div className="stage-desc">{stage.description}</div>
            </div>
            <div className="stage-status">
              {stage.status === 'pending' && 'Pending'}
              {stage.status === 'running' && <span className="spinner-small" />}
              {stage.status === 'done' && (
                <span className="done-check">{stage.duration ? `${stage.duration.toFixed(0)}ms` : 'Done'}</span>
              )}
              {stage.status === 'error' && 'Error'}
            </div>
          </div>
        ))}
      </div>
    </section>
  )
}
