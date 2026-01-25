---

description: "Task list for Backend Core & Data Layer implementation"
---

# Tasks: Backend Core & Data Layer

**Input**: Design documents from `/specs/001-backend-core/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are NOT requested in the feature specification, so no test tasks are included.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/src/`, `backend/tests/`
- Paths shown below use backend/ prefix as defined in plan.md

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create backend directory structure (backend/src/, backend/tests/)
- [ ] T002 Create requirements.txt with FastAPI 0.104+, SQLModel 0.0.14+, Pydantic 2.5+, uvicorn, asyncpg, python-dotenv, pytest, pytest-asyncio, httpx
- [ ] T003 Create .env.example file with DATABASE_URL placeholder in backend/
- [ ] T004 [P] Create backend/src/__init__.py
- [ ] T005 [P] Create backend/tests/__init__.py
- [ ] T006 [P] Create backend/README.md with setup instructions

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T007 Create backend/src/core/__init__.py
- [ ] T008 Create backend/src/core/config.py with Settings class (DATABASE_URL from environment)
- [ ] T009 Create backend/src/core/database.py with async engine, session factory, and get_session dependency
- [ ] T010 [P] Create backend/src/models/__init__.py
- [ ] T011 Create backend/src/models/user.py with User SQLModel (id, created_at, updated_at, tasks relationship)
- [ ] T012 Create backend/src/models/task.py with Task SQLModel (id, title, description, completed, user_id, created_at, updated_at, user relationship)
- [ ] T013 [P] Create backend/src/schemas/__init__.py
- [ ] T014 [P] Create backend/src/schemas/error.py with ErrorResponse Pydantic schema
- [ ] T015 [P] Create backend/src/api/__init__.py
- [ ] T016 [P] Create backend/src/api/deps.py with get_db dependency function
- [ ] T017 [P] Create backend/src/api/routes/__init__.py
- [ ] T018 Create backend/src/main.py with FastAPI app initialization, CORS middleware, and router registration

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Create and Store Tasks (Priority: P1) 🎯 MVP

**Goal**: API consumers can create new tasks for a specific user and have them persisted in the database

**Independent Test**: Send POST request with task data and user_id, verify task is stored and can be retrieved with unique identifier

### Implementation for User Story 1

- [ ] T019 [P] [US1] Create backend/src/schemas/task.py with TaskCreate Pydantic schema (title, description)
- [ ] T020 [P] [US1] Add TaskResponse Pydantic schema to backend/src/schemas/task.py (id, title, description, completed, user_id, created_at, updated_at)
- [ ] T021 [US1] Create backend/src/api/routes/tasks.py with APIRouter and POST /users/{user_id}/tasks endpoint
- [ ] T022 [US1] Implement create_task function in backend/src/api/routes/tasks.py with validation (title non-empty, max 500 chars, description max 5000 chars)
- [ ] T023 [US1] Add user_id scoping to create_task - set task.user_id from path parameter
- [ ] T024 [US1] Add error handling to create_task - return 400 for validation errors, 500 for database errors
- [ ] T025 [US1] Register tasks router in backend/src/main.py

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Retrieve User's Tasks (Priority: P1)

**Goal**: API consumers can retrieve all tasks belonging to a specific user, or retrieve a single task by its identifier

**Independent Test**: Create multiple tasks for different users, verify retrieving tasks for user_id=123 returns only that user's tasks, and retrieving specific task_id returns correct task only if it belongs to requesting user

### Implementation for User Story 2

- [ ] T026 [P] [US2] Implement GET /users/{user_id}/tasks endpoint in backend/src/api/routes/tasks.py (get_tasks function)
- [ ] T027 [P] [US2] Implement GET /users/{user_id}/tasks/{task_id} endpoint in backend/src/api/routes/tasks.py (get_task function)
- [ ] T028 [US2] Add user_id filtering to get_tasks - query WHERE user_id = path parameter
- [ ] T029 [US2] Add user_id filtering to get_task - query WHERE user_id = path parameter AND id = task_id
- [ ] T030 [US2] Add error handling to get_task - return 404 when task not found or belongs to different user
- [ ] T031 [US2] Ensure get_tasks returns empty list (not error) when user has no tasks

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Update Task Status and Details (Priority: P2)

**Goal**: API consumers can modify existing tasks for a user, including updating the title, description, and completion status

**Independent Test**: Create a task, update its fields and verify changes persist, verify attempts to update another user's task are rejected with 404

### Implementation for User Story 3

- [ ] T032 [P] [US3] Add TaskUpdate Pydantic schema to backend/src/schemas/task.py (title, description, completed - all optional)
- [ ] T033 [US3] Implement PUT /users/{user_id}/tasks/{task_id} endpoint in backend/src/api/routes/tasks.py (update_task function)
- [ ] T034 [US3] Add user_id filtering to update_task - query WHERE user_id = path parameter AND id = task_id
- [ ] T035 [US3] Implement partial update logic - only update fields provided in request body
- [ ] T036 [US3] Add validation to update_task - title non-empty if provided, max lengths enforced
- [ ] T037 [US3] Add error handling to update_task - return 404 when task not found or belongs to different user, 400 for validation errors
- [ ] T038 [US3] Update updated_at timestamp automatically on task modification

