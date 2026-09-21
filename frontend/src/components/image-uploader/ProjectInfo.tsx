import React from 'react'

interface Props {
  projectId: number | null
}

export function ProjectInfo({ projectId }: Props) {
  if (!projectId) return null

  return (
    <div className="project-info">
      <p>
        Project ID: <code>{projectId}</code>
      </p>
    </div>
  )
}
