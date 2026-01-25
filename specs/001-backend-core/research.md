# Research: Backend Core & Data Layer

**Feature**: Backend Core & Data Layer
**Date**: 2026-01-12
**Purpose**: Document technical decisions, best practices, and patterns for FastAPI + SQLModel + Neon PostgreSQL backend

## Research Areas

### 1. FastAPI REST API Design

**Decision**: Use FastAPI's automatic OpenAPI generation with Pydantic models for request/response validation

**Rationale**:
- FastAPI automatically generates OpenAPI documentation from type hints
- Pydantic v2 provides fast validation and serialization
- Async support enables high concurrency
- Built-in dependency injection for database sessions

**Best Practices Identified**:
- Separate Pydantic schemas (API contracts) from SQLModel models (database)
- Use APIRouter for organizing endpoints by resource
- Leverage dependency injection for database sessions (avoid global state)
- Return appropriate HTTP status codes: 200 (OK), 201 (Created), 400 (Bad Request), 404 (Not Found), 500 (Internal Server Error)
- Use HTTPException for error responses with detail messages

**Alternatives Considered**:
- Flask: Rejected - requires more boilerplate, no automatic validation
- Django REST Framework: Rejected - too heavyweight for simple CRUD API
- Express.js: Rejected - project requires Python stack

**References**:
- FastAPI documentation: https://fastapi.tiangolo.com/
- Pydantic v2 migration guide for performance improvements

---

### 2. SQLModel for Database Models

**Decision**: Use SQLModel for unified Pydantic + SQLAlchemy models

**Rationale**:
- SQLModel combines Pydantic validation with SQLAlchemy ORM
- Single model definition for both API and database
- Type safety across application layers
- Automatic table creation from models
- Compatible with Alembic for migrations

**Best Practices Identified**:
- Define separate classes for database models (with table=True) and API schemas
- Use Optional fields for nullable database columns
- Leverage Field() for constraints (max_length, default values)
- Use relationships for foreign keys (User -> Tasks one-to-many)
- Enable cascade deletes for user-task relationship

**Pattern for User Isolation**:
```python
# All queries must filter by user_id
tasks = session.exec(
    select(Task).where(Task.user_id == user_id)
).all()
```

**Alternatives Considered**:
- Pure SQLAlchemy: Rejected - more verbose, no Pydantic integration
- Tortoise ORM: Rejected - less mature, smaller ecosystem
- Raw SQL: Rejected - no type safety, more error-prone

**References**:
- SQLModel documentation: https://sqlmodel.tiangolo.com/
- SQLAlchemy 2.0 style queries

---

### 3. Neon Serverless PostgreSQL

**Decision**: Use Neon's connection pooling with asyncpg driver

**Rationale**:
- Neon provides serverless PostgreSQL with automatic scaling
- Connection pooling handles concurrent requests efficiently
- asyncpg is the fastest PostgreSQL driver for Python
- Neon supports standard PostgreSQL features (foreign keys, transactions)

**Configuration Pattern**:
```python
DATABASE_URL = "postgresql+asyncpg://user:pass@host/db"
engine = create_async_engine(DATABASE_URL, echo=True, pool_pre_ping=True)
```

**Best Practices Identified**:
- Use environment variables for connection string (never hardcode)
- Enable pool_pre_ping to handle stale connections
- Use async sessions for non-blocking I/O
- Configure connection pool size based on expected load
- Use transactions for multi-step operations

**Connection String Format**:
- Neon provides connection string in format: `postgresql://user:password@ep-xxx.region.aws.neon.tech/dbname`
- Add `?sslmode=require` for secure connections

**Alternatives Considered**:
- Supabase: Rejected - project specifies Neon
- AWS RDS: Rejected - more expensive, requires manual scaling
- Local PostgreSQL: Rejected - not serverless, deployment complexity

**References**:
- Neon documentation: https://neon.tech/docs
- asyncpg performance benchmarks

---

### 4. User Isolation & Multi-Tenancy

**Decision**: Row-level user_id filtering on all queries (query-based isolation)

**Rationale**:
- Simple to implement and understand
- Enforced at application level (prepares for JWT integration)
- No database-level complexity (no RLS policies needed)
- Easy to test and verify

**Implementation Pattern**:
```python
# CREATE: Always set user_id from parameter
task = Task(title=title, description=desc, user_id=user_id)

# READ: Always filter by user_id
task = session.exec(
    select(Task).where(Task.id == task_id, Task.user_id == user_id)
).first()

# UPDATE/DELETE: Filter by user_id (returns None if not owned)
```