**Checkpoint**: All user stories (1, 2, 3) should now be independently functional

---

## Phase 6: User Story 4 - Delete Tasks (Priority: P3)

**Goal**: API consumers can permanently remove tasks for a specific user

**Independent Test**: Create a task, delete it, verify it no longer appears in user's task list and cannot be retrieved by ID

### Implementation for User Story 4

- [ ] T039 [US4] Implement DELETE /users/{user_id}/tasks/{task_id} endpoint in backend/src/api/routes/tasks.py (delete_task function)
- [ ] T040 [US4] Add user_id filtering to delete_task - query WHERE user_id = path parameter AND id = task_id
- [ ] T041 [US4] Add error handling to delete_task - return 404 when task not found or belongs to different user
- [ ] T042 [US4] Return success message {"message": "Task deleted successfully"} on successful deletion

**Checkpoint**: All user stories should now be independently functional

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T043 [P] Add comprehensive error logging to all endpoints in backend/src/api/routes/tasks.py
- [ ] T044 [P] Verify all endpoints return correct HTTP status codes (200, 201, 400, 404, 500)
- [ ] T045 [P] Add API documentation strings (docstrings) to all endpoint functions
- [ ] T046 Verify database connection pooling is configured in backend/src/core/database.py
- [ ] T047 Test concurrent request handling - create 100 tasks simultaneously and verify no data corruption
- [ ] T048 Test data persistence - restart server and verify tasks still exist
- [ ] T049 Run quickstart.md validation checklist to verify all acceptance criteria

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P1 → P2 → P3)
- **Polish (Phase 7)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories (can run parallel with US1)
- **User Story 3 (P2)**: Can start after Foundational (Phase 2) - No dependencies on other stories (can run parallel with US1/US2)
- **User Story 4 (P3)**: Can start after Foundational (Phase 2) - No dependencies on other stories (can run parallel with US1/US2/US3)

### Within Each User Story

- Tasks marked [P] within a story can run in parallel (different files)
- Schema tasks (Pydantic models) before endpoint implementation
- Endpoint implementation before error handling
- All tasks within a story must complete before story is considered done

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel (T004, T005, T006)
- All Foundational tasks marked [P] can run in parallel within their groups:
  - T010, T013, T015, T016, T017 (directory initialization)
  - T011 and T012 can run in parallel (different model files)
  - T014 can run in parallel with models
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- Within User Story 1: T019 and T020 can run in parallel (same file but different schemas)
- Within User Story 2: T026 and T027 can run in parallel (different endpoints)
- Within User Story 3: T032 can run in parallel with other US3 tasks initially
- Polish tasks T043, T044, T045 can run in parallel (different concerns)

---

## Parallel Example: After Foundational Phase

```bash
# All user stories can start simultaneously after Phase 2:

# Developer A works on User Story 1 (Create Tasks):
Task T019: Create TaskCreate schema
Task T020: Create TaskResponse schema
Task T021: Create POST endpoint
...

# Developer B works on User Story 2 (Retrieve Tasks):
Task T026: Create GET /tasks endpoint
Task T027: Create GET /tasks/{id} endpoint
...

# Developer C works on User Story 3 (Update Tasks):
Task T032: Create TaskUpdate schema
Task T033: Create PUT endpoint
...

# Developer D works on User Story 4 (Delete Tasks):
Task T039: Create DELETE endpoint
...
```

---

## Implementation Strategy

### MVP First (User Stories 1 & 2 Only)

1. Complete Phase 1: Setup (T001-T006)
2. Complete Phase 2: Foundational (T007-T018) - CRITICAL, blocks all stories
3. Complete Phase 3: User Story 1 (T019-T025) - Create tasks
4. Complete Phase 4: User Story 2 (T026-T031) - Retrieve tasks
5. **STOP and VALIDATE**: Test US1 and US2 independently
6. Deploy/demo if ready (MVP complete!)

**MVP Scope**: With just US1 and US2, you have a functional backend that can create and retrieve tasks with full user isolation.

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (can create tasks!)
3. Add User Story 2 → Test independently → Deploy/Demo (can read tasks - MVP!)
4. Add User Story 3 → Test independently → Deploy/Demo (can update tasks)
5. Add User Story 4 → Test independently → Deploy/Demo (can delete tasks - full CRUD!)
6. Add Polish → Final validation → Production ready

Each story adds value without breaking previous stories.

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (T001-T018)
2. Once Foundational is done:
   - Developer A: User Story 1 (T019-T025)
   - Developer B: User Story 2 (T026-T031)
   - Developer C: User Story 3 (T032-T038)
   - Developer D: User Story 4 (T039-T042)
3. Stories complete and integrate independently
4. Team collaborates on Polish (T043-T049)

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
- Tests are NOT included (not requested in spec)
- Use Database Agent for model tasks (T011, T012)
- Use Backend Agent for API endpoint tasks (T021-T042)
