'use client';
import Link from 'next/link';
import { useState } from 'react';
import { usePathname } from 'next/navigation';
import { env } from '@/utils/env';
import Cookies from 'js-cookie';
import { useAuth } from '@/contexts/AuthContext';

export default function Header() {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const pathname = usePathname();
  const { isAuthenticated, setIsAuthenticated } = useAuth();

  const handleSignOut = () => {
    Cookies.remove(env.jwtStorageKey);
    setIsAuthenticated(false);
    setIsMenuOpen(false);
    window.location.href = '/';
  };

  const handleLinkClick = () => {
    setIsMenuOpen(false);
  };

  const navLinks = [
    { href: '/', label: 'Home' },
    { href: '/about', label: 'About' },
    ...(isAuthenticated ? [{ href: '/chat', label: 'Chat' }] : []),
    { href: '/privacy', label: 'Privacy' },
  ];

  const authLinks = isAuthenticated ? (
    <button
      onClick={handleSignOut}
      className="text-gray-700 hover:text-gray-900"
    >
      Sign Out
    </button>
  ) : (
    <div className="flex items-center space-x-4">
      <Link
        href="/login"
        className="text-gray-700 hover:text-gray-900"
      >
        Sign In
      </Link>
      <Link
        href="/register"
        className="bg-blue-600 text-white hover:bg-blue-700 py-2 px-4 rounded-md"
      >
        Register
      </Link>
    </div>
  );

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
              className={`${isMenuOpen ? 'hidden' : 'block'} h-6 w-6`}
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M4 6h16M4 12h16M4 18h16"
              />
            </svg>
            <svg
              className={`${isMenuOpen ? 'block' : 'hidden'} h-6 w-6`}
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M6 18L18 6M6 6l12 12"
              />
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
            {authLinks}
          </nav>
        </div>

        {/* Mobile Navigation */}
        <nav
          className={`${
            isMenuOpen ? 'block' : 'hidden'
          } md:hidden mt-4 pb-4 space-y-4`}
          data-testid="mobile-menu"
        >
          {navLinks.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className={`block text-gray-700 hover:text-gray-900 py-2 ${
                pathname === link.href ? 'font-semibold' : ''
              }`}
              onClick={handleLinkClick}
            >
              {link.label}
            </Link>
          ))}
          {isAuthenticated ? (
            <button
              onClick={handleSignOut}
              className="block text-gray-700 hover:text-gray-900 py-2"
            >
              Sign Out
            </button>
          ) : (
            <>
              <Link
                href="/login"
                className="block text-gray-700 hover:text-gray-900 py-2"
                onClick={handleLinkClick}
              >
                Sign In
              </Link>
              <Link
                href="/register"
                className="block bg-blue-600 text-white hover:bg-blue-700 py-2 px-4 rounded-md text-center"
                onClick={handleLinkClick}
              >
                Register
              </Link>
            </>
          )}
        </nav>
      </div>
    </header>
  );
}
