import React from 'react'

interface Props {
  onDragOver: (e: React.DragEvent<HTMLDivElement>) => void
  onDrop: (e: React.DragEvent<HTMLDivElement>) => void
  onFileSelect: (e: React.ChangeEvent<HTMLInputElement>) => void
}

export function UploadArea({ onDragOver, onDrop, onFileSelect }: Props) {
  return (
    <div className="upload-area" onDragOver={onDragOver} onDrop={onDrop}>
      <input
        type="file"
        id="file-input"
        className="file-input"
        accept="image/jpeg,image/png,image/webp"
        aria-label="Choose source image"
        onChange={onFileSelect}
      />
      <label htmlFor="file-input" className="upload-label">
        <h3>Choose a screenshot</h3>
        <p>Drag and drop or click to select</p>
        <p className="upload-hint">JPEG, PNG, WebP (max 5MB)</p>
      </label>
    </div>
  )
}
