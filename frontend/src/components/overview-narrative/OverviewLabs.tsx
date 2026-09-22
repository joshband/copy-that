import { useState, type ReactNode } from 'react'

const LABS_OPEN_KEY = 'copythat::labs-open'

interface OverviewLabsProps {
  children: ReactNode
}

/**
 * Collapsed-by-default Labs disclosure for costly / async Overview features.
 * Mood board lives here so default Overview stays extract → narrative focused.
 */
export function OverviewLabs({ children }: OverviewLabsProps) {
  const [open, setOpen] = useState(() => {
    try {
      return localStorage.getItem(LABS_OPEN_KEY) === '1'
    } catch {
      return false
    }
  })

  const onToggle = (next: boolean) => {
    setOpen(next)
    try {
      localStorage.setItem(LABS_OPEN_KEY, next ? '1' : '0')
    } catch {
      // ignore quota / private mode
    }
  }

  return (
    <details
      className="overview-labs"
      data-testid="overview-labs"
      open={open}
      onToggle={(e) => onToggle((e.target as HTMLDetailsElement).open)}
    >
      <summary className="overview-labs__summary">
        <span className="overview-labs__eyebrow">Labs</span>
        <span className="overview-labs__title">Mood boards &amp; inspiration</span>
        <span className="overview-labs__hint">Optional · Celery · cost-aware</span>
      </summary>
      <div className="overview-labs__body">{children}</div>
    </details>
  )
}
