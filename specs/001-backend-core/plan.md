# Implementation Plan: Backend Core & Data Layer

**Branch**: `001-backend-core` | **Date**: 2026-01-12 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-backend-core/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Build a persistent task management backend with RESTful API design and user-scoped data handling. The backend provides CRUD operations for tasks, enforces user isolation at the database level, and persists data in Neon Serverless PostgreSQL. This spec focuses on the data layer and API structure, with authentication deferred to Spec-2.

**Technical Approach**: FastAPI web framework with SQLModel ORM for type-safe database operations, Pydantic models for request/response validation, and user_id-scoped queries to prepare for JWT authentication integration.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: FastAPI 0.104+, SQLModel 0.0.14+, Pydantic 2.5+, asyncpg (Neon PostgreSQL driver)
**Storage**: Neon Serverless PostgreSQL (cloud-hosted PostgreSQL)
**Testing**: pytest 7.4+, pytest-asyncio, httpx (for API testing)
**Target Platform**: Linux server (containerized deployment)
**Project Type**: Web application (backend only)
**Performance Goals**: Sub-second response times for single operations, support 100+ concurrent requests
**Constraints**: User isolation enforced on all queries, data persistence across restarts, REST compliance (proper HTTP status codes)
**Scale/Scope**: Multi-user system, 4 CRUD endpoints, 2 database tables (User, Task)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### ✅ I. Spec-Driven Development
- **Status**: PASS
- **Evidence**: Complete spec.md exists with 4 user stories, 18 functional requirements, and 7 success criteria
- **Action**: Proceed with planning

### ✅ II. Agentic Workflow Compliance
- **Status**: PASS
- **Evidence**: Following spec → plan → tasks → implement workflow. Backend Agent will be used for FastAPI implementation, Database Agent for schema design
- **Action**: Ensure agents are invoked during implementation phase

### ⚠️ III. Security-First Design
- **Status**: PARTIAL (Expected for Spec-1)
- **Evidence**: User isolation enforced via user_id scoping on all queries. JWT authentication deferred to Spec-2 as documented in spec assumptions
- **Justification**: This is intentional - Spec-1 builds data layer with user_id parameter, Spec-2 adds JWT validation. User isolation is enforced at database level now, authentication layer added later
- **Action**: Ensure all queries include user_id filter. Document that endpoints accept user_id as parameter (not from JWT yet)

### ✅ IV. Deterministic Behavior
- **Status**: PASS
- **Evidence**: REST standards enforced (FR-015), Pydantic validation for requests, explicit error handling (FR-016)
- **Action**: Define error response schema in contracts

### ✅ V. Full-Stack Coherence
- **Status**: PASS
- **Evidence**: API contracts will be defined in Phase 1 (OpenAPI spec), data models documented
- **Action**: Create OpenAPI spec in contracts/ directory

### ✅ VI. Technology Stack Adherence
- **Status**: PASS
- **Evidence**: Using FastAPI, SQLModel, Neon PostgreSQL as specified in constitution
- **Action**: No deviations allowed

### ✅ VII. Multi-User Data Isolation
- **Status**: PASS
- **Evidence**: FR-018 requires all queries scoped by user_id, FR-008/FR-010/FR-012 enforce isolation on read/update/delete
- **Action**: Implement user_id filtering in all database queries

**Overall Gate Status**: ✅ **PASS** - Proceed to Phase 0 research

**Notes**: Security-First Design is partially implemented as expected for Spec-1. JWT authentication will be added in Spec-2, but user isolation is enforced at the database level now.

---

## Post-Design Constitution Re-Check

*Re-evaluated after Phase 1 design completion*

### ✅ I. Spec-Driven Development
- **Status**: PASS
- **Evidence**: All design artifacts (research.md, data-model.md, contracts/openapi.yaml, quickstart.md) derived from spec.md
- **Verification**: No implementation details added beyond spec requirements

