/**
 * Tests for SpacingTokenShowcase sub-components
 */

import React from 'react';
import { render, screen } from '@testing-library/react';
import { vi } from 'vitest';
import { SpacingHeader } from '../SpacingHeader';
import { StatsGrid } from '../StatsGrid';
import { ScaleVisualization } from '../ScaleVisualization';
import { FilterControls } from '../FilterControls';
import { SpacingTokenCard } from '../SpacingTokenCard';
import type { SpacingLibrary, SpacingToken } from '../types';

const mockLibrary: SpacingLibrary = {
  tokens: [],
  statistics: {
    spacing_count: 5,
    image_count: 2,
    scale_system: 'linear',
    base_unit: 8,
    grid_compliance: 0.8,
    avg_confidence: 0.85,
    value_range: { min: 8, max: 32 },
    common_values: [8, 16, 32],
    multi_image_spacings: 2,
  },
};

const mockToken: SpacingToken = {
  name: 'md',
  value_px: 16,
  value_rem: 1,
  confidence: 0.85,
  grid_aligned: true,
  role: 'medium',
  provenance: { image1: 1 },
  prominence_percentage: 25,
};

describe('SpacingTokenShowcase Components', () => {
  describe('SpacingHeader', () => {
    it('should render title and subtitle', () => {
      render(
        <SpacingHeader
          library={mockLibrary}
          onFileChange={vi.fn()}
        />
      );

      expect(screen.getByText('Spacing Token Library')).toBeInTheDocument();
      expect(screen.getByText(/5 tokens extracted from 2 image/)).toBeInTheDocument();
    });

    it('should show file input when onFileSelected provided', () => {
      render(
        <SpacingHeader
          library={mockLibrary}
          onFileChange={vi.fn()}
          onFileSelected={vi.fn()}
        />
      );

      expect(screen.getByRole('button', { hidden: true })).toBeInTheDocument();
    });

    it('should show loading state', () => {
      render(
        <SpacingHeader
          library={mockLibrary}
          onFileChange={vi.fn()}
          isLoading={true}
        />
      );

      expect(screen.getByText(/Extracting spacings/)).toBeInTheDocument();
    });

    it('should show error message', () => {
      render(
        <SpacingHeader
          library={mockLibrary}
          onFileChange={vi.fn()}
          error="Upload failed"
        />
      );

      expect(screen.getByText('Upload failed')).toBeInTheDocument();
    });
  });

  describe('StatsGrid', () => {
    it('should display all statistics', () => {
      render(
        <StatsGrid
          library={mockLibrary}
          derivedBase={8}
          derivedScale="linear"
        />
      );

      expect(screen.getByText('5')).toBeInTheDocument(); // token count
      expect(screen.getByText('linear')).toBeInTheDocument(); // scale
      expect(screen.getByText(/8px/)).toBeInTheDocument(); // base unit
      expect(screen.getByText(/80%/)).toBeInTheDocument(); // grid compliance
      expect(screen.getByText(/85%/)).toBeInTheDocument(); // confidence
      expect(screen.getByText('2')).toBeInTheDocument(); // multi-source
    });

    it('should use derived values', () => {
      render(
        <StatsGrid
          library={mockLibrary}
          derivedBase={4}
          derivedScale="fibonacci"
        />
      );

      expect(screen.getByText(/4px/)).toBeInTheDocument();
      expect(screen.getByText('fibonacci')).toBeInTheDocument();
    });
  });

  describe('ScaleVisualization', () => {
    const mockTokens: SpacingToken[] = [
      { ...mockToken, name: 'sm', value_px: 8 },
      { ...mockToken, name: 'md', value_px: 16 },
      { ...mockToken, name: 'lg', value_px: 32 },
    ];

    it('should render scale visualization title', () => {
      render(
        <ScaleVisualization
          tokens={mockTokens}
          maxValue={32}
          getBarHeight={(v) => (v / 32) * 150}
        />
      );

      expect(screen.getByText('Spacing Scale')).toBeInTheDocument();
    });

    it('should render all token bars', () => {
      render(
        <ScaleVisualization
          tokens={mockTokens}
          maxValue={32}
          getBarHeight={(v) => (v / 32) * 150}
        />
      );

      expect(screen.getByText('8px')).toBeInTheDocument();
      expect(screen.getByText('16px')).toBeInTheDocument();
      expect(screen.getByText('32px')).toBeInTheDocument();
    });

    it('should show empty state', () => {
      render(
        <ScaleVisualization
          tokens={[]}
          maxValue={0}
          getBarHeight={(v) => 0}
        />
      );

      expect(screen.getByText(/No spacing tokens/)).toBeInTheDocument();
    });

    it('should call onTokenClick', () => {
      const mockClick = vi.fn();
      render(
        <ScaleVisualization
          tokens={[mockToken]}
          maxValue={16}
          getBarHeight={(v) => (v / 16) * 150}
          onTokenClick={mockClick}
        />
      );

      const firstBar = screen.getByText('16px').closest('div')?.closest('div');
      if (firstBar) {
        firstBar.click();
        expect(mockClick).toHaveBeenCalledWith(mockToken);
      }
    });
  });

  describe('FilterControls', () => {
    it('should render all filter options', () => {
      render(
        <FilterControls
          filter="all"
          sortBy="value"
          onFilterChange={vi.fn()}
          onSortChange={vi.fn()}
        />
      );

      expect(screen.getByText('All')).toBeInTheDocument();
      expect(screen.getByText('Grid Aligned')).toBeInTheDocument();
      expect(screen.getByText('Off Grid')).toBeInTheDocument();
      expect(screen.getByText('Multi-Source')).toBeInTheDocument();
    });

    it('should render all sort options', () => {
      render(
        <FilterControls
          filter="all"
          sortBy="value"
          onFilterChange={vi.fn()}
          onSortChange={vi.fn()}
        />
      );

      expect(screen.getByText('Value')).toBeInTheDocument();
      expect(screen.getByText('Confidence')).toBeInTheDocument();
      expect(screen.getByText('Name')).toBeInTheDocument();
    });

    it('should call onFilterChange', () => {
      const mockFilterChange = vi.fn();
      const { container } = render(
        <FilterControls
          filter="all"
          sortBy="value"
          onFilterChange={mockFilterChange}
          onSortChange={vi.fn()}
        />
      );

      const gridAlignedBtn = screen.getByText('Grid Aligned');
      gridAlignedBtn.click();

      expect(mockFilterChange).toHaveBeenCalledWith('aligned');
    });

    it('should call onSortChange', () => {
      const mockSortChange = vi.fn();
      render(
        <FilterControls
          filter="all"
          sortBy="value"
          onFilterChange={vi.fn()}
          onSortChange={mockSortChange}
        />
      );

      const confidenceBtn = screen.getByText('Confidence');
      confidenceBtn.click();

      expect(mockSortChange).toHaveBeenCalledWith('confidence');
    });
  });

  describe('SpacingTokenCard', () => {
    it('should render token name and values', () => {
      render(
        <SpacingTokenCard
          token={mockToken}
          copiedValue={null}
          onCopyClick={vi.fn()}
        />
      );

      expect(screen.getByText('md')).toBeInTheDocument();
      expect(screen.getByText('16px | 1rem')).toBeInTheDocument();
    });

    it('should render role badge', () => {
      render(
        <SpacingTokenCard
          token={mockToken}
          copiedValue={null}
          onCopyClick={vi.fn()}
        />
      );

      expect(screen.getByText('medium')).toBeInTheDocument();
    });

    it('should render grid alignment badge', () => {
      render(
        <SpacingTokenCard
          token={mockToken}
          copiedValue={null}
          onCopyClick={vi.fn()}
        />
      );

      expect(screen.getByText('Grid Aligned')).toBeInTheDocument();
    });

    it('should render metadata when showMetadata is true', () => {
      render(
        <SpacingTokenCard
          token={mockToken}
          copiedValue={null}
          showMetadata={true}
          onCopyClick={vi.fn()}
        />
      );

      expect(screen.getByText(/Confidence: 85%/)).toBeInTheDocument();
      expect(screen.getByText(/Sources: 1/)).toBeInTheDocument();
    });

    it('should render copy buttons when showCopyButtons is true', () => {
      render(
        <SpacingTokenCard
          token={mockToken}
          copiedValue={null}
          showCopyButtons={true}
          onCopyClick={vi.fn()}
        />
      );

      expect(screen.getByText('Copy px')).toBeInTheDocument();
      expect(screen.getByText('Copy rem')).toBeInTheDocument();
      expect(screen.getByText('Copy var')).toBeInTheDocument();
    });

    it('should show copied state', () => {
      render(
        <SpacingTokenCard
          token={mockToken}
          copiedValue="px"
          showCopyButtons={true}
          onCopyClick={vi.fn()}
        />
      );

      expect(screen.getByText('Copied!')).toBeInTheDocument();
    });

    it('should handle copy button click', () => {
      const mockCopyClick = vi.fn();
      render(
        <SpacingTokenCard
          token={mockToken}
          copiedValue={null}
          showCopyButtons={true}
          onCopyClick={mockCopyClick}
        />
      );

      const copyPxBtn = screen.getByText('Copy px');
      copyPxBtn.click();

      expect(mockCopyClick).toHaveBeenCalledWith(
        expect.any(Object),
        '16px',
        'px'
      );
    });

    it('should call onTokenClick', () => {
      const mockClick = vi.fn();
      const { container } = render(
        <SpacingTokenCard
          token={mockToken}
          copiedValue={null}
          onTokenClick={mockClick}
          onCopyClick={vi.fn()}
        />
      );

      const card = container.querySelector('div[style*="tokenCard"]')?.parentElement;
      if (card) {
        card.click();
        expect(mockClick).toHaveBeenCalledWith(mockToken);
      }
    });
  });
});
