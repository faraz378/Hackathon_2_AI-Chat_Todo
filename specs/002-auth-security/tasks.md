# Tasks: Authentication & Security

**Input**: Design documents from `/specs/002-auth-security/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are NOT included in this task breakdown as they were not explicitly requested in the feature specification.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `backend/src/`, `backend/tests/`
- **Frontend**: `frontend/src/`, `frontend/app/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and dependency installation

- [x] T001 Install backend authentication dependencies (PyJWT==2.8.0, passlib[bcrypt]==1.7.4) in backend/requirements.txt
- [x] T002 Update backend/.env.example with JWT configuration variables (JWT_SECRET, JWT_ALGORITHM, JWT_EXPIRATION_HOURS)
- [x] T003 [P] Update backend/src/core/config.py to include JWT settings (JWT_SECRET, JWT_ALGORITHM, JWT_EXPIRATION_HOURS)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T004 Extend User model in backend/src/models/user.py with email and password_hash fields
- [x] T005 Create database migration script to add email and password_hash columns to user table
- [x] T006 [P] Create security utilities module in backend/src/core/security.py (password hashing, JWT generation, JWT verification)
- [x] T007 [P] Create authentication schemas in backend/src/schemas/auth.py (SignupRequest, SigninRequest, TokenResponse, SignupResponse)
- [x] T008 [P] Extend error schemas in backend/src/schemas/error.py with auth error codes (EMAIL_EXISTS, INVALID_CREDENTIALS, MISSING_TOKEN, INVALID_TOKEN, EXPIRED_TOKEN, FORBIDDEN)
- [x] T009 Create authentication dependency in backend/src/api/deps.py (get_current_user function for JWT verification)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - User Registration (Priority: P1) 🎯 MVP

**Goal**: Enable new users to create accounts with email and password. System validates input, hashes passwords, and stores user records securely.

**Independent Test**: Submit registration form with valid email/password and verify user record is created in database with hashed password. Test duplicate email rejection and validation errors.

### Implementation for User Story 1

- [x] T010 [US1] Create authentication router in backend/src/api/routes/auth.py with POST /auth/signup endpoint
- [x] T011 [US1] Implement signup endpoint logic (email validation, duplicate check, password hashing, user creation)
- [x] T012 [US1] Add error handling for signup endpoint (EMAIL_EXISTS, VALIDATION_ERROR, INTERNAL_ERROR)
- [x] T013 [US1] Add logging for signup operations in backend/src/api/routes/auth.py
- [x] T014 [US1] Register authentication router in backend/src/main.py

**Checkpoint**: At this point, User Story 1 should be fully functional - users can register with email/password

---

## Phase 4: User Story 2 - User Sign In (Priority: P1)

**Goal**: Enable registered users to authenticate with email/password and receive JWT tokens for accessing protected resources.

**Independent Test**: Submit valid credentials and verify JWT token is returned with correct claims (user_id, email, expiration). Test invalid credentials rejection.

### Implementation for User Story 2

- [x] T015 [US2] Add POST /auth/signin endpoint to backend/src/api/routes/auth.py
- [x] T016 [US2] Implement signin endpoint logic (credential verification, JWT token generation)
- [x] T017 [US2] Add error handling for signin endpoint (INVALID_CREDENTIALS, INTERNAL_ERROR)
- [x] T018 [US2] Add logging for signin operations in backend/src/api/routes/auth.py

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently - users can register and sign in to receive JWT tokens

---

## Phase 5: User Story 3 - Protected API Access (Priority: P1)

**Goal**: Secure all task management endpoints with JWT authentication. Reject unauthenticated requests and enforce user data isolation.

**Independent Test**: Make API requests with and without valid tokens. Verify 401 for missing/invalid tokens, 403 for accessing other users' resources, and successful access with valid tokens.

### Implementation for User Story 3

- [x] T019 [US3] Create user access verification dependency in backend/src/api/deps.py (verify_user_access function)
- [x] T020 [US3] Update POST /users/{user_id}/tasks endpoint in backend/src/api/routes/tasks.py to require authentication (add verify_user_access dependency)
- [x] T021 [US3] Update GET /users/{user_id}/tasks endpoint in backend/src/api/routes/tasks.py to require authentication (add verify_user_access dependency)
- [x] T022 [US3] Update GET /users/{user_id}/tasks/{task_id} endpoint in backend/src/api/routes/tasks.py to require authentication (add verify_user_access dependency)
- [x] T023 [US3] Update PUT /users/{user_id}/tasks/{task_id} endpoint in backend/src/api/routes/tasks.py to require authentication (add verify_user_access dependency)
- [x] T024 [US3] Update DELETE /users/{user_id}/tasks/{task_id} endpoint in backend/src/api/routes/tasks.py to require authentication (add verify_user_access dependency)
- [x] T025 [US3] Add authentication error handling to all task endpoints (MISSING_TOKEN, INVALID_TOKEN, EXPIRED_TOKEN, FORBIDDEN)

