import RegisterForm from '@/components/auth/RegisterForm';
import Link from 'next/link';

export default function RegisterPage() {
    return (
        <div className="min-h-screen flex flex-col items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-8">
                <h1 className="text-3xl font-bold text-gray-900">Welcome to GenZen</h1>
                <p className="mt-2 text-gray-600">Create an account to get started</p>
            </div>

            <RegisterForm />

            <p className="mt-4 text-center text-gray-600">
                Already have an account?{' '}
                <Link href="/login" className="text-blue-600 hover:text-blue-500">
                    Sign in
                </Link>
            </p>
        </div>
    );
} 