import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import LoginForm from '../LoginForm';
import { AuthProvider } from '@/contexts/AuthContext';
import { env } from '@/utils/env';
import Cookies from 'js-cookie';

// Mock js-cookie
jest.mock('js-cookie');

// Create a mock router
const mockPush = jest.fn();

// Mock next/navigation
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: mockPush,
  }),
  useSearchParams: () => ({
    get: jest.fn().mockReturnValue(null),
  }),
}));

describe('LoginForm', () => {
  beforeEach(() => {
    // Clear all mocks before each test
    jest.clearAllMocks();
    mockPush.mockClear();
  });

  it('should handle successful login and redirect to chat', async () => {
    // Mock successful API response
    global.fetch = jest.fn().mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ access_token: 'test-token' }),
    });

    render(
      <AuthProvider>
        <LoginForm />
      </AuthProvider>
    );

    // Fill in the form
    fireEvent.change(screen.getByLabelText(/username/i), {
      target: { value: 'testuser' },
    });
    fireEvent.change(screen.getByLabelText(/password/i), {
      target: { value: 'password123' },
    });

    // Submit the form
    fireEvent.click(screen.getByRole('button', { name: /sign in/i }));

    // Create FormData for comparison
    const expectedFormData = new FormData();
    expectedFormData.append('username', 'testuser');
    expectedFormData.append('password', 'password123');

    // Wait for the API call to complete
    await waitFor(() => {
      const fetchCalls = (global.fetch as jest.Mock).mock.calls;
      expect(fetchCalls.length).toBe(1);
      expect(fetchCalls[0][0]).toBe(`${env.apiUrl}/auth/login`);
      
      const options = fetchCalls[0][1];
      expect(options.method).toBe('POST');
      expect(options.credentials).toBe('include');
      
      // Convert the sent FormData to an object for comparison
      const sentFormData = options.body;
      expect(sentFormData.get('username')).toBe('testuser');
      expect(sentFormData.get('password')).toBe('password123');
    });

    // Verify token was stored
    expect(Cookies.set).toHaveBeenCalledWith(env.jwtStorageKey, 'test-token', {
      expires: 7,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'strict',
    });

    // Verify redirection to chat page
    expect(mockPush).toHaveBeenCalledWith('/chat');
  });

  it('should handle successful login with redirect URL', async () => {
    // Mock successful API response
    global.fetch = jest.fn().mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ access_token: 'test-token' }),
    });

    // Mock searchParams to return a redirect URL
    const mockSearchParams = {
      get: jest.fn().mockReturnValue('/dashboard'),
    };
    jest.spyOn(require('next/navigation'), 'useSearchParams').mockReturnValue(mockSearchParams);

    render(
      <AuthProvider>
        <LoginForm />
      </AuthProvider>
    );

    // Fill in the form
    fireEvent.change(screen.getByLabelText(/username/i), {
      target: { value: 'testuser' },
    });
    fireEvent.change(screen.getByLabelText(/password/i), {
      target: { value: 'password123' },
    });

    // Submit the form
    fireEvent.click(screen.getByRole('button', { name: /sign in/i }));

    // Create FormData for comparison
    const expectedFormData = new FormData();
    expectedFormData.append('username', 'testuser');
    expectedFormData.append('password', 'password123');

    // Wait for the API call to complete
    await waitFor(() => {
      const fetchCalls = (global.fetch as jest.Mock).mock.calls;
      expect(fetchCalls.length).toBe(1);
      expect(fetchCalls[0][0]).toBe(`${env.apiUrl}/auth/login`);
      
      const options = fetchCalls[0][1];
      expect(options.method).toBe('POST');
      expect(options.credentials).toBe('include');
      
      // Convert the sent FormData to an object for comparison
      const sentFormData = options.body;
      expect(sentFormData.get('username')).toBe('testuser');
      expect(sentFormData.get('password')).toBe('password123');
    });

    // Verify token was stored
    expect(Cookies.set).toHaveBeenCalledWith(env.jwtStorageKey, 'test-token', {
      expires: 7,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'strict',
    });

    // Verify redirection to the specified URL
    expect(mockPush).toHaveBeenCalledWith('/dashboard');
  });

  it('should handle login error', async () => {
    // Mock failed API response
    global.fetch = jest.fn().mockResolvedValueOnce({
      ok: false,
      json: () => Promise.resolve({ detail: 'Invalid credentials' }),
    });

    render(
      <AuthProvider>
        <LoginForm />
      </AuthProvider>
    );

    // Fill in the form
    fireEvent.change(screen.getByLabelText(/username/i), {
      target: { value: 'testuser' },
    });
    fireEvent.change(screen.getByLabelText(/password/i), {
      target: { value: 'wrongpassword' },
    });

    // Submit the form
    fireEvent.click(screen.getByRole('button', { name: /sign in/i }));

    // Wait for the error message
    await waitFor(() => {
      expect(screen.getByText(/invalid credentials/i)).toBeInTheDocument();
    });

    // Verify no token was stored
    expect(Cookies.set).not.toHaveBeenCalled();

    // Verify no redirection occurred
    expect(mockPush).not.toHaveBeenCalled();
  });
}); 