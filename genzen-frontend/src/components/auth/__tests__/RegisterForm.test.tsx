import '@testing-library/jest-dom';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import RegisterForm from '../RegisterForm';
import { AuthProvider } from '@/contexts/AuthContext';
import { env } from '@/utils/env';
import Cookies from 'js-cookie';

// Mock next/navigation
jest.mock('next/navigation', () => ({
    useRouter: () => ({
        push: jest.fn(),
    }),
}));

// Mock js-cookie
jest.mock('js-cookie');

describe('RegisterForm', () => {
    beforeEach(() => {
        // Clear all mocks before each test
        jest.clearAllMocks();
    });

    it('should handle successful registration', async () => {
        // Mock successful API response
        global.fetch = jest.fn().mockResolvedValueOnce({
            ok: true,
            json: () => Promise.resolve({ access_token: 'test-token' }),
        });

        render(
            <AuthProvider>
                <RegisterForm />
            </AuthProvider>
        );

        // Fill in the form
        fireEvent.change(screen.getByLabelText(/username/i), {
            target: { value: 'testuser' },
        });
        fireEvent.change(screen.getByLabelText(/email/i), {
            target: { value: 'test@example.com' },
        });
        fireEvent.change(screen.getByLabelText(/^password$/i), {
            target: { value: 'password123' },
        });
        fireEvent.change(screen.getByLabelText(/verify password/i), {
            target: { value: 'password123' },
        });

        // Submit the form
        fireEvent.click(screen.getByRole('button', { name: /create account/i }));

        // Wait for the API call to complete
        await waitFor(() => {
            expect(global.fetch).toHaveBeenCalledWith(`${env.apiUrl}/auth/register`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'include',
                body: JSON.stringify({
                    username: 'testuser',
                    email: 'test@example.com',
                    password: 'password123',
                    role: 'user',
                }),
            });
        });

        // Verify token was stored
        expect(Cookies.set).toHaveBeenCalledWith(env.jwtStorageKey, 'test-token', {
            expires: 7,
            secure: process.env.NODE_ENV === 'production',
            sameSite: 'strict',
        });
    });

    it('should handle password mismatch', async () => {
        render(
            <AuthProvider>
                <RegisterForm />
            </AuthProvider>
        );

        // Fill in the form with mismatched passwords
        fireEvent.change(screen.getByLabelText(/username/i), {
            target: { value: 'testuser' },
        });
        fireEvent.change(screen.getByLabelText(/email/i), {
            target: { value: 'test@example.com' },
        });
        fireEvent.change(screen.getByLabelText(/^password$/i), {
            target: { value: 'password123' },
        });
        fireEvent.change(screen.getByLabelText(/verify password/i), {
            target: { value: 'different' },
        });

        // Submit the form
        fireEvent.click(screen.getByRole('button', { name: /create account/i }));

        // Verify error message
        await waitFor(() => {
            expect(screen.getByText(/passwords do not match/i)).toBeInTheDocument();
        });
    });

    it('should handle registration error', async () => {
        // Mock failed API response
        global.fetch = jest.fn().mockResolvedValueOnce({
            ok: false,
            json: () => Promise.resolve({ detail: 'Registration failed' }),
        });

        render(
            <AuthProvider>
                <RegisterForm />
            </AuthProvider>
        );

        // Fill in the form
        fireEvent.change(screen.getByLabelText(/username/i), {
            target: { value: 'testuser' },
        });
        fireEvent.change(screen.getByLabelText(/email/i), {
            target: { value: 'test@example.com' },
        });
        fireEvent.change(screen.getByLabelText(/^password$/i), {
            target: { value: 'password123' },
        });
        fireEvent.change(screen.getByLabelText(/verify password/i), {
            target: { value: 'password123' },
        });

        // Submit the form
        fireEvent.click(screen.getByRole('button', { name: /create account/i }));

        // Wait for the error message
        await waitFor(() => {
            expect(screen.getByText(/registration failed/i)).toBeInTheDocument();
        });
    });
}); 