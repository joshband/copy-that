/**
 * FilterControls sub-component
 * Displays filter and sort buttons
 */

import React from 'react';
import { FilterType, SortType } from './types';
import { styles } from './styles';

interface FilterControlsProps {
  filter: FilterType;
  sortBy: SortType;
  onFilterChange: (filter: FilterType) => void;
  onSortChange: (sort: SortType) => void;
}

export const FilterControls: React.FC<FilterControlsProps> = ({
  filter,
  sortBy,
  onFilterChange,
  onSortChange,
}) => {
  const filterOptions: { value: FilterType; label: string }[] = [
    { value: 'all', label: 'All' },
    { value: 'aligned', label: 'Grid Aligned' },
    { value: 'misaligned', label: 'Off Grid' },
    { value: 'multi-source', label: 'Multi-Source' },
  ];

  const sortOptions: { value: SortType; label: string }[] = [
    { value: 'value', label: 'Value' },
    { value: 'confidence', label: 'Confidence' },
    { value: 'name', label: 'Name' },
  ];

  return (
    <div style={styles.filterBar}>
      {filterOptions.map((option) => (
        <button
          key={option.value}
          onClick={() => onFilterChange(option.value)}
          style={{
            ...styles.filterButton,
            ...(filter === option.value ? styles.filterButtonActive : {}),
          }}
        >
          {option.label}
        </button>
      ))}
      <span style={{ marginLeft: 'auto', color: '#666', fontSize: '0.8rem' }}>
        Sort by:
      </span>
      {sortOptions.map((option) => (
        <button
          key={option.value}
          onClick={() => onSortChange(option.value)}
          style={{
            ...styles.filterButton,
            ...(sortBy === option.value ? styles.filterButtonActive : {}),
          }}
        >
          {option.label}
        </button>
      ))}
    </div>
  );
};

export default FilterControls;
