import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import SessionSelector from '../SessionSelector';
import '@testing-library/jest-dom';

// Mock Response globally
const mockResponse = (body: any, init?: ResponseInit) => {
  return {
    ok: init?.status ? init.status >= 200 && init.status < 300 : true,
    status: init?.status || 200,
    json: async () => body,
    headers: new Map(Object.entries(init?.headers || {})),
  };
};

describe('SessionSelector', () => {
  const mockOnSessionSelect = jest.fn();
  const mockSessions = {
    sessions: [
      { session_id: '1', session_name: 'Test Session 1', timestamp: new Date().toISOString() },
      { session_id: '2', session_name: 'Test Session 2', timestamp: new Date().toISOString() }
    ]
  };

  beforeEach(() => {
    jest.clearAllMocks();
    
    // Mock fetch with proper Response implementation
    global.fetch = jest.fn().mockImplementation(() =>
      Promise.resolve(mockResponse(mockSessions))
    );
  });

  it('shows loading state initially', () => {
    render(<SessionSelector onSessionSelect={mockOnSessionSelect} currentSessionId={null} />);
    expect(screen.getByTestId('loading-spinner')).toBeInTheDocument();
  });

  it('displays sessions after loading', async () => {
    render(<SessionSelector onSessionSelect={mockOnSessionSelect} currentSessionId={null} />);

    await waitFor(() => {
      expect(screen.getByText('Test Session 1')).toBeInTheDocument();
      expect(screen.getByText('Test Session 2')).toBeInTheDocument();
    });
  });

  it('handles session selection', async () => {
    render(<SessionSelector onSessionSelect={mockOnSessionSelect} currentSessionId={null} />);

    await waitFor(() => {
      expect(screen.getByText('Test Session 1')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText('Test Session 1'));
    expect(mockOnSessionSelect).toHaveBeenCalledWith('1');
  });

  it('handles new chat button click', async () => {
    render(<SessionSelector onSessionSelect={mockOnSessionSelect} currentSessionId={null} />);

    await waitFor(() => {
      expect(screen.getByText('New Chat')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText('New Chat'));
    expect(mockOnSessionSelect).toHaveBeenCalledWith(null);
  });

  it('highlights current session', async () => {
    render(<SessionSelector onSessionSelect={mockOnSessionSelect} currentSessionId="1" />);

    await waitFor(() => {
      const sessionButton = screen.getByText('Test Session 1').closest('button');
      expect(sessionButton).toHaveClass('bg-blue-100');
    });
  });

  it('handles fetch error gracefully', async () => {
    // Mock fetch to reject
    global.fetch = jest.fn().mockImplementation(() =>
      Promise.resolve(mockResponse({ error: 'Failed to fetch' }, { status: 500 }))
    );

    render(<SessionSelector onSessionSelect={mockOnSessionSelect} currentSessionId={null} />);

    // Should still render without crashing
    await waitFor(() => {
      expect(screen.getByText('Chat Sessions')).toBeInTheDocument();
    });
  });
}); 