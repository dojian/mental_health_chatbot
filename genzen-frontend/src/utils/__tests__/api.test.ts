import { sendChatMessage } from '../api';
import { env } from '../env';
import Cookies from 'js-cookie';

// Mock js-cookie
jest.mock('js-cookie', () => ({
  get: jest.fn(),
}));

// Mock fetch
global.fetch = jest.fn();

describe('sendChatMessage', () => {
  const mockToken = 'test-token';
  const mockRequest = {
    query: 'Hello',
    session_metadata: {
      emotional_history: [],
      topic_engagement: {},
      suggestion_enabled: true,
    },
  };

  const mockResponse = {
    session_id: 'test-session-id',
    query: 'Hello',
    response: 'Hi there! How can I help you today?',
  };

  beforeEach(() => {
    // Reset all mocks before each test
    jest.clearAllMocks();
    
    // Setup default mock implementations
    (Cookies.get as jest.Mock).mockReturnValue(mockToken);
    (global.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(mockResponse),
    });
  });

  it('should successfully send a chat message', async () => {
    const response = await sendChatMessage(mockRequest);

    expect(Cookies.get).toHaveBeenCalledWith(env.jwtStorageKey);
    expect(global.fetch).toHaveBeenCalledWith(
      `${env.apiUrl}/v1/agent-chat`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${mockToken}`,
        },
        body: JSON.stringify(mockRequest),
      }
    );
    expect(response).toEqual(mockResponse);
  });

  it('should throw error when no authentication token is found', async () => {
    (Cookies.get as jest.Mock).mockReturnValue(null);

    await expect(sendChatMessage(mockRequest)).rejects.toThrow('No authentication token found');
    expect(global.fetch).not.toHaveBeenCalled();
  });

  it('should throw error when API request fails', async () => {
    const errorStatus = 500;
    (global.fetch as jest.Mock).mockResolvedValue({
      ok: false,
      status: errorStatus,
    });

    await expect(sendChatMessage(mockRequest)).rejects.toThrow(`HTTP error! status: ${errorStatus}`);
  });
}); 