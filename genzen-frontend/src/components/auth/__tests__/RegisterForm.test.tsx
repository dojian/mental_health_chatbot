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
jest.mock('js-cookie', () => ({
    set: jest.fn(),
}));

describe('RegisterForm', () => {
    const fillForm = (username: string, email: string, password: string, verifyPassword: string) => {
        fireEvent.change(screen.getByLabelText(/username/i), { target: { value: username } });
        fireEvent.change(screen.getByLabelText(/email/i), { target: { value: email } });
        fireEvent.change(screen.getByLabelText(/^password$/i), { target: { value: password } });
        fireEvent.change(screen.getByLabelText(/verify password/i), { target: { value: verifyPassword } });
    };

    beforeEach(() => {
        global.fetch = jest.fn().mockResolvedValue({
            ok: true,
            json: () => Promise.resolve({ token: 'test-token' }),
        });
    });

    it('validates username requirements', async () => {
        render(
            <AuthProvider>
                <RegisterForm />
            </AuthProvider>
        );

        fillForm('ab', 'test@example.com', 'ValidP@ss1', 'ValidP@ss1');
        fireEvent.click(screen.getByRole('button', { name: /create account/i }));

        await waitFor(() => {
            expect(screen.getByText(/username must be at least 3 characters/i)).toBeInTheDocument();
        });
    });

    it('validates email requirements', async () => {
        render(
            <AuthProvider>
                <RegisterForm />
            </AuthProvider>
        );

        fillForm('validuser', 'invalid-email', 'ValidP@ss1', 'ValidP@ss1');
        fireEvent.click(screen.getByRole('button', { name: /create account/i }));

        await waitFor(() => {
            expect(screen.getByText(/invalid email format/i)).toBeInTheDocument();
        });
    });

    it('validates password requirements', async () => {
        render(
            <AuthProvider>
                <RegisterForm />
            </AuthProvider>
        );

        fillForm('validuser', 'test@example.com', 'weak', 'weak');
        fireEvent.click(screen.getByRole('button', { name: /create account/i }));

        await waitFor(() => {
            expect(screen.getByText(/password must be at least 8 characters/i)).toBeInTheDocument();
        });
    });

    it('validates password match', async () => {
        render(
            <AuthProvider>
                <RegisterForm />
            </AuthProvider>
        );

        fillForm('validuser', 'test@example.com', 'ValidP@ss1', 'DifferentP@ss');
        fireEvent.click(screen.getByRole('button', { name: /create account/i }));

        await waitFor(() => {
            expect(screen.getByText(/passwords do not match/i)).toBeInTheDocument();
        });
    });

    it('clears validation errors when user starts typing', async () => {
        render(
            <AuthProvider>
                <RegisterForm />
            </AuthProvider>
        );

        // Trigger validation error
        fillForm('ab', 'test@example.com', 'ValidP@ss1', 'ValidP@ss1');
        fireEvent.click(screen.getByRole('button', { name: /create account/i }));

        await waitFor(() => {
            expect(screen.getByText(/username must be at least 3 characters/i)).toBeInTheDocument();
        });

        // Start typing to clear error
        fillForm('validuser', 'test@example.com', 'ValidP@ss1', 'ValidP@ss1');

        await waitFor(() => {
            expect(screen.queryByText(/username must be at least 3 characters/i)).not.toBeInTheDocument();
        });
    });

    it('handles successful registration', async () => {
        const mockFetch = jest.fn().mockResolvedValue({
            ok: true,
            json: () => Promise.resolve({ token: 'test-token' }),
        });
        global.fetch = mockFetch;

        render(
            <AuthProvider>
                <RegisterForm />
            </AuthProvider>
        );

        fillForm('validuser', 'test@example.com', 'ValidP@ss1', 'ValidP@ss1');
        fireEvent.click(screen.getByRole('button', { name: /create account/i }));

        await waitFor(() => {
            expect(mockFetch).toHaveBeenCalled();
        });
    });

    it('handles registration errors', async () => {
        const mockFetch = jest.fn().mockResolvedValue({
            ok: false,
            json: () => Promise.resolve({ error: 'Username already exists' }),
        });
        global.fetch = mockFetch;

        render(
            <AuthProvider>
                <RegisterForm />
            </AuthProvider>
        );

        fillForm('existinguser', 'test@example.com', 'ValidP@ss1', 'ValidP@ss1');
        fireEvent.click(screen.getByRole('button', { name: /create account/i }));

        await waitFor(() => {
            expect(screen.getByText(/username already exists/i)).toBeInTheDocument();
        });
    });
}); 
}); 