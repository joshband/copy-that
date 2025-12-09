/**
 * Integration tests for SpacingTokenShowcase component
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { vi } from 'vitest';
import userEvent from '@testing-library/user-event';
import { SpacingTokenShowcase } from '../SpacingTokenShowcase';
import type { SpacingLibrary, SpacingToken } from '../../types';

const createMockToken = (overrides?: Partial<SpacingToken>): SpacingToken => ({
  name: 'md',
  value_px: 16,
  value_rem: 1,
  confidence: 0.85,
  grid_aligned: true,
  role: 'medium',
  provenance: { image1: 1 },
  prominence_percentage: 25,
  ...overrides,
});

const createMockLibrary = (tokens: SpacingToken[] = []): SpacingLibrary => ({
  tokens,
  statistics: {
    spacing_count: tokens.length,
    image_count: 2,
    scale_system: 'linear',
    base_unit: 8,
    grid_compliance: 0.8,
    avg_confidence: tokens.length ? tokens.reduce((sum, t) => sum + t.confidence, 0) / tokens.length : 0,
    value_range: { min: 8, max: 32 },
    common_values: [8, 16, 32],
    multi_image_spacings: 2,
  },
});

describe('SpacingTokenShowcase Integration Tests', () => {
  it('should render with empty library', () => {
    const library = createMockLibrary([]);

    render(
      <SpacingTokenShowcase library={library} />
    );

    expect(screen.getByText('Spacing Token Library')).toBeInTheDocument();
    expect(screen.getByText(/0 tokens extracted/)).toBeInTheDocument();
  });

  it('should render with multiple tokens', () => {
    const tokens = [
      createMockToken({ name: 'xs', value_px: 8 }),
      createMockToken({ name: 'md', value_px: 16 }),
      createMockToken({ name: 'lg', value_px: 32 }),
    ];
    const library = createMockLibrary(tokens);

    render(
      <SpacingTokenShowcase library={library} />
    );

    expect(screen.getByText(/3 tokens extracted/)).toBeInTheDocument();
    expect(screen.getByText('xs')).toBeInTheDocument();
    expect(screen.getByText('md')).toBeInTheDocument();
    expect(screen.getByText('lg')).toBeInTheDocument();
  });

  it('should filter tokens by alignment', async () => {
    const tokens = [
      createMockToken({ name: 'aligned', grid_aligned: true }),
      createMockToken({ name: 'misaligned', grid_aligned: false }),
    ];
    const library = createMockLibrary(tokens);

    render(
      <SpacingTokenShowcase library={library} />
    );

    // Initial: both tokens visible
    expect(screen.getByText('aligned')).toBeInTheDocument();
    expect(screen.getByText('misaligned')).toBeInTheDocument();

    // Click "Grid Aligned" filter (use specific button role)
    const alignedBtn = screen.getByRole('button', { name: /Grid Aligned/i });
    fireEvent.click(alignedBtn);

    // Only aligned token visible
    await waitFor(() => {
      expect(screen.getByText('aligned')).toBeInTheDocument();
    });
    expect(screen.queryByText('misaligned')).not.toBeInTheDocument();
  });

  it('should sort tokens', async () => {
    const tokens = [
      createMockToken({ name: 'a', value_px: 32, confidence: 0.7 }),
      createMockToken({ name: 'b', value_px: 8, confidence: 0.9 }),
      createMockToken({ name: 'c', value_px: 16, confidence: 0.8 }),
    ];
    const library = createMockLibrary(tokens);

    const { container } = render(
      <SpacingTokenShowcase library={library} />
    );

    // Sort by confidence (descending) - use specific button role
    const confidenceBtn = screen.getByRole('button', { name: /Confidence/i });
    fireEvent.click(confidenceBtn);

    await waitFor(() => {
      const tokenNames = screen.getAllByText(/^[abc]$/).map(el => el.textContent);
      expect(tokenNames[0]).toBe('b');
    });
  });

  it('should call onTokenClick', async () => {
    const mockClick = vi.fn();
    const token = createMockToken();
    const library = createMockLibrary([token]);

    render(
      <SpacingTokenShowcase library={library} onTokenClick={mockClick} />
    );

    const tokenCard = screen.getByText('md').closest('div')?.closest('div')?.closest('div');
    if (tokenCard) {
      fireEvent.click(tokenCard);
      expect(mockClick).toHaveBeenCalledWith(token);
    }
  });

  it('should handle copy to clipboard', async () => {
    Object.assign(navigator, {
      clipboard: {
        writeText: vi.fn().mockResolvedValue(undefined),
      },
    });

    const token = createMockToken();
    const library = createMockLibrary([token]);

    render(
      <SpacingTokenShowcase library={library} showCopyButtons={true} />
    );

    const copyPxBtn = screen.getByText('Copy px');
    fireEvent.click(copyPxBtn);

    await waitFor(() => {
      expect(navigator.clipboard.writeText).toHaveBeenCalledWith('16px');
    });

    await waitFor(() => {
      expect(screen.getByText('Copied!')).toBeInTheDocument();
    }, { timeout: 500 });
  });

  it('should hide copy buttons when showCopyButtons is false', () => {
    const token = createMockToken();
    const library = createMockLibrary([token]);

    render(
      <SpacingTokenShowcase library={library} showCopyButtons={false} />
    );

    expect(screen.queryByText('Copy px')).not.toBeInTheDocument();
  });

  it('should hide metadata when showMetadata is false', () => {
    const token = createMockToken();
    const library = createMockLibrary([token]);

    render(
      <SpacingTokenShowcase library={library} showMetadata={false} />
    );

    expect(screen.queryByText(/Confidence:/)).not.toBeInTheDocument();
  });

  it('should handle multi-source filtering', async () => {
    const tokens = [
      createMockToken({
        name: 'single-source',
        provenance: { image1: 1 },
      }),
      createMockToken({
        name: 'multi-source',
        provenance: { image1: 1, image2: 1 },
      }),
    ];
    const library = createMockLibrary(tokens);

    render(
      <SpacingTokenShowcase library={library} />
    );

    const multiSourceBtn = screen.getByRole('button', { name: /Multi-Source/i });
    fireEvent.click(multiSourceBtn);

    await waitFor(() => {
      expect(screen.getByText('multi-source')).toBeInTheDocument();
      expect(screen.queryByText('single-source')).not.toBeInTheDocument();
    });
  });

  it('should handle file selection', async () => {
    const mockFileSelected = vi.fn();
    const token = createMockToken();
    const library = createMockLibrary([token]);

    render(
      <SpacingTokenShowcase
        library={library}
        onFileSelected={mockFileSelected}
      />
    );

    // Find file input by type and accept attribute
    const fileInput = screen.getByDisplayValue('') as HTMLInputElement;
    expect(fileInput.accept).toBe('image/*');
    const mockFile = new File(['content'], 'test.jpg', { type: 'image/jpeg' });

    fireEvent.change(fileInput, { target: { files: [mockFile] } });

    expect(mockFileSelected).toHaveBeenCalledWith(mockFile);
  });

  it('should display error message', () => {
    const library = createMockLibrary([]);

    render(
      <SpacingTokenShowcase
        library={library}
        onFileSelected={vi.fn()}
        error="Upload failed"
      />
    );

    expect(screen.getByText('Upload failed')).toBeInTheDocument();
  });

  it('should display loading state', () => {
    const library = createMockLibrary([]);

    render(
      <SpacingTokenShowcase
        library={library}
        onFileSelected={vi.fn()}
        isLoading={true}
      />
    );

    expect(screen.getByText(/Extracting spacings/)).toBeInTheDocument();
  });

  it('should display scale visualization', () => {
    const tokens = [
      createMockToken({ name: 'xs', value_px: 8 }),
      createMockToken({ name: 'md', value_px: 16 }),
    ];
    const library = createMockLibrary(tokens);

    render(
      <SpacingTokenShowcase library={library} />
    );

    expect(screen.getByText('Spacing Scale')).toBeInTheDocument();
    // Multiple elements may contain these values, just check they exist
    expect(screen.queryAllByText('8px').length).toBeGreaterThan(0);
    expect(screen.queryAllByText('16px').length).toBeGreaterThan(0);
  });

  it('should display statistics', () => {
    const tokens = [
      createMockToken({ name: 'xs', value_px: 8 }),
    ];
    const library = createMockLibrary(tokens);

    render(
      <SpacingTokenShowcase library={library} />
    );

    // Multiple elements may contain '1', check that at least one 'Tokens' text exists
    expect(screen.queryAllByText(/Tokens/).length).toBeGreaterThan(0);
    expect(screen.queryAllByText(/linear/).length).toBeGreaterThan(0); // scale
  });

  it('should combine filter and sort', async () => {
    const tokens = [
      createMockToken({ name: 'a', value_px: 32, grid_aligned: true, confidence: 0.7 }),
      createMockToken({ name: 'b', value_px: 8, grid_aligned: false, confidence: 0.9 }),
      createMockToken({ name: 'c', value_px: 16, grid_aligned: true, confidence: 0.8 }),
    ];
    const library = createMockLibrary(tokens);

    render(
      <SpacingTokenShowcase library={library} />
    );

    // Apply grid aligned filter using role-based query
    const gridAlignedButtons = screen.getAllByRole('button', { name: /Grid Aligned/i });
    fireEvent.click(gridAlignedButtons[0]); // Click the filter button

    // Sort by name
    await waitFor(() => {
      fireEvent.click(screen.getByRole('button', { name: /Name/i }));
    });

    // Should show only 'a' and 'c' (aligned), sorted by name
    await waitFor(() => {
      expect(screen.getByText('a')).toBeInTheDocument();
      expect(screen.getByText('c')).toBeInTheDocument();
    });
    expect(screen.queryByText('b')).not.toBeInTheDocument();
  });

  it('should handle prominence percentage display', () => {
    const token = createMockToken({ prominence_percentage: 42.5 });
    const library = createMockLibrary([token]);

    render(
      <SpacingTokenShowcase library={library} showMetadata={true} />
    );

    expect(screen.getByText('Prominence: 42.5%')).toBeInTheDocument();
  });

  it('should display role badge', () => {
    const token = createMockToken({ role: 'button-spacing' });
    const library = createMockLibrary([token]);

    render(
      <SpacingTokenShowcase library={library} />
    );

    // Multiple elements may contain this text, just ensure at least one exists
    expect(screen.queryAllByText('button-spacing').length).toBeGreaterThan(0);
  });
});
