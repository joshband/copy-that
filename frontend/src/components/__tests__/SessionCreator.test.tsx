import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { SessionCreator } from '../SessionCreator';

// Mock the API hooks
vi.mock('../../api/hooks', () => ({
  useCreateSession: () => ({
    mutateAsync: vi.fn().mockResolvedValue({
      session_id: 1,
      project_id: 1,
      session_name: 'Test Session',
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

describe('SessionCreator', () => {
  const mockOnSessionCreated = vi.fn();

  beforeEach(() => {
    mockOnSessionCreated.mockClear();
    vi.clearAllMocks();
  });

  it('renders the session creator form', () => {
    render(<SessionCreator onSessionCreated={mockOnSessionCreated} />, { wrapper });

    expect(screen.getByText('Create Extraction Session')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('e.g., Brand Colors - Q1 2025')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('What are you extracting tokens from?')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Create Session & Continue/i })).toBeInTheDocument();
  });

  it('displays project selector dropdown', () => {
    render(<SessionCreator onSessionCreated={mockOnSessionCreated} />, { wrapper });

    const select = screen.getByDisplayValue('Default Project');
    expect(select).toBeInTheDocument();
  });

  it('shows error when session name is empty', async () => {
    render(<SessionCreator onSessionCreated={mockOnSessionCreated} />, { wrapper });

    const button = screen.getByRole('button', { name: /Create Session & Continue/i });
    expect(button).toBeDisabled();
  });

  it('enables create button when session name is filled', async () => {
    render(<SessionCreator onSessionCreated={mockOnSessionCreated} />, { wrapper });

    const input = screen.getByPlaceholderText('e.g., Brand Colors - Q1 2025');
    fireEvent.change(input, { target: { value: 'My Test Session' } });

    const button = screen.getByRole('button', { name: /Create Session & Continue/i });
    expect(button).not.toBeDisabled();
  });

  it('accepts session description input', () => {
    render(<SessionCreator onSessionCreated={mockOnSessionCreated} />, { wrapper });

    const textarea = screen.getByPlaceholderText('What are you extracting tokens from?');
    fireEvent.change(textarea, { target: { value: 'Test description' } });

    expect(textarea).toHaveValue('Test description');
  });

  it('displays info panel with workflow explanation', () => {
    render(<SessionCreator onSessionCreated={mockOnSessionCreated} />, { wrapper });

    expect(screen.getByText('What is a Session?')).toBeInTheDocument();
    expect(screen.getByText(/automatic color deduplication/i)).toBeInTheDocument();
    expect(screen.getByText(/export in multiple formats/i)).toBeInTheDocument();
  });

  it('has default project selected', () => {
    render(<SessionCreator onSessionCreated={mockOnSessionCreator} />, { wrapper });

    const select = screen.getByDisplayValue('Default Project') as HTMLSelectElement;
    expect(select.value).toBe('1');
  });

  it('allows changing selected project', () => {
    render(<SessionCreator onSessionCreated={mockOnSessionCreated} />, { wrapper });

    const select = screen.getByDisplayValue('Default Project') as HTMLSelectElement;
    fireEvent.change(select, { target: { value: '2' } });

    expect(select.value).toBe('2');
  });

  it('shows New Project button', () => {
    render(<SessionCreator onSessionCreated={mockOnSessionCreated} />, { wrapper });

    const newProjectBtn = screen.getByRole('button', { name: /New Project/i });
    expect(newProjectBtn).toBeInTheDocument();
  });
});
