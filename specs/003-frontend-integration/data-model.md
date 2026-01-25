# Data Model & State Management: Frontend & Integration

**Feature**: 003-frontend-integration
**Date**: 2026-01-13
**Purpose**: Define TypeScript types, state management patterns, and data flow for the Next.js frontend

## Overview

The frontend data model mirrors the backend Pydantic schemas from Spec-1 and Spec-2. All types are defined in TypeScript for compile-time type safety. State management is minimal, using React Context for authentication state and component-level state for UI interactions.

---

## TypeScript Type Definitions

### Authentication Types

```typescript
// types/auth.ts

/**
 * User registration request payload
 * Matches backend SignupRequest schema
 */
export interface SignupRequest {
  email: string;
  password: string;
}

/**
 * User sign-in request payload
 * Matches backend SigninRequest schema
 */
export interface SigninRequest {
  email: string;
  password: string;
}

/**
 * JWT token response from backend
 * Matches backend TokenResponse schema
 */
export interface TokenResponse {
  access_token: string;
  token_type: 'bearer';
}

/**
 * User registration response
 * Matches backend SignupResponse schema
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
  sub: number;        // user_id
  email: string;
  exp: number;        // expiration timestamp
}

/**
 * User object for frontend state
 * Derived from JWT payload
 */
export interface User {
  id: number;
  email: string;
}
```

### Task Types

```typescript
// types/task.ts

/**
 * Task object returned by backend
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
 * Task creation request payload
 * Matches backend TaskCreate schema
 */
export interface TaskCreate {
  title: string;
  description?: string;
}

/**
 * Task update request payload
 * Matches backend TaskUpdate schema
 */
export interface TaskUpdate {
  title?: string;
  description?: string;
  completed?: boolean;
}

/**
 * Task completion toggle request
 * Matches backend TaskComplete schema
 */
export interface TaskComplete {
  completed: boolean;
}
```

### API Error Types

```typescript
// types/api.ts

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
 * Matches backend ErrorResponse schema
 */
export interface ErrorResponse {
  error: {
    code: ErrorCode;
    message: string;
    details?: Record<string, unknown>;
  };
}

/**
 * API client error (thrown by apiClient)
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
}
```

---

## State Management Architecture

### Authentication State (Global)

**Location**: `lib/auth/context.tsx`

**State Shape**:
```typescript
interface AuthState {
  user: User | null;           // Current authenticated user
  token: string | null;        // JWT access token
  isLoading: boolean;          // Loading state during auth operations
  error: string | null;        // Error message from auth operations
}
```

**Actions**:
```typescript
interface AuthActions {
  signin: (email: string, password: string) => Promise<void>;
  signup: (email: string, password: string) => Promise<void>;
  signout: () => void;
  clearError: () => void;
}
```

**State Flow**:
1. **Initial Load**: Check localStorage for token, decode to get user
2. **Signup**: Call API → Store token → Decode user → Redirect to dashboard
3. **Signin**: Call API → Store token → Decode user → Redirect to dashboard
4. **Signout**: Clear token from localStorage → Clear user state → Redirect to signin
5. **Token Expiration**: API returns 401 → Clear token → Redirect to signin

**Persistence**:
- Token stored in localStorage (key: `auth_token`)
- Token also stored in cookie for middleware access
- User derived from token on every page load (decode JWT)

### Task State (Component-Level)

**Location**: Individual components (TaskList, TaskForm, etc.)

**State Shape**:
```typescript
// In TaskList component
interface TaskListState {
  tasks: Task[];
  isLoading: boolean;
  error: string | null;
}

// In TaskForm component
interface TaskFormState {
  title: string;
  description: string;
  isSubmitting: boolean;
  errors: Record<string, string>;
}
```

