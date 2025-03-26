import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import ChatPage from '../page';
import { sendChatMessage } from '@/utils/api';

// Mock the API function
jest.mock('@/utils/api', () => ({
  sendChatMessage: jest.fn(),
}));

// Mock scrollIntoView
const mockScrollIntoView = jest.fn();
window.HTMLElement.prototype.scrollIntoView = mockScrollIntoView;

describe('ChatPage', () => {
  const mockResponse = {
    session_id: 'test-session-id',
    query: 'Hello',
    response: 'Hi there! How can I help you today?',
  };

  beforeEach(() => {
    // Reset all mocks before each test
    jest.clearAllMocks();
    mockScrollIntoView.mockClear();
    
    // Setup default mock implementation for sendChatMessage
    (sendChatMessage as jest.Mock).mockResolvedValue(mockResponse);
  });

  it('renders chat interface correctly', () => {
    render(<ChatPage />);
    
    // Check for input field and send button
    expect(screen.getByPlaceholderText('Type your message...')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /send/i })).toBeInTheDocument();
  });

  it('handles message submission correctly', async () => {
    render(<ChatPage />);
    
    const input = screen.getByPlaceholderText('Type your message...');
    const sendButton = screen.getByRole('button', { name: /send/i });
    
    // Type and send a message
    fireEvent.change(input, { target: { value: 'Hello' } });
    fireEvent.click(sendButton);
    
    // Check if message appears in chat
    expect(screen.getByText('Hello')).toBeInTheDocument();
    
    // Wait for API call and response
    await waitFor(() => {
      expect(sendChatMessage).toHaveBeenCalledWith({
        query: 'Hello',
        session_id: null,
        session_metadata: {
          emotional_history: [],
          topic_engagement: {},
          suggestion_enabled: true,
          last_memory_access: expect.any(String),
          memory_context: [],
        },
      });
    });
    
    // Check if bot response appears
    expect(screen.getByText(mockResponse.response)).toBeInTheDocument();
  });

  it('includes session ID in subsequent requests', async () => {
    render(<ChatPage />);
    
    const input = screen.getByPlaceholderText('Type your message...');
    const sendButton = screen.getByRole('button', { name: /send/i });
    
    // Send first message
    fireEvent.change(input, { target: { value: 'Hello' } });
    fireEvent.click(sendButton);
    
    // Wait for first API call to complete
    await waitFor(() => {
      expect(sendChatMessage).toHaveBeenCalledWith({
        query: 'Hello',
        session_id: null,
        session_metadata: {
          emotional_history: [],
          topic_engagement: {},
          suggestion_enabled: true,
          last_memory_access: expect.any(String),
          memory_context: [],
        },
      });
    });
    
    // Send second message
    fireEvent.change(input, { target: { value: 'How are you?' } });
    fireEvent.click(sendButton);
    
    // Wait for second API call and verify session ID is included
    await waitFor(() => {
      expect(sendChatMessage).toHaveBeenCalledWith({
        query: 'How are you?',
        session_id: 'test-session-id',
        session_metadata: {
          emotional_history: [],
          topic_engagement: {},
          suggestion_enabled: true,
          last_memory_access: expect.any(String),
          memory_context: [],
        },
      });
    });
  });

  it('disables input and button while loading', async () => {
    render(<ChatPage />);
    
    const input = screen.getByPlaceholderText('Type your message...');
    const sendButton = screen.getByRole('button', { name: /send/i });
    
    // Type and send a message
    fireEvent.change(input, { target: { value: 'Hello' } });
    fireEvent.click(sendButton);
    
    // Check if input and button are disabled while loading
    expect(input).toBeDisabled();
    expect(sendButton).toBeDisabled();
    
    // Wait for API call to complete
    await waitFor(() => {
      expect(input).not.toBeDisabled();
    });

    // Type something new to enable the button
    fireEvent.change(input, { target: { value: 'New message' } });
    expect(sendButton).not.toBeDisabled();
  });

  it('displays error message when API call fails', async () => {
    const errorMessage = 'API Error';
    (sendChatMessage as jest.Mock).mockRejectedValue(new Error(errorMessage));
    
    render(<ChatPage />);
    
    const input = screen.getByPlaceholderText('Type your message...');
    const sendButton = screen.getByRole('button', { name: /send/i });
    
    // Type and send a message
    fireEvent.change(input, { target: { value: 'Hello' } });
    fireEvent.click(sendButton);
    
    // Wait for error message to appear
    await waitFor(() => {
      expect(screen.getByText(errorMessage)).toBeInTheDocument();
    });
  });

  it('does not send empty messages', () => {
    render(<ChatPage />);
    
    const input = screen.getByPlaceholderText('Type your message...');
    const sendButton = screen.getByRole('button', { name: /send/i });
    
    // Try to send empty message
    fireEvent.click(sendButton);
    
    // Check that API was not called
    expect(sendChatMessage).not.toHaveBeenCalled();
  });

  it('clears input after sending message', async () => {
    render(<ChatPage />);
    
    const input = screen.getByPlaceholderText('Type your message...');
    const sendButton = screen.getByRole('button', { name: /send/i });
    
    // Type and send a message
    fireEvent.change(input, { target: { value: 'Hello' } });
    fireEvent.click(sendButton);
    
    // Check that input is cleared
    expect(input).toHaveValue('');
    
    // Wait for API call to complete
    await waitFor(() => {
      expect(sendChatMessage).toHaveBeenCalled();
    });
  });
}); 