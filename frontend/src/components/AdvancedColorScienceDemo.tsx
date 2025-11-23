import { useState, useCallback } from 'react'
import './AdvancedColorScienceDemo.css'

interface ColorToken {
  id?: number
  hex: string
  rgb?: string
  hsl?: string
  hsv?: string
  name: string
  design_intent?: string
  semantic_names?: Record<string, string> | null
  confidence: number
  harmony?: string
  temperature?: string
  saturation_level?: string
  lightness_level?: string
  category?: string
  usage?: string | string[]
  wcag_contrast_on_white?: number
  wcag_contrast_on_black?: number
  wcag_aa_compliant_text?: boolean
  wcag_aaa_compliant_text?: boolean
  wcag_aa_compliant_normal?: boolean
  wcag_aaa_compliant_normal?: boolean
  colorblind_safe?: boolean
  tint_color?: string
  shade_color?: string
  tone_color?: string
  closest_web_safe?: string
  closest_css_named?: string
  is_neutral?: boolean
  provenance?: Record<string, number>
  extraction_metadata?: Record<string, unknown>
}

interface PipelineStage {
  id: string
  name: string
  description: string
  status: 'pending' | 'running' | 'done' | 'error'
  duration?: number
}

interface ExtractionResult {
  colors: ColorToken[]
  extractor_used: string
  color_palette?: string
}

