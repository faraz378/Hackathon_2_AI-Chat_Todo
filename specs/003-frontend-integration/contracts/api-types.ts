/**
 * API Type Definitions for Frontend Integration
 *
 * This file contains TypeScript types that mirror the backend API contracts
 * from Spec-1 (Backend Core) and Spec-2 (Authentication & Security).
 *
 * These types are used by the API client (lib/api/client.ts) to ensure
 * type-safe communication with the backend.
 */

// ============================================================================
// Authentication Types (Spec-2)
// ============================================================================

/**
 * POST /auth/signup - Request body
 */
export interface SignupRequest {
  email: string;
  password: string;
}

/**
 * POST /auth/signup - Response body (201 Created)
 */
export interface SignupResponse {
  message: string;
  user_id: number;
}

/**
 * POST /auth/signin - Request body
 */
export interface SigninRequest {
  email: string;
  password: string;
}

/**
 * POST /auth/signin - Response body (200 OK)
 */
export interface TokenResponse {
  access_token: string;
  token_type: 'bearer';
}

/**
 * Decoded JWT payload (client-side only, for display purposes)
 * Backend is the authoritative source for user identity
 */
export interface JWTPayload {
  sub: number;        // user_id
  email: string;
  exp: number;        // expiration timestamp (Unix time)
  iat?: number;       // issued at timestamp (optional)
}

/**
 * User object derived from JWT payload
 */
export interface User {
  id: number;
  email: string;
}

// ============================================================================
// Task Types (Spec-1)
// ============================================================================

/**
 * Task object returned by all task endpoints
 * Matches backend TaskResponse schema
 */
export interface Task {
  id: number;
  title: string;
  description: string | null;
  completed: boolean;
  user_id: number;
  created_at: string;      // ISO 8601 format
  updated_at: string;      // ISO 8601 format
}

/**
 * POST /users/{user_id}/tasks - Request body
 */
export interface TaskCreate {
  title: string;
  description?: string;
}

/**
 * PUT /users/{user_id}/tasks/{task_id} - Request body
 */
export interface TaskUpdate {
  title?: string;
  description?: string;
  completed?: boolean;
}

/**
 * PATCH /users/{user_id}/tasks/{task_id}/complete - Request body
 */
export interface TaskComplete {
  completed: boolean;
}

// ============================================================================
// Error Types (Spec-2)
// ============================================================================

/**
 * Error codes returned by backend
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
   */
  getUserMessage(): string {
    switch (this.code) {
      case ErrorCode.EMAIL_EXISTS:
        return 'This email is already registered. Please sign in instead.';
      case ErrorCode.INVALID_CREDENTIALS:
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

// ============================================================================
// API Client Interface
// ============================================================================

/**
 * API client methods for authentication
 */
export interface AuthAPI {
  /**
   * Register a new user
   * @throws ApiError with EMAIL_EXISTS if email already registered
   * @throws ApiError with VALIDATION_ERROR if input invalid
   */
  signup(data: SignupRequest): Promise<SignupResponse>;

  /**
   * Sign in an existing user
   * @throws ApiError with INVALID_CREDENTIALS if credentials wrong
   */
  signin(data: SigninRequest): Promise<TokenResponse>;
}

/**
 * API client methods for task management
 * All methods require authentication (JWT token)
 */
export interface TaskAPI {
  /**
   * Get all tasks for the authenticated user
   * @throws ApiError with EXPIRED_TOKEN if token expired
   * @throws ApiError with FORBIDDEN if user_id mismatch
   */
  getTasks(userId: number): Promise<Task[]>;

  /**
   * Get a single task by ID
   * @throws ApiError with NOT_FOUND if task doesn't exist
   * @throws ApiError with FORBIDDEN if task belongs to another user
   */
  getTask(userId: number, taskId: number): Promise<Task>;

  /**
   * Create a new task
   * @throws ApiError with VALIDATION_ERROR if input invalid
   */
  createTask(userId: number, data: TaskCreate): Promise<Task>;

  /**
   * Update an existing task
   * @throws ApiError with NOT_FOUND if task doesn't exist
   * @throws ApiError with FORBIDDEN if task belongs to another user
   */
  updateTask(userId: number, taskId: number, data: TaskUpdate): Promise<Task>;

  /**
   * Delete a task
   * @throws ApiError with NOT_FOUND if task doesn't exist
   * @throws ApiError with FORBIDDEN if task belongs to another user
   */
  deleteTask(userId: number, taskId: number): Promise<void>;
}

// ============================================================================
// API Configuration
// ============================================================================

/**
 * API client configuration
 */
export interface ApiConfig {
  baseUrl: string;
  timeout?: number;
  headers?: Record<string, string>;
}

/**
 * Default API configuration
 */
export const DEFAULT_API_CONFIG: ApiConfig = {
  baseUrl: process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000',
  timeout: 30000, // 30 seconds
  headers: {
    'Content-Type': 'application/json',
  },
};

// ============================================================================
// HTTP Method Types
// ============================================================================

/**
 * HTTP methods supported by API client
 */
export type HttpMethod = 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';

/**
 * Request options for API client
 */
export interface RequestOptions extends Omit<RequestInit, 'method' | 'body'> {
  method?: HttpMethod;
  body?: unknown;
  requiresAuth?: boolean;
}

// ============================================================================
// Endpoint Definitions
// ============================================================================

/**
 * API endpoint paths
 * Centralized for easy maintenance
 */
export const API_ENDPOINTS = {
  // Authentication
  SIGNUP: '/auth/signup',
  SIGNIN: '/auth/signin',

  // Tasks
  TASKS: (userId: number) => `/users/${userId}/tasks`,
  TASK: (userId: number, taskId: number) => `/users/${userId}/tasks/${taskId}`,
} as const;

// ============================================================================
// Type Guards
// ============================================================================

/**
 * Type guard to check if error is an ApiError
 */
export function isApiError(error: unknown): error is ApiError {
  return error instanceof ApiError;
}

/**
 * Type guard to check if response is an ErrorResponse
 */
export function isErrorResponse(data: unknown): data is ErrorResponse {
  return (
    typeof data === 'object' &&
    data !== null &&
    'error' in data &&
    typeof (data as ErrorResponse).error === 'object' &&
    'code' in (data as ErrorResponse).error &&
    'message' in (data as ErrorResponse).error
  );
}

/**
 * Type guard to check if token response is valid
 */
export function isTokenResponse(data: unknown): data is TokenResponse {
  return (
    typeof data === 'object' &&
    data !== null &&
    'access_token' in data &&
    'token_type' in data &&
    typeof (data as TokenResponse).access_token === 'string' &&
    (data as TokenResponse).token_type === 'bearer'
  );
}

/**
 * Type guard to check if task is valid
 */
export function isTask(data: unknown): data is Task {
  return (
    typeof data === 'object' &&
    data !== null &&
    'id' in data &&
    'title' in data &&
    'completed' in data &&
    'user_id' in data &&
    typeof (data as Task).id === 'number' &&
    typeof (data as Task).title === 'string' &&
    typeof (data as Task).completed === 'boolean' &&
    typeof (data as Task).user_id === 'number'
  );
}
