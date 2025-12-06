import React from 'react'

interface Props {
  preview: string | null
  fileName: string | null
}

export function PreviewSection({ preview, fileName }: Props) {
  if (!preview) return null

  return (
    <div className="preview-section">
      <h4>Preview</h4>
      <img src={preview} alt="Preview" className="preview-image" />
      <p className="preview-name">{fileName}</p>
    </div>
  )
}