**Why Component-Level**:
- Tasks are only used in dashboard pages
- No need for global state (not shared across unrelated components)
- Simpler to reason about (state lives where it's used)
- Easier to test (no global state dependencies)

**Data Fetching Pattern**:
```typescript
// In TaskList component
useEffect(() => {
  async function fetchTasks() {
    setIsLoading(true);
    try {
      const tasks = await getTasks(user.id);
      setTasks(tasks);
    } catch (error) {
      setError(error.message);
    } finally {
      setIsLoading(false);
    }
  }
  fetchTasks();
}, [user.id]);
```

---

## Data Flow Diagrams

### Authentication Flow

```
┌─────────────┐
│   Browser   │
└──────┬──────┘
       │
       │ 1. User submits signin form
       ▼
┌─────────────────┐
│  SigninForm     │
│  Component      │
└──────┬──────────┘
       │
       │ 2. Call signin() from AuthContext
       ▼
┌─────────────────┐
│  AuthContext    │
│  Provider       │
└──────┬──────────┘
       │
       │ 3. POST /auth/signin
       ▼
┌─────────────────┐
│  API Client     │
│  (lib/api)      │
└──────┬──────────┘
       │
       │ 4. HTTP Request with credentials
       ▼
┌─────────────────┐
│  Backend API    │
│  (FastAPI)      │
└──────┬──────────┘
       │
       │ 5. Return JWT token
       ▼
┌─────────────────┐
│  API Client     │
└──────┬──────────┘
       │
       │ 6. Return token to AuthContext
       ▼
┌─────────────────┐
│  AuthContext    │
└──────┬──────────┘
       │
       │ 7. Store token in localStorage
       │ 8. Decode token to get user
       │ 9. Update state (user, token)
       ▼
┌─────────────────┐
│  SigninForm     │
└──────┬──────────┘
       │
       │ 10. Redirect to /dashboard
       ▼
┌─────────────────┐
│  Dashboard      │
│  Page           │
└─────────────────┘
```

### Task CRUD Flow

```
┌─────────────┐
│  Dashboard  │
│  Page       │
└──────┬──────┘
       │
       │ 1. useEffect on mount
       ▼
┌─────────────────┐
│  TaskList       │
│  Component      │
└──────┬──────────┘
       │
       │ 2. Call getTasks(user_id)
       ▼
┌─────────────────┐
│  API Client     │
│  (lib/api)      │
└──────┬──────────┘
       │
       │ 3. GET /users/{user_id}/tasks
       │    Authorization: Bearer {token}
       ▼
┌─────────────────┐
│  Backend API    │
└──────┬──────────┘
       │
       │ 4. Verify JWT, filter by user_id
       │ 5. Return tasks array
       ▼
┌─────────────────┐
│  API Client     │
└──────┬──────────┘
       │
       │ 6. Return tasks to component
       ▼
┌─────────────────┐
│  TaskList       │
└──────┬──────────┘
       │
       │ 7. Update state (tasks)
       │ 8. Render task items
       ▼
┌─────────────────┐
│  TaskItem       │
│  Components     │
└─────────────────┘
```

### Error Handling Flow

```
┌─────────────┐
│  Component  │
└──────┬──────┘
       │
       │ 1. API call fails
       ▼
┌─────────────────┐
│  API Client     │
└──────┬──────────┘
       │
       │ 2. Check response status
       │
       ├─ 401 Unauthorized
       │  └─> Clear token, redirect to /signin
       │
       ├─ 400/404/500
       │  └─> Parse ErrorResponse, throw ApiError
       │
       └─ Network error
          └─> Throw generic error
       ▼
┌─────────────────┐
│  Component      │
│  (catch block)  │
└──────┬──────────┘
       │
       │ 3. Update error state
       │ 4. Display error message to user
       ▼
┌─────────────────┐
│  ErrorMessage   │
│  Component      │
└─────────────────┘
```

---

## Form Validation Schemas

### Signup/Signin Validation

```typescript
// lib/validation/schemas.ts
import { z } from 'zod';

export const signupSchema = z.object({
  email: z
    .string()
    .min(1, 'Email is required')
    .email('Invalid email format'),
  password: z
    .string()
    .min(8, 'Password must be at least 8 characters')
    .max(100, 'Password is too long'),
});

export const signinSchema = z.object({
  email: z
    .string()
    .min(1, 'Email is required')
    .email('Invalid email format'),
  password: z
    .string()
    .min(1, 'Password is required'),
});

// Type inference
export type SignupFormData = z.infer<typeof signupSchema>;
export type SigninFormData = z.infer<typeof signinSchema>;
```

### Task Validation

```typescript
export const taskCreateSchema = z.object({
  title: z
    .string()
    .min(1, 'Title is required')
    .max(200, 'Title must be 200 characters or less'),
  description: z
    .string()
    .max(1000, 'Description must be 1000 characters or less')
    .optional(),
});

export const taskUpdateSchema = z.object({
  title: z
    .string()
    .min(1, 'Title is required')
    .max(200, 'Title must be 200 characters or less')
    .optional(),
  description: z
    .string()
    .max(1000, 'Description must be 1000 characters or less')
    .optional(),
  completed: z.boolean().optional(),
});

// Type inference
export type TaskFormData = z.infer<typeof taskCreateSchema>;
export type TaskUpdateFormData = z.infer<typeof taskUpdateSchema>;
```

---

## Component State Patterns

### Loading States

```typescript
// Pattern 1: Initial data loading
const [tasks, setTasks] = useState<Task[]>([]);
const [isLoading, setIsLoading] = useState(true);

// Pattern 2: Form submission
const [isSubmitting, setIsSubmitting] = useState(false);

// Pattern 3: Optimistic updates
const [optimisticTasks, setOptimisticTasks] = useState<Task[]>([]);
```

### Error States

```typescript
// Pattern 1: Component-level error
const [error, setError] = useState<string | null>(null);

// Pattern 2: Field-level errors (forms)
const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});

// Pattern 3: Global error (AuthContext)
const { error: authError } = useAuth();
```

### Form States

```typescript
// Controlled form pattern
const [formData, setFormData] = useState<TaskFormData>({
  title: '',
  description: '',
});

const handleChange = (field: keyof TaskFormData, value: string) => {
  setFormData(prev => ({ ...prev, [field]: value }));
};

const handleSubmit = async (e: React.FormEvent) => {
  e.preventDefault();

  // Validate
  const result = taskCreateSchema.safeParse(formData);
  if (!result.success) {
    setFieldErrors(result.error.flatten().fieldErrors);
    return;
  }

  // Submit
  setIsSubmitting(true);
  try {
    await createTask(user.id, result.data);
    // Success: clear form, refresh list
  } catch (error) {
    setError(error.message);
  } finally {
    setIsSubmitting(false);
  }
};
```

---

## Data Synchronization

### Token Synchronization

**Problem**: Token needs to be accessible in both API client (localStorage) and middleware (cookies)

**Solution**: Store token in both locations on signin/signup

```typescript
// lib/auth/storage.ts
export function setToken(token: string) {
  // For API client
  localStorage.setItem('auth_token', token);

  // For middleware
  document.cookie = `token=${token}; path=/; max-age=${24 * 60 * 60}; SameSite=Strict`;
}

export function clearToken() {
  localStorage.removeItem('auth_token');
  document.cookie = 'token=; path=/; max-age=0';
}
```

### Task List Synchronization

**Problem**: Task list needs to update after create/update/delete operations

**Solution**: Refetch tasks after mutations (simple, reliable)

```typescript
// Alternative 1: Refetch (simple, always correct)
async function handleCreateTask(data: TaskFormData) {
  await createTask(user.id, data);
  await fetchTasks(); // Refetch from server
}

// Alternative 2: Optimistic update (faster UX, more complex)
async function handleCreateTask(data: TaskFormData) {
  const tempId = Date.now();
  const optimisticTask = { ...data, id: tempId, completed: false };
  setTasks(prev => [...prev, optimisticTask]);

  try {
    const newTask = await createTask(user.id, data);
    setTasks(prev => prev.map(t => t.id === tempId ? newTask : t));
  } catch (error) {
    setTasks(prev => prev.filter(t => t.id !== tempId));
    throw error;
  }
}
```

**Decision**: Use refetch pattern for simplicity. Optimistic updates can be added later if needed.

---

## Type Safety Guarantees

### API Response Validation

```typescript
// lib/api/client.ts
export async function apiClient<T>(
  endpoint: string,
  options?: RequestInit
): Promise<T> {
  // ... fetch logic ...

  // TypeScript ensures response matches expected type
  const data: T = await response.json();
  return data;
}

// Usage with type safety
const tasks: Task[] = await apiClient<Task[]>('/users/1/tasks');
//    ^-- TypeScript knows this is Task[]
```

### Form Data Validation

```typescript
// Zod ensures runtime validation matches TypeScript types
const result = taskCreateSchema.safeParse(formData);
if (result.success) {
  // result.data is typed as TaskFormData
  await createTask(user.id, result.data);
}
```

---

## Summary

**State Management**:
- Global: Authentication state (React Context)
- Local: Task data, form state, UI state (component useState)

**Type Safety**:
- All API types mirror backend schemas
- Zod validation with type inference
- Strict TypeScript mode enabled

**Data Flow**:
- Unidirectional: User action → API call → State update → UI render
- Error handling at API client level (401 redirects)
- Loading states for all async operations

**Synchronization**:
- Token in localStorage + cookies
- Task list refetched after mutations
- No client-side caching (rely on browser cache)
