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

    expect(screen.getByText(/Upload Images for Batch Extraction/i)).toBeInTheDocument();
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

    const input = screen.getByPlaceholderText('https://example.com/image.jpg');
    fireEvent.change(input, { target: { value: 'https://test.com/image.png' } });

    expect(input).toHaveValue('https://test.com/image.png');
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

    // Check for indication of max URL count
    expect(screen.getByText(/Maximum 50 images/i)).toBeInTheDocument();
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
