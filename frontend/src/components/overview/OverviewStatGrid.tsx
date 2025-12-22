import type { ReactNode } from 'react'
import './OverviewLayout.css'

export interface OverviewStat {
  label: string
  value: ReactNode
  hint?: string
}

interface OverviewStatGridProps {
  stats: OverviewStat[]
  className?: string
}

export function OverviewStatGrid({ stats, className }: OverviewStatGridProps) {
  const classes = ['overview-stat-grid', className].filter(Boolean).join(' ')

  return (
    <div className={classes}>
      {stats.map((stat) => (
        <div className="overview-stat" key={stat.label}>
          <span className="overview-stat__label">{stat.label}</span>
          <span className="overview-stat__value">{stat.value}</span>
          {stat.hint && <span className="overview-stat__hint">{stat.hint}</span>}
        </div>
      ))}
    </div>
  )
}