**Security Considerations**:
- Every query MUST include user_id filter
- Return 404 (not 403) when task not found or not owned (prevents information leakage)
- Validate user_id format (integer) to prevent injection
- In Spec-2, user_id will be extracted from JWT token (not request parameter)

**Alternatives Considered**:
- PostgreSQL Row-Level Security (RLS): Rejected - adds complexity, harder to test
- Separate databases per user: Rejected - not scalable
- Schema-based isolation: Rejected - overkill for this use case

**References**:
- Multi-tenancy patterns in SaaS applications
- OWASP guidelines for data isolation

---

### 5. Error Handling Strategy

**Decision**: Structured error responses with consistent JSON format

**Rationale**:
- Predictable error format for API consumers
- HTTP status codes convey error category
- Detail messages provide actionable information
- Supports internationalization (error codes)

**Error Response Schema**:
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Task title is required",
    "details": {
      "field": "title",
      "constraint": "non_empty"
    }
  }
}
```

**HTTP Status Code Mapping**:
- **200 OK**: Successful GET, PUT, DELETE
- **201 Created**: Successful POST (task created)
- **400 Bad Request**: Validation errors (empty title, oversized fields)
- **404 Not Found**: Task doesn't exist or doesn't belong to user
- **500 Internal Server Error**: Database errors, unexpected exceptions

**Implementation**:
- Use FastAPI's HTTPException for all errors
- Create custom exception handler for database errors
- Log all 500 errors for debugging
- Never expose internal error details (stack traces) to API consumers

**Alternatives Considered**:
- Problem Details (RFC 7807): Rejected - overkill for simple API
- Plain text errors: Rejected - not machine-readable
- HTTP status only: Rejected - insufficient detail

**References**:
- REST API error handling best practices
- FastAPI exception handling documentation

---

### 6. Testing Strategy

**Decision**: Pytest with test database and API client fixtures

**Rationale**:
- Pytest is Python standard for testing
- FastAPI provides TestClient for API testing
- SQLModel supports in-memory SQLite for fast tests
- Fixtures enable test isolation and reusability

**Test Categories**:
1. **API Tests** (test_tasks_api.py):
   - Test each endpoint (POST, GET, PUT, DELETE)
   - Verify HTTP status codes
   - Validate response schemas
   - Test validation errors (empty title, oversized fields)

2. **User Isolation Tests** (test_user_isolation.py):
   - Verify user A cannot access user B's tasks
   - Test cross-user update attempts (should fail)
   - Test cross-user delete attempts (should fail)
   - Verify 404 responses (not 403)

3. **Persistence Tests**:
   - Create task, restart app, verify task still exists
   - Test concurrent operations (no race conditions)

**Test Database Strategy**:
- Use SQLite in-memory for unit tests (fast)
- Use test Neon database for integration tests (realistic)
- Reset database between tests (fixtures)

**Alternatives Considered**:
- unittest: Rejected - pytest is more Pythonic
- Mock database: Rejected - doesn't test real SQL queries
- Shared test database: Rejected - tests interfere with each other

**References**:
- Pytest documentation
- FastAPI testing guide

---

## Summary of Key Decisions

| Area | Decision | Rationale |
|------|----------|-----------|
| Web Framework | FastAPI 0.104+ | Async support, automatic validation, OpenAPI generation |
| ORM | SQLModel 0.0.14+ | Unified Pydantic + SQLAlchemy, type safety |
| Database | Neon Serverless PostgreSQL | Serverless, auto-scaling, standard PostgreSQL |
| Database Driver | asyncpg | Fastest async PostgreSQL driver for Python |
| User Isolation | Query-based filtering by user_id | Simple, testable, prepares for JWT integration |
| Error Handling | Structured JSON with HTTP status codes | Consistent, predictable, machine-readable |
| Testing | Pytest with TestClient and fixtures | Standard Python testing, good FastAPI support |
| Project Structure | backend/ with models, schemas, api, core | Clear separation of concerns, scalable |

## Open Questions

**None** - All technical decisions resolved. Ready for Phase 1 (Design & Contracts).

## Next Steps

1. Create data-model.md with User and Task entity definitions
2. Generate OpenAPI specification in contracts/openapi.yaml
3. Write quickstart.md with setup and testing instructions
4. Proceed to /sp.tasks for task breakdown
