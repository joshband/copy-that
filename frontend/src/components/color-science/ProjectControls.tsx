import React from 'react'

interface ProjectControlsProps {
  projectName: string
  projectId: number
  loadProjectId: string
  colors: any[]
  spacingTokens: any[]
  imageBase64: string | null
  imageMediaType: string
  onProjectNameChange: (name: string) => void
  onSaveProject: () => void
  onLoadProjectIdChange: (id: string) => void
  onLoadProject: () => void
  onLoadSnapshot: () => void
}

export function ProjectControls({
  projectName,
  projectId,
  loadProjectId,
  colors,
  spacingTokens,
  imageBase64,
  imageMediaType,
  onProjectNameChange,
  onSaveProject,
  onLoadProjectIdChange,
  onLoadProject,
  onLoadSnapshot,
}: ProjectControlsProps) {
  return (
    <section className="panel-card">
      <h2>Project / Session</h2>
      <div className="project-controls">
        <label className="field">
          <span>Project Name</span>
          <input
            type="text"
            value={projectName}
            onChange={(e) => onProjectNameChange(e.target.value)}
            placeholder="My Colors"
          />
        </label>
        <div className="project-actions">
          <button
            className="small-btn"
            onClick={onSaveProject}
            disabled={!colors.length && !spacingTokens.length}
            title={!colors.length && !spacingTokens.length ? 'Extract tokens first' : undefined}
          >
            Save Project
          </button>
          <div className="load-row">
            <input
              type="number"
              value={loadProjectId}
              onChange={(e) => onLoadProjectIdChange(e.target.value)}
              className="load-input"
              placeholder="Project ID"
            />
            <button className="small-btn" onClick={onLoadProject}>
              Load Project
            </button>
          </div>
          <div className="load-row">
            <button className="small-btn" onClick={onLoadSnapshot} title="Load most recent snapshot">
              Load Latest Snapshot
            </button>
          </div>
          <div className="project-meta">Current Project ID: {projectId}</div>
        </div>
      </div>
    </section>
  )
}
