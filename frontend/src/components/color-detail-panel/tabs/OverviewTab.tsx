import type { ColorToken } from '../../types'
import { formatSemanticValue } from '../../utils/semanticNames'
import type { TabProps } from '../types'

export function OverviewTab({ color }: TabProps) {
  return (
    <div className="overview-content">
      <section className="overview-section">
        <h3>Color Identity</h3>
        <div className="info-grid">
          {color.design_intent != null && color.design_intent !== '' && (
            <div className="info-item">
              <label>Design Intent</label>
              <span>{color.design_intent}</span>
            </div>
          )}
          {color.category != null && color.category !== '' && (
            <div className="info-item">
              <label>Category</label>
              <span>{color.category}</span>
            </div>
          )}
          {color.temperature != null && color.temperature !== '' && (
            <div className="info-item">
              <label>Temperature</label>
              <span className="temp-badge" data-temp={color.temperature}>
                {color.temperature}
              </span>
            </div>
          )}
          {color.is_neutral === true && (
            <div className="info-item">
              <label>Neutral</label>
              <span>✓ Yes</span>
            </div>
          )}
        </div>
      </section>

      {(() => {
        const entries =
          typeof color.semantic_names === 'string'
            ? [['label', color.semantic_names] as const]
            : color.semantic_names
              ? Object.entries(color.semantic_names)
              : []

        return entries.length > 0 ? (
          <section className="overview-section">
            <h3>Semantic Names</h3>
            <div className="semantic-grid">
              {(entries as any).map(([key, value]: [string, any]) => {
                const formatted = formatSemanticValue(value)
                return (
                  <div key={key} className="semantic-item">
                    <span className="semantic-key">{key}</span>
                    <span className="semantic-value">{formatted}</span>
                  </div>
                )
              })}
            </div>
          </section>
        ) : null
      })()}

      {color.prominence_percentage != null && (
        <section className="overview-section">
          <h3>Prominence</h3>
          <div className="prominence-bar">
            <div
              className="prominence-fill"
              style={{ width: `${color.prominence_percentage}%` }}
            />
          </div>
          <span className="prominence-value">
            {color.prominence_percentage?.toFixed(1)}% of image
          </span>
        </section>
      )}
      {color.extraction_metadata && (
        <section className="overview-section">
          <h3>Source & Model</h3>
          <div className="info-grid">
            {color.extraction_metadata.model && (
              <div className="info-item">
                <label>Model</label>
                <span>{String(color.extraction_metadata.model)}</span>
              </div>
            )}
            {color.extraction_metadata.extractor && (
              <div className="info-item">
                <label>Extractor</label>
                <span>{String(color.extraction_metadata.extractor)}</span>
              </div>
            )}
            {color.extraction_metadata.source && (
              <div className="info-item">
                <label>Source</label>
                <span>{String(color.extraction_metadata.source)}</span>
              </div>
            )}
            {color.histogram_significance != null && (
              <div className="info-item">
                <label>Histogram Significance</label>
                <span>{(color.histogram_significance * 100).toFixed(2)}%</span>
              </div>
            )}
          </div>
        </section>
      )}
    </div>
  )
}
