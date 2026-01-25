/**
 * Next.js Middleware for protected route enforcement
 * Redirects unauthenticated users to signin page
 * Validates JWT token signature and expiration
 */

import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';
import { jwtVerify } from 'jose';

/**
 * Validate redirect URL to prevent open redirect attacks
 * Only allows relative paths starting with /
 */
function isValidRedirect(path: string): boolean {
  // Only allow relative paths starting with /
  // Reject protocol-relative URLs (//) and absolute URLs
  return path.startsWith('/') && !path.startsWith('//');
}

/**
 * Redirect to signin page with optional redirect parameter
 */
function redirectToSignin(request: NextRequest, clearCookie: boolean = false): NextResponse {
  const signinUrl = new URL('/signin', request.url);
  const redirectPath = request.nextUrl.pathname;

  // Only set redirect parameter if it's a valid relative path
  if (isValidRedirect(redirectPath)) {
    signinUrl.searchParams.set('redirect', redirectPath);
  }

  const response = NextResponse.redirect(signinUrl);

  // Clear invalid cookie if requested
  if (clearCookie) {
    response.cookies.delete('auth_token');
  }

  return response;
}

export async function middleware(request: NextRequest) {
  const token = request.cookies.get('auth_token')?.value;
  const isProtectedRoute = request.nextUrl.pathname.startsWith('/dashboard');

  // Check if accessing protected route
  if (isProtectedRoute) {
    // No token present
    if (!token) {
      return redirectToSignin(request);
    }

    // Validate token signature and expiration
    try {
      const secret = new TextEncoder().encode(process.env.JWT_SECRET);

      if (!process.env.JWT_SECRET) {
        console.error('JWT_SECRET environment variable is not set');
        return redirectToSignin(request, true);
      }

      // Verify token signature and expiration
      await jwtVerify(token, secret, {
        algorithms: ['HS256'],
      });

      // Token is valid, allow request to proceed
      return NextResponse.next();
    } catch (error) {
      // Token is invalid or expired
      console.error('Token validation failed:', error);
      return redirectToSignin(request, true);
    }
  }

  return NextResponse.next();
}

export const config = {
  matcher: ['/dashboard/:path*'],
};
