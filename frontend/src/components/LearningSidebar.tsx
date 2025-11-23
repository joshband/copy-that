import { useState } from 'react'
import './LearningSidebar.css'

interface LearningSidebarProps {
  isOpen: boolean
  onToggle: () => void
}

export function LearningSidebar({ isOpen, onToggle }: LearningSidebarProps) {
  const [expandedSection, setExpandedSection] = useState<string | null>('pipeline')

  const toggleSection = (section: string) => {
    setExpandedSection(expandedSection === section ? null : section)
  }

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
            <button
              className="section-header"
              onClick={() => toggleSection('pipeline')}
            >
              <span className="section-icon">⚙️</span>
              <span>Algorithm Pipeline</span>
              <span className="section-toggle">
                {expandedSection === 'pipeline' ? '▼' : '▶'}
              </span>
            </button>
            {expandedSection === 'pipeline' && (
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
                  Colors are extracted using AI vision analysis, then enriched with color science
                  calculations (harmony, accessibility, semantic naming).
                </p>
              </div>
            )}
          </section>

          {/* Color Theory */}
          <section className="learning-section">
            <button
              className="section-header"
              onClick={() => toggleSection('theory')}
            >
              <span className="section-icon">🌈</span>
              <span>Color Theory</span>
              <span className="section-toggle">
                {expandedSection === 'theory' ? '▼' : '▶'}
              </span>
            </button>
            {expandedSection === 'theory' && (
              <div className="section-content">
                <div className="theory-content">
                  <h4>Harmony Types (9)</h4>
                  <ul className="theory-list">
                    <li>
                      <strong>Monochromatic</strong>
                      <span className="desc">Single hue with variations</span>
                    </li>
                    <li>
                      <strong>Analogous</strong>
                      <span className="desc">Adjacent hues on wheel</span>
                    </li>
                    <li>
                      <strong>Complementary</strong>
                      <span className="desc">Opposite hues</span>
                    </li>
                    <li>
                      <strong>Triadic</strong>
                      <span className="desc">3 equally spaced hues</span>
                    </li>
                    <li>
                      <strong>Tetradic</strong>
                      <span className="desc">4 equally spaced hues</span>
                    </li>
                  </ul>

                  <h4 style={{ marginTop: '0.75rem' }}>Properties</h4>
                  <div className="properties-grid">
                    <div className="property">
                      <span className="prop-label">Temperature</span>
                      <span className="prop-value">🔥 Warm / Cool ❄️</span>
                    </div>
                    <div className="property">
                      <span className="prop-label">Saturation</span>
                      <span className="prop-value">Vibrant ↔️ Muted</span>
                    </div>
                    <div className="property">
                      <span className="prop-label">Lightness</span>
                      <span className="prop-value">Light ↔️ Dark</span>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </section>

          {/* Semantic Naming */}
          <section className="learning-section">
            <button
              className="section-header"
              onClick={() => toggleSection('naming')}
            >
              <span className="section-icon">🏷️</span>
              <span>Semantic Naming</span>
              <span className="section-toggle">
                {expandedSection === 'naming' ? '▼' : '▶'}
              </span>
            </button>
            {expandedSection === 'naming' && (
              <div className="section-content">
                <div className="naming-content">
                  <p className="naming-intro">
                    Each color gets 5 semantic names for different contexts:
                  </p>
                  <ul className="naming-list">
                    <li>
                      <span className="naming-type">Simple</span>
                      <span className="naming-example">red, blue, green</span>
                    </li>
                    <li>
                      <span className="naming-type">Descriptive</span>
                      <span className="naming-example">warm red, sky blue</span>
                    </li>
                    <li>
                      <span className="naming-type">Emotional</span>
                      <span className="naming-example">passionate, serene</span>
                    </li>
                    <li>
                      <span className="naming-type">Technical</span>
                      <span className="naming-example">#FF5733</span>
                    </li>
                    <li>
                      <span className="naming-type">Vibrancy</span>
                      <span className="naming-example">vivid, muted, desaturated</span>
                    </li>
                  </ul>
                </div>
              </div>
            )}
          </section>

          {/* Technical Details */}
          <section className="learning-section">
            <button
              className="section-header"
              onClick={() => toggleSection('tech')}
            >
              <span className="section-icon">⚡</span>
              <span>Technical Details</span>
              <span className="section-toggle">
                {expandedSection === 'tech' ? '▼' : '▶'}
              </span>
            </button>
            {expandedSection === 'tech' && (
              <div className="section-content">
                <div className="tech-content">
                  <div className="tech-item">
                    <strong>Delta-E (CIEDE2000)</strong>
                    <p>Perceptual color difference metric. Values: 0 (identical) - 100 (very different)</p>
                  </div>
                  <div className="tech-item">
                    <strong>WCAG Contrast Ratio</strong>
                    <p>How distinguishable two colors are. AA requires 4.5:1 for text, AAA requires 7:1</p>
                  </div>
                  <div className="tech-item">
                    <strong>Color Spaces</strong>
                    <p>RGB for display, HSL for design intent, Oklch for perceptual uniformity</p>
                  </div>
                  <div className="tech-item">
                    <strong>Gamut Mapping</strong>
                    <p>Ensures colors are displayable on sRGB screens</p>
                  </div>
                </div>
              </div>
            )}
          </section>

          {/* Resources */}
          <section className="learning-section">
            <button
              className="section-header"
              onClick={() => toggleSection('resources')}
            >
              <span className="section-icon">📖</span>
              <span>Learn More</span>
              <span className="section-toggle">
                {expandedSection === 'resources' ? '▼' : '▶'}
              </span>
            </button>
            {expandedSection === 'resources' && (
              <div className="section-content">
                <div className="resources-content">
                  <a href="#" className="resource-link">
                    Color Theory Basics
                  </a>
                  <a href="#" className="resource-link">
                    WCAG Accessibility Guide
                  </a>
                  <a href="#" className="resource-link">
                    Design Tokens Specification
                  </a>
                  <a href="#" className="resource-link">
                    Color Science Deep Dive
                  </a>
                </div>
              </div>
            )}
          </section>
        </div>
      )}
    </aside>
  )
}
