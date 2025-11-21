import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { SessionWorkflow } from '../SessionWorkflow';

vi.mock('../SessionCreator', () => ({
  SessionCreator: ({ onSessionCreated }: any) => (
    <div data-testid="session-creator">SessionCreator Mock</div>
  ),
}));

vi.mock('../BatchImageUploader', () => ({
  BatchImageUploader: ({ onExtractionComplete }: any) => (
    <div data-testid="batch-uploader">BatchImageUploader Mock</div>
  ),
}));

vi.mock('../LibraryCurator', () => ({
  LibraryCurator: ({ onCurationComplete }: any) => (
    <div data-testid="curator">LibraryCurator Mock</div>
  ),
}));

vi.mock('../ExportDownloader', () => ({
  ExportDownloader: ({ onReset }: any) => (
    <div data-testid="exporter">ExportDownloader Mock</div>
  ),
}));

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { retry: false },
  },
});

const wrapper = ({ children }: { children: React.ReactNode }) => (
  <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
);

describe('SessionWorkflow', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders the workflow header', () => {
    render(<SessionWorkflow />, { wrapper });

    expect(screen.getByText(/Token Extraction Workflow/i)).toBeInTheDocument();
    expect(screen.getByText(/Extract, aggregate, and export/i)).toBeInTheDocument();
  });

  it('displays step indicators', () => {
    render(<SessionWorkflow />, { wrapper });

    expect(screen.getByText('1')).toBeInTheDocument();
    expect(screen.getByText('2')).toBeInTheDocument();
    expect(screen.getByText('3')).toBeInTheDocument();
    expect(screen.getByText('4')).toBeInTheDocument();
  });

  it('shows step labels', () => {
    render(<SessionWorkflow />, { wrapper });

    expect(screen.getByText('Create Session')).toBeInTheDocument();
    expect(screen.getByText('Extract Colors')).toBeInTheDocument();
    expect(screen.getByText('Curate Tokens')).toBeInTheDocument();
    expect(screen.getByText('Export')).toBeInTheDocument();
  });

  it('starts with session creator step', () => {
    render(<SessionWorkflow />, { wrapper });

    expect(screen.getByTestId('session-creator')).toBeInTheDocument();
    expect(screen.queryByTestId('batch-uploader')).not.toBeInTheDocument();
  });

  it('has initial state with null session and library IDs', () => {
    render(<SessionWorkflow />, { wrapper });

    // Should only show session creator initially
    expect(screen.getByTestId('session-creator')).toBeInTheDocument();
  });

  it('renders without crashing', () => {
    const { container } = render(<SessionWorkflow />, { wrapper });
    expect(container).toBeTruthy();
  });

  it('displays workflow content container', () => {
    render(<SessionWorkflow />, { wrapper });

    const container = document.querySelector('.workflow-content');
    expect(container).toBeTruthy();
  });

  it('displays step indicators container', () => {
    render(<SessionWorkflow />, { wrapper });

    const indicators = document.querySelector('.step-indicator');
    expect(indicators).toBeTruthy();
  });

  it('has proper CSS classes for styling', () => {
    render(<SessionWorkflow />, { wrapper });

    expect(document.querySelector('.session-workflow')).toBeTruthy();
    expect(document.querySelector('.workflow-header')).toBeTruthy();
    expect(document.querySelector('.workflow-steps')).toBeTruthy();
  });

  it('displays emoji in header', () => {
    render(<SessionWorkflow />, { wrapper });

    // Header contains emoji
    const header = screen.getByText(/🎨/);
    expect(header).toBeInTheDocument();
  });
});
