/**
 * ColorTokenPicker
 *
 * A dropdown component for selecting color tokens to link to shadow layers
 * Phase 2: Color Linking implementation
 */

import React, { useState, useRef, useEffect } from 'react'
import type { ColorTokenOption } from '../../../../../store/shadowStore'
import './ColorTokenPicker.css'

interface Props {
  /** Currently selected color token ID (empty string if none) */
  selectedColorId: string
  /** Available color tokens to choose from */
  availableColors: ColorTokenOption[]
  /** Current hex color (shown when no token linked) */
  currentHex: string
  /** Callback when a color token is selected */
  onSelectColor: (colorId: string) => void
  /** Callback when unlinking the color token */
  onUnlink: () => void
  /** Optional: disable the picker */
  disabled?: boolean
}

export const ColorTokenPicker: React.FC<Props> = ({
  selectedColorId,
  availableColors,
  currentHex,
  onSelectColor,
  onUnlink,
  disabled = false,
}) => {
  const [isOpen, setIsOpen] = useState(false)
  const [searchTerm, setSearchTerm] = useState('')
  const containerRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  // Find the selected color
  const selectedColor = availableColors.find((c) => c.id === selectedColorId)
  const displayHex = selectedColor?.hex || currentHex

  // Filter colors by search term
  const filteredColors = availableColors.filter((color) => {
    const term = searchTerm.toLowerCase()
    return (
      color.id.toLowerCase().includes(term) ||
      color.hex.toLowerCase().includes(term) ||
      (color.name && color.name.toLowerCase().includes(term))
    )
  })

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setIsOpen(false)
        setSearchTerm('')
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  // Focus input when dropdown opens
  useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus()
    }
  }, [isOpen])

  const handleToggle = () => {
    if (!disabled) {
      setIsOpen(!isOpen)
      if (!isOpen) {
        setSearchTerm('')
      }
    }
  }

  const handleSelectColor = (colorId: string) => {
    onSelectColor(colorId)
    setIsOpen(false)
    setSearchTerm('')
  }

  const handleUnlink = (e: React.MouseEvent) => {
    e.stopPropagation()
    onUnlink()
    setIsOpen(false)
    setSearchTerm('')
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Escape') {
      setIsOpen(false)
      setSearchTerm('')
    }
  }

  return (
    <div
      className={`color-token-picker ${disabled ? 'disabled' : ''}`}
      ref={containerRef}
      onKeyDown={handleKeyDown}
    >
      {/* Trigger Button */}
      <button
        type="button"
        className={`color-picker-trigger ${isOpen ? 'open' : ''} ${selectedColorId ? 'linked' : ''}`}
        onClick={handleToggle}
        disabled={disabled}
        title={selectedColorId ? `Linked to: ${selectedColorId}` : 'Click to link a color token'}
      >
        <span
          className="color-preview-swatch"
          style={{ backgroundColor: displayHex }}
        />
        <span className="color-info">
          {selectedColorId ? (
            <>
              <span className="token-name">{selectedColor?.name || selectedColorId}</span>
              <span className="token-ref">{`{${selectedColorId}}`}</span>
            </>
          ) : (
            <>
              <span className="hex-value">{currentHex}</span>
              <span className="link-hint">Link to token</span>
            </>
          )}
        </span>
        <span className="chevron">{isOpen ? '\u25B2' : '\u25BC'}</span>
      </button>

      {/* Dropdown */}
      {isOpen && (
        <div className="color-picker-dropdown">
          {/* Search Input */}
          <div className="color-picker-search">
            <input
              ref={inputRef}
              type="text"
              placeholder="Search colors..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="color-search-input"
            />
          </div>

          {/* Unlink Option (if linked) */}
          {selectedColorId && (
            <button
              type="button"
              className="color-option unlink-option"
              onClick={handleUnlink}
            >
              <span className="unlink-icon">\u2716</span>
              <span>Unlink (use raw hex)</span>
            </button>
          )}

          {/* Color Options */}
          <div className="color-options-list">
            {filteredColors.length === 0 ? (
              <div className="no-colors-message">
                {searchTerm ? 'No matching colors found' : 'No color tokens available'}
              </div>
            ) : (
              filteredColors.map((color) => (
                <button
                  key={color.id}
                  type="button"
                  className={`color-option ${color.id === selectedColorId ? 'selected' : ''}`}
                  onClick={() => handleSelectColor(color.id)}
                >
                  <span
                    className="option-swatch"
                    style={{ backgroundColor: color.hex }}
                  />
                  <span className="option-info">
                    <span className="option-name">{color.name || color.id}</span>
                    <span className="option-hex">{color.hex}</span>
                  </span>
                  {color.id === selectedColorId && (
                    <span className="check-mark">\u2713</span>
                  )}
                </button>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  )
}

export default ColorTokenPicker
