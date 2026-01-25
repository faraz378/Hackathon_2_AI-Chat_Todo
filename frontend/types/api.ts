/**
 * API error types and utilities
 * Matches backend error schema from Spec-2
 */

/**
 * Error codes from backend
 * Matches backend ErrorCode enum
 */
export enum ErrorCode {
  // Authentication errors
  EMAIL_EXISTS = 'EMAIL_EXISTS',
  INVALID_CREDENTIALS = 'INVALID_CREDENTIALS',
  MISSING_TOKEN = 'MISSING_TOKEN',
  INVALID_TOKEN = 'INVALID_TOKEN',
  EXPIRED_TOKEN = 'EXPIRED_TOKEN',
  FORBIDDEN = 'FORBIDDEN',

  // Validation errors
  VALIDATION_ERROR = 'VALIDATION_ERROR',

  // Resource errors
  NOT_FOUND = 'NOT_FOUND',

  // Server errors
  INTERNAL_ERROR = 'INTERNAL_ERROR',
}

/**
 * Error response structure from backend
 * Returned for 4xx and 5xx responses
 */
export interface ErrorResponse {
  error: {
    code: ErrorCode;
    message: string;
    details?: Record<string, unknown>;
  };
}

/**
 * Custom error class for API errors
 * Thrown by API client when requests fail
 */
export class ApiError extends Error {
  constructor(
    public code: ErrorCode,
    message: string,
    public details?: Record<string, unknown>
  ) {
    super(message);
    this.name = 'ApiError';
  }

  /**
   * Check if error is a specific error code
   */
  is(code: ErrorCode): boolean {
    return this.code === code;
  }

  /**
   * Get user-friendly error message
   * Uses generic messages to prevent user enumeration attacks
   */
  getUserMessage(): string {
    switch (this.code) {
      case ErrorCode.EMAIL_EXISTS:
      case ErrorCode.INVALID_CREDENTIALS:
        // Use same message for both to prevent email enumeration
        return 'Invalid email or password. Please try again.';
      case ErrorCode.EXPIRED_TOKEN:
        return 'Your session has expired. Please sign in again.';
      case ErrorCode.FORBIDDEN:
        return 'You do not have permission to access this resource.';
      case ErrorCode.NOT_FOUND:
        return 'The requested resource was not found.';
      case ErrorCode.VALIDATION_ERROR:
        return this.message; // Use specific validation message
      default:
        return 'An unexpected error occurred. Please try again.';
    }
  }
}
