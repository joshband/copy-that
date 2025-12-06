import React from 'react'

interface Props {
  projectName: string
  maxColors: number
  projectId: number | null
  onProjectNameChange: (name: string) => void
  onMaxColorsChange: (count: number) => void
}

export function SettingsPanel({
  projectName,
  maxColors,
  projectId,
  onProjectNameChange,
  onMaxColorsChange,
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
