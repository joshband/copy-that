import React from 'react'

interface EducationPanelProps {
  expandedEducation: string | null
  onExpandTopic: (topic: string | null) => void
  paletteDescription: string
}

export function EducationPanel({ expandedEducation, onExpandTopic, paletteDescription }: EducationPanelProps) {
  const toggleTopic = (topic: string) => {
    onExpandTopic(expandedEducation === topic ? null : topic)
  }

  return (
    <section className="panel-card education-section">
      <h2>Color Science Education</h2>

      {/* Pipeline Education */}
      <div className="edu-topic">
        <button
          className="edu-header"
          onClick={() => toggleTopic('pipeline')}
        >
          <span>Algorithm Pipeline</span>
          <span className="expand-icon">{expandedEducation === 'pipeline' ? '-' : '+'}</span>
        </button>
        {expandedEducation === 'pipeline' && (
          <div className="edu-content">
            <p><strong>Preprocess:</strong> SSRF protection, image validation, resize to 1920x1080, CLAHE enhancement</p>
            <p><strong>Extract:</strong> Claude Sonnet 4.5 with Tool Use API for structured extraction</p>
            <p><strong>Aggregate:</strong> Delta-E 2000 deduplication (JND = 2.0), provenance tracking</p>
            <p><strong>Validate:</strong> WCAG contrast ratios, colorblind safety, quality scoring</p>
            <p><strong>Generate:</strong> W3C Design Tokens, CSS, React, Tailwind output</p>
          </div>
        )}
      </div>

      {/* Delta-E Education */}
      <div className="edu-topic">
        <button
          className="edu-header"
          onClick={() => toggleTopic('deltae')}
        >
          <span>Delta-E (CIEDE2000)</span>
          <span className="expand-icon">{expandedEducation === 'deltae' ? '-' : '+'}</span>
        </button>
        {expandedEducation === 'deltae' && (
          <div className="edu-content">
            <p>Perceptual color difference metric based on human vision.</p>
            <ul>
              <li><strong>0-1:</strong> Not perceptible by human eyes</li>
              <li><strong>1-2:</strong> Perceptible through close observation</li>
              <li><strong>2-10:</strong> Perceptible at a glance</li>
              <li><strong>11-49:</strong> More similar than opposite</li>
              <li><strong>100:</strong> Exact opposite colors</li>
            </ul>
            <p className="highlight">JND threshold: 2.0 (Just Noticeable Difference)</p>
          </div>
        )}
      </div>

      {/* WCAG Education */}
      <div className="edu-topic">
        <button
          className="edu-header"
          onClick={() => toggleTopic('wcag')}
        >
          <span>WCAG Accessibility</span>
          <span className="expand-icon">{expandedEducation === 'wcag' ? '-' : '+'}</span>
        </button>
        {expandedEducation === 'wcag' && (
          <div className="edu-content">
            <p><strong>Level AA (Minimum):</strong></p>
            <ul>
              <li>Normal text: 4.5:1 ratio</li>
              <li>Large text (18pt+): 3:1 ratio</li>
            </ul>
            <p><strong>Level AAA (Enhanced):</strong></p>
            <ul>
              <li>Normal text: 7:1 ratio</li>
              <li>Large text: 4.5:1 ratio</li>
            </ul>
            <p className="highlight">Formula: (L1 + 0.05) / (L2 + 0.05)</p>
          </div>
        )}
      </div>

      {/* Color Spaces Education */}
      <div className="edu-topic">
        <button
          className="edu-header"
          onClick={() => toggleTopic('spaces')}
        >
          <span>Color Spaces</span>
          <span className="expand-icon">{expandedEducation === 'spaces' ? '-' : '+'}</span>
        </button>
        {expandedEducation === 'spaces' && (
          <div className="edu-content">
            <p><strong>RGB:</strong> Additive color for displays (Red, Green, Blue)</p>
            <p><strong>HSL:</strong> Human-readable (Hue, Saturation, Lightness)</p>
            <p><strong>HSV:</strong> Design-friendly (Hue, Saturation, Value)</p>
            <p><strong>LAB:</strong> Perceptually uniform (Lightness, A, B)</p>
            <p><strong>Oklch:</strong> Modern perceptual space for CSS</p>
          </div>
        )}
      </div>

      {/* Semantic Naming */}
      <div className="edu-topic">
        <button
          className="edu-header"
          onClick={() => toggleTopic('semantic')}
        >
          <span>Semantic Naming</span>
          <span className="expand-icon">{expandedEducation === 'semantic' ? '-' : '+'}</span>
        </button>
        {expandedEducation === 'semantic' && (
          <div className="edu-content">
            <p>5-dimension naming system:</p>
            <ul>
              <li><strong>Simple:</strong> red, blue, green</li>
              <li><strong>Descriptive:</strong> warm red, ocean blue</li>
              <li><strong>Emotional:</strong> passionate, calm, energetic</li>
              <li><strong>Technical:</strong> #FF5733, rgb(255, 87, 51)</li>
              <li><strong>Vibrancy:</strong> vivid, muted, desaturated, balanced</li>
            </ul>
            {paletteDescription && <p className="highlight">Palette Story: {paletteDescription}</p>}
          </div>
        )}
      </div>

      {/* Narrative */}
      <div className="edu-topic">
        <button
          className="edu-header"
          onClick={() => toggleTopic('narrative')}
        >
          <span>Palette Narrative</span>
          <span className="expand-icon">{expandedEducation === 'narrative' ? '-' : '+'}</span>
        </button>
        {expandedEducation === 'narrative' && (
          <div className="edu-content">
            <p>
              This palette blends technical rigor with creative tone. Use dominant hues for backgrounds, pair
              high-confidence accents for calls-to-action, and reserve muted tones for surfaces and dividers.
            </p>
            <p>
              Accessibility: prioritize the highest contrast pairings for primary text, and validate secondary accents
              against both light and dark surfaces.
            </p>
          </div>
        )}
      </div>
    </section>
  )
}
