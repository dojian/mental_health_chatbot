import { render, screen, fireEvent } from '@testing-library/react';
import Header from '../Header';
import { AuthProvider } from '@/contexts/AuthContext';
import { env } from '@/utils/env';
import Cookies from 'js-cookie';

// Mock js-cookie
jest.mock('js-cookie', () => ({
  get: jest.fn(),
  set: jest.fn(),
  remove: jest.fn(),
}));

// Mock next/navigation
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: jest.fn(),
  }),
  usePathname: () => '/',
}));

describe('Header', () => {
  beforeEach(() => {
    // Clear all mocks before each test
    jest.clearAllMocks();
  });

  it('should show default navigation for unauthenticated users', () => {
    render(
      <AuthProvider>
        <Header />
      </AuthProvider>
    );

    // Check for default navigation items
    expect(screen.getAllByText('Home')[0]).toBeInTheDocument();
    expect(screen.getAllByText('Sign In')[0]).toBeInTheDocument();
    expect(screen.getAllByText('Register')[0]).toBeInTheDocument();

    // Check that authenticated-only items are not present
    expect(screen.queryByText('Chat')).not.toBeInTheDocument();
    expect(screen.queryByText('Sign Out')).not.toBeInTheDocument();
  });

  it('should show different navigation for authenticated users', () => {
    // Mock authenticated state
    (Cookies.get as jest.Mock).mockReturnValue('test-token');

    render(
      <AuthProvider>
        <Header />
      </AuthProvider>
    );

    // Check for authenticated navigation items
    expect(screen.getAllByText('Home')[0]).toBeInTheDocument();
    expect(screen.getAllByText('Chat')[0]).toBeInTheDocument();
    expect(screen.getAllByText('Sign Out')[0]).toBeInTheDocument();

    // Check that unauthenticated items are not present
    expect(screen.queryByText('Sign In')).not.toBeInTheDocument();
    expect(screen.queryByText('Register')).not.toBeInTheDocument();
  });

  it('should handle sign out correctly', () => {
    // Mock authenticated state
    (Cookies.get as jest.Mock).mockReturnValue('test-token');

    render(
      <AuthProvider>
        <Header />
      </AuthProvider>
    );

    // Click the sign out button
    fireEvent.click(screen.getAllByText('Sign Out')[0]);

    // Verify token was removed
    expect(Cookies.remove).toHaveBeenCalledWith(env.jwtStorageKey);
  });

  it('should toggle mobile menu', () => {
    render(
      <AuthProvider>
        <Header />
      </AuthProvider>
    );

    // Get the menu button and mobile menu
    const menuButton = screen.getByRole('button', { name: /menu/i });
    const mobileMenu = screen.getByTestId('mobile-menu');

    // Initially, mobile menu should be hidden
    expect(mobileMenu).toHaveClass('hidden');

    // Click menu button
    fireEvent.click(menuButton);

    // Mobile menu should be visible
    expect(mobileMenu).not.toHaveClass('hidden');

    // Click menu button again
    fireEvent.click(menuButton);

    // Mobile menu should be hidden again
    expect(mobileMenu).toHaveClass('hidden');
  });
}); 