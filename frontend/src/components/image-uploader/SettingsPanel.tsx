import React from 'react'

interface Props {
  projectName: string
  maxColors: number
  projectId: number | null
  includeScienceArtifacts: boolean
  onProjectNameChange: (name: string) => void
  onMaxColorsChange: (count: number) => void
  onIncludeScienceArtifactsChange: (value: boolean) => void
}

export function SettingsPanel({
  projectName,
  maxColors,
  projectId,
  includeScienceArtifacts,
  onProjectNameChange,
  onMaxColorsChange,
  onIncludeScienceArtifactsChange,
}: Props) {
  return (
    <>
      {/* Max colors slider */}
      <div className="setting-group inline-setting">
        <label htmlFor="max-colors">
          Max Colors: <span className="value">{maxColors}</span>
        </label>
        <input
          id="max-colors"
          type="range"
          min="1"
          max="50"
          value={maxColors}
          onChange={(e) => onMaxColorsChange(parseInt(e.target.value))}
          className="range-slider"
        />
      </div>

      <div className="setting-group">
        <label className="setting-toggle" htmlFor="science-artifacts">
          <input
            id="science-artifacts"
            type="checkbox"
            checked={includeScienceArtifacts}
            onChange={(e) => onIncludeScienceArtifactsChange(e.target.checked)}
          />
          <span>Include science artifacts</span>
        </label>
        <p className="setting-hint">
          Adds palette-level visuals (OKLCH, Delta-E, contrast, temperature).
        </p>
      </div>

      {/* Project name settings */}
      <div className="settings">
        <div className="setting-group">
          <label htmlFor="project-name">Project Name:</label>
          <input
            id="project-name"
            type="text"
            value={projectName}
            onChange={(e) => onProjectNameChange(e.target.value)}
            placeholder="My Colors"
            disabled={projectId !== null}
          />
        </div>
      </div>
    </>
  )
}