export default function AdvancedColorScienceDemo() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [preview, setPreview] = useState<string | null>(null)
  const [isExtracting, setIsExtracting] = useState(false)
  const [colors, setColors] = useState<ColorToken[]>([])
  const [selectedColorIndex, setSelectedColorIndex] = useState<number | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [paletteDescription, setPaletteDescription] = useState<string>('')
  const [extractorUsed, setExtractorUsed] = useState<string>('')
  const [expandedEducation, setExpandedEducation] = useState<string | null>('pipeline')

  const [stages, setStages] = useState<PipelineStage[]>([
    { id: 'preprocess', name: 'Preprocess', description: 'Validate, resize, enhance image', status: 'pending' },
    { id: 'extract', name: 'Extract', description: 'AI-powered color detection', status: 'pending' },
    { id: 'aggregate', name: 'Aggregate', description: 'Delta-E deduplication', status: 'pending' },
    { id: 'validate', name: 'Validate', description: 'WCAG accessibility checks', status: 'pending' },
    { id: 'generate', name: 'Generate', description: 'W3C Design Tokens output', status: 'pending' }
  ])

  const handleFileChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      setSelectedFile(file)
      const reader = new FileReader()
      reader.onload = (e) => {
        setPreview(e.target?.result as string)
      }
      reader.readAsDataURL(file)
      setError(null)
      resetStages()
    }
  }, [])

  const handleDrop = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    const file = e.dataTransfer.files[0]
    if (file && file.type.startsWith('image/')) {
      setSelectedFile(file)
      const reader = new FileReader()
      reader.onload = (e) => {
        setPreview(e.target?.result as string)
      }
      reader.readAsDataURL(file)
      setError(null)
      resetStages()
    }
  }, [])

  const resetStages = () => {
    setStages(prev => prev.map(s => ({ ...s, status: 'pending', duration: undefined })))
  }

  const updateStage = (id: string, status: PipelineStage['status'], duration?: number) => {
    setStages(prev => prev.map(s =>
      s.id === id ? { ...s, status, duration } : s
    ))
  }

  const extractColors = async () => {
    if (!selectedFile || !preview) return

    setIsExtracting(true)
    setError(null)
    setColors([])
    setSelectedColorIndex(null)
    resetStages()

    try {
      // Ensure project exists
      let projectId = 1
      try {
        const projectRes = await fetch('/api/v1/projects/1/colors')
        if (projectRes.status === 404) {
          const createRes = await fetch('/api/v1/projects', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name: 'Color Science Demo', description: 'Advanced pipeline demo' })
          })
          if (createRes.ok) {
            const project = await createRes.json()
            projectId = project.id
          }
        }
      } catch {
        // Use default project
      }

      // Stage 1: Preprocess
      const preprocessStart = performance.now()
      updateStage('preprocess', 'running')
      await delay(300)
      updateStage('preprocess', 'done', performance.now() - preprocessStart)

      // Stage 2: Extract
      const extractStart = performance.now()
      updateStage('extract', 'running')

      const response = await fetch('/api/v1/colors/extract', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          image_base64: preview,
          project_id: projectId,
          max_colors: 12
        })
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Extraction failed')
      }

      updateStage('extract', 'done', performance.now() - extractStart)

      // Stage 3: Aggregate
      const aggStart = performance.now()
      updateStage('aggregate', 'running')
      await delay(200)
      updateStage('aggregate', 'done', performance.now() - aggStart)

      // Stage 4: Validate
      const valStart = performance.now()
      updateStage('validate', 'running')
      await delay(200)
      updateStage('validate', 'done', performance.now() - valStart)

      // Stage 5: Generate
      const genStart = performance.now()
      updateStage('generate', 'running')
      await delay(150)
      updateStage('generate', 'done', performance.now() - genStart)

      const result: ExtractionResult = await response.json()
      setColors(result.colors || [])
      setPaletteDescription(result.color_palette || '')
      setExtractorUsed(result.extractor_used || 'claude')

      if (result.colors?.length > 0) {
        setSelectedColorIndex(0)
      }

    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
      const currentRunning = stages.find(s => s.status === 'running')
      if (currentRunning) {
        updateStage(currentRunning.id, 'error')
      }
    } finally {
      setIsExtracting(false)
    }
  }

  const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms))

  const selectedColor = selectedColorIndex !== null ? colors[selectedColorIndex] : null

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text)
  }

  return (
    <div className="advanced-color-science-demo">
      {/* Header */}
      <header className="demo-header">
        <h1>Advanced Color Science Demo</h1>
        <p>Full 5-stage pipeline visualization with color science education</p>
      </header>

      <div className="demo-layout">
        {/* Left Panel - Upload & Pipeline */}
        <aside className="left-panel">
          {/* Upload Section */}
          <section className="panel-card upload-section">
            <h2>Upload Image</h2>
            <div
              className={`upload-area ${preview ? 'has-preview' : ''}`}
              onDrop={handleDrop}
              onDragOver={(e) => e.preventDefault()}
              onClick={() => document.getElementById('file-input')?.click()}
            >
              {preview ? (
                <img src={preview} alt="Preview" className="preview-image" />
              ) : (
                <>
                  <span className="upload-icon">+</span>
                  <p>Drop image or click to browse</p>
                </>
              )}
              <input
                id="file-input"
                type="file"
                accept="image/*"
                onChange={handleFileChange}
                style={{ display: 'none' }}
              />
            </div>
            {selectedFile && (
              <button
                className="extract-btn"
                onClick={extractColors}
                disabled={isExtracting}
              >
                {isExtracting ? 'Extracting...' : 'Extract Colors'}
              </button>
            )}
          </section>

          {/* Pipeline Visualization */}
          <section className="panel-card pipeline-section">
            <h2>Pipeline Stages</h2>
            <div className="pipeline-stages">
              {stages.map((stage, index) => (
                <div key={stage.id} className={`pipeline-stage ${stage.status}`}>
                  <div className="stage-number">{index + 1}</div>
                  <div className="stage-info">
                    <div className="stage-name">{stage.name}</div>
                    <div className="stage-desc">{stage.description}</div>
                  </div>
                  <div className="stage-status">
                    {stage.status === 'pending' && 'Pending'}
                    {stage.status === 'running' && <span className="spinner-small" />}
                    {stage.status === 'done' && (
                      <span className="done-check">
                        {stage.duration ? `${stage.duration.toFixed(0)}ms` : 'Done'}
                      </span>
                    )}
                    {stage.status === 'error' && 'Error'}
                  </div>
                </div>
              ))}
            </div>
          </section>

          {/* Education Panel */}
          <section className="panel-card education-section">
            <h2>Color Science Education</h2>

            {/* Pipeline Education */}
            <div className="edu-topic">
              <button
                className="edu-header"
                onClick={() => setExpandedEducation(expandedEducation === 'pipeline' ? null : 'pipeline')}
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
                onClick={() => setExpandedEducation(expandedEducation === 'deltae' ? null : 'deltae')}
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
                onClick={() => setExpandedEducation(expandedEducation === 'wcag' ? null : 'wcag')}
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
                onClick={() => setExpandedEducation(expandedEducation === 'spaces' ? null : 'spaces')}
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
                onClick={() => setExpandedEducation(expandedEducation === 'semantic' ? null : 'semantic')}
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
                    <li><strong>Vibrancy:</strong> vivid, muted, desaturated</li>
                  </ul>
                </div>
              )}
            </div>
          </section>
        </aside>

        {/* Center Panel - Results */}
        <main className="center-panel">
          {error && <div className="error-message">{error}</div>}

          {colors.length === 0 && !isExtracting && (
            <div className="empty-state">
              <p>Upload an image to extract and analyze colors</p>
            </div>
          )}

          {isExtracting && (
            <div className="loading-state">
              <div className="spinner" />
              <p>Processing through pipeline...</p>
            </div>
          )}

          {colors.length > 0 && (
            <>
              {/* Stats */}
              <section className="panel-card stats-section">
                <div className="stats-grid">
                  <div className="stat-item">
                    <div className="stat-value">{colors.length}</div>
                    <div className="stat-label">Colors</div>
                  </div>
                  <div className="stat-item">
                    <div className="stat-value">
                      {(colors.reduce((a, c) => a + c.confidence, 0) / colors.length * 100).toFixed(0)}%
                    </div>
                    <div className="stat-label">Avg Confidence</div>
                  </div>
                  <div className="stat-item">
                    <div className="stat-value">
                      {colors.filter(c => c.wcag_aa_compliant_text).length}
                    </div>
                    <div className="stat-label">WCAG AA</div>
                  </div>
                  <div className="stat-item">
                    <div className="stat-value">{extractorUsed}</div>
                    <div className="stat-label">Extractor</div>
                  </div>
                </div>
                {paletteDescription && (
                  <p className="palette-description">{paletteDescription}</p>
                )}
              </section>

              {/* Color Grid */}
              <section className="panel-card colors-section">
                <h2>Extracted Colors</h2>
                <div className="colors-grid">
                  {colors.map((color, index) => (
                    <div
                      key={index}
                      className={`color-card ${selectedColorIndex === index ? 'selected' : ''}`}
                      onClick={() => setSelectedColorIndex(index)}
                    >
                      <div
                        className="color-swatch"
                        style={{ backgroundColor: color.hex }}
                        onClick={(e) => {
                          e.stopPropagation()
                          copyToClipboard(color.hex)
                        }}
                        title={`Click to copy ${color.hex}`}
                      />
                      <div className="color-info">
                        <div className="color-name">{color.name}</div>
                        <div className="color-hex">{color.hex}</div>
                        <div className="color-tags">
                          {color.harmony && <span className="tag harmony">{color.harmony}</span>}
                          {color.temperature && <span className="tag temp">{color.temperature}</span>}
                          {color.wcag_aa_compliant_text && <span className="tag wcag-pass">AA</span>}
                        </div>
                        <div className="confidence-bar">
                          <div
                            className="confidence-fill"
                            style={{ width: `${color.confidence * 100}%` }}
                          />
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </section>
            </>
          )}
        </main>

        {/* Right Panel - Selected Color Details */}
        <aside className="right-panel">
          {selectedColor ? (
            <section className="panel-card details-section">
              <h2>Color Analysis</h2>

              {/* Main Swatch */}
              <div
                className="detail-swatch"
                style={{ backgroundColor: selectedColor.hex }}
              />

              <h3 className="detail-name">{selectedColor.name}</h3>
              <div className="detail-confidence">
                Confidence: {(selectedColor.confidence * 100).toFixed(1)}%
              </div>

              {/* Color Values */}
              <div className="detail-group">
                <h4>Color Values</h4>
                <div className="value-grid">
                  <div className="value-item">
                    <span className="value-label">HEX</span>
                    <span className="value-data mono">{selectedColor.hex}</span>
                  </div>
                  {selectedColor.rgb && (
                    <div className="value-item">
                      <span className="value-label">RGB</span>
                      <span className="value-data mono">{selectedColor.rgb}</span>
                    </div>
                  )}
                  {selectedColor.hsl && (
                    <div className="value-item">
                      <span className="value-label">HSL</span>
                      <span className="value-data mono">{selectedColor.hsl}</span>
                    </div>
                  )}
                  {selectedColor.hsv && (
                    <div className="value-item">
                      <span className="value-label">HSV</span>
                      <span className="value-data mono">{selectedColor.hsv}</span>
                    </div>
                  )}
                </div>
              </div>

              {/* Properties */}
              <div className="detail-group">
                <h4>Properties</h4>
                <div className="props-grid">
                  {selectedColor.temperature && (
                    <div className="prop-item">
                      <span className="prop-label">Temperature</span>
                      <span className="prop-value">{selectedColor.temperature}</span>
                    </div>
                  )}
                  {selectedColor.saturation_level && (
                    <div className="prop-item">
                      <span className="prop-label">Saturation</span>
                      <span className="prop-value">{selectedColor.saturation_level}</span>
                    </div>
                  )}
                  {selectedColor.lightness_level && (
                    <div className="prop-item">
                      <span className="prop-label">Lightness</span>
                      <span className="prop-value">{selectedColor.lightness_level}</span>
                    </div>
                  )}
                  {selectedColor.harmony && (
                    <div className="prop-item">
                      <span className="prop-label">Harmony</span>
                      <span className="prop-value">{selectedColor.harmony}</span>
                    </div>
                  )}
                </div>
              </div>

              {/* WCAG Accessibility */}
              <div className="detail-group">
                <h4>WCAG Accessibility</h4>
                <div className="wcag-details">
                  {selectedColor.wcag_contrast_on_white != null && (
                    <div className="wcag-row">
                      <span className="wcag-label">On White</span>
                      <span className={`wcag-ratio ${selectedColor.wcag_contrast_on_white >= 4.5 ? 'pass' : 'fail'}`}>
                        {selectedColor.wcag_contrast_on_white.toFixed(2)}:1
                      </span>
                      <div className="wcag-badges">
                        <span className={`badge ${selectedColor.wcag_aa_compliant_text ? 'pass' : 'fail'}`}>
                          AA {selectedColor.wcag_aa_compliant_text ? 'Pass' : 'Fail'}
                        </span>
                        <span className={`badge ${selectedColor.wcag_aaa_compliant_text ? 'pass' : 'fail'}`}>
                          AAA {selectedColor.wcag_aaa_compliant_text ? 'Pass' : 'Fail'}
                        </span>
                      </div>
                    </div>
                  )}
                  {selectedColor.wcag_contrast_on_black != null && (
                    <div className="wcag-row">
                      <span className="wcag-label">On Black</span>
                      <span className={`wcag-ratio ${selectedColor.wcag_contrast_on_black >= 4.5 ? 'pass' : 'fail'}`}>
                        {selectedColor.wcag_contrast_on_black.toFixed(2)}:1
                      </span>
                    </div>
                  )}
                  {selectedColor.colorblind_safe && (
                    <div className="colorblind-safe">Colorblind Safe</div>
                  )}
                </div>
              </div>

              {/* Color Variants */}
              {(selectedColor.tint_color || selectedColor.shade_color || selectedColor.tone_color) && (
                <div className="detail-group">
                  <h4>Color Variants</h4>
                  <div className="variants-row">
                    {selectedColor.tint_color && (
                      <div className="variant-item">
                        <div
                          className="variant-swatch"
                          style={{ backgroundColor: selectedColor.tint_color }}
                        />
                        <span className="variant-label">Tint</span>
                      </div>
                    )}
                    <div className="variant-item">
                      <div
                        className="variant-swatch"
                        style={{ backgroundColor: selectedColor.hex }}
                      />
                      <span className="variant-label">Base</span>
                    </div>
                    {selectedColor.shade_color && (
                      <div className="variant-item">
                        <div
                          className="variant-swatch"
                          style={{ backgroundColor: selectedColor.shade_color }}
                        />
                        <span className="variant-label">Shade</span>
                      </div>
                    )}
                    {selectedColor.tone_color && (
                      <div className="variant-item">
                        <div
                          className="variant-swatch"
                          style={{ backgroundColor: selectedColor.tone_color }}
                        />
                        <span className="variant-label">Tone</span>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Semantic Names */}
              {selectedColor.semantic_names && Object.keys(selectedColor.semantic_names).length > 0 && (
                <div className="detail-group">
                  <h4>Semantic Names</h4>
                  <div className="semantic-list">
                    {Object.entries(selectedColor.semantic_names).map(([type, name]) => (
                      <div key={type} className="semantic-item">
                        <span className="semantic-type">{type}</span>
                        <span className="semantic-name">{name}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Design Intent */}
              {selectedColor.design_intent && (
                <div className="detail-group">
                  <h4>Design Intent</h4>
                  <p className="design-intent">{selectedColor.design_intent}</p>
                </div>
              )}

              {/* Web Safe & CSS Named */}
              {(selectedColor.closest_web_safe || selectedColor.closest_css_named) && (
                <div className="detail-group">
                  <h4>Web Integration</h4>
                  <div className="web-info">
                    {selectedColor.closest_web_safe && (
                      <div className="web-item">
                        <span className="web-label">Web Safe</span>
                        <span className="web-value">{selectedColor.closest_web_safe}</span>
                      </div>
                    )}
                    {selectedColor.closest_css_named && (
                      <div className="web-item">
                        <span className="web-label">CSS Named</span>
                        <span className="web-value">{selectedColor.closest_css_named}</span>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Provenance */}
              {selectedColor.provenance && Object.keys(selectedColor.provenance).length > 0 && (
                <div className="detail-group">
                  <h4>Provenance</h4>
                  <div className="provenance-list">
                    {Object.entries(selectedColor.provenance).map(([source, conf]) => (
                      <div key={source} className="provenance-item">
                        <span className="prov-source">{source}</span>
                        <span className="prov-confidence">{(Number(conf) * 100).toFixed(0)}%</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </section>
          ) : (
            <section className="panel-card details-section empty">
              <p>Select a color to see detailed analysis</p>
            </section>
          )}
        </aside>
      </div>
    </div>
  )
}
