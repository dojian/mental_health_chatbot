'use client';
import Link from 'next/link';
import { useState } from 'react';
import { usePathname } from 'next/navigation';

export default function Header() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const pathname = usePathname();

  return (
    <header className="bg-white border-b">
      <div className="container mx-auto px-4 py-4 flex justify-between items-center">
        {/* Logo */}
        <h1 className="text-2xl font-bold text-gray-900">
          <Link href="/">GenZen</Link>
        </h1>

        {/* Navigation Links */}
        <nav className="space-x-8">
          <Link 
            href="/" 
            className={`text-gray-700 hover:text-gray-900 pb-2 ${pathname === '/' ? 'border-b-2 border-gray-900' : ''}`}
          >
            Home
          </Link>
          <Link 
            href="/about" 
            className={`text-gray-700 hover:text-gray-900 pb-2 ${pathname === '/about' ? 'border-b-2 border-gray-900' : ''}`}
          >
            About
          </Link>
          <Link 
            href="/chat" 
            className={`text-gray-700 hover:text-gray-900 pb-2 ${pathname === '/chat' ? 'border-b-2 border-gray-900' : ''}`}
          >
            Chat
          </Link>
          <Link 
            href="/privacy" 
            className={`text-gray-700 hover:text-gray-900 pb-2 ${pathname === '/privacy' ? 'border-b-2 border-gray-900' : ''}`}
          >
            Privacy
          </Link>
        </nav>

        {/* Login/Logout Button */}
        <button
          onClick={() => setIsAuthenticated(!isAuthenticated)}
          className="border border-gray-300 bg-gray-50 hover:bg-gray-100 text-gray-700 py-2 px-6 rounded-full"
        >
          {isAuthenticated ? 'Logout' : 'Login'}
        </button>
      </div>
    </header>
  );
}
