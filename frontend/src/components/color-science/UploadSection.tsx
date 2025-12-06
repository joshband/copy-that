import React, { useCallback } from 'react'

interface UploadSectionProps {
  preview: string | null
  isExtracting: boolean
  onFileChange: (e: React.ChangeEvent<HTMLInputElement>) => void
  onDrop: (e: React.DragEvent<HTMLDivElement>) => void
  onExtract: () => void
  selectedFile: File | null
}

export function UploadSection({
  preview,
  isExtracting,
  onFileChange,
  onDrop,
  onExtract,
  selectedFile,
}: UploadSectionProps) {
  return (
    <section className="panel-card upload-section">
      <h2>Upload Image</h2>
      <div
        className={`upload-area ${preview ? 'has-preview' : ''}`}
        onDrop={onDrop}
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
          onChange={onFileChange}
          style={{ display: 'none' }}
        />
      </div>
      <button
        className="extract-btn"
        onClick={() => void onExtract()}
        disabled={isExtracting || !selectedFile}
      >
        {isExtracting ? 'Extracting...' : 'Extract Color Tokens'}
      </button>
    </section>
  )
}
