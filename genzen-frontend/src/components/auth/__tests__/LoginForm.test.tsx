import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import LoginForm from '../LoginForm';
import { AuthProvider } from '@/contexts/AuthContext';
import { env } from '@/utils/env';
import Cookies from 'js-cookie';
import { useRouter } from 'next/navigation';

// Mock next/navigation
jest.mock('next/navigation', () => ({
    useRouter: jest.fn(),
    useSearchParams: () => ({
        get: jest.fn().mockReturnValue(null)
    }),
}));

// Mock js-cookie
jest.mock('js-cookie');

describe('LoginForm', () => {
    const mockRouter = {
        push: jest.fn(),
    };

    beforeEach(() => {
        // Reset mocks
        jest.clearAllMocks();
        (useRouter as jest.Mock).mockReturnValue(mockRouter);
        (Cookies.set as jest.Mock) = jest.fn();
    });

    const fillForm = (username: string, password: string) => {
        const usernameInput = screen.getByLabelText(/username/i);
        const passwordInput = screen.getByLabelText(/password/i);

        fireEvent.change(usernameInput, { target: { value: username } });
        fireEvent.change(passwordInput, { target: { value: password } });
    };

    it('validates required fields', async () => {
        render(<AuthProvider><LoginForm /></AuthProvider>);
        
        const submitButton = screen.getByRole('button', { name: /sign in/i });
        fireEvent.click(submitButton);

        await waitFor(() => {
            expect(screen.getByText(/username is required/i)).toBeInTheDocument();
            expect(screen.getByText(/password is required/i)).toBeInTheDocument();
        });
    });

    it('validates username length', async () => {
        render(<AuthProvider><LoginForm /></AuthProvider>);
        
        fillForm('ab', 'ValidP@ss1');
        fireEvent.click(screen.getByRole('button', { name: /sign in/i }));

        await waitFor(() => {
            expect(screen.getByText(/username must be at least 3 characters/i)).toBeInTheDocument();
        });
    });

    it('clears validation errors when user starts typing', async () => {
        render(<AuthProvider><LoginForm /></AuthProvider>);
        
        // First trigger validation error
        fillForm('ab', 'ValidP@ss1');
        fireEvent.click(screen.getByRole('button', { name: /sign in/i }));

        // Wait for error to appear
        await waitFor(() => {
            expect(screen.getByText(/username must be at least 3 characters/i)).toBeInTheDocument();
        });

        // Start typing valid input
        fillForm('validuser', 'ValidP@ss1');

        // Error should be cleared
        await waitFor(() => {
            expect(screen.queryByText(/username must be at least 3 characters/i)).not.toBeInTheDocument();
        });
    });

    it('handles successful login', async () => {
        global.fetch = jest.fn().mockResolvedValueOnce({
            ok: true,
            json: () => Promise.resolve({ token: 'test-token' }),
        });

        render(<AuthProvider><LoginForm /></AuthProvider>);
        
        fillForm('validuser', 'ValidP@ss1');
        fireEvent.click(screen.getByRole('button', { name: /sign in/i }));

        await waitFor(() => {
            expect(Cookies.set).toHaveBeenCalledWith('token', 'test-token');
            expect(mockRouter.push).toHaveBeenCalledWith('/chat');
        });
    });

    it('handles login errors', async () => {
        global.fetch = jest.fn().mockResolvedValueOnce({
            ok: false,
            json: () => Promise.resolve({ message: 'Invalid credentials' }),
        });

        render(<AuthProvider><LoginForm /></AuthProvider>);
        
        fillForm('validuser', 'WrongP@ss1');
        fireEvent.click(screen.getByRole('button', { name: /sign in/i }));

        await waitFor(() => {
            expect(screen.getByText('Login failed')).toBeInTheDocument();
            expect(Cookies.set).not.toHaveBeenCalled();
        });
    });
}); 