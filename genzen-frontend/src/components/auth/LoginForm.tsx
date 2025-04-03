'use client';

import { useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { env } from '@/utils/env';
import Cookies from 'js-cookie';
import { useAuth } from '@/contexts/AuthContext';

export default function LoginForm() {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const router = useRouter();
    const searchParams = useSearchParams();
    const { setIsAuthenticated } = useAuth();

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        setIsLoading(true);

        try {
            const formData = new FormData();
            formData.append('username', username);
            formData.append('password', password);
            
            console.log('Sending login request to:', `${env.apiUrl}/auth/login`);

            const response = await fetch(`${env.apiUrl}/auth/login`, {
                method: 'POST',
                credentials: 'include',
                body: formData,
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || 'Login failed');
            }

            // Store the token in a cookie
            Cookies.set(env.jwtStorageKey, data.access_token, {
                expires: 7, // Token expires in 7 days
                secure: process.env.NODE_ENV === 'production',
                sameSite: 'strict',
            });

            // Update authentication state
            setIsAuthenticated(true);

            // Redirect to the original URL or chat page
            const redirectTo = searchParams.get('redirect') || '/chat';
            router.push(redirectTo);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Login failed');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="w-full max-w-md mx-auto p-6">
            <form onSubmit={handleSubmit} className="bg-white/80 rounded-lg shadow-md p-8 space-y-6">
                <h2 className="text-2xl font-semibold text-gray-800 mb-6">Sign In</h2>
                
                {error && (
                    <div className="bg-red-50 text-red-500 p-3 rounded-md">
                        {error}
                    </div>
                )}

                <div className="space-y-4">
                    <div>
                        <label htmlFor="username" className="block text-sm font-medium text-gray-700 mb-1">
                            Username
                        </label>
                        <input
                            type="text"
                            id="username"
                            name="username"
                            required
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-black"
                            placeholder="Enter your username"
                        />
                    </div>

                    <div>
                        <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-1">
                            Password
                        </label>
                        <input
                            type="password"
                            id="password"
                            name="password"
                            required
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-black"
                            placeholder="Enter your password"
                        />
                    </div>
                </div>

                <button
                    type="submit"
                    disabled={isLoading}
                    className={`w-full py-2 px-4 border border-transparent rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 ${
                        isLoading ? 'opacity-50 cursor-not-allowed' : ''
                    }`}
                >
                    {isLoading ? 'Signing In...' : 'Sign In'}
                </button>
            </form>
        </div>
    );
} 