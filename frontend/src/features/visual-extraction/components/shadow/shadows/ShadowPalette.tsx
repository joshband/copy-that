/**
 * ShadowPalette
 *
 * Unified view of all shadow tokens with filtering, search, and batch operations
 * Phase 3: Shadow Palette implementation
 */

import React, { useState, useMemo, useCallback } from 'react'
import { useShadowStore, type ShadowTokenWithMeta } from '../../../../../store/shadowStore'
import { ShadowColorLink } from './ShadowColorLink'
import './ShadowPalette.css'

type ElevationFilter = 'all' | 'subtle' | 'medium' | 'prominent'
type ShadowTypeFilter = 'all' | 'drop' | 'inner' | 'inset'
type ViewMode = 'grid' | 'list'

interface Props {
  /** Optional: Pass shadows directly instead of using store */
  shadows?: ShadowTokenWithMeta[]
  /** Optional: Callback when a shadow is selected */
  onSelectShadow?: (shadow: ShadowTokenWithMeta) => void
  /** Optional: Enable multi-select mode */
  enableMultiSelect?: boolean
  /** Optional: Show color linking UI */
  showColorLinking?: boolean
}

export const ShadowPalette: React.FC<Props> = ({
  shadows: propShadows,
  onSelectShadow,
  enableMultiSelect = true,
  showColorLinking = true,
}) => {
  // Store
  const {
    shadows: storeShadows,
    availableColors,
    selectedShadowId,
    selectShadow,
    linkColorToShadow,
    unlinkColorFromShadow,
  } = useShadowStore()

  // Use prop shadows or store shadows
  const allShadows = propShadows || storeShadows

  // Local state
  const [searchTerm, setSearchTerm] = useState('')
  const [elevationFilter, setElevationFilter] = useState<ElevationFilter>('all')
  const [shadowTypeFilter, setShadowTypeFilter] = useState<ShadowTypeFilter>('all')
  const [viewMode, setViewMode] = useState<ViewMode>('grid')
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set())
  const [copiedId, setCopiedId] = useState<string | null>(null)

  // Determine elevation from shadow properties
  const getElevation = useCallback((shadow: ShadowTokenWithMeta): ElevationFilter => {
    // Use semantic role if available
    if (shadow.semanticRole) {
      const role = shadow.semanticRole.toLowerCase()
      if (role.includes('subtle') || role.includes('sm') || role.includes('small')) return 'subtle'
      if (role.includes('prominent') || role.includes('lg') || role.includes('large')) return 'prominent'
      return 'medium'
    }

    // Infer from blur radius
    const rawValue = shadow.raw.$value
    const layer = Array.isArray(rawValue) ? rawValue[0] : rawValue
    const blur = typeof layer?.blur === 'object' ? layer.blur.value : layer?.blur || 0

    if (blur <= 4) return 'subtle'
    if (blur >= 16) return 'prominent'
    return 'medium'
  }, [])

  // Determine shadow type
  const getShadowType = useCallback((shadow: ShadowTokenWithMeta): ShadowTypeFilter => {
    if (shadow.shadowType) {
      const type = shadow.shadowType.toLowerCase()
      if (type.includes('inner') || type.includes('inset')) return 'inner'
      return 'drop'
    }

    // Check for inset in raw value
    const rawValue = shadow.raw.$value
    const layer = Array.isArray(rawValue) ? rawValue[0] : rawValue
    if ((layer as any)?.inset) return 'inner'

    return 'drop'
  }, [])

  // Filter shadows
  const filteredShadows = useMemo(() => {
    return allShadows.filter((shadow) => {
      // Search filter
      if (searchTerm) {
        const term = searchTerm.toLowerCase()
        const nameMatch = (shadow.name || shadow.id).toLowerCase().includes(term)
        const typeMatch = (shadow.shadowType || '').toLowerCase().includes(term)
        const roleMatch = (shadow.semanticRole || '').toLowerCase().includes(term)
        if (!nameMatch && !typeMatch && !roleMatch) return false
      }

      // Elevation filter
      if (elevationFilter !== 'all') {
        if (getElevation(shadow) !== elevationFilter) return false
      }

      // Shadow type filter
      if (shadowTypeFilter !== 'all') {
        const type = getShadowType(shadow)
        if (shadowTypeFilter === 'inset') {
          if (type !== 'inner') return false
        } else if (type !== shadowTypeFilter) {
          return false
        }
      }

      return true
    })
  }, [allShadows, searchTerm, elevationFilter, shadowTypeFilter, getElevation, getShadowType])

  // Get shadow CSS string for preview
  const getShadowStyle = useCallback((shadow: ShadowTokenWithMeta): string => {
    const rawValue = shadow.raw.$value
    const layer = Array.isArray(rawValue) ? rawValue[0] : rawValue
    if (!layer) return 'none'

    const x = typeof layer.x === 'object' ? layer.x.value : layer.x || 0
    const y = typeof layer.y === 'object' ? layer.y.value : layer.y || 0
    const blur = typeof layer.blur === 'object' ? layer.blur.value : layer.blur || 0
    const spread = typeof layer.spread === 'object' ? layer.spread.value : layer.spread || 0

    // Get color from linked color or original
    let color = shadow.originalColors[0] || '#000000'
    if (shadow.linkedColorIds[0]) {
      const linkedColor = availableColors.find((c) => c.id === shadow.linkedColorIds[0])
      if (linkedColor) color = linkedColor.hex
    }

    const inset = (layer as any)?.inset ? 'inset ' : ''
    return `${inset}${x}px ${y}px ${blur}px ${spread}px ${color}`
  }, [availableColors])

  // Handle shadow selection
  const handleSelectShadow = useCallback((shadow: ShadowTokenWithMeta, event: React.MouseEvent) => {
    if (enableMultiSelect && (event.ctrlKey || event.metaKey)) {
      setSelectedIds((prev) => {
        const next = new Set(prev)
        if (next.has(shadow.id)) {
          next.delete(shadow.id)
        } else {
          next.add(shadow.id)
        }
        return next
      })
    } else if (enableMultiSelect && event.shiftKey && selectedIds.size > 0) {
      // Shift-click range selection
      const lastSelected = Array.from(selectedIds).pop()
      const lastIndex = filteredShadows.findIndex((s) => s.id === lastSelected)
      const currentIndex = filteredShadows.findIndex((s) => s.id === shadow.id)
      if (lastIndex !== -1 && currentIndex !== -1) {
        const start = Math.min(lastIndex, currentIndex)
        const end = Math.max(lastIndex, currentIndex)
        const rangeIds = filteredShadows.slice(start, end + 1).map((s) => s.id)
        setSelectedIds(new Set(rangeIds))
      }
    } else {
      setSelectedIds(new Set([shadow.id]))
      selectShadow(shadow.id)
      onSelectShadow?.(shadow)
    }
  }, [enableMultiSelect, selectedIds, filteredShadows, selectShadow, onSelectShadow])

  // Copy shadow CSS
  const handleCopyShadow = useCallback((shadow: ShadowTokenWithMeta, event: React.MouseEvent) => {
    event.stopPropagation()
    const css = getShadowStyle(shadow)
    navigator.clipboard.writeText(`box-shadow: ${css};`)
    setCopiedId(shadow.id)
    setTimeout(() => setCopiedId(null), 2000)
  }, [getShadowStyle])

  // Select all visible
  const handleSelectAll = useCallback(() => {
    setSelectedIds(new Set(filteredShadows.map((s) => s.id)))
  }, [filteredShadows])

  // Clear selection
  const handleClearSelection = useCallback(() => {
    setSelectedIds(new Set())
  }, [])

  // Get elevation badge color
  const getElevationBadgeClass = (elevation: ElevationFilter): string => {
    switch (elevation) {
      case 'subtle': return 'elevation-subtle'
      case 'prominent': return 'elevation-prominent'
      default: return 'elevation-medium'
    }
  }

  // Stats
  const stats = useMemo(() => ({
    total: allShadows.length,
    filtered: filteredShadows.length,
    selected: selectedIds.size,
    linked: allShadows.filter((s) => s.linkedColorIds.some(Boolean)).length,
  }), [allShadows, filteredShadows, selectedIds])

  if (allShadows.length === 0) {
    return (
      <div className="shadow-palette empty">
        <div className="empty-state">
          <div className="empty-icon">&#9728;</div>
          <h3>No Shadows Yet</h3>
          <p>Extract shadows from an image to see them here.</p>
        </div>
      </div>
    )
  }

  return (
    <div className="shadow-palette">
      {/* Header */}
      <div className="palette-header">
        <div className="header-title">
          <h2>Shadow Palette</h2>
          <span className="shadow-count">
            {stats.filtered} of {stats.total} shadows
            {stats.linked > 0 && <span className="linked-count"> ({stats.linked} linked)</span>}
          </span>
        </div>

        {/* View Mode Toggle */}
        <div className="view-toggle">
          <button
            className={`view-btn ${viewMode === 'grid' ? 'active' : ''}`}
            onClick={() => setViewMode('grid')}
            title="Grid view"
          >
            &#9638;
          </button>
          <button
            className={`view-btn ${viewMode === 'list' ? 'active' : ''}`}
            onClick={() => setViewMode('list')}
            title="List view"
          >
            &#9776;
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="palette-filters">
        {/* Search */}
        <div className="search-box">
          <input
            type="text"
            placeholder="Search shadows..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="search-input"
          />
          {searchTerm && (
            <button
              className="clear-search"
              onClick={() => setSearchTerm('')}
              title="Clear search"
            >
              &#10005;
            </button>
          )}
        </div>

        {/* Filter Pills */}
        <div className="filter-pills">
          {/* Elevation Filter */}
          <div className="filter-group">
            <label>Elevation:</label>
            <select
              value={elevationFilter}
              onChange={(e) => setElevationFilter(e.target.value as ElevationFilter)}
              className="filter-select"
            >
              <option value="all">All</option>
              <option value="subtle">Subtle</option>
              <option value="medium">Medium</option>
              <option value="prominent">Prominent</option>
            </select>
          </div>

          {/* Shadow Type Filter */}
          <div className="filter-group">
            <label>Type:</label>
            <select
              value={shadowTypeFilter}
              onChange={(e) => setShadowTypeFilter(e.target.value as ShadowTypeFilter)}
              className="filter-select"
            >
              <option value="all">All</option>
              <option value="drop">Drop Shadow</option>
              <option value="inner">Inner Shadow</option>
            </select>
          </div>
        </div>
      </div>

      {/* Batch Actions (when items selected) */}
      {enableMultiSelect && selectedIds.size > 0 && (
        <div className="batch-actions">
          <span className="selection-info">
            {selectedIds.size} selected
          </span>
          <button className="batch-btn" onClick={handleSelectAll}>
            Select All ({filteredShadows.length})
          </button>
          <button className="batch-btn" onClick={handleClearSelection}>
            Clear Selection
          </button>
        </div>
      )}

      {/* Shadow Grid/List */}
      <div className={`shadow-container ${viewMode}`}>
        {filteredShadows.length === 0 ? (
          <div className="no-results">
            <p>No shadows match your filters.</p>
            <button
              className="reset-filters-btn"
              onClick={() => {
                setSearchTerm('')
                setElevationFilter('all')
                setShadowTypeFilter('all')
              }}
            >
              Reset Filters
            </button>
          </div>
        ) : (
          filteredShadows.map((shadow) => {
            const elevation = getElevation(shadow)
            const shadowType = getShadowType(shadow)
            const isSelected = selectedIds.has(shadow.id) || selectedShadowId === shadow.id
            const style = getShadowStyle(shadow)

            // Get layer values
            const rawValue = shadow.raw.$value
            const layer = Array.isArray(rawValue) ? rawValue[0] : rawValue
            const x = typeof layer?.x === 'object' ? layer.x.value : layer?.x || 0
            const y = typeof layer?.y === 'object' ? layer.y.value : layer?.y || 0
            const blur = typeof layer?.blur === 'object' ? layer.blur.value : layer?.blur || 0
            const spread = typeof layer?.spread === 'object' ? layer.spread.value : layer?.spread || 0
            const opacity = (layer as any)?.opacity ?? 1

            return (
              <div
                key={shadow.id}
                className={`shadow-item ${isSelected ? 'selected' : ''}`}
                onClick={(e) => handleSelectShadow(shadow, e)}
              >
                {/* Preview */}
                <div className="shadow-preview">
                  <div
                    className="preview-box"
                    style={{ boxShadow: style }}
                  />
                </div>

                {/* Info */}
                <div className="shadow-details">
                  <div className="shadow-name">{shadow.name || shadow.id}</div>

                  <div className="shadow-badges">
                    <span className={`badge ${getElevationBadgeClass(elevation)}`}>
                      {elevation}
                    </span>
                    <span className={`badge shadow-type-${shadowType}`}>
                      {shadowType}
                    </span>
                    {shadow.linkedColorIds[0] && (
                      <span className="badge linked-badge">
                        &#128279; Linked
                      </span>
                    )}
                  </div>

                  {viewMode === 'list' && (
                    <div className="shadow-values">
                      <span>X: {x}px</span>
                      <span>Y: {y}px</span>
                      <span>Blur: {blur}px</span>
                      {spread !== 0 && <span>Spread: {spread}px</span>}
                    </div>
                  )}

                  {/* Color Link (in list mode or expanded) */}
                  {showColorLinking && viewMode === 'list' && (
                    <div className="shadow-color-section">
                      <ShadowColorLink
                        layerIndex={0}
                        linkedColorId={shadow.linkedColorIds[0] || ''}
                        currentHex={shadow.originalColors[0] || '#000000'}
                        opacity={opacity}
                        availableColors={availableColors}
                        onLinkColor={(colorId) => linkColorToShadow(shadow.id, 0, colorId)}
                        onUnlinkColor={() => unlinkColorFromShadow(shadow.id, 0)}
                        compact={true}
                      />
                    </div>
                  )}

                  {shadow.confidence !== undefined && (
                    <div className="confidence-indicator">
                      {Math.round((shadow.confidence || 0) * 100)}% confidence
                    </div>
                  )}
                </div>

                {/* Actions */}
                <div className="shadow-actions">
                  <button
                    className="action-btn copy-btn"
                    onClick={(e) => handleCopyShadow(shadow, e)}
                    title="Copy CSS"
                  >
                    {copiedId === shadow.id ? '✓' : '📋'}
                  </button>
                </div>

                {/* Selection Checkbox (multi-select mode) */}
                {enableMultiSelect && (
                  <div className="selection-checkbox">
                    <input
                      type="checkbox"
                      checked={selectedIds.has(shadow.id)}
                      onChange={() => {}}
                      onClick={(e) => e.stopPropagation()}
                    />
                  </div>
                )}
              </div>
            )
          })
        )}
      </div>
    </div>
  )
}

export default ShadowPalette
