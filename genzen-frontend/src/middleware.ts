import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';
import { env } from '@/utils/env';

export function middleware(request: NextRequest) {
  // Get the token from cookies
  const token = request.cookies.get(env.jwtStorageKey)?.value;

  // Check if the request is for the chat page
  if (request.nextUrl.pathname.startsWith('/chat')) {
    // If no token is present, redirect to login
    if (!token) {
      const loginUrl = new URL('/login', request.url);
      // Add the current URL as a redirect parameter
      loginUrl.searchParams.set('redirect', request.nextUrl.pathname);
      return NextResponse.redirect(loginUrl);
    }
  }

  return NextResponse.next();
}

// Configure which routes to run middleware on
export const config = {
  matcher: [
    '/chat/:path*',
    '/api/chat/:path*',
  ],
}; 