# Implementation Plan: Frontend & Integration

**Branch**: `003-frontend-integration` | **Date**: 2026-01-13 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-frontend-integration/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Build a Next.js 16+ frontend application that integrates with the FastAPI backend (Spec-1) and authentication system (Spec-2). The frontend provides user registration, sign-in, and task management UI with JWT-based authentication, responsive design, and comprehensive error handling. All API communication follows the contracts defined in Spec-1 and Spec-2, with automatic JWT token injection for authenticated requests.

## Technical Context

**Language/Version**: TypeScript 5.x with Next.js 16+ (App Router)
**Primary Dependencies**:
- Next.js 16+ (App Router, React Server Components)
- React 19+
- TypeScript 5.x
- Tailwind CSS 3.x (styling)
- Zod (form validation)
- Fetch API (HTTP client)

**Storage**: Browser localStorage for JWT token persistence, no direct database access
**Testing**: Jest + React Testing Library for component tests, Playwright for E2E tests
**Target Platform**: Modern web browsers (Chrome 90+, Firefox 88+, Safari 14+, Edge 90+)
**Project Type**: Web application (frontend only, consumes backend APIs)
**Performance Goals**:
- Initial page load < 3 seconds
- Task list render < 1 second after API response
- Form submission feedback < 100ms
- Lighthouse score > 90 for Performance and Accessibility

**Constraints**:
- Must use Next.js App Router (not Pages Router)
- Stateless frontend (no server-side session management)
- All protected routes require JWT authentication
- Must handle token expiration gracefully
- Responsive design (320px - 1920px viewports)
- No offline support or service workers

**Scale/Scope**:
- 5 pages (landing, signup, signin, dashboard, task detail/edit)
- ~15 React components (forms, task list, task item, layout, navigation)
- 1 API client module with automatic JWT injection
- 1 authentication context provider
- Integration with 7 backend endpoints (2 auth + 5 task CRUD)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. Spec-Driven Development ✅
- **Status**: PASS
- **Evidence**: Feature has approved spec.md with 4 user stories, 24 functional requirements, and 8 success criteria
- **Compliance**: Implementation will follow spec → plan → tasks → implement workflow

### II. Agentic Workflow Compliance ✅
- **Status**: PASS
- **Evidence**: Using /sp.plan command to generate plan, will use /sp.tasks for task breakdown, /sp.implement for execution
- **Agent Usage**: Frontend Agent will be used for Next.js pages and React components

### III. Security-First Design ✅
- **Status**: PASS
- **Evidence**:
  - JWT tokens stored securely in localStorage (not in URLs or cookies without httpOnly)
  - All protected routes require authentication
  - Automatic token injection in API requests via Authorization header
  - Token expiration handling with redirect to signin
  - No sensitive data exposed in browser console or URLs
- **Compliance**: Frontend enforces authentication at route level and API client level

### IV. Deterministic Behavior ✅
- **Status**: PASS
- **Evidence**:
  - API client follows REST conventions from Spec-1 and Spec-2
  - Error handling matches backend error schema (ErrorCode enum)
  - Form validation with Zod ensures consistent input handling
  - Loading states prevent race conditions from duplicate submissions
- **Compliance**: Frontend behavior is predictable and matches backend contracts

### V. Full-Stack Coherence ✅
- **Status**: PASS
- **Evidence**:
  - Frontend consumes exact API contracts from Spec-1 (task CRUD) and Spec-2 (auth)
  - TypeScript types will mirror backend Pydantic schemas
  - Error codes match backend ErrorCode enum
  - JWT token format matches backend expectations (Bearer token in Authorization header)
- **Compliance**: No mismatches between frontend and backend contracts

### VI. Technology Stack Adherence ✅
- **Status**: PASS
- **Evidence**: Using Next.js 16+ App Router as specified in constitution
- **Compliance**: No deviations from approved stack

### VII. Multi-User Data Isolation ✅
- **Status**: PASS
- **Evidence**:
  - JWT token contains user_id, automatically included in all API requests
  - Backend enforces user isolation (verified in Spec-2)
  - Frontend displays only data returned by backend (no client-side filtering needed)
  - User cannot manipulate user_id in requests (extracted from JWT by backend)
- **Compliance**: Frontend relies on backend enforcement, does not bypass isolation

### Gate Decision: ✅ PROCEED TO PHASE 0
All constitution principles are satisfied. No violations to justify.

---

## Post-Design Constitution Re-Check

*Re-evaluated after Phase 1 design completion*

### I. Spec-Driven Development ✅
- **Status**: PASS
- **Evidence**: Complete plan with research.md (10 decisions), data-model.md (types, state management), contracts (API types), and quickstart.md (setup guide)

### II. Agentic Workflow Compliance ✅
- **Status**: PASS
- **Evidence**: Plan follows workflow, ready for /sp.tasks to generate task breakdown

