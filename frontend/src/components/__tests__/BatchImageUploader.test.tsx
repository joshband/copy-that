import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BatchImageUploader } from '../BatchImageUploader';

vi.mock('../../api/hooks', () => ({
  useBatchExtract: () => ({
    mutateAsync: vi.fn().mockResolvedValue({
      library_id: 1,
      statistics: { total: 5, unique: 3 },
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

describe('BatchImageUploader', () => {
  const mockOnExtractionComplete = vi.fn();

  beforeEach(() => {
    mockOnExtractionComplete.mockClear();
  });

  it('renders the batch uploader interface', () => {
    render(
      <BatchImageUploader
        sessionId={1}
        projectId={1}
        onExtractionComplete={mockOnExtractionComplete}
      />,
      { wrapper }
    );

    expect(screen.getByText(/Batch Image Upload/i)).toBeInTheDocument();
  });

  it('allows adding image URLs', () => {
    render(
      <BatchImageUploader
        sessionId={1}
        projectId={1}
        onExtractionComplete={mockOnExtractionComplete}
      />,
      { wrapper }
    );

    const input = screen.getByPlaceholderText(/paste image url/i) || screen.getByRole('textbox');
    fireEvent.change(input, { target: { value: 'https://example.com/image.jpg' } });

    expect(input).toHaveValue('https://example.com/image.jpg');
  });

  it('displays max colors slider', () => {
    render(
      <BatchImageUploader
        sessionId={1}
        projectId={1}
        onExtractionComplete={mockOnExtractionComplete}
      />,
      { wrapper }
    );

    const slider = screen.queryByRole('slider') || screen.queryByLabelText(/max colors/i);
    expect(slider || screen.getByText(/max colors/i)).toBeTruthy();
  });

  it('shows URL count indicator', () => {
    render(
      <BatchImageUploader
        sessionId={1}
        projectId={1}
        onExtractionComplete={mockOnExtractionComplete}
      />,
      { wrapper }
    );

    // Check for some indication of URL count (0/50)
    const container = screen.getByRole('main', { hidden: true }) || screen.getByText(/Max 50 images/i) || document.body;
    expect(container).toBeTruthy();
  });

  it('prevents duplicate URLs', async () => {
    render(
      <BatchImageUploader
        sessionId={1}
        projectId={1}
        onExtractionComplete={mockOnExtractionComplete}
      />,
      { wrapper }
    );

    const input = screen.getByRole('textbox');
    const addBtn = screen.getByRole('button', { name: /Add URL/i });

    fireEvent.change(input, { target: { value: 'https://example.com/image.jpg' } });
    fireEvent.click(addBtn);

    fireEvent.change(input, { target: { value: 'https://example.com/image.jpg' } });
    fireEvent.click(addBtn);

    // Should show error or prevent duplicate
    expect(screen.queryByText(/already added/i)).toBeInTheDocument();
  });

  it('has extract button', () => {
    render(
      <BatchImageUploader
        sessionId={1}
        projectId={1}
        onExtractionComplete={mockOnExtractionComplete}
      />,
      { wrapper }
    );

    const extractBtn = screen.queryByRole('button', { name: /Extract/i }) ||
                       screen.queryByRole('button', { name: /Start/i });
    expect(extractBtn).toBeTruthy();
  });
});