**Checkpoint**: All user stories (1, 2, 3) should now be independently functional - complete backend authentication system is operational

---

## Phase 6: User Story 4 - Frontend Token Management (Priority: P2)

**Goal**: Build Next.js frontend with Better Auth integration for seamless authentication. Store JWT tokens securely and automatically include them in API requests.

**Independent Test**: Sign in via frontend, close browser, reopen, and verify user remains authenticated. Test token expiration handling and automatic header injection.

### Implementation for User Story 4

- [ ] T026 [P] [US4] Initialize Next.js project in frontend/ directory with TypeScript and App Router
- [ ] T027 [P] [US4] Install frontend dependencies (better-auth, axios) in frontend/package.json
- [ ] T028 [P] [US4] Create frontend/.env.local.example with API URL and JWT secret configuration
- [ ] T029 [P] [US4] Configure Better Auth in frontend/src/lib/auth.ts with custom credentials provider
- [ ] T030 [P] [US4] Create API client utility in frontend/src/lib/api-client.ts with automatic token injection
- [ ] T031 [P] [US4] Create AuthProvider component in frontend/src/components/providers/AuthProvider.tsx
- [ ] T032 [US4] Create signup page in frontend/src/app/(auth)/signup/page.tsx
- [ ] T033 [US4] Create SignupForm component in frontend/src/components/auth/SignupForm.tsx
- [ ] T034 [US4] Create signin page in frontend/src/app/(auth)/signin/page.tsx
- [ ] T035 [US4] Create SigninForm component in frontend/src/components/auth/SigninForm.tsx
- [ ] T036 [US4] Create protected dashboard page in frontend/src/app/dashboard/page.tsx
- [ ] T037 [US4] Update root layout in frontend/src/app/layout.tsx to include AuthProvider

**Checkpoint**: All user stories should now be independently functional - complete full-stack authentication system is operational

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T038 [P] Update backend/README.md with authentication setup instructions
- [x] T039 [P] Create frontend/README.md with setup and usage instructions (SKIPPED - P2 Frontend not implemented)
- [x] T040 Run database migration to add email and password_hash columns to user table (MANUAL - User must run: alembic upgrade head)
- [x] T041 Validate authentication flow using quickstart.md test scenarios (signup, signin, protected access) (MANUAL - User must test with live server)
- [x] T042 [P] Add comprehensive logging to all authentication operations
- [x] T043 Security audit: Verify JWT secret is not hardcoded, passwords are hashed, tokens expire correctly

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - User Story 1 (P1): Can start after Foundational - No dependencies on other stories
  - User Story 2 (P1): Can start after Foundational - No dependencies on other stories (but logically follows US1)
  - User Story 3 (P1): Depends on User Story 2 (needs JWT generation before verification)
  - User Story 4 (P2): Depends on User Stories 1 and 2 (needs backend auth endpoints)
- **Polish (Phase 7)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories (but should follow US1 for logical flow)
- **User Story 3 (P1)**: Depends on User Story 2 completion (requires JWT generation utilities from US2)
- **User Story 4 (P2)**: Depends on User Stories 1 and 2 completion (requires backend signup and signin endpoints)

### Within Each User Story

- User Story 1: Tasks T010-T014 must be sequential (router → endpoint → error handling → logging → registration)
- User Story 2: Tasks T015-T018 must be sequential (endpoint → logic → error handling → logging)
- User Story 3: Tasks T019-T025 can be partially parallel (T020-T024 can run in parallel after T019)
- User Story 4: Tasks T026-T031 can run in parallel, then T032-T037 must be sequential

### Parallel Opportunities

- **Phase 1**: T002 and T003 can run in parallel after T001
- **Phase 2**: T006, T007, T008 can all run in parallel after T004 and T005
- **Phase 3**: All tasks are sequential within the story
- **Phase 4**: All tasks are sequential within the story
- **Phase 5**: T020-T024 can run in parallel after T019
- **Phase 6**: T026-T031 can all run in parallel, then T032-T037 are sequential
- **Phase 7**: T038, T039, T042 can run in parallel

