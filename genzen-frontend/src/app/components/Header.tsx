'use client';
import Link from 'next/link';
import { useState } from 'react';

export default function Header() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  return (
    <header className="bg-gray-800 shadow-md">
      <div className="container mx-auto px-4 py-4 flex justify-between items-center">
        {/* Logo */}
        <h1 className="text-2xl font-bold text-white">
          <Link href="/">GenZen</Link>
        </h1>

        {/* Navigation Links */}
        <nav className="space-x-6 text-white">
          <Link href="/" className="hover:text-blue-400">Home</Link>
          <Link href="/about" className="hover:text-blue-400">About</Link>
          <Link href="/chat" className="hover:text-blue-400">Chat</Link>
          <Link href="/privacy" className="hover:text-blue-400">Privacy</Link>
        </nav>

        {/* Login/Logout Button */}
        <button
          onClick={() => setIsAuthenticated(!isAuthenticated)}
          className="bg-blue-500 hover:bg-blue-600 text-white py-2 px-4 rounded"
        >
          {isAuthenticated ? 'Logout' : 'Login'}
        </button>
      </div>
    </header>
  );
}
