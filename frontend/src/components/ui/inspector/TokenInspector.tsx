import React, { useMemo, useState } from 'react'
import { Tabs, TabList, TabPanel, TabPanels, TabTrigger } from '../tabs/Tabs'
import './TokenInspector.css'

export type TokenBinding = {
  property: string
  token: string
  intent?: string
  example?: string
}

export type SlotAccessibility = {
  role?: string
  intent?: string
  aria?: Record<string, string>
  notes?: string[]
}

export type AnatomySlot = {
  name: string
  description?: string
  tokens: TokenBinding[]
  accessibility?: SlotAccessibility
}

export type ComponentAccessibility = {
  intent?: string
  notes?: string[]
  aria?: Record<string, string>
  role?: string
}

export type ComponentMeta = {
  component: string
  variant?: string
  description?: string
  accessibility?: ComponentAccessibility
  slots: AnatomySlot[]
}

type Props = {
  componentMeta: ComponentMeta
  className?: string
}

const slugify = (value: string) => value.toLowerCase().replace(/\s+/g, '-')

const EmptyState = () => (
  <div className="token-inspector__empty" data-testid="token-inspector-empty">
    <p>No anatomy slots provided.</p>
    <p className="token-inspector__muted standin">Pass componentMeta.slots to visualize bindings.</p>
  </div>
)

export function TokenInspector({ componentMeta, className }: Props) {
  const { slots } = componentMeta
  const [activeSlot, setActiveSlot] = useState(() => (slots[0] ? slugify(slots[0].name) : ''))

  const header = useMemo(() => {
    const pieces = [componentMeta.component]
    if (componentMeta.variant) pieces.push(`(${componentMeta.variant})`)
    return pieces.join(' ')
  }, [componentMeta.component, componentMeta.variant])

  const containerClass = ['token-inspector', className].filter(Boolean).join(' ').trim()

  if (!slots.length) {
    return (
      <div className={containerClass}>
        <Header componentLabel={header} description={componentMeta.description} accessibility={componentMeta.accessibility} />
        <EmptyState />
      </div>
    )
  }

  return (
    <div className={containerClass} data-testid="token-inspector">
      <Header componentLabel={header} description={componentMeta.description} accessibility={componentMeta.accessibility} />

      <Tabs value={activeSlot} onValueChange={setActiveSlot} className="token-inspector__tabs">
        <TabList className="token-inspector__tab-list">
          {slots.map((slot) => {
            const tabValue = slugify(slot.name)
            return (
              <TabTrigger key={tabValue} value={tabValue} className="token-inspector__tab">
                {slot.name}
              </TabTrigger>
            )
          })}
        </TabList>

        <TabPanels className="token-inspector__panels">
          {slots.map((slot) => {
            const tabValue = slugify(slot.name)
            return (
              <TabPanel key={tabValue} value={tabValue} className="token-inspector__panel">
                <SlotPanel slot={slot} />
              </TabPanel>
            )
          })}
        </TabPanels>
      </Tabs>
    </div>
  )
}

type HeaderProps = {
  componentLabel: string
  description?: string
  accessibility?: ComponentAccessibility
}

function Header({ componentLabel, description, accessibility }: HeaderProps) {
  return (
    <header className="token-inspector__header">
      <div>
        <h3 className="token-inspector__title">{componentLabel}</h3>
        {description && <p className="token-inspector__description">{description}</p>}
      </div>
      {accessibility && (accessibility.intent || accessibility.notes?.length || accessibility.role) && (
        <div className="token-inspector__a11y">
          <div className="token-inspector__pill">Accessibility</div>
          {accessibility.role && <p className="token-inspector__a11y-text">Role: {accessibility.role}</p>}
          {accessibility.intent && <p className="token-inspector__a11y-text">{accessibility.intent}</p>}
          {accessibility.notes?.length ? (
            <ul className="token-inspector__a11y-list">
              {accessibility.notes.map((note) => (
                <li key={note}>{note}</li>
              ))}
            </ul>
          ) : null}
          {accessibility.aria && (
            <dl className="token-inspector__a11y-dl">
              {Object.entries(accessibility.aria).map(([key, value]) => (
                <div key={key} className="token-inspector__a11y-pair">
                  <dt>{key}</dt>
                  <dd>{value}</dd>
                </div>
              ))}
            </dl>
          )}
        </div>
      )}
    </header>
  )
}

type SlotPanelProps = {
  slot: AnatomySlot
}

function SlotPanel({ slot }: SlotPanelProps) {
  return (
    <div className="token-inspector__slot" data-testid="token-slot">
      <div className="token-inspector__slot-header">
        <div>
          <div className="token-inspector__slot-label">Anatomy Slot</div>
          <h4 className="token-inspector__slot-title">{slot.name}</h4>
          {slot.description && <p className="token-inspector__slot-description">{slot.description}</p>}
        </div>
        {slot.accessibility && (slot.accessibility.intent || slot.accessibility.role) && (
          <div className="token-inspector__slot-a11y">
            {slot.accessibility.role && <span className="token-inspector__pill">Role: {slot.accessibility.role}</span>}
            {slot.accessibility.intent && <p className="token-inspector__muted">{slot.accessibility.intent}</p>}
          </div>
        )}
      </div>

      <section className="token-inspector__tokens" aria-label="Token bindings">
        <div className="token-inspector__tokens-header">
          <span>Property</span>
          <span>Token</span>
          <span>Intent</span>
        </div>
        {slot.tokens.length === 0 ? (
          <div className="token-inspector__muted standin">No token bindings provided.</div>
        ) : (
          <ul className="token-inspector__token-list">
            {slot.tokens.map((binding, idx) => (
              <li key={`${binding.property}-${binding.token}-${idx}`} className="token-inspector__token-row" data-testid="token-binding">
                <span className="token-inspector__mono">{binding.property}</span>
                <code className="token-inspector__mono">{binding.token}</code>
                <span className={binding.intent || binding.example ? 'token-inspector__muted' : 'token-inspector__muted standin'}>
                  {binding.intent || binding.example || '—'}
                </span>
              </li>
            ))}
          </ul>
        )}
      </section>

      {slot.accessibility?.aria && (
        <section className="token-inspector__slot-aria" aria-label="Accessibility guidance">
          <h5 className="token-inspector__slot-subtitle">ARIA hooks</h5>
          <dl className="token-inspector__a11y-dl">
            {Object.entries(slot.accessibility.aria).map(([key, value]) => (
              <div key={key} className="token-inspector__a11y-pair">
                <dt>{key}</dt>
                <dd>{value}</dd>
              </div>
            ))}
          </dl>
        </section>
      )}

      {slot.accessibility?.notes?.length ? (
        <section className="token-inspector__slot-notes" aria-label="Accessibility notes">
          <h5 className="token-inspector__slot-subtitle">Notes</h5>
          <ul>
            {slot.accessibility.notes.map((note) => (
              <li key={note}>{note}</li>
            ))}
          </ul>
        </section>
      ) : null}
    </div>
  )
}

export default TokenInspector
