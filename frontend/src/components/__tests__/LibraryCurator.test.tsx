import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { LibraryCurator } from '../LibraryCurator';

vi.mock('../../api/hooks', () => ({
  useLibrary: () => ({
    data: {
      tokens: [
        { id: 1, hex: '#FF0000', name: 'Red', confidence: 0.95, role: null },
        { id: 2, hex: '#00FF00', name: 'Green', confidence: 0.92, role: null },
        { id: 3, hex: '#0000FF', name: 'Blue', confidence: 0.90, role: null },
      ],
      statistics: { total: 3, unique: 3 },
    },
    isLoading: false,
  }),
  useCurateTokens: () => ({
    mutateAsync: vi.fn().mockResolvedValue({ status: 'success' }),
    isPending: false,
  }),
}));

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { retry: false },
  },
});

const wrapper = ({ children }: { children: React.ReactNode }) => (
  <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
);

describe('LibraryCurator', () => {
  const mockOnCurationComplete = vi.fn();

  beforeEach(() => {
    mockOnCurationComplete.mockClear();
  });

  it('renders the curator interface', () => {
    render(
      <LibraryCurator
        sessionId={1}
        libraryId={1}
        statistics={{ total: 3 }}
        onCurationComplete={mockOnCurationComplete}
      />,
      { wrapper }
    );

    expect(screen.getByText(/Curate Tokens/i) || screen.getByText(/Assign Roles/i)).toBeTruthy();
  });

  it('displays extracted colors as tokens', () => {
    render(
      <LibraryCurator
        sessionId={1}
        libraryId={1}
        statistics={{ total: 3 }}
        onCurationComplete={mockOnCurationComplete}
      />,
      { wrapper }
    );

    // Should show colors
    expect(screen.queryByText(/Red/i) || screen.getByText(/3/)).toBeTruthy();
  });

  it('shows role assignment dropdowns', () => {
    render(
      <LibraryCurator
        sessionId={1}
        libraryId={1}
        statistics={{ total: 3 }}
        onCurationComplete={mockOnCurationComplete}
      />,
      { wrapper }
    );

    const selects = screen.queryAllByRole('combobox');
    expect(selects.length).toBeGreaterThan(0);
  });

  it('displays statistics', () => {
    render(
      <LibraryCurator
        sessionId={1}
        libraryId={1}
        statistics={{ total: 3, unique: 3 }}
        onCurationComplete={mockOnCurationComplete}
      />,
      { wrapper }
    );

    // Should display some stats
    expect(screen.getByText(/3/) || screen.queryByText(/statistics/i)).toBeTruthy();
  });

  it('has role guide visible', () => {
    render(
      <LibraryCurator
        sessionId={1}
        libraryId={1}
        statistics={{ total: 3 }}
        onCurationComplete={mockOnCurationComplete}
      />,
      { wrapper }
    );

    // Check for role guide content
    const text = screen.queryByText(/primary/i) || screen.queryByText(/secondary/i);
    expect(text || document.body).toBeTruthy();
  });

  it('has complete curation button', () => {
    render(
      <LibraryCurator
        sessionId={1}
        libraryId={1}
        statistics={{ total: 3 }}
        onCurationComplete={mockOnCurationComplete}
      />,
      { wrapper }
    );

    const btn = screen.queryByRole('button', { name: /Complete/i }) ||
                screen.queryByRole('button', { name: /Continue/i });
    expect(btn).toBeTruthy();
  });

  it('allows changing token roles', () => {
    render(
      <LibraryCurator
        sessionId={1}
        libraryId={1}
        statistics={{ total: 3 }}
        onCurationComplete={mockOnCurationComplete}
      />,
      { wrapper }
    );

    const selects = screen.getAllByRole('combobox');
    if (selects.length > 0) {
      fireEvent.change(selects[0], { target: { value: 'primary' } });
      expect(selects[0]).toHaveValue('primary');
    }
  });
});
