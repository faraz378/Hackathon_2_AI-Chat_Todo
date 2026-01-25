# Data Model: Backend Core & Data Layer

**Feature**: Backend Core & Data Layer
**Date**: 2026-01-12
**Purpose**: Define database schema, entities, relationships, and validation rules

## Entity Definitions

### User Entity

**Purpose**: Represents a user account in the system. In Spec-1, users are referenced by ID but full user management (signup, signin, password) is deferred to Spec-2.

**Attributes**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | Integer | Primary Key, Auto-increment | Unique user identifier |
| created_at | DateTime | Not Null, Default: now() | Timestamp when user was created |
| updated_at | DateTime | Not Null, Default: now(), Auto-update | Timestamp of last update |

**Relationships**:
- **One-to-Many** with Task: A user can have multiple tasks
- **Cascade Delete**: When a user is deleted, all their tasks are deleted (to be implemented in Spec-2)

**Validation Rules**:
- id must be positive integer
- created_at cannot be in the future
- updated_at must be >= created_at

**Notes**:
- Minimal user entity for Spec-1 (just ID and timestamps)
- Email, password, and authentication fields added in Spec-2
- User creation/deletion not exposed via API in Spec-1 (handled in Spec-2)

**SQLModel Definition Pattern**:
```python
class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship
    tasks: List["Task"] = Relationship(back_populates="user")
```

---

### Task Entity

**Purpose**: Represents a todo item belonging to a specific user

**Attributes**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | Integer | Primary Key, Auto-increment | Unique task identifier |
| title | String | Not Null, Max Length: 500 | Task title/summary |
| description | Text | Nullable, Max Length: 5000 | Detailed task description (optional) |
| completed | Boolean | Not Null, Default: false | Task completion status |
| user_id | Integer | Foreign Key (User.id), Not Null, Indexed | Owner of the task |
| created_at | DateTime | Not Null, Default: now() | Timestamp when task was created |
| updated_at | DateTime | Not Null, Default: now(), Auto-update | Timestamp of last update |

**Relationships**:
- **Many-to-One** with User: Each task belongs to exactly one user
- **Foreign Key**: user_id references User.id

**Validation Rules**:
- title must be non-empty (min length: 1)
- title max length: 500 characters (FR-004)
- description max length: 5000 characters when provided (FR-005)
- completed must be boolean (true/false)
- user_id must reference existing user
- created_at cannot be in the future
- updated_at must be >= created_at

**Indexes**:
- Primary index on id (automatic)
- Index on user_id (for efficient user-scoped queries)
- Composite index on (user_id, id) for lookups by user and task

**SQLModel Definition Pattern**:
```python
class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(max_length=500, min_length=1)
    description: Optional[str] = Field(default=None, max_length=5000)
    completed: bool = Field(default=False)
    user_id: int = Field(foreign_key="user.id", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship
    user: User = Relationship(back_populates="tasks")
```

---

## Entity Relationship Diagram

```
┌─────────────────┐
│      User       │
├─────────────────┤
│ id (PK)         │
│ created_at      │
│ updated_at      │
└────────┬────────┘
         │
         │ 1
         │
         │ has many
         │
         │ N
         │
┌────────▼────────┐
│      Task       │
├─────────────────┤
│ id (PK)         │
│ title           │
│ description     │
│ completed       │
│ user_id (FK)    │
│ created_at      │
│ updated_at      │
└─────────────────┘
```

**Relationship Type**: One-to-Many (User → Tasks)
**Cardinality**: One user can have zero or more tasks; each task belongs to exactly one user
**Referential Integrity**: user_id in Task must reference valid User.id

---

## Database Schema (SQL)

```sql
-- User table
CREATE TABLE user (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Task table
CREATE TABLE task (
    id SERIAL PRIMARY KEY,
    title VARCHAR(500) NOT NULL CHECK (LENGTH(title) > 0),
    description TEXT CHECK (description IS NULL OR LENGTH(description) <= 5000),
    completed BOOLEAN NOT NULL DEFAULT FALSE,
    user_id INTEGER NOT NULL REFERENCES user(id),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_task_user_id ON task(user_id);
CREATE INDEX idx_task_user_id_id ON task(user_id, id);

-- Trigger to auto-update updated_at (PostgreSQL)
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_task_updated_at
    BEFORE UPDATE ON task
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_updated_at
    BEFORE UPDATE ON user
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

---

## State Transitions

### Task Completion State

```
┌─────────────┐
│  completed  │
│   = false   │
│  (default)  │
└──────┬──────┘
       │
       │ User marks task complete
       │ (PUT /users/{user_id}/tasks/{task_id})
       │
       ▼
┌─────────────┐
│  completed  │
│   = true    │
└──────┬──────┘
       │
       │ User marks task incomplete
       │ (PUT /users/{user_id}/tasks/{task_id})
       │
       ▼
