import '@testing-library/jest-dom';
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import ChatPage from '../page';
import { sendChatMessage } from '@/utils/api';
import { AuthProvider } from '@/contexts/AuthContext';
import Cookies from 'js-cookie';

// Mock the API module
jest.mock('@/utils/api', () => ({
    sendChatMessage: jest.fn(),
}));

// Mock js-cookie
jest.mock('js-cookie', () => ({
    get: jest.fn().mockReturnValue('test-token'),
}));

// Mock next/navigation
jest.mock('next/navigation', () => ({
    useRouter: () => ({
        push: jest.fn(),
    }),
}));

const mockResponse = {
    session_id: 'test-session-id',
    query: 'test message',
    response: 'test response',
    session_metadata: {
        emotional_history: [],
        topic_engagement: {},
        suggestion_enabled: true
    }
};

const mockSessions = {
    data: [
        { id: '1', name: 'Test Session 1' },
        { id: '2', name: 'Test Session 2' }
    ]
};

const setupFetchMocks = () => {
    // First call is for pre-chat survey
    global.fetch = jest.fn()
        .mockResolvedValueOnce({
            ok: true,
            json: () => Promise.resolve({ success: true })
        })
        // Second call is for loading sessions
        .mockResolvedValueOnce({
            ok: true,
            json: () => Promise.resolve({ data: mockSessions })
        });
};

const acceptDisclaimer = async () => {
    const acceptButton = screen.getByText('I Understand and Accept');
    await act(async () => {
        fireEvent.click(acceptButton);
    });

    // Wait for the chat interface to be visible
    await waitFor(() => {
        expect(screen.getByPlaceholderText('Type your message...')).toBeInTheDocument();
    });
};

const sendMessage = async (message: string) => {
  const input = screen.getByPlaceholderText(/type your message/i);
  const button = screen.getByText(/send/i);

  await act(async () => {
    fireEvent.change(input, { target: { value: message } });
    fireEvent.click(button);
  });
};

// Create a mock Response class
class MockResponse {
  ok: boolean;
  status: number;
  statusText: string;
  _data: any;

  constructor(data: any, options: any = {}) {
    this.ok = options.ok !== undefined ? options.ok : true;
    this.status = options.status || 200;
    this.statusText = options.statusText || 'OK';
    this._data = data;
  }

  json() {
    return Promise.resolve(this._data);
  }
}

