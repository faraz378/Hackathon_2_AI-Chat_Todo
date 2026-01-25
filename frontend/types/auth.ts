/**
 * Authentication type definitions
 * Matches backend Pydantic schemas from Spec-2
 */

/**
 * User registration request payload
 * POST /auth/signup
 */
export interface SignupRequest {
  email: string;
  password: string;
}

/**
 * User sign-in request payload
 * POST /auth/signin
 */
export interface SigninRequest {
  email: string;
  password: string;
}

/**
 * JWT token response from backend
 * Returned by POST /auth/signin
 */
export interface TokenResponse {
  access_token: string;
  token_type: 'bearer';
  expires_in: number;  // Token expiration in seconds
}

/**
 * User registration response
 * Returned by POST /auth/signup
 */
export interface SignupResponse {
  message: string;
  user_id: number;
}

/**
 * Decoded JWT payload (client-side only, for display)
 * Backend is authoritative source
 */
export interface JWTPayload {
  sub: string;        // user_id as string (JWT standard)
  email: string;
  exp: number;        // expiration timestamp (Unix time)
  iat?: number;       // issued at timestamp (optional)
}

/**
 * User object for frontend state
 * Derived from JWT payload
 */
export interface User {
  id: number;
  email: string;
}
