interface DesignInsightCardProps {
  icon: string
  label: string
  title: string
  description: string
  elaborations: string[]
  confidence?: number
  source?: string
}

export function DesignInsightCard({
  icon,
  label,
  title,
  description,
  elaborations,
  confidence,
  source,
}: DesignInsightCardProps) {
  return (
    <div
      style={{
        border: '1px solid #e5e7eb',
        borderRadius: '8px',
        padding: '24px',
        backgroundColor: '#f9fafb',
        display: 'flex',
        flexDirection: 'column',
        height: '100%',
      }}
    >
      {/* Card Header - Label */}
      <h4
        style={{
          fontSize: '14px',
          fontWeight: 'bold',
          color: '#111827',
          marginBottom: '12px',
        }}
      >
        {label}
      </h4>

      {/* Title */}
      <h3
        style={{
          fontSize: '18px',
          fontWeight: 'bold',
          color: '#111827',
          marginBottom: '16px',
          paddingBottom: '16px',
          borderBottom: '1px solid #e5e7eb',
        }}
      >
        {title}
      </h3>

      {/* Description - Primary elaboration */}
      {description && (
        <p
          style={{
            fontSize: '14px',
            color: '#374151',
            lineHeight: '1.5',
            marginBottom: '12px',
            marginTop: '8px',
          }}
        >
          {description}
        </p>
      )}

      {/* Additional elaborations */}
      {elaborations.length > 0 && (
        <div style={{ marginBottom: '16px' }}>
          {elaborations.map((elaboration, idx) => (
            <div
              key={idx}
              style={{
                fontSize: '14px',
                color: '#374151',
                lineHeight: '1.5',
                marginBottom: '4px',
              }}
            >
              • {elaboration}
            </div>
          ))}
        </div>
      )}

      {/* Uncertainty message for low-confidence items */}
      {confidence !== undefined && confidence < 60 && (
        <p
          style={{
            fontSize: '12px',
            color: '#4b5563',
            marginBottom: '16px',
            fontStyle: 'italic',
          }}
        >
          Multiple interpretations possible
        </p>
      )}

      {/* Source Badge - Bottom centered, distinctive chip inside card */}
      <div
        style={{
          display: 'flex',
          justifyContent: 'center',
          paddingTop: '16px',
          borderTop: '1px solid #e5e7eb',
          marginTop: 'auto',
        }}
      >
        {source && (
          <span
            style={{
              display: 'inline-block',
              padding: '4px 12px',
              backgroundColor: '#dbeafe',
              color: '#1e40af',
              fontSize: '12px',
              fontWeight: '500',
              borderRadius: '4px',
            }}
            title={`Inferred from ${source} data`}
            data-source={source}
          >
            {source}
          </span>
        )}
      </div>
    </div>
  )
}
