import React, { createContext, useContext, useMemo, useCallback } from 'react'

type TabsContextValue = {
  value: string
  onChange: (value: string) => void
}

const TabsContext = createContext<TabsContextValue | null>(null)

type CommonProps = {
  className?: string
  children: React.ReactNode
}

export function Tabs({ value, onValueChange, className, children }: { value: string; onValueChange: (value: string) => void } & CommonProps) {
  const handleChange = useCallback(
    (next: string) => {
      if (next !== value) {
        onValueChange(next)
      }
    },
    [onValueChange, value],
  )

  const contextValue = useMemo<TabsContextValue>(() => ({ value, onChange: handleChange }), [value, handleChange])

  return (
    <TabsContext.Provider value={contextValue}>
      <div className={className}>{children}</div>
    </TabsContext.Provider>
  )
}

function useTabsContext() {
  const ctx = useContext(TabsContext)
  if (!ctx) {
    throw new Error('Tab components must be used within <Tabs>')
  }
  return ctx
}

export function TabList({ className, children }: CommonProps) {
  return <div className={className}>{children}</div>
}

export function TabTrigger({
  value,
  children,
  className,
  activeClassName = 'active',
  'aria-label': ariaLabel,
}: CommonProps & { value: string; activeClassName?: string; 'aria-label'?: string }) {
  const { value: activeValue, onChange } = useTabsContext()
  const isActive = activeValue === value
  const classes = [className, isActive ? activeClassName : ''].filter(Boolean).join(' ').trim()

  return (
    <button
      type="button"
      className={classes || undefined}
      aria-label={ariaLabel}
      aria-pressed={isActive}
      data-active={isActive}
      onClick={() => onChange(value)}
    >
      {children}
    </button>
  )
}

export function TabPanels({ className, children }: CommonProps) {
  return <div className={className}>{children}</div>
}

export function TabPanel({ value, className, children }: CommonProps & { value: string }) {
  const { value: activeValue } = useTabsContext()
  if (activeValue !== value) return null
  return <div className={className}>{children}</div>
}