describe('ChatPage', () => {
  beforeEach(() => {
    // Reset all mocks before each test
    jest.clearAllMocks();
    
    // Mock global fetch for sessions and chat responses
    global.fetch = jest.fn().mockImplementation((url) => {
      if (url.includes('/api/sessions')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockSessions)
        });
      }
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve(mockResponse)
      });
    });

    // Mock scrollIntoView
    window.HTMLElement.prototype.scrollIntoView = jest.fn();

    // Mock Cookies.get to return a token
    (Cookies.get as jest.Mock).mockReturnValue('test-token');
  });

  afterEach(() => {
    jest.resetAllMocks();
  });

  it('shows disclaimer modal initially', () => {
    render(<ChatPage />);
    expect(screen.getByText('Important Disclaimer')).toBeInTheDocument();
  });

  it('handles disclaimer acceptance', async () => {
    render(<ChatPage />);
    const acceptButton = screen.getByText('I Understand and Accept');
    
    await act(async () => {
      fireEvent.click(acceptButton);
    });

    await waitFor(() => {
      expect(screen.queryByText('Important Disclaimer')).not.toBeInTheDocument();
    });
  });

  it('handles session selection', async () => {
    render(<AuthProvider><ChatPage /></AuthProvider>);
    
    await acceptDisclaimer();

    // Wait for sessions to load
    await waitFor(() => {
      expect(screen.getByText('Test Session 1')).toBeInTheDocument();
    });

    // Click on a session
    const sessionButton = screen.getByRole('button', { name: /Test Session 1/ });
    await act(async () => {
      fireEvent.click(sessionButton);
    });

    // Verify the session is selected
    expect(sessionButton).toHaveClass('bg-blue-100');
  });

  it('validates empty messages', async () => {
    render(
      <AuthProvider>
        <ChatPage />
      </AuthProvider>
    );

    await acceptDisclaimer();

    // Wait for sessions to load
    await waitFor(() => {
      expect(screen.getByText('Test Session 1')).toBeInTheDocument();
    });

    // Select a session
    fireEvent.click(screen.getByText('Test Session 1'));

    // Get the input and button
    const input = screen.getByPlaceholderText(/type your message/i);
    const button = screen.getByText(/send/i);

    // Initially the button should be disabled
    expect(button).toBeDisabled();

    // Type a space
    fireEvent.change(input, { target: { value: ' ' } });

    // Button should still be disabled for whitespace-only messages
    expect(button).toBeDisabled();

    // Type actual text
    fireEvent.change(input, { target: { value: 'test' } });

    // Button should be enabled
    expect(button).not.toBeDisabled();
  });

  it('validates message length', async () => {
    render(<AuthProvider><ChatPage /></AuthProvider>);
    
    await acceptDisclaimer();

    // Mock chat API call
    global.fetch = jest.fn().mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ error: 'Message is too long' })
    });

    await sendMessage('a'.repeat(1001));
    
    await waitFor(() => {
        expect(screen.getByText(/message is too long/i)).toBeInTheDocument();
    });
  });

  it('trims whitespace from messages', async () => {
    render(<AuthProvider><ChatPage /></AuthProvider>);
    
    await acceptDisclaimer();

    // Mock chat API call
    global.fetch = jest.fn().mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockResponse)
    });

    await sendMessage('   test message   ');
    
    await waitFor(() => {
        expect(screen.getByText('test message')).toBeInTheDocument();
    });
  });

  it('validates session metadata', async () => {
    render(
      <AuthProvider>
        <ChatPage />
      </AuthProvider>
    );

    await acceptDisclaimer();

    // Wait for sessions to load
    await waitFor(() => {
      expect(screen.getByText('Test Session 1')).toBeInTheDocument();
    });

    // Select a session
    fireEvent.click(screen.getByText('Test Session 1'));

    // Mock API response with invalid metadata
    (sendChatMessage as jest.Mock).mockRejectedValueOnce(
      new Error('Invalid session metadata')
    );

    // Send a message
    const input = screen.getByPlaceholderText(/type your message/i);
    const button = screen.getByText(/send/i);

    await act(async () => {
      fireEvent.change(input, { target: { value: 'test message' } });
      fireEvent.click(button);
    });

    // Wait for the error message
    await waitFor(() => {
      expect(screen.getByText('Invalid session metadata')).toBeInTheDocument();
    });
  });

  it('handles validation errors gracefully', async () => {
    (sendChatMessage as jest.Mock).mockRejectedValueOnce(new Error('Invalid message format'));

    render(<AuthProvider><ChatPage /></AuthProvider>);
    await acceptDisclaimer();
    await sendMessage('test message');

    await waitFor(() => {
      expect(screen.getByText(/invalid message format/i)).toBeInTheDocument();
    });
  });

  it('displays messages and responses', async () => {
    render(
      <AuthProvider>
        <ChatPage />
      </AuthProvider>
    );

    await acceptDisclaimer();

    // Wait for sessions to load
    await waitFor(() => {
      expect(screen.getByText('Test Session 1')).toBeInTheDocument();
    });

    // Select a session
    fireEvent.click(screen.getByText('Test Session 1'));

    // Mock successful API response
    (sendChatMessage as jest.Mock).mockResolvedValueOnce({
      session_id: 'test-session-id',
      query: 'test message',
      response: 'test response',
      session_metadata: {
        emotional_history: [],
        topic_engagement: {},
        suggestion_enabled: true
      }
    });

    // Send a message
    const input = screen.getByPlaceholderText(/type your message/i);
    const button = screen.getByText(/send/i);

    await act(async () => {
      fireEvent.change(input, { target: { value: 'test message' } });
      fireEvent.click(button);
    });

    // Wait for both the user message and bot response to appear
    await waitFor(() => {
      const userMessage = screen.getByText('test message');
      const botResponse = screen.getByText('test response');
      expect(userMessage).toBeInTheDocument();
      expect(botResponse).toBeInTheDocument();
    });
  });

  it('handles API errors', async () => {
    render(
      <AuthProvider>
        <ChatPage />
      </AuthProvider>
    );

    await acceptDisclaimer();

    // Wait for sessions to load
    await waitFor(() => {
      expect(screen.getByText('Test Session 1')).toBeInTheDocument();
    });

    // Select a session
    fireEvent.click(screen.getByText('Test Session 1'));

    // Mock API error
    (sendChatMessage as jest.Mock).mockRejectedValueOnce(
      new Error('Failed to send message')
    );

    // Send a message
    const input = screen.getByPlaceholderText(/type your message/i);
    const button = screen.getByText(/send/i);

    await act(async () => {
      fireEvent.change(input, { target: { value: 'test message' } });
      fireEvent.click(button);
    });

    // Wait for the error message
    await waitFor(() => {
      expect(screen.getByText('Failed to send message')).toBeInTheDocument();
    });

    // Input should be re-enabled after error
    expect(input).not.toHaveAttribute('disabled');
    expect(button).not.toBeDisabled();
  });

  it('disables input while sending', async () => {
    render(
      <AuthProvider>
        <ChatPage />
      </AuthProvider>
    );

    await acceptDisclaimer();

    // Wait for sessions to load
    await waitFor(() => {
      expect(screen.getByText('Test Session 1')).toBeInTheDocument();
    });

    // Select a session
    fireEvent.click(screen.getByText('Test Session 1'));

    // Mock a slow API response
    (sendChatMessage as jest.Mock).mockImplementation(
      () => new Promise(resolve => setTimeout(() => resolve(mockResponse), 1000))
    );

    // Type a message
    const input = screen.getByPlaceholderText(/type your message/i);
    const button = screen.getByText(/send/i);
    
    await act(async () => {
      fireEvent.change(input, { target: { value: 'test message' } });
    });

    // Submit the message
    await act(async () => {
      fireEvent.click(button);
    });

    // Check that input and button are disabled while sending
    expect(input).toHaveAttribute('disabled');
    expect(button).toBeDisabled();

    // Wait for the response
    await waitFor(() => {
      expect(input).not.toHaveAttribute('disabled');
      expect(button).not.toBeDisabled();
    }, { timeout: 2000 });
  });
}); 