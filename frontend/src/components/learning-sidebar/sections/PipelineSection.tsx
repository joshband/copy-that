interface Props {
  isExpanded: boolean
}

export function PipelineSection({ isExpanded }: Props) {
  if (!isExpanded) return null

  return (
    <div className="section-content">
      <div className="pipeline">
        <div className="pipeline-step">
          <div className="step-icon">🖼️</div>
          <div className="step-label">Image</div>
        </div>
        <div className="pipeline-arrow">→</div>
        <div className="pipeline-step">
          <div className="step-icon">🤖</div>
          <div className="step-label">AI Vision</div>
        </div>
        <div className="pipeline-arrow">→</div>
        <div className="pipeline-step">
          <div className="step-icon">🎨</div>
          <div className="step-label">Extract</div>
        </div>
      </div>
      <div className="pipeline">
        <div className="pipeline-step">
          <div className="step-icon">🔍</div>
          <div className="step-label">Analyze</div>
        </div>
        <div className="pipeline-arrow">→</div>
        <div className="pipeline-step">
          <div className="step-icon">💾</div>
          <div className="step-label">Store</div>
        </div>
        <div className="pipeline-arrow">→</div>
        <div className="pipeline-step">
          <div className="step-icon">📊</div>
          <div className="step-label">Display</div>
        </div>
      </div>
      <p className="pipeline-description">
        Colors are extracted using AI vision analysis, then enriched with color science calculations
        (harmony, accessibility, semantic naming).
      </p>
    </div>
  )
}
