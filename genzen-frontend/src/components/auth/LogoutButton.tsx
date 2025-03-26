'use client';

import { logout } from '@/utils/auth';

export default function LogoutButton() {
    const handleLogout = async () => {
        await logout();
    };

    return (
        <button
            onClick={handleLogout}
            className="text-gray-600 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium"
        >
            Sign Out
        </button>
    );
} 