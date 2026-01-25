# Research & Technology Decisions: Frontend & Integration

**Feature**: 003-frontend-integration
**Date**: 2026-01-13
**Purpose**: Document technology choices, architecture patterns, and best practices for Next.js frontend

## Decision 1: Next.js App Router Architecture

**Decision**: Use Next.js 16+ App Router with React Server Components (RSC) for routing and page structure

**Rationale**:
- App Router is the modern Next.js architecture (Pages Router is legacy)
- Server Components reduce client-side JavaScript bundle size
- Built-in support for layouts, loading states, and error boundaries
- File-system based routing simplifies navigation structure
- Better performance with automatic code splitting

**Alternatives Considered**:
1. **Pages Router**: Rejected - legacy approach, not recommended for new projects
2. **Client-side routing only (React Router)**: Rejected - loses Next.js benefits (SSR, automatic optimization)
3. **Full Server-Side Rendering**: Rejected - authentication requires client-side state management

**Implementation Pattern**:
```
app/
├── layout.tsx           # Root layout with AuthProvider
├── page.tsx             # Public landing page (Server Component)
├── signup/page.tsx      # Public signup (Client Component for forms)
├── signin/page.tsx      # Public signin (Client Component for forms)
└── dashboard/
    ├── layout.tsx       # Protected layout with auth check
    └── page.tsx         # Task list (Client Component for interactivity)
```

**Key Considerations**:
- Use "use client" directive for components needing interactivity (forms, auth context)
- Server Components for static content and layouts
- Middleware for route protection (redirect unauthenticated users)

---

## Decision 2: Authentication State Management

**Decision**: React Context API with custom hooks for authentication state

**Rationale**:
- Simple, built-in solution (no external state management library needed)
- Sufficient for authentication state (user, token, loading, error)
- Easy to test and understand
- Minimal bundle size impact
- Works well with Next.js App Router

**Alternatives Considered**:
1. **Redux/Redux Toolkit**: Rejected - overkill for simple auth state, adds complexity and bundle size
2. **Zustand**: Rejected - unnecessary dependency for this scope
3. **SWR/React Query**: Rejected - designed for server state, not auth state
4. **localStorage only**: Rejected - no reactive updates across components

**Implementation Pattern**:
```typescript
// lib/auth/context.tsx
interface AuthContextType {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  error: string | null;
  signin: (email: string, password: string) => Promise<void>;
  signup: (email: string, password: string) => Promise<void>;
  signout: () => void;
}

// lib/auth/hooks.ts
export function useAuth() { /* ... */ }
export function useRequireAuth() { /* redirect if not authenticated */ }
```

**Key Considerations**:
- Store token in localStorage for persistence across sessions
- Provide loading state during token validation
- Clear token on signout or 401 errors
- Expose user info from JWT payload (decode client-side for display only)

---

## Decision 3: API Client with JWT Injection

**Decision**: Custom fetch wrapper with automatic JWT header injection and error handling

**Rationale**:
- Native fetch API is sufficient (no need for axios)
- Centralized error handling for consistent UX
- Automatic token injection prevents forgetting Authorization header
- Easy to add request/response interceptors
- TypeScript types ensure type safety

**Alternatives Considered**:
1. **Axios**: Rejected - adds 13KB to bundle, fetch is sufficient
2. **Manual fetch in each component**: Rejected - duplicates token logic, error-prone
3. **SWR/React Query**: Rejected - adds complexity, not needed for simple CRUD

**Implementation Pattern**:
```typescript
// lib/api/client.ts
export async function apiClient<T>(
  endpoint: string,
  options?: RequestInit
): Promise<T> {
  const token = getToken(); // from localStorage
  const headers = {
    'Content-Type': 'application/json',
    ...(token && { Authorization: `Bearer ${token}` }),
    ...options?.headers,
  };

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (response.status === 401) {
    clearToken();
    window.location.href = '/signin';
    throw new Error('Session expired');
  }

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error?.message || 'Request failed');
  }

  return response.json();
}
```

**Key Considerations**:
- Handle 401 globally (token expired, redirect to signin)
- Parse backend error schema (ErrorCode enum)
- Support both authenticated and public endpoints
- TypeScript generics for type-safe responses

---

## Decision 4: Form Validation Strategy

**Decision**: Zod for schema validation with client-side validation before API calls

**Rationale**:
- TypeScript-first schema validation
- Reusable schemas across forms
- Type inference from schemas (no duplicate type definitions)
- Composable and extensible
- Small bundle size (~8KB)

**Alternatives Considered**:
1. **Yup**: Rejected - larger bundle, less TypeScript-friendly
2. **React Hook Form + Yup**: Rejected - React Hook Form adds complexity for simple forms
3. **Manual validation**: Rejected - error-prone, not reusable
4. **HTML5 validation only**: Rejected - inconsistent UX, limited error messages

