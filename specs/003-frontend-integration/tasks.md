# Tasks: Frontend & Integration

**Input**: Design documents from `/specs/003-frontend-integration/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are NOT included in this task breakdown as they were not explicitly requested in the feature specification.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Frontend**: `frontend/src/` for all source code
- **Backend**: Already exists from Spec-1 and Spec-2

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create frontend directory and initialize Next.js 16+ project with TypeScript and Tailwind CSS
- [ ] T002 Install core dependencies: zod for validation, configure tsconfig.json with strict mode
- [ ] T003 [P] Create directory structure: frontend/src/{app,components,lib,types,styles}
- [ ] T004 [P] Configure Tailwind CSS in tailwind.config.js with custom theme and responsive breakpoints
- [ ] T005 [P] Create .env.local.example with NEXT_PUBLIC_API_BASE_URL placeholder
- [ ] T006 [P] Configure next.config.js for production optimization

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T007 [P] Create TypeScript type definitions in frontend/src/types/auth.ts (SignupRequest, SigninRequest, TokenResponse, User, JWTPayload)
- [ ] T008 [P] Create TypeScript type definitions in frontend/src/types/task.ts (Task, TaskCreate, TaskUpdate, TaskComplete)
- [ ] T009 [P] Create TypeScript type definitions in frontend/src/types/api.ts (ErrorCode enum, ErrorResponse, ApiError class)
- [ ] T010 [P] Create token storage utilities in frontend/src/lib/auth/storage.ts (setToken, getToken, clearToken for localStorage and cookies)
- [ ] T011 Create API client base in frontend/src/lib/api/client.ts with automatic JWT injection, 401 handling, and error parsing
- [ ] T012 [P] Create auth API functions in frontend/src/lib/api/auth.ts (signup, signin using API client)
- [ ] T013 [P] Create task API functions in frontend/src/lib/api/tasks.ts (getTasks, getTask, createTask, updateTask, deleteTask using API client)
- [ ] T014 Create AuthContext provider in frontend/src/lib/auth/context.tsx with user, token, loading, error state
- [ ] T015 Create auth hooks in frontend/src/lib/auth/hooks.ts (useAuth, useRequireAuth with redirect logic)
- [ ] T016 [P] Create Zod validation schemas in frontend/src/lib/validation/schemas.ts (signupSchema, signinSchema, taskCreateSchema, taskUpdateSchema)
- [ ] T017 Create root layout in frontend/src/app/layout.tsx with AuthProvider wrapper and global styles
- [ ] T018 [P] Create Next.js middleware in frontend/middleware.ts for protected route enforcement

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - User Registration & Sign In (Priority: P1) 🎯 MVP

**Goal**: Enable users to create accounts and sign in to access the application

**Independent Test**: Navigate to signup page, create account with email/password, verify redirect to dashboard. Sign out, sign in with same credentials, verify access to dashboard.

### Implementation for User Story 1

- [ ] T019 [P] [US1] Create landing page in frontend/src/app/page.tsx with navigation to signup/signin
- [ ] T020 [P] [US1] Create signup page in frontend/src/app/signup/page.tsx with form and error handling
- [ ] T021 [P] [US1] Create signin page in frontend/src/app/signin/page.tsx with form and error handling
- [ ] T022 [P] [US1] Create SignupForm component in frontend/src/components/auth/SignupForm.tsx with Zod validation and loading state
- [ ] T023 [P] [US1] Create SigninForm component in frontend/src/components/auth/SigninForm.tsx with Zod validation and loading state
- [ ] T024 [US1] Integrate SignupForm with AuthContext signup function and handle success/error states
- [ ] T025 [US1] Integrate SigninForm with AuthContext signin function and handle success/error states
- [ ] T026 [US1] Add redirect logic after successful signup/signin to dashboard page
- [ ] T027 [US1] Test protected route redirect: unauthenticated user accessing /dashboard should redirect to /signin

**Checkpoint**: At this point, User Story 1 should be fully functional - users can signup, signin, and be redirected appropriately

---

## Phase 4: User Story 2 - Task Management (Priority: P1) 🎯 MVP

**Goal**: Enable authenticated users to view, create, edit, complete, and delete their tasks

**Independent Test**: Sign in as a user, view empty state, create a task, edit it, mark it complete, delete it. Verify all operations work and UI updates immediately.

### Implementation for User Story 2

- [ ] T028 [P] [US2] Create dashboard page in frontend/src/app/dashboard/page.tsx with task list and create button
- [ ] T029 [P] [US2] Create TaskList component in frontend/src/components/tasks/TaskList.tsx with loading and error states
- [ ] T030 [P] [US2] Create TaskItem component in frontend/src/components/tasks/TaskItem.tsx with complete checkbox, edit, and delete buttons
- [ ] T031 [P] [US2] Create TaskForm component in frontend/src/components/tasks/TaskForm.tsx for create/edit with Zod validation
- [ ] T032 [P] [US2] Create EmptyState component in frontend/src/components/tasks/EmptyState.tsx with prompt to create first task
- [ ] T033 [US2] Integrate TaskList with task API to fetch tasks on mount and display them
- [ ] T034 [US2] Implement task creation flow: TaskForm submission → API call → refresh task list
- [ ] T035 [US2] Implement task update flow: TaskItem edit → TaskForm → API call → refresh task list
- [ ] T036 [US2] Implement task completion toggle: TaskItem checkbox → API call → update UI optimistically
- [ ] T037 [US2] Implement task deletion flow: TaskItem delete button → confirmation → API call → remove from list
- [ ] T038 [US2] Add error handling for all task operations with user-friendly messages
- [ ] T039 [US2] Test user isolation: create second user, verify they only see their own tasks

**Checkpoint**: At this point, User Story 2 should be fully functional - users can perform all CRUD operations on tasks

---

## Phase 5: User Story 3 - Session Management & Sign Out (Priority: P2)

**Goal**: Enable users to sign out and handle expired sessions gracefully

**Independent Test**: Sign in, perform task operations, sign out, verify redirect to signin and token cleared. Manually expire token, attempt operation, verify session expired message and redirect.

### Implementation for User Story 3

- [ ] T040 [P] [US3] Create Header component in frontend/src/components/layout/Header.tsx with sign out button
- [ ] T041 [P] [US3] Create Navigation component in frontend/src/components/layout/Navigation.tsx with user email display
- [ ] T042 [US3] Implement signout function in AuthContext: clear token, clear user state, redirect to signin
- [ ] T043 [US3] Add sign out button to Header component with confirmation dialog
- [ ] T044 [US3] Implement token expiration detection in API client: 401 response → clear token → redirect to signin with message
- [ ] T045 [US3] Add session persistence: on app load, check localStorage for token, decode to get user, update AuthContext
- [ ] T046 [US3] Test session persistence: sign in, close browser, reopen, verify still signed in (if within 24 hours)

**Checkpoint**: At this point, User Story 3 should be fully functional - users can sign out and expired sessions are handled

---

## Phase 6: User Story 4 - Responsive Design & Error Handling (Priority: P2)

**Goal**: Ensure consistent experience across devices and clear feedback for errors and loading states

**Independent Test**: Access application on mobile (320px), tablet (768px), and desktop (1920px) viewports. Trigger validation errors, network errors, and verify appropriate messages. Verify loading indicators appear during operations.

### Implementation for User Story 4

- [ ] T047 [P] [US4] Create Button component in frontend/src/components/ui/Button.tsx with loading state and disabled prop
- [ ] T048 [P] [US4] Create Input component in frontend/src/components/ui/Input.tsx with error message display
- [ ] T049 [P] [US4] Create LoadingSpinner component in frontend/src/components/ui/LoadingSpinner.tsx
- [ ] T050 [P] [US4] Create ErrorMessage component in frontend/src/components/ui/ErrorMessage.tsx with retry button
- [ ] T051 [US4] Update all forms to use Button and Input components with consistent styling
- [ ] T052 [US4] Add loading indicators to all async operations (form submissions, API calls)
- [ ] T053 [US4] Implement form validation error display: show field-specific errors next to inputs
- [ ] T054 [US4] Implement network error handling: catch fetch errors, display user-friendly message with retry
- [ ] T055 [US4] Add responsive layout to dashboard: mobile (single column), tablet (2 columns), desktop (3 columns with max-width)
- [ ] T056 [US4] Add responsive navigation: mobile (hamburger menu), desktop (horizontal nav)
- [ ] T057 [US4] Test responsive design on 320px, 768px, and 1920px viewports, verify all functionality accessible
- [ ] T058 [US4] Add loading.tsx and error.tsx files to app/dashboard/ for Next.js App Router error boundaries

**Checkpoint**: At this point, User Story 4 should be fully functional - responsive design and error handling complete

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Final touches, documentation, and deployment preparation

- [ ] T059 [P] Create frontend README.md with setup instructions, environment variables, and development workflow
- [ ] T060 [P] Add global CSS styles in frontend/src/styles/globals.css for consistent typography and spacing
- [ ] T061 [P] Create Footer component in frontend/src/components/layout/Footer.tsx with copyright and links
- [ ] T062 [P] Add meta tags and SEO optimization to root layout (title, description, viewport)
- [ ] T063 Verify all environment variables are documented in .env.local.example
- [ ] T064 Run production build (npm run build) and verify no errors or warnings
- [ ] T065 Test complete user flow: signup → signin → create task → edit → complete → delete → signout
- [ ] T066 Verify multi-user isolation: two users cannot see each other's tasks
- [ ] T067 Verify token expiration handling: expired token triggers signin redirect
- [ ] T068 Verify responsive design: test on mobile, tablet, desktop viewports

**Checkpoint**: Application is complete, tested, and ready for deployment

---

## Dependencies & Execution Order

### User Story Completion Order

```
Phase 1 (Setup)
    ↓
