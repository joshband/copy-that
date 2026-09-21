import { useCallback, useState } from 'react'
import '../AdvancedColorScienceDemo.css'
import {
  PipelineVisualization,
  EducationPanel,
  UploadSection,
  ProjectControls,
} from '../color-science'
import {
  useImageUpload,
  usePipelineStages,
  useExtractionResults,
  useProjectState,
  delay,
} from './hooks'
import { ExtractionPanel } from './ExtractionPanel'

/**
 * Advanced Color Science Demo - Orchestrator
 * Manages state and extraction logic for the full color science pipeline
 */
export default function AdvancedColorScienceDemo() {
  // State management via custom hooks
  const imageUpload = useImageUpload()
  const pipeline = usePipelineStages()
  const extraction = useExtractionResults()
  const project = useProjectState()

  // Extract handler
  const handleExtract = useCallback(async () => {
    if (!imageUpload.selectedFile || !imageUpload.preview) return

    extraction.setIsExtracting(true)
    extraction.setError(null)
    extraction.reset()
    pipeline.resetStages()

    try {
      // Ensure project exists
      let workingProjectId = project.projectId
      try {
        const projectRes = await fetch(`/api/v1/projects/${workingProjectId}/colors`)
        if (projectRes.status === 404) {
          const createRes = await fetch('/api/v1/projects', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              name: project.projectName || 'Color Science Demo',
              description: 'Advanced pipeline demo'
            })
          })
          if (createRes.ok) {
            const proj = await createRes.json()
            workingProjectId = proj.id
            project.setProjectId(proj.id)
            project.setLoadProjectId(String(proj.id))
          }
        }
      } catch {
        // Use default project
      }

      const tokenTypes = ['color', 'spacing'] as const

      // Stage 1: Preprocess
      const preprocessStart = performance.now()
      pipeline.updateStage('preprocess', 'running')
      await delay(300)
      pipeline.updateStage('preprocess', 'done', performance.now() - preprocessStart)

      // Stage 2: Extract (SSE CV-first, AI-second)
      const extractStart = performance.now()
      pipeline.updateStage('extract', 'running')

      const body = JSON.stringify({
        image_base64: imageUpload.preview,
        image_media_type: imageUpload.imageMediaType || 'image/png',
        project_id: workingProjectId,
        token_types: tokenTypes,
        max_colors: 12,
        max_spacing_tokens: 20,
      })

      const response = await fetch('/api/v1/extract/stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body,
      })

      if (!response.ok || !response.body) {
        throw new Error(`Extraction failed (status ${response.status})`)
      }

      const reader = response.body.getReader()
      const decoder = new TextDecoder('utf-8')
      let buffer = ''

      const applyTokens = (type: string, source: string, payload: any[], metadata?: Record<string, any>) => {
        if (type === 'color') {
          extraction.setColors((prev) => (source === 'ai' ? payload : prev.length ? prev : payload))
          if (payload.length > 0) extraction.setSelectedColorIndex(0)
        } else if (type === 'spacing') {
          extraction.setSpacingTokens((prev) => (source === 'ai' ? payload : prev.length ? prev : payload))
          if (payload.length > 0) {
            const uniq = payload.map((p) => p.value_px)
            const base = metadata?.base_unit ?? payload[0].base_unit ?? payload[0].value_px ?? 0
            const confidenceLabel =
              metadata?.base_unit_confidence != null
                ? ` · confidence ${Math.round(metadata.base_unit_confidence * 100)}%`
                : ''
            const valuesLabel = uniq.slice(0, 6).join(', ')
            extraction.setSpacingSummary(
              `${payload.length} spacing · base ${base}px${confidenceLabel}${
                valuesLabel ? ` · values ${valuesLabel}` : ''
              }`
            )
          }
        }
      }

      while (true) {
        const { value, done } = await reader.read()
        if (done) break
        buffer += decoder.decode(value, { stream: true })
        const events = buffer.split('\n\n')
        buffer = events.pop() || ''
        for (const evt of events) {
          const lines = evt.split('\n')
          const eventLine = lines.find((l) => l.startsWith('event:'))
          const dataLine = lines.find((l) => l.startsWith('data:'))
          if (!eventLine || !dataLine) continue
          const event = eventLine.replace('event:', '').trim()
          const data = JSON.parse(dataLine.replace('data:', '').trim() || '{}')
          console.log('SSE event', event, data)
          if (event === 'token') {
            const { type, source, tokens, metadata } = data
            if (type && tokens) applyTokens(type, source || 'cv', tokens, metadata)
          } else if (event === 'complete') {
            pipeline.updateStage('extract', 'done', performance.now() - extractStart)
          } else if (event === 'error') {
            throw new Error(data.error || 'Extraction failed')
          }
        }
      }

      pipeline.updateStage('extract', 'done', performance.now() - extractStart)

      // Stage 3: Aggregate
      const aggStart = performance.now()
      pipeline.updateStage('aggregate', 'running')
      await delay(200)
      pipeline.updateStage('aggregate', 'done', performance.now() - aggStart)

      // Stage 4: Validate
      const valStart = performance.now()
      pipeline.updateStage('validate', 'running')
      await delay(200)
      pipeline.updateStage('validate', 'done', performance.now() - valStart)

      // Stage 5: Generate
      const genStart = performance.now()
      pipeline.updateStage('generate', 'running')
      await delay(150)
      pipeline.updateStage('generate', 'done', performance.now() - genStart)

    } catch (err) {
      extraction.setError(err instanceof Error ? err.message : 'An error occurred')
      const currentRunning = pipeline.stages.find(s => s.status === 'running')
      if (currentRunning) {
        pipeline.updateStage(currentRunning.id, 'error')
      }
    } finally {
      extraction.setIsExtracting(false)
    }
  }, [
    imageUpload.selectedFile,
    imageUpload.preview,
    imageUpload.imageMediaType,
    extraction,
    pipeline,
    project.projectId,
    project.projectName,
  ])

  // Save project handler
  const handleSaveProject = useCallback(async () => {
    try {
      const res = await fetch('/api/v1/projects', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: project.projectName || 'My Colors',
          description: 'Saved session',
          image_base64: imageUpload.imageBase64,
          image_media_type: imageUpload.imageMediaType,
          spacing_tokens: extraction.spacingTokens,
        }),
      })
      if (res.ok) {
        const proj = await res.json()
        project.setProjectId(proj.id)
        project.setLoadProjectId(String(proj.id))
        extraction.setError(null)
      } else {
        const err = await res.json()
        extraction.setError(err.detail || 'Failed to save project')
      }
    } catch (e) {
      extraction.setError(e instanceof Error ? e.message : 'Failed to save project')
    }
  }, [project, imageUpload, extraction])

  // Load project handler
  const handleLoadProject = useCallback(async () => {
    try {
      const pid = Number(project.loadProjectId || project.projectId)
      try {
        const projRes = await fetch(`/api/v1/projects/${pid}`)
        if (projRes.ok) {
          const proj = await projRes.json()
          if (proj.image_base64) {
            imageUpload.imageBase64 && (proj.image_base64)
            imageUpload.imageMediaType && (proj.image_media_type || 'image/png')
            // Note: Unable to directly set preview without ref, would need to be passed
          }
          if (proj.spacing_tokens) {
            extraction.setSpacingTokens(proj.spacing_tokens)
            extraction.setSpacingSummary(proj.spacing_tokens.length ? `${proj.spacing_tokens.length} spacing tokens (loaded)` : '')
          }
          if (proj.name) project.setProjectName(proj.name)
        }
      } catch (_) {
        // ignore
      }
      const res = await fetch(`/api/v1/projects/${pid}/colors`)
      if (!res.ok) {
        const err = await res.json()
        throw new Error(err.detail || 'Load failed')
      }
      const data = await res.json()
      extraction.setColors(data || [])
      extraction.setPaletteDescription('')
      project.setProjectId(pid)
      extraction.setError(null)
      extraction.setSelectedColorIndex(data?.length ? 0 : null)
      try {
        const spacRes = await fetch(`/api/v1/spacing/projects/${pid}/spacing`)
        if (spacRes.ok) {
          const spac = await spacRes.json()
          extraction.setSpacingTokens(spac || [])
          extraction.setSpacingSummary(spac?.length ? `${spac.length} spacing tokens loaded` : extraction.spacingSummary)
        }
      } catch (_) {
        // ignore
      }
    } catch (e) {
      extraction.setError(e instanceof Error ? e.message : 'Failed to load project')
    }
  }, [project, imageUpload, extraction])

  // Load snapshot handler
  const handleLoadSnapshot = useCallback(async () => {
    try {
      const pid = Number(project.loadProjectId || project.projectId)
      const listRes = await fetch(`/api/v1/projects/${pid}/snapshots`)
      if (!listRes.ok) throw new Error('No snapshots found')
      const snaps = await listRes.json()
      if (!snaps.length) throw new Error('No snapshots available')
      const snapId = snaps[0].id
      const snapRes = await fetch(`/api/v1/projects/${pid}/snapshots/${snapId}`)
      if (!snapRes.ok) throw new Error('Failed to load snapshot')
      const snap = await snapRes.json()
      const data = snap.data || {}
      if (data.colors) extraction.setColors(data.colors)
      if (data.spacing) {
        extraction.setSpacingTokens(data.spacing)
        extraction.setSpacingSummary(data.spacing.length ? `${data.spacing.length} spacing (snapshot)` : '')
      }
      project.setProjectId(pid)
      extraction.setSelectedColorIndex(data.colors?.length ? 0 : null)
      extraction.setError(null)
    } catch (e) {
      extraction.setError(e instanceof Error ? e.message : 'Failed to load snapshot')
    }
  }, [project, extraction])

  const [expandedEducation, setExpandedEducation] = useState<string | null>('pipeline')

  return (
    <div className="advanced-color-science-demo">
      <header className="demo-header">
        <h1>Advanced Color Science Demo</h1>
        <p>Full 5-stage pipeline visualization with color science education</p>
      </header>

      <div className="demo-layout">
        <aside className="left-panel">
          <UploadSection
            preview={imageUpload.preview}
            isExtracting={extraction.isExtracting}
            onFileChange={imageUpload.handleFileChange}
            onDrop={imageUpload.handleDrop}
            onExtract={handleExtract}
            selectedFile={imageUpload.selectedFile}
          />
          <ProjectControls
            projectName={project.projectName}
            projectId={project.projectId}
            loadProjectId={project.loadProjectId}
            colors={extraction.colors}
            spacingTokens={extraction.spacingTokens}
            imageBase64={imageUpload.imageBase64}
            imageMediaType={imageUpload.imageMediaType}
            onProjectNameChange={project.setProjectName}
            onSaveProject={handleSaveProject}
            onLoadProjectIdChange={project.setLoadProjectId}
            onLoadProject={handleLoadProject}
            onLoadSnapshot={handleLoadSnapshot}
          />
          <PipelineVisualization stages={pipeline.stages} />
          <EducationPanel
            expandedEducation={expandedEducation}
            onExpandTopic={setExpandedEducation}
            paletteDescription={extraction.paletteDescription}
          />
        </aside>

        <ExtractionPanel
          isExtracting={extraction.isExtracting}
          error={extraction.error}
          colors={extraction.colors}
          spacingTokens={extraction.spacingTokens}
          selectedColorIndex={extraction.selectedColorIndex}
          extractorUsed={extraction.extractorUsed}
          paletteDescription={extraction.paletteDescription}
          spacingSummary={extraction.spacingSummary}
          onSelectColor={extraction.setSelectedColorIndex}
        />
      </div>
    </div>
  )
}
