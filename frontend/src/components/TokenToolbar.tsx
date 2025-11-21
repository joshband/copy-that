/**
 * TokenToolbar
 *
 * Generic toolbar for token filtering, sorting, and view mode selection
 * Renders controls based on registry schema
 */

import React from 'react';
import { useTokenStore, ViewMode, SortOption } from '../store/tokenStore';
import { tokenTypeRegistry } from '../config/tokenTypeRegistry';
import './TokenToolbar.css';

export const TokenToolbar: React.FC = () => {
  const {
    tokenType,
    viewMode,
    sortBy,
    filters,
    setViewMode,
    setSortBy,
    setFilter,
    clearFilters,
  } = useTokenStore();

  const schema = tokenTypeRegistry[tokenType];
  if (!schema) return null;

  const hasActiveFilters = Object.values(filters).some(v => v);

  return (
    <div className="token-toolbar">
      {/* View Mode */}
      <div className="token-toolbar__group">
        <label className="token-toolbar__label">View:</label>
        <div className="token-toolbar__button-group">
          {(['grid', 'list', 'table'] as ViewMode[]).map(mode => (
            <button
              key={mode}
              className={`token-toolbar__btn ${viewMode === mode ? 'active' : ''}`}
              onClick={() => setViewMode(mode)}
              title={`${mode} view`}
            >
              {mode === 'grid' && '⊞'}
              {mode === 'list' && '☰'}
              {mode === 'table' && '⊞⊞'}
            </button>
          ))}
        </div>
      </div>

      {/* Sorting */}
      <div className="token-toolbar__group">
        <label htmlFor="sort" className="token-toolbar__label">Sort:</label>
        <select
          id="sort"
          className="token-toolbar__select"
          value={sortBy}
          onChange={e => setSortBy(e.target.value as SortOption)}
        >
          <option value="hue">Hue</option>
          <option value="name">Name</option>
          <option value="confidence">Confidence</option>
          {tokenType === 'color' && (
            <>
              <option value="temperature">Temperature</option>
              <option value="saturation">Saturation</option>
            </>
          )}
        </select>
      </div>

      {/* Filters */}
      {schema.filters.length > 0 && (
        <div className="token-toolbar__group">
          <label className="token-toolbar__label">Filters:</label>
          <div className="token-toolbar__filters">
            {schema.filters.map(filter => (
              <select
                key={filter.key}
                className="token-toolbar__select"
                value={filters[filter.key] || ''}
                onChange={e => setFilter(filter.key, e.target.value)}
                title={filter.label}
              >
                <option value="">{filter.label}</option>
                {filter.values.map(value => (
                  <option key={value} value={value}>
                    {value}
                  </option>
                ))}
              </select>
            ))}
            {hasActiveFilters && (
              <button
                className="token-toolbar__clear-btn"
                onClick={clearFilters}
                title="Clear all filters"
              >
                ✕ Clear
              </button>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default TokenToolbar;
