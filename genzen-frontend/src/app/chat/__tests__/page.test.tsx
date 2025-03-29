import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import ChatPage from '../page';
import { sendChatMessage } from '@/utils/api';
import '@testing-library/jest-dom';

// Mock the sendChatMessage function
jest.mock('@/utils/api', () => ({
  sendChatMessage: jest.fn(),
}));

// Mock the next/navigation module
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: jest.fn(),
    replace: jest.fn(),
    refresh: jest.fn(),
    back: jest.fn(),
    forward: jest.fn(),
  }),
}));

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
    
    // Mock global fetch
    global.fetch = jest.fn().mockImplementation((url: string) => {
      if (url.includes('/api/chat/recent-sessions')) {
        return Promise.resolve(new MockResponse({
          sessions: [
            { session_id: '1', session_name: 'Test Session 1', timestamp: new Date().toISOString() },
            { session_id: '2', session_name: 'Test Session 2', timestamp: new Date().toISOString() }
          ]
        }));
      }
      return Promise.resolve(new MockResponse({}));
    });

    // Mock scrollIntoView
    window.HTMLElement.prototype.scrollIntoView = jest.fn();
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
    render(<ChatPage />);
    
    // Accept disclaimer first
    const acceptButton = screen.getByText('I Understand and Accept');
    await act(async () => {
      fireEvent.click(acceptButton);
    });

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

  it('sends messages and receives responses', async () => {
    const mockResponse = { message: 'Test response', session_id: '123', query: 'Test message', response: 'Test response' };
    (sendChatMessage as jest.Mock).mockResolvedValueOnce(mockResponse);

    render(<ChatPage />);
    
    // Accept disclaimer first
    const acceptButton = screen.getByText('I Understand and Accept');
    await act(async () => {
      fireEvent.click(acceptButton);
    });

    await waitFor(() => {
      const input = screen.getByPlaceholderText('Type your message...');
      expect(input).toBeInTheDocument();
    });

    const input = screen.getByPlaceholderText('Type your message...');
    const sendButton = screen.getByText('Send');

    // Type and send a message
    await act(async () => {
      fireEvent.change(input, { target: { value: 'Test message' } });
      fireEvent.click(sendButton);
    });

    // Wait for the response
    await waitFor(() => {
      const responseElement = screen.getByText('Test response');
      expect(responseElement).toBeInTheDocument();
      expect(responseElement.closest('div')).toHaveClass('bg-white');
    });
  });

  it('disables input and button while loading', async () => {
    // Make the sendChatMessage function take some time to resolve
    (sendChatMessage as jest.Mock).mockImplementation(() => new Promise(resolve => {
      setTimeout(() => resolve({ message: 'Test response', session_id: '123' }), 100);
    }));

    render(<ChatPage />);
    
    // Accept disclaimer first
    const acceptButton = screen.getByText('I Understand and Accept');
    await act(async () => {
      fireEvent.click(acceptButton);
    });

    await waitFor(() => {
      const input = screen.getByPlaceholderText('Type your message...');
      expect(input).toBeInTheDocument();
    });

    const input = screen.getByPlaceholderText('Type your message...');
    const sendButton = screen.getByText('Send');

    // Type and send a message
    await act(async () => {
      fireEvent.change(input, { target: { value: 'Test message' } });
      fireEvent.click(sendButton);
    });

    // Check that input and button are disabled
    expect(input).toBeDisabled();
    expect(sendButton).toBeDisabled();
  });

  it('handles API errors', async () => {
    (sendChatMessage as jest.Mock).mockRejectedValueOnce(new Error('API Error'));

    render(<ChatPage />);
    
    // Accept disclaimer first
    const acceptButton = screen.getByText('I Understand and Accept');
    await act(async () => {
      fireEvent.click(acceptButton);
    });

    await waitFor(() => {
      const input = screen.getByPlaceholderText('Type your message...');
      expect(input).toBeInTheDocument();
    });

    const input = screen.getByPlaceholderText('Type your message...');
    const sendButton = screen.getByText('Send');

    // Type and send a message
    await act(async () => {
      fireEvent.change(input, { target: { value: 'Test message' } });
      fireEvent.click(sendButton);
    });

    // Wait for error message
    await waitFor(() => {
      expect(screen.getByText(/error/i)).toBeInTheDocument();
    });
  });
}); 