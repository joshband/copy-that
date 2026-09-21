import type { ReactNode } from 'react'
import './OverviewLayout.css'

interface OverviewCardProps {
  title?: string
  subtitle?: string
  actions?: ReactNode
  children: ReactNode
  className?: string
}

export function OverviewCard({ title, subtitle, actions, children, className }: OverviewCardProps) {
  const classes = ['overview-card', className].filter(Boolean).join(' ')
  const hasHeader = Boolean(title || subtitle || actions)

  return (
    <div className={classes}>
      {hasHeader && (
        <div className="overview-card__header">
          <div className="overview-card__heading">
            {title && <h3 className="overview-card__title">{title}</h3>}
            {subtitle && <p className="overview-card__subtitle">{subtitle}</p>}
          </div>
          {actions && <div className="overview-card__actions">{actions}</div>}
        </div>
      )}
      <div className="overview-card__body">{children}</div>
    </div>
  )
}
