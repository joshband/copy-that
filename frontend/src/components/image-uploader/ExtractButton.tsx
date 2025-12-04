import React from 'react'

interface Props {
  disabled: boolean
  onClick: () => void
}

export function ExtractButton({ disabled, onClick }: Props) {
  return (
    <button
      className="extract-btn"
      onClick={onClick}
      disabled={disabled}
      title={disabled ? 'Please select an image first' : 'Ready to extract colors'}
    >
      ✨ Extract Colors
    </button>
  )
}
