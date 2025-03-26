import { env } from './env';

export async function logout() {
    try {
        // Get the token from localStorage
        const token = localStorage.getItem(env.jwtStorageKey);
        if (!token) return;

        // Call the logout endpoint
        await fetch(`${env.apiUrl}/auth/logout`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
            },
        });
    } finally {
        // Always remove the token from localStorage
        localStorage.removeItem(env.jwtStorageKey);
        // Redirect to login page
        window.location.href = '/login';
    }
} 