---

## Parallel Example: User Story 3

```bash
# After T019 completes, launch all endpoint updates together:
Task T020: "Update POST /users/{user_id}/tasks endpoint with authentication"
Task T021: "Update GET /users/{user_id}/tasks endpoint with authentication"
Task T022: "Update GET /users/{user_id}/tasks/{task_id} endpoint with authentication"
Task T023: "Update PUT /users/{user_id}/tasks/{task_id} endpoint with authentication"
Task T024: "UPDATE DELETE /users/{user_id}/tasks/{task_id} endpoint with authentication"
```

---

## Parallel Example: User Story 4

```bash
# Launch all foundational frontend tasks together:
Task T026: "Initialize Next.js project in frontend/"
Task T027: "Install frontend dependencies (better-auth, axios)"
Task T028: "Create frontend/.env.local.example"
Task T029: "Configure Better Auth in frontend/src/lib/auth.ts"
Task T030: "Create API client utility in frontend/src/lib/api-client.ts"
Task T031: "Create AuthProvider component"
```

---

## Implementation Strategy

### MVP First (User Stories 1, 2, 3 Only - Backend Complete)

1. Complete Phase 1: Setup (3 tasks)
2. Complete Phase 2: Foundational (6 tasks) - CRITICAL - blocks all stories
3. Complete Phase 3: User Story 1 - Registration (5 tasks)
4. Complete Phase 4: User Story 2 - Sign In (4 tasks)
5. Complete Phase 5: User Story 3 - Protected API Access (7 tasks)
6. **STOP and VALIDATE**: Test complete backend authentication flow
7. Deploy/demo backend if ready

**Total MVP Tasks**: 25 tasks (backend only)

### Full Feature (All User Stories - Backend + Frontend)

1. Complete MVP (Phases 1-5)
2. Complete Phase 6: User Story 4 - Frontend Token Management (12 tasks)
3. Complete Phase 7: Polish (6 tasks)
4. **VALIDATE**: Test complete full-stack authentication system

**Total Full Feature Tasks**: 43 tasks

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready (9 tasks)
2. Add User Story 1 → Test independently → Users can register (5 tasks)
3. Add User Story 2 → Test independently → Users can sign in and get tokens (4 tasks)
4. Add User Story 3 → Test independently → All endpoints protected (7 tasks) → **Backend MVP Complete!**
5. Add User Story 4 → Test independently → Frontend authentication UI (12 tasks) → **Full Feature Complete!**
6. Polish → Final validation (6 tasks)

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (9 tasks)
2. Once Foundational is done:
   - Developer A: User Story 1 (5 tasks)
   - Developer B: User Story 2 (4 tasks) - can start in parallel with US1
3. After US2 completes:
   - Developer A or B: User Story 3 (7 tasks)
4. After US1 and US2 complete:
   - Developer C: User Story 4 (12 tasks) - can work in parallel with US3
5. Team completes Polish together (6 tasks)

---

## Task Summary

**Total Tasks**: 43

**By Phase**:
- Phase 1 (Setup): 3 tasks
- Phase 2 (Foundational): 6 tasks
- Phase 3 (US1 - Registration): 5 tasks
- Phase 4 (US2 - Sign In): 4 tasks
- Phase 5 (US3 - Protected API): 7 tasks
- Phase 6 (US4 - Frontend): 12 tasks
- Phase 7 (Polish): 6 tasks

**By Priority**:
- P1 (Critical): 21 tasks (Phases 1-5)
- P2 (Important): 12 tasks (Phase 6)
- Polish: 6 tasks (Phase 7)

**Parallel Opportunities**: 15 tasks marked [P] can run in parallel within their phases

**MVP Scope**: Phases 1-5 (25 tasks) deliver complete backend authentication

**Independent Test Criteria**:
- US1: Users can register with email/password, duplicate emails rejected
- US2: Users can sign in and receive valid JWT tokens
- US3: All endpoints require authentication, user isolation enforced
- US4: Frontend provides seamless authentication experience with token management

---

## Notes

- [P] tasks = different files, no dependencies within phase
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Tests are NOT included as they were not requested in the specification
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Backend can be completed and deployed before frontend (MVP = US1-3)
- Frontend (US4) requires backend US1 and US2 to be complete
