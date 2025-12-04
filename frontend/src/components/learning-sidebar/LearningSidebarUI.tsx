import { useSectionExpansion } from './hooks'
import { SectionHeader } from './SectionHeader'
import { PipelineSection } from './sections/PipelineSection'
import { TheorySection } from './sections/TheorySection'
import { NamingSection } from './sections/NamingSection'
import { TechSection } from './sections/TechSection'
import { ResourcesSection } from './sections/ResourcesSection'
import type { LearningSidebarProps } from './types'

interface UIProps extends LearningSidebarProps {}

export function LearningSidebarUI({ isOpen, onToggle }: UIProps) {
  const { expandedSection, toggleSection } = useSectionExpansion()

  return (
    <aside className={`learning-sidebar ${isOpen ? 'open' : 'collapsed'}`}>
      {/* Toggle Button */}
      <button className="sidebar-toggle" onClick={onToggle} title="Toggle learning">
        {isOpen ? '📚' : '📘'}
      </button>

      {isOpen && (
        <div className="sidebar-content">
          {/* Algorithm Pipeline */}
          <section className="learning-section">
            <SectionHeader
              section="pipeline"
              icon="⚙️"
              title="Algorithm Pipeline"
              isExpanded={expandedSection === 'pipeline'}
              onToggle={toggleSection}
            />
            <PipelineSection isExpanded={expandedSection === 'pipeline'} />
          </section>

          {/* Color Theory */}
          <section className="learning-section">
            <SectionHeader
              section="theory"
              icon="🌈"
              title="Color Theory"
              isExpanded={expandedSection === 'theory'}
              onToggle={toggleSection}
            />
            <TheorySection isExpanded={expandedSection === 'theory'} />
          </section>

          {/* Semantic Naming */}
          <section className="learning-section">
            <SectionHeader
              section="naming"
              icon="🏷️"
              title="Semantic Naming"
              isExpanded={expandedSection === 'naming'}
              onToggle={toggleSection}
            />
            <NamingSection isExpanded={expandedSection === 'naming'} />
          </section>

          {/* Technical Details */}
          <section className="learning-section">
            <SectionHeader
              section="tech"
              icon="⚡"
              title="Technical Details"
              isExpanded={expandedSection === 'tech'}
              onToggle={toggleSection}
            />
            <TechSection isExpanded={expandedSection === 'tech'} />
          </section>

          {/* Resources */}
          <section className="learning-section">
            <SectionHeader
              section="resources"
              icon="📖"
              title="Learn More"
              isExpanded={expandedSection === 'resources'}
              onToggle={toggleSection}
            />
            <ResourcesSection isExpanded={expandedSection === 'resources'} />
          </section>
        </div>
      )}
    </aside>
  )
}