┌─────────────┐
│  completed  │
│   = false   │
└─────────────┘
```

**State Rules**:
- Tasks start with completed=false (FR-003)
- completed can be toggled between true/false any number of times
- No other states exist (no "archived", "deleted" states - deletion is permanent)

---

## Data Integrity Rules

### Referential Integrity
- **Foreign Key Constraint**: task.user_id MUST reference valid user.id
- **On User Delete**: Cascade delete all tasks (implemented in Spec-2 when user deletion is added)
- **On Task Delete**: No cascade (task deletion is independent)

### Validation at Database Level
- title NOT NULL and length > 0
- description length <= 5000 when not null
- completed NOT NULL (must be true or false)
- user_id NOT NULL and must reference existing user

### Validation at Application Level (Pydantic)
- title: min_length=1, max_length=500
- description: Optional, max_length=5000
- completed: bool (no other values accepted)
- user_id: positive integer

### Concurrency Control
- **Optimistic Locking**: Use updated_at timestamp to detect concurrent modifications
- **Database Transactions**: Use for multi-step operations (not needed for single CRUD ops)
- **Isolation Level**: Read Committed (PostgreSQL default) - sufficient for this use case

---

## Migration Strategy

### Initial Schema Creation
- SQLModel can create tables automatically: `SQLModel.metadata.create_all(engine)`
- For production: Use Alembic migrations for version control

### Future Schema Changes (Spec-2 and beyond)
- Add email, password_hash to User table
- Add indexes for email lookup
- Add soft delete columns if needed (deleted_at)
- Add task priority, due_date, tags (if scope expands)

### Backward Compatibility
- Spec-1 schema is minimal and extensible
- Adding columns in Spec-2 won't break existing data
- Foreign key relationships already established

---

## Performance Considerations

### Query Optimization
- **Index on user_id**: Enables fast filtering by user (all queries are user-scoped)
- **Composite index (user_id, id)**: Optimizes lookups by user and task ID
- **Avoid N+1 queries**: Use eager loading if fetching user with tasks (not needed in Spec-1)

### Expected Query Patterns
1. **Get all tasks for user**: `SELECT * FROM task WHERE user_id = ?` (uses idx_task_user_id)
2. **Get specific task for user**: `SELECT * FROM task WHERE user_id = ? AND id = ?` (uses idx_task_user_id_id)
3. **Create task**: `INSERT INTO task (...)` (no index needed)
4. **Update task**: `UPDATE task SET ... WHERE id = ? AND user_id = ?` (uses idx_task_user_id_id)
5. **Delete task**: `DELETE FROM task WHERE id = ? AND user_id = ?` (uses idx_task_user_id_id)

### Scalability
- Current schema supports millions of tasks per user
- Pagination not implemented in Spec-1 (can be added later if needed)
- Connection pooling handles concurrent requests

---

## Security Considerations

### User Isolation
- **Every query MUST filter by user_id** (enforced at application level)
- **No cross-user access**: Queries return empty/null if task doesn't belong to user
- **404 responses**: Return 404 (not 403) to avoid information leakage

### SQL Injection Prevention
- **Parameterized queries**: SQLModel/SQLAlchemy uses parameterized queries by default
- **Input validation**: Pydantic validates all inputs before database access
- **No raw SQL**: Avoid raw SQL queries; use ORM methods

### Data Exposure
- **No sensitive data in Spec-1**: Only task title/description (user-generated content)
- **Timestamps**: created_at/updated_at are informational, not sensitive
- **User IDs**: Integer IDs are not sensitive (no email/username exposed)

---

## Testing Data Model

### Test Scenarios
1. **Create user and task**: Verify foreign key relationship
2. **Create task with invalid title**: Verify validation error (empty, too long)
3. **Create task with invalid description**: Verify validation error (too long)
4. **Query tasks by user_id**: Verify only user's tasks returned
5. **Update task with different user_id**: Verify 404 response
6. **Delete task with different user_id**: Verify 404 response
7. **Concurrent task creation**: Verify no race conditions

### Test Data
```python
# Test user
user1 = User(id=1)
user2 = User(id=2)

# Test tasks
task1 = Task(title="Buy groceries", user_id=1)
task2 = Task(title="Call dentist", description="Schedule checkup", user_id=1)
task3 = Task(title="User 2 task", user_id=2)
```

---

## Summary

**Entities**: 2 (User, Task)
**Relationships**: 1 (User → Tasks, one-to-many)
**Indexes**: 2 (user_id, composite user_id+id)
**Constraints**: Foreign key, NOT NULL, length limits, default values
**State Transitions**: 1 (Task completion toggle)
**Security**: User isolation via user_id filtering on all queries
