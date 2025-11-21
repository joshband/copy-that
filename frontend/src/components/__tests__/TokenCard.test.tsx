/**
 * TokenCard Tests
 *
 * Tests for the generic TokenCard wrapper component
 * Should work with any token type via registry schema
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, fireEvent, within } from '@testing-library/react';
import { TokenCard } from '../TokenCard';
import { ColorToken } from '../../types';
import { useTokenStore } from '../../store/tokenStore';

// Mock the registry
vi.mock('../../config/tokenTypeRegistry', () => ({
  tokenTypeRegistry: {
    color: {
      name: 'Color',
      icon: () => <div>🎨</div>,
      primaryVisual: ({ token }: { token: Partial<ColorToken> }) => (
        <div data-testid="primary-visual">{token.name}</div>
      ),
      formatTabs: [
        {
          name: 'RGB',
          component: () => <div data-testid="rgb-content">RGB Format</div>,
        },
      ],
      playgroundTabs: [
        {
          name: 'Adjuster',
          component: () => <div data-testid="adjuster-content">Color Adjuster</div>,
        },
      ],
      filters: [
        { key: 'temperature', label: 'Temperature', values: ['warm', 'cool'] },
      ],
    },
  },
}));

describe('TokenCard', () => {
  const mockToken: ColorToken = {
    id: '1',
    hex: '#FF0000',
    rgb: 'rgb(255, 0, 0)',
    name: 'Red',
    confidence: 0.95,
  };

  beforeEach(() => {
    // Reset store
    useTokenStore.setState({
      tokens: [mockToken],
      selectedTokenId: null,
      editingToken: null,
    });
  });

  describe('Rendering', () => {
    it('should render token header with name and hex', () => {
      render(<TokenCard token={mockToken} tokenType="color" />);

      // Card exists
      expect(screen.getByTestId('token-card')).toBeInTheDocument();
      // Name appears in header and primary-visual
      expect(screen.getAllByText('Red')).toHaveLength(2);
      expect(screen.getByText('#FF0000')).toBeInTheDocument();
    });

    it('should render confidence score', () => {
      render(<TokenCard token={mockToken} tokenType="color" />);

      expect(screen.getByText(/95%/)).toBeInTheDocument();
    });

    it('should render primary visual component', () => {
      render(<TokenCard token={mockToken} tokenType="color" />);

      expect(screen.getByTestId('primary-visual')).toBeInTheDocument();
      expect(screen.getByTestId('primary-visual')).toHaveTextContent('Red');
    });

    it('should render color swatch with hex color', () => {
      render(<TokenCard token={mockToken} tokenType="color" />);

      const swatch = screen.getByTestId('color-swatch');
      expect(swatch).toHaveStyle({ backgroundColor: '#FF0000' });
    });
  });

  describe('Selection', () => {
    it('should select token when clicked', () => {
      render(<TokenCard token={mockToken} tokenType="color" />);
      const card = screen.getByTestId('token-card');

      fireEvent.click(card);

      expect(useTokenStore.getState().selectedTokenId).toBe('1');
    });

    it('should show selected state when token is selected', () => {
      useTokenStore.setState({ selectedTokenId: '1' });

      render(<TokenCard token={mockToken} tokenType="color" />);
      const card = screen.getByTestId('token-card');

      expect(card).toHaveClass('selected');
    });

    it('should deselect token when clicking again', () => {
      useTokenStore.setState({ selectedTokenId: '1' });

      render(<TokenCard token={mockToken} tokenType="color" />);
      const card = screen.getByTestId('token-card');

      fireEvent.click(card);

      expect(useTokenStore.getState().selectedTokenId).toBeNull();
    });
  });

  describe('Expansion', () => {
    it('should be collapsed by default', () => {
      render(<TokenCard token={mockToken} tokenType="color" />);

      expect(screen.queryByTestId('rgb-tab')).not.toBeInTheDocument();
    });

    it('should expand when expand button is clicked', () => {
      render(<TokenCard token={mockToken} tokenType="color" />);
      const expandButton = screen.getByTestId('expand-button');

      fireEvent.click(expandButton);

      expect(screen.getByTestId('rgb-tab')).toBeInTheDocument();
    });

    it('should show format tabs when expanded', () => {
      render(<TokenCard token={mockToken} tokenType="color" />);
      const expandButton = screen.getByTestId('expand-button');

      fireEvent.click(expandButton);

      expect(screen.getByText('RGB')).toBeInTheDocument();
      expect(screen.getByTestId('rgb-tab')).toBeInTheDocument();
    });

    it('should collapse when expand button is clicked again', () => {
      render(<TokenCard token={mockToken} tokenType="color" />);
      const expandButton = screen.getByTestId('expand-button');

      fireEvent.click(expandButton);
      fireEvent.click(expandButton);

      expect(screen.queryByTestId('rgb-tab')).not.toBeInTheDocument();
    });
  });

  describe('Actions', () => {
    it('should edit token when edit button is clicked', () => {
      render(<TokenCard token={mockToken} tokenType="color" />);
      const editButton = screen.getByTestId('edit-button');

      fireEvent.click(editButton);

      expect(useTokenStore.getState().editingToken).toEqual(mockToken);
    });

    it('should delete token when delete button is clicked', () => {
      const { rerender } = render(
        <TokenCard token={mockToken} tokenType="color" />
      );
      const deleteButton = screen.getByTestId('delete-button');

      fireEvent.click(deleteButton);

      expect(useTokenStore.getState().tokens).toHaveLength(0);
    });

    it('should duplicate token when duplicate button is clicked', () => {
      render(<TokenCard token={mockToken} tokenType="color" />);
      const duplicateButton = screen.getByTestId('duplicate-button');

      fireEvent.click(duplicateButton);

      const tokens = useTokenStore.getState().tokens;
      expect(tokens).toHaveLength(2);
      expect(tokens[1]).toMatchObject({
        hex: mockToken.hex,
        rgb: mockToken.rgb,
        confidence: mockToken.confidence,
        name: `${mockToken.name} (copy)`,
        id: expect.any(String),
      });
    });
  });

  describe('Format Tabs', () => {
    it('should render all format tabs when expanded', () => {
      render(<TokenCard token={mockToken} tokenType="color" />);
      const expandButton = screen.getByTestId('expand-button');

      fireEvent.click(expandButton);

      expect(screen.getByText('RGB')).toBeInTheDocument();
    });

    it('should switch between tabs', () => {
      render(<TokenCard token={mockToken} tokenType="color" />);
      const expandButton = screen.getByTestId('expand-button');

      fireEvent.click(expandButton);

      const rgbTab = screen.getByText('RGB');
      fireEvent.click(rgbTab);

      // The tab button should have 'active' class, not the content
      expect(rgbTab).toHaveClass('active');
    });
  });

  describe('Responsive', () => {
    it('should render on mobile', () => {
      const { container } = render(
        <TokenCard token={mockToken} tokenType="color" />
      );

      expect(container.querySelector('.token-card')).toBeInTheDocument();
    });
  });
});
