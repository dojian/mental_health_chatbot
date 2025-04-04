'use client';

import { useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { env } from '@/utils/env';
import Cookies from 'js-cookie';
import { useAuth } from '@/contexts/AuthContext';
import { loginSchema, type LoginSchema } from '@/lib/validations/auth';
import { ZodError } from 'zod';

interface FormErrors extends Partial<Record<keyof LoginSchema, string>> {
    form?: string;
}

export default function LoginForm() {
    const [formData, setFormData] = useState<LoginSchema>({
        username: '',
        password: '',
    });
    const [errors, setErrors] = useState<FormErrors>({});
    const [isLoading, setIsLoading] = useState(false);
    const router = useRouter();
    const searchParams = useSearchParams();
    const { setIsAuthenticated } = useAuth();

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));
        // Clear error when user starts typing
        if (errors[name as keyof LoginSchema]) {
            setErrors(prev => ({ ...prev, [name]: '' }));
        }
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setErrors({});

        try {
            // Validate form data
            const validatedData = loginSchema.parse(formData);
            setIsLoading(true);

            const loginFormData = new FormData();
            loginFormData.append('username', validatedData.username);
            loginFormData.append('password', validatedData.password);

            const response = await fetch(`/api/auth/login`, {
                method: 'POST',
                credentials: 'include',
                body: loginFormData,
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
            if (err instanceof Error) {
                setErrors({ form: err.message });
            } else if (err instanceof ZodError) {
                // Handle Zod validation errors
                const validationErrors: FormErrors = {};
                err.errors.forEach((error) => {
                    if (error.path[0]) {
                        validationErrors[error.path[0] as keyof LoginSchema] = error.message;
                    }
                });
                setErrors(validationErrors);
            }
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="w-full max-w-md mx-auto p-6">
            <form onSubmit={handleSubmit} className="bg-white/80 rounded-lg shadow-md p-8 space-y-6">
                <h2 className="text-2xl font-semibold text-gray-800 mb-6">Sign In</h2>
                
                {errors.form && (
                    <div className="bg-red-50 text-red-500 p-3 rounded-md">
                        {errors.form}
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
                            value={formData.username}
                            onChange={handleChange}
                            className={`w-full px-3 py-2 border ${errors.username ? 'border-red-500' : 'border-gray-300'} rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-black`}
                            placeholder="Enter your username"
                        />
                        {errors.username && (
                            <p className="mt-1 text-sm text-red-500">{errors.username}</p>
                        )}
                    </div>

                    <div>
                        <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-1">
                            Password
                        </label>
                        <input
                            type="password"
                            id="password"
                            name="password"
                            value={formData.password}
                            onChange={handleChange}
                            className={`w-full px-3 py-2 border ${errors.password ? 'border-red-500' : 'border-gray-300'} rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-black`}
                            placeholder="Enter your password"
                        />
                        {errors.password && (
                            <p className="mt-1 text-sm text-red-500">{errors.password}</p>
                        )}
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