**Implementation Pattern**:
```typescript
// lib/validation/schemas.ts
import { z } from 'zod';

export const signupSchema = z.object({
  email: z.string().email('Invalid email format'),
  password: z.string().min(8, 'Password must be at least 8 characters'),
});

export const taskSchema = z.object({
  title: z.string().min(1, 'Title is required').max(200),
  description: z.string().max(1000).optional(),
});

// Infer TypeScript types from schemas
export type SignupInput = z.infer<typeof signupSchema>;
export type TaskInput = z.infer<typeof taskSchema>;
```

**Key Considerations**:
- Validate on form submission (not on every keystroke for better UX)
- Display field-specific errors next to inputs
- Backend validation is still authoritative (frontend is UX enhancement)

---

## Decision 5: Protected Route Implementation

**Decision**: Next.js middleware for route protection with redirect to signin

**Rationale**:
- Middleware runs before page renders (no flash of protected content)
- Centralized auth logic (not duplicated in every protected page)
- Works with App Router architecture
- Can check token validity before rendering

**Alternatives Considered**:
1. **Component-level protection**: Rejected - causes flash of content, duplicates logic
2. **Higher-order component (HOC)**: Rejected - not idiomatic in App Router
3. **Server-side auth check in each page**: Rejected - duplicates logic, harder to maintain

**Implementation Pattern**:
```typescript
// middleware.ts (root level)
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  const token = request.cookies.get('token')?.value;
  const isProtectedRoute = request.nextUrl.pathname.startsWith('/dashboard');

  if (isProtectedRoute && !token) {
    return NextResponse.redirect(new URL('/signin', request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ['/dashboard/:path*'],
};
```

**Key Considerations**:
- Store token in both localStorage (for API calls) and cookies (for middleware)
- Middleware only checks token existence, not validity (backend validates)
- Public routes (/signup, /signin, /) are not protected

---

## Decision 6: Loading and Error State Management

**Decision**: React Suspense boundaries with loading.tsx and error.tsx files (App Router convention)

**Rationale**:
- Built-in Next.js App Router feature
- Automatic loading states during navigation
- Error boundaries catch runtime errors
- Consistent UX across all pages
- No manual loading state management needed

**Alternatives Considered**:
1. **Manual loading state in each component**: Rejected - duplicates logic, inconsistent UX
2. **Global loading indicator**: Rejected - doesn't show which part is loading
3. **No loading states**: Rejected - poor UX on slow connections

**Implementation Pattern**:
```typescript
// app/dashboard/loading.tsx
export default function Loading() {
  return <LoadingSpinner />;
}

// app/dashboard/error.tsx
'use client';
export default function Error({ error, reset }: { error: Error; reset: () => void }) {
  return (
    <div>
      <h2>Something went wrong!</h2>
      <p>{error.message}</p>
      <button onClick={reset}>Try again</button>
    </div>
  );
}
```

**Additional Patterns**:
- Form submission loading: Disable button, show spinner
- API call loading: Use React state (isLoading) in components
- Optimistic updates: Update UI immediately, rollback on error

**Key Considerations**:
- loading.tsx shows during page navigation
- error.tsx catches component errors (not API errors)
- API errors handled in try-catch blocks with user-friendly messages

---

## Decision 7: Responsive Design Strategy

**Decision**: Tailwind CSS with mobile-first responsive utilities

**Rationale**:
- Utility-first CSS reduces custom CSS
- Built-in responsive breakpoints (sm, md, lg, xl)
- Mobile-first approach (default styles for mobile, override for desktop)
- Excellent developer experience with IntelliSense
- Small production bundle (unused styles purged)

**Alternatives Considered**:
1. **CSS Modules**: Rejected - more verbose, manual responsive logic
2. **Styled Components**: Rejected - runtime CSS-in-JS has performance cost
3. **Bootstrap**: Rejected - opinionated design, larger bundle
4. **Plain CSS with media queries**: Rejected - more code, less maintainable

**Implementation Pattern**:
```tsx
// Mobile-first responsive component
<div className="
  flex flex-col gap-4           // Mobile: vertical stack
  md:flex-row md:gap-6          // Tablet: horizontal layout
  lg:max-w-6xl lg:mx-auto       // Desktop: constrained width
">
  <TaskList />
</div>
```

**Breakpoints**:
- Default (< 640px): Mobile
- sm (640px+): Large mobile / small tablet
- md (768px+): Tablet
- lg (1024px+): Desktop
- xl (1280px+): Large desktop