### III. Security-First Design ✅
- **Status**: PASS
- **Evidence**:
  - Token storage strategy defined (localStorage + cookies)
  - API client automatically injects JWT in Authorization header
  - 401 errors trigger automatic signout and redirect
  - No sensitive data in URLs or console logs
  - Type guards prevent malformed data

### IV. Deterministic Behavior ✅
- **Status**: PASS
- **Evidence**:
  - TypeScript types mirror backend schemas exactly
  - Zod validation ensures consistent input handling
  - Error codes match backend ErrorCode enum
  - API client has predictable error handling (401 → redirect, 4xx/5xx → ApiError)

### V. Full-Stack Coherence ✅
- **Status**: PASS
- **Evidence**:
  - All TypeScript types in contracts/api-types.ts match backend Pydantic schemas
  - API endpoints match Spec-1 and Spec-2 contracts
  - Error handling matches backend error schema
  - JWT format matches backend expectations

### VI. Technology Stack Adherence ✅
- **Status**: PASS
- **Evidence**: Next.js 16+ App Router confirmed in research.md and data-model.md

### VII. Multi-User Data Isolation ✅
- **Status**: PASS
- **Evidence**:
  - Frontend includes user_id from JWT in all API requests
  - Backend enforces isolation (verified in Spec-2)
  - No client-side user_id manipulation possible
  - Type safety prevents accidental data leaks

### Final Gate Decision: ✅ PROCEED TO PHASE 2 (/sp.tasks)
All constitution principles remain satisfied after design phase. Implementation plan is complete and ready for task breakdown.

## Project Structure

### Documentation (this feature)

```text
specs/003-frontend-integration/
├── spec.md              # Feature specification (completed)
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (technology decisions)
├── data-model.md        # Phase 1 output (TypeScript types, state management)
├── quickstart.md        # Phase 1 output (setup and testing guide)
├── contracts/           # Phase 1 output (TypeScript API client interfaces)
│   └── api-types.ts     # TypeScript types matching backend schemas
├── checklists/
│   └── requirements.md  # Specification validation (completed)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
frontend/
├── src/
│   ├── app/                    # Next.js App Router pages
│   │   ├── layout.tsx          # Root layout with auth provider
│   │   ├── page.tsx            # Landing page (public)
│   │   ├── signup/
│   │   │   └── page.tsx        # Signup page (public)
│   │   ├── signin/
│   │   │   └── page.tsx        # Signin page (public)
│   │   └── dashboard/
│   │       ├── page.tsx        # Task list (protected)
│   │       └── [taskId]/
│   │           └── page.tsx    # Task detail/edit (protected)
│   ├── components/             # React components
│   │   ├── auth/
│   │   │   ├── SignupForm.tsx
│   │   │   ├── SigninForm.tsx
│   │   │   └── ProtectedRoute.tsx
│   │   ├── tasks/
│   │   │   ├── TaskList.tsx
│   │   │   ├── TaskItem.tsx
│   │   │   ├── TaskForm.tsx
│   │   │   └── EmptyState.tsx
│   │   ├── layout/
│   │   │   ├── Header.tsx
│   │   │   ├── Navigation.tsx
│   │   │   └── Footer.tsx
│   │   └── ui/
│   │       ├── Button.tsx
│   │       ├── Input.tsx
│   │       ├── LoadingSpinner.tsx
│   │       └── ErrorMessage.tsx
│   ├── lib/                    # Core utilities
│   │   ├── api/
│   │   │   ├── client.ts       # API client with JWT injection
│   │   │   ├── auth.ts         # Auth API calls (signup, signin)
│   │   │   └── tasks.ts        # Task API calls (CRUD)
│   │   ├── auth/
│   │   │   ├── context.tsx     # Auth context provider
│   │   │   ├── hooks.ts        # useAuth, useRequireAuth hooks
│   │   │   └── storage.ts      # Token storage (localStorage)
│   │   └── validation/
│   │       └── schemas.ts      # Zod validation schemas
│   ├── types/                  # TypeScript type definitions
│   │   ├── api.ts              # API request/response types
│   │   ├── auth.ts             # Auth-related types
│   │   └── task.ts             # Task-related types
│   └── styles/
│       └── globals.css         # Global styles (Tailwind)
├── public/                     # Static assets
├── tests/
│   ├── components/             # Component tests (Jest + RTL)
│   └── e2e/                    # End-to-end tests (Playwright)
├── package.json
├── tsconfig.json
├── tailwind.config.js
├── next.config.js
└── .env.local.example          # Environment variables template

backend/                        # Existing from Spec-1 and Spec-2
└── [existing backend structure]
```

**Structure Decision**: Using Next.js App Router structure with clear separation of concerns:
- `app/` directory for routing and pages (App Router convention)
- `components/` for reusable UI components organized by domain
- `lib/` for business logic, API clients, and utilities
- `types/` for TypeScript type definitions matching backend schemas
- Frontend is in `frontend/` directory, backend already exists in `backend/`

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

N/A - No constitution violations. All principles satisfied without exceptions.