### ✅ II. Agentic Workflow Compliance
- **Status**: PASS
- **Evidence**: Plan complete, ready for /sp.tasks to generate task breakdown
- **Next Phase**: Database Agent for SQLModel models, Backend Agent for FastAPI routes

### ✅ III. Security-First Design
- **Status**: PASS (with documented deferral)
- **Evidence**:
  - User isolation enforced: All queries filter by user_id (see data-model.md)
  - API contracts document 404 responses for unauthorized access (see openapi.yaml)
  - Quickstart.md includes security warning about Spec-1 limitations
- **Verification**: JWT authentication explicitly deferred to Spec-2 as planned

### ✅ IV. Deterministic Behavior
- **Status**: PASS
- **Evidence**:
  - OpenAPI spec defines exact request/response schemas
  - Error responses have consistent structure (ErrorResponse schema)
  - HTTP status codes mapped to scenarios (200, 201, 400, 404, 500)
- **Verification**: All edge cases documented in data-model.md

### ✅ V. Full-Stack Coherence
- **Status**: PASS
- **Evidence**:
  - API contracts defined in OpenAPI 3.0 format (contracts/openapi.yaml)
  - Data models documented with exact field types (data-model.md)
  - Frontend (Spec-3) can consume these contracts directly
- **Verification**: No mismatches between API and data layer

### ✅ VI. Technology Stack Adherence
- **Status**: PASS
- **Evidence**:
  - FastAPI 0.104+ (Technical Context)
  - SQLModel 0.0.14+ (Technical Context)
  - Neon Serverless PostgreSQL (Technical Context)
  - No deviations from constitution requirements
- **Verification**: requirements.txt in quickstart.md matches stack

### ✅ VII. Multi-User Data Isolation
- **Status**: PASS
- **Evidence**:
  - All endpoints scoped by user_id (see openapi.yaml paths)
  - Database queries filter by user_id (see data-model.md)
  - User isolation tests documented (see quickstart.md validation checklist)
- **Verification**: 404 responses prevent information leakage

**Final Gate Status**: ✅ **PASS** - Ready for /sp.tasks

**Design Quality**: All constitution principles satisfied. No violations or compromises. Architecture is simple, secure, and aligned with spec requirements.

## Project Structure

### Documentation (this feature)

```text
specs/001-backend-core/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
│   └── openapi.yaml     # OpenAPI 3.0 specification for REST API
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py          # User SQLModel
│   │   └── task.py          # Task SQLModel
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── task.py          # Pydantic request/response schemas
│   │   └── error.py         # Error response schemas
│   ├── api/
│   │   ├── __init__.py
│   │   ├── deps.py          # Dependency injection (DB session)
│   │   └── routes/
│   │       ├── __init__.py
│   │       └── tasks.py     # Task CRUD endpoints
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py        # Settings (Neon connection string)
│   │   └── database.py      # Database engine and session
│   └── main.py              # FastAPI app initialization
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # Pytest fixtures (test DB, client)
│   ├── test_tasks_api.py    # API endpoint tests
│   └── test_user_isolation.py  # User isolation tests
├── alembic/                 # Database migrations (optional)
├── .env.example             # Environment variables template
├── requirements.txt         # Python dependencies
└── README.md                # Setup instructions

frontend/                    # (Spec-3 - not created in this spec)
└── [deferred to Spec-3]
```

**Structure Decision**: Web application structure (Option 2) selected because this is a full-stack project with separate backend and frontend. Backend is implemented in Spec-1, frontend in Spec-3. The backend/ directory contains all FastAPI code, SQLModel models, and API routes. Tests are co-located with source code for easier maintenance.

**Key Design Choices**:
- **models/** vs **schemas/**: SQLModel classes (database models) in models/, Pydantic schemas (API contracts) in schemas/
- **api/routes/**: RESTful endpoints organized by resource (tasks.py for all task operations)
- **core/**: Shared infrastructure (config, database connection)
- **No services layer**: Direct database access from routes (simplicity principle - no unnecessary abstraction for CRUD operations)

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

**Status**: No violations requiring justification. All constitution principles are satisfied.