Phase 2 (Foundational) ← MUST complete before any user story
    ↓
    ├─→ Phase 3 (US1: Auth) ← MUST complete first (blocks US2, US3)
    │       ↓
    │   Phase 4 (US2: Tasks) ← Can start after US1
    │       ↓
    ├─→ Phase 5 (US3: Session) ← Can start after US1
    │
    └─→ Phase 6 (US4: Responsive) ← Can start after US1, US2
            ↓
        Phase 7 (Polish)
```

### Critical Path

1. **Setup** (T001-T006) → **Foundational** (T007-T018) → **US1** (T019-T027) → **US2** (T028-T039)
2. This is the minimum viable product (MVP) path

### Parallel Opportunities

**Within Phase 2 (Foundational)**:
- T007, T008, T009 (types) can run in parallel
- T010, T012, T013, T016 can run in parallel after types are done
- T011, T014, T015 depend on types and storage

**Within Phase 3 (US1)**:
- T019, T020, T021 (pages) can run in parallel
- T022, T023 (forms) can run in parallel
- T024, T025 (integration) can run in parallel after forms

**Within Phase 4 (US2)**:
- T028, T029, T030, T031, T032 (components) can run in parallel
- T033-T038 (integration) must run sequentially

**Within Phase 6 (US4)**:
- T047, T048, T049, T050 (UI components) can run in parallel
- T051-T058 (integration) must run sequentially

**Across User Stories**:
- Phase 5 (US3) and Phase 6 (US4) can run in parallel after Phase 4 (US2) is complete

---

## Implementation Strategy

### MVP Scope (Minimum Viable Product)

**Phases to Complete**: 1, 2, 3, 4 (T001-T039)

**What You Get**:
- ✅ User registration and sign in
- ✅ Task CRUD operations (create, read, update, delete, complete)
- ✅ User data isolation
- ✅ Basic error handling
- ✅ Protected routes

**What's Missing**:
- ❌ Sign out functionality (manual token clearing required)
- ❌ Responsive design (works on desktop only)
- ❌ Polished UI components
- ❌ Comprehensive error handling

**Time Estimate**: ~25-30 tasks for MVP

### Full Feature Scope

**Phases to Complete**: 1, 2, 3, 4, 5, 6, 7 (T001-T068)

**What You Get**:
- ✅ Complete authentication flow with sign out
- ✅ Full task management
- ✅ Session management and token expiration handling
- ✅ Responsive design (mobile, tablet, desktop)
- ✅ Polished UI with loading and error states
- ✅ Production-ready application

**Time Estimate**: ~68 tasks for full feature

### Incremental Delivery

1. **Iteration 1** (MVP): Phases 1-4 → Deliver working auth + task management
2. **Iteration 2** (Session): Phase 5 → Add sign out and session handling
3. **Iteration 3** (Polish): Phases 6-7 → Add responsive design and polish

---

## Task Summary

**Total Tasks**: 68
- **Phase 1 (Setup)**: 6 tasks
- **Phase 2 (Foundational)**: 12 tasks (blocks all user stories)
- **Phase 3 (US1 - Auth)**: 9 tasks (P1, MVP)
- **Phase 4 (US2 - Tasks)**: 12 tasks (P1, MVP)
- **Phase 5 (US3 - Session)**: 7 tasks (P2)
- **Phase 6 (US4 - Responsive)**: 12 tasks (P2)
- **Phase 7 (Polish)**: 10 tasks

**MVP Tasks**: 39 tasks (Phases 1-4)
**Full Feature Tasks**: 68 tasks (All phases)

**Parallel Opportunities**: 28 tasks marked with [P] can run in parallel within their phase

**Independent Testing**:
- Each user story has clear independent test criteria
- US1 can be tested without US2, US3, US4
- US2 can be tested independently after US1
- US3 and US4 can be tested independently after US1

---

## Validation Checklist

- [x] All tasks follow format: `- [ ] T### [P?] [Story?] Description with file path`
- [x] Tasks organized by user story (US1, US2, US3, US4)
- [x] Each user story has independent test criteria
- [x] Foundational phase clearly marked as blocking
- [x] Dependencies documented in execution order section
- [x] Parallel opportunities identified with [P] marker
- [x] MVP scope clearly defined (Phases 1-4)
- [x] File paths included in all implementation tasks
- [x] No test tasks included (not requested in spec)
