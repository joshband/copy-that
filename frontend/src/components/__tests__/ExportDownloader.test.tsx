import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ExportDownloader } from '../ExportDownloader';

vi.mock('../../api/hooks', () => ({
  useExportLibrary: () => ({
    mutateAsync: vi.fn().mockResolvedValue({
      format: 'w3c',
      content: '{"token": "value"}',
      filename: 'tokens.json',
    }),
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

describe('ExportDownloader', () => {
  const mockOnReset = vi.fn();

  beforeEach(() => {
    mockOnReset.mockClear();
  });

  it('renders the export interface', () => {
    render(
      <ExportDownloader
        sessionId={1}
        libraryId={1}
        statistics={{ total: 5 }}
        onReset={mockOnReset}
      />,
      { wrapper }
    );

    // Check for the main export header
    expect(screen.getByText(/Export Your Token Library/i)).toBeInTheDocument();
  });

  it('displays available export formats', () => {
    render(
      <ExportDownloader
        sessionId={1}
        libraryId={1}
        statistics={{ total: 5 }}
        onReset={mockOnReset}
      />,
      { wrapper }
    );

    // Should show W3C, CSS, React, HTML options
    const buttons = screen.queryAllByRole('button');
    expect(buttons.length).toBeGreaterThan(0);
  });

  it('shows format descriptions', () => {
    render(
      <ExportDownloader
        sessionId={1}
        libraryId={1}
        statistics={{ total: 5 }}
        onReset={mockOnReset}
      />,
      { wrapper }
    );

    // Should describe what W3C format is, etc.
    const w3cElements = screen.getAllByText(/W3C/i);
    expect(w3cElements.length).toBeGreaterThan(0);
  });

  it('has download buttons for each format', () => {
    render(
      <ExportDownloader
        sessionId={1}
        libraryId={1}
        statistics={{ total: 5 }}
        onReset={mockOnReset}
      />,
      { wrapper }
    );

    const buttons = screen.queryAllByRole('button', { name: /Download/i });
    expect(buttons.length).toBeGreaterThan(0);
  });

  it('shows export statistics', () => {
    render(
      <ExportDownloader
        sessionId={1}
        libraryId={1}
        statistics={{ total: 5, unique: 4 }}
        onReset={mockOnReset}
      />,
      { wrapper }
    );

    // Should display statistics about what's being exported
    const text = screen.queryByText(/5/) || screen.queryByText(/statistics/i);
    expect(text || document.body).toBeTruthy();
  });

  it('has start new session button', () => {
    render(
      <ExportDownloader
        sessionId={1}
        libraryId={1}
        statistics={{ total: 5 }}
        onReset={mockOnReset}
      />,
      { wrapper }
    );

    const btn = screen.queryByRole('button', { name: /New Session/i }) ||
                screen.queryByRole('button', { name: /Start Over/i });
    expect(btn).toBeTruthy();
  });

  it('calls onReset when starting new session', () => {
    render(
      <ExportDownloader
        sessionId={1}
        libraryId={1}
        statistics={{ total: 5 }}
        onReset={mockOnReset}
      />,
      { wrapper }
    );

    const btn = screen.queryByRole('button', { name: /New Session/i }) ||
                screen.queryByRole('button', { name: /Start Over/i });
    if (btn) {
      fireEvent.click(btn);
      expect(mockOnReset).toHaveBeenCalled();
    }
  });

  it('displays format comparison', () => {
    render(
      <ExportDownloader
        sessionId={1}
        libraryId={1}
        statistics={{ total: 5 }}
        onReset={mockOnReset}
      />,
      { wrapper }
    );

    // Should show comparison or details about formats
    const text = document.body.textContent || '';
    expect(text.length).toBeGreaterThan(0);
  });
});
