'use client';
import Link from 'next/link';
import { useState } from 'react';
import { usePathname } from 'next/navigation';

export default function Header() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const pathname = usePathname();

  const navLinks = [
    { href: '/', label: 'Home' },
    { href: '/about', label: 'About' },
    { href: '/chat', label: 'Chat' },
    { href: '/privacy', label: 'Privacy' },
  ];

  return (
    <header className="bg-white border-b">
      <div className="container mx-auto px-4 py-4">
        <div className="flex justify-between items-center">
          {/* Logo */}
          <h1 className="text-2xl font-bold text-gray-900">
            <Link href="/">GenZen</Link>
          </h1>

          {/* Mobile Menu Button */}
          <button
            onClick={() => setIsMenuOpen(!isMenuOpen)}
            className="md:hidden p-2 text-gray-600 hover:text-gray-900"
            aria-label="Toggle menu"
          >
            <svg
              className="w-6 h-6"
              fill="none"
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="2"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              {isMenuOpen ? (
                <path d="M6 18L18 6M6 6l12 12" />
              ) : (
                <path d="M4 6h16M4 12h16M4 18h16" />
              )}
            </svg>
          </button>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center space-x-8">
            {navLinks.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                className={`text-gray-700 hover:text-gray-900 pb-2 ${
                  pathname === link.href ? 'border-b-2 border-gray-900' : ''
                }`}
              >
                {link.label}
              </Link>
            ))}
            <button
              onClick={() => setIsAuthenticated(!isAuthenticated)}
              className="border border-gray-300 bg-gray-50 hover:bg-gray-100 text-gray-700 py-2 px-6 rounded-full"
            >
              {isAuthenticated ? 'Logout' : 'Login'}
            </button>
          </nav>
        </div>

        {/* Mobile Navigation */}
        <nav
          className={`${
            isMenuOpen ? 'block' : 'hidden'
          } md:hidden mt-4 pb-4 space-y-4`}
        >
          {navLinks.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className={`block text-gray-700 hover:text-gray-900 py-2 ${
                pathname === link.href ? 'font-semibold' : ''
              }`}
              onClick={() => setIsMenuOpen(false)}
            >
              {link.label}
            </Link>
          ))}
          <button
            onClick={() => {
              setIsAuthenticated(!isAuthenticated);
              setIsMenuOpen(false);
            }}
            className="w-full text-left border border-gray-300 bg-gray-50 hover:bg-gray-100 text-gray-700 py-2 px-6 rounded-full"
          >
            {isAuthenticated ? 'Logout' : 'Login'}
          </button>
        </nav>
      </div>
    </header>
  );
}
