import { env } from './env';
import Cookies from 'js-cookie';

export async function logout() {
    try {
        // Get the token from cookies
        const token = Cookies.get(env.jwtStorageKey);
        if (!token) return;

        // Call the logout endpoint
        await fetch(`/api/auth/logout`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
            },
        });
    } finally {
        // Always remove the token from cookies
        Cookies.remove(env.jwtStorageKey);
        // Redirect to login page
        window.location.href = '/login';
    }
} 