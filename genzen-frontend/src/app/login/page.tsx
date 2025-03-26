import LoginForm from '@/components/auth/LoginForm';
import Link from 'next/link';

export default function LoginPage() {
    return (
        <div className="min-h-screen flex flex-col items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-8">
                <h1 className="text-3xl font-bold text-gray-900">Welcome Back</h1>
                <p className="mt-2 text-gray-600">Sign in to continue to GenZen</p>
            </div>

            <LoginForm />

            <div className="mt-4 text-center">
                <p className="text-gray-600">
                    Don&apos;t have an account?{' '}
                    <Link href="/register" className="text-blue-600 hover:text-blue-500">
                        Create one now
                    </Link>
                </p>
            </div>
        </div>
    );
} 