**Key Considerations**:
- Test on 320px (iPhone SE), 768px (iPad), 1920px (desktop)
- Touch-friendly targets (min 44x44px for buttons)
- Readable text sizes (16px minimum)

---

## Decision 8: TypeScript Type Safety

**Decision**: Strict TypeScript with types mirroring backend Pydantic schemas

**Rationale**:
- Catch type errors at compile time
- IntelliSense for better developer experience
- Self-documenting code
- Prevents runtime errors from API mismatches

**Implementation Pattern**:
```typescript
// types/task.ts (mirrors backend TaskResponse schema)
export interface Task {
  id: number;
  title: string;
  description: string | null;
  completed: boolean;
  user_id: number;
  created_at: string;
  updated_at: string;
}

// types/auth.ts (mirrors backend auth schemas)
export interface SignupRequest {
  email: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: 'bearer';
}

export interface User {
  id: number;
  email: string;
}
```

**Key Considerations**:
- Keep frontend types in sync with backend schemas
- Use strict mode in tsconfig.json
- Avoid `any` type (use `unknown` if type is truly unknown)

---

## Decision 9: Testing Strategy

**Decision**: Multi-layer testing with Jest + React Testing Library (unit/component) and Playwright (E2E)

**Rationale**:
- Jest + RTL is standard for React component testing
- Playwright provides reliable E2E tests across browsers
- Component tests verify UI logic in isolation
- E2E tests verify full user flows

**Test Coverage**:
1. **Component Tests** (Jest + RTL):
   - Form validation (SignupForm, SigninForm, TaskForm)
   - Task list rendering (TaskList, TaskItem)
   - Loading and error states
   - Button interactions

2. **E2E Tests** (Playwright):
   - Complete signup → signin → create task → edit task → delete task flow
   - Protected route redirect (unauthenticated user)
   - Token expiration handling
   - Multi-user isolation (two users, verify data separation)

**Alternatives Considered**:
1. **Cypress**: Rejected - Playwright has better TypeScript support and faster execution
2. **No E2E tests**: Rejected - critical for verifying full-stack integration
3. **Only E2E tests**: Rejected - slow feedback loop, harder to debug

**Key Considerations**:
- Mock API calls in component tests (don't hit real backend)
- Use real backend in E2E tests (verify actual integration)
- Test responsive behavior (mobile and desktop viewports)

---

## Decision 10: Environment Configuration

**Decision**: Environment variables for API base URL and configuration

**Rationale**:
- Different API URLs for development, staging, production
- No hardcoded URLs in code
- Easy to configure per environment

**Implementation Pattern**:
```bash
# .env.local (development)
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000

# .env.production (production)
NEXT_PUBLIC_API_BASE_URL=https://api.production.com
```

**Key Considerations**:
- Use `NEXT_PUBLIC_` prefix for client-side variables
- Never commit .env.local (add to .gitignore)
- Provide .env.local.example for documentation

---

## Summary of Technology Stack

| Layer | Technology | Rationale |
|-------|-----------|-----------|
| Framework | Next.js 16+ App Router | Modern React framework with SSR, routing, optimization |
| Language | TypeScript 5.x | Type safety, better DX, catch errors at compile time |
| Styling | Tailwind CSS 3.x | Utility-first, responsive, small bundle |
| Validation | Zod | TypeScript-first, type inference, composable |
| State Management | React Context | Simple, sufficient for auth state |
| API Client | Fetch API + wrapper | Native, lightweight, automatic JWT injection |
| Testing (Unit) | Jest + RTL | Standard React testing tools |
| Testing (E2E) | Playwright | Reliable, fast, multi-browser support |
| Forms | Controlled components | React standard, works with Zod validation |

---

## Integration Points with Backend

### Spec-1 (Backend Core) Endpoints:
- `GET /users/{user_id}/tasks` - Fetch all tasks
- `POST /users/{user_id}/tasks` - Create task
- `GET /users/{user_id}/tasks/{task_id}` - Get single task
- `PUT /users/{user_id}/tasks/{task_id}` - Update task
- `DELETE /users/{user_id}/tasks/{task_id}` - Delete task

### Spec-2 (Authentication) Endpoints:
- `POST /auth/signup` - User registration
- `POST /auth/signin` - User authentication (returns JWT)

### Error Handling:
Frontend must handle backend error codes:
- `EMAIL_EXISTS` - Email already registered
- `INVALID_CREDENTIALS` - Wrong email/password
- `MISSING_TOKEN` - No Authorization header
- `INVALID_TOKEN` - Malformed or invalid JWT
- `EXPIRED_TOKEN` - JWT past expiration
- `FORBIDDEN` - User accessing another user's data
- `VALIDATION_ERROR` - Invalid request data

---

## Open Questions Resolved

All technology decisions are finalized. No open questions remain.
