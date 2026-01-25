# Data Model: Authentication & Security

**Feature**: 002-auth-security | **Date**: 2026-01-13
**Phase**: 1 (Design) | **Plan**: [plan.md](plan.md)

## Overview

This document defines the database schema extensions and JWT token structure for authentication. The User model from Spec-1 is extended with authentication fields, and the JWT token structure is specified for stateless verification.

---

## Database Schema

### User Model Extension

**File**: `backend/src/models/user.py`

#### Current State (Spec-1)

```python
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .task import Task


class User(SQLModel, table=True):
    """User model for task ownership (Spec-1 minimal version)."""

    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationships
    tasks: List["Task"] = Relationship(back_populates="user")
```

#### Extended State (Spec-2)

```python
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .task import Task


class User(SQLModel, table=True):
    """
    User model with authentication support.

    Extensions from Spec-1:
    - email: Unique identifier for authentication
    - password_hash: Hashed password (bcrypt)
    """

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(
        unique=True,
        index=True,
        max_length=255,
        nullable=False,
        description="User email address (unique identifier)"
    )
    password_hash: str = Field(
        max_length=255,
        nullable=False,
        description="Hashed password (bcrypt with work factor 12)"
    )
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationships
    tasks: List["Task"] = Relationship(back_populates="user")
```

#### Field Specifications

| Field | Type | Constraints | Purpose |
|-------|------|-------------|---------|
| `id` | Integer | Primary key, auto-increment | Unique user identifier |
| `email` | String(255) | Unique, indexed, not null | Authentication identifier |
| `password_hash` | String(255) | Not null | Hashed password (bcrypt) |
| `created_at` | Timestamp | Not null, default now() | Account creation time |
| `updated_at` | Timestamp | Not null, default now() | Last modification time |

#### Indexes

```sql
-- Primary key index (automatic)
CREATE UNIQUE INDEX pk_user_id ON user(id);

-- Email uniqueness and lookup index
CREATE UNIQUE INDEX idx_user_email ON user(email);
```

**Index Rationale**:
- `idx_user_email`: Required for fast signin lookups (email → user_id)
- Unique constraint prevents duplicate registrations
- B-tree index suitable for exact match queries

---

## Database Migration

### Migration Script

**File**: `backend/migrations/versions/002_add_auth_fields.py`

```python
"""Add authentication fields to user table

Revision ID: 002
Revises: 001
Create Date: 2026-01-13

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add email and password_hash columns to user table."""

    # Add email column (nullable initially for existing users)
    op.add_column('user', sa.Column('email', sa.String(length=255), nullable=True))

    # Add password_hash column (nullable initially for existing users)
    op.add_column('user', sa.Column('password_hash', sa.String(length=255), nullable=True))

    # Create unique index on email
    op.create_index('idx_user_email', 'user', ['email'], unique=True)

    # Note: Existing users will need to be migrated manually or via admin tool
    # After migration, make columns NOT NULL:
    # op.alter_column('user', 'email', nullable=False)
    # op.alter_column('user', 'password_hash', nullable=False)


def downgrade() -> None:
    """Remove authentication fields from user table."""

    # Drop index
    op.drop_index('idx_user_email', table_name='user')

    # Drop columns
    op.drop_column('user', 'password_hash')
    op.drop_column('user', 'email')
```

### Migration Strategy

**For New Installations**:
1. Run migration to add columns
2. Columns are NOT NULL from the start
3. Users created via signup endpoint

**For Existing Installations** (if Spec-1 has users):
1. Run migration (columns nullable initially)
2. Migrate existing users:
   - Option A: Admin tool to set email/password for existing users
   - Option B: Force all users to re-register
   - Option C: Generate temporary passwords and email users
3. After migration complete, make columns NOT NULL

**Recommended**: For hackathon/demo, assume fresh installation (no existing users).

---

## SQL Schema (Complete)

```sql
-- User table with authentication fields
CREATE TABLE user (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE UNIQUE INDEX idx_user_email ON user(email);

-- Trigger to update updated_at on modification
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_user_updated_at
    BEFORE UPDATE ON user
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Task table (unchanged from Spec-1, included for reference)
CREATE TABLE task (
    id SERIAL PRIMARY KEY,
    title VARCHAR(500) NOT NULL CHECK (LENGTH(title) > 0),
    description TEXT CHECK (description IS NULL OR LENGTH(description) <= 5000),
    completed BOOLEAN NOT NULL DEFAULT FALSE,
    user_id INTEGER NOT NULL REFERENCES user(id) ON DELETE CASCADE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Task indexes
CREATE INDEX idx_task_user_id ON task(user_id);

-- Task updated_at trigger
CREATE TRIGGER update_task_updated_at
    BEFORE UPDATE ON task
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

---

## JWT Token Structure

### Token Format

JWT tokens follow the standard format: `header.payload.signature`

**Example Token**:
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOjEyMywiZW1haWwiOiJ1c2VyQGV4YW1wbGUuY29tIiwiaWF0IjoxNzA1MTA0MDAwLCJleHAiOjE3MDUxOTA0MDB9.signature_here
```

### Header

```json
{
  "alg": "HS256",
  "typ": "JWT"
}
```

| Field | Value | Description |
|-------|-------|-------------|
| `alg` | HS256 | HMAC-SHA256 signing algorithm |
| `typ` | JWT | Token type |

### Payload (Claims)

```json
{
  "sub": 123,
  "email": "user@example.com",
  "iat": 1705104000,
  "exp": 1705190400
}
```

| Claim | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| `sub` | Integer | Yes | Subject: User ID | 123 |
| `email` | String | Yes | User email address | "user@example.com" |
| `iat` | Integer | Yes | Issued at (Unix timestamp) | 1705104000 |
| `exp` | Integer | Yes | Expiration (Unix timestamp) | 1705190400 |

**Claim Specifications**:

- **`sub` (Subject)**: Standard JWT claim for user identifier
  - Type: Integer (user.id from database)
  - Used for: User identification and authorization
  - Extracted by middleware for user_id verification

- **`email`**: Custom claim for user email
  - Type: String (user.email from database)
  - Used for: Display purposes, avoiding DB lookup
  - Not used for authorization (sub is authoritative)

- **`iat` (Issued At)**: Standard JWT claim
  - Type: Integer (Unix timestamp)
  - Used for: Token age calculation, debugging
  - Set to: `datetime.utcnow()` at token generation

- **`exp` (Expiration)**: Standard JWT claim
  - Type: Integer (Unix timestamp)
  - Used for: Token validity verification
  - Set to: `iat + 24 hours` (86400 seconds)
  - Enforced by: PyJWT library during verification

### Signature

```
HMACSHA256(
  base64UrlEncode(header) + "." + base64UrlEncode(payload),
  secret
)
```

**Signature Parameters**:
- **Algorithm**: HMAC-SHA256 (HS256)
- **Secret**: Shared secret from environment variable (JWT_SECRET)
- **Purpose**: Verify token integrity and authenticity
- **Verification**: Backend verifies signature on every request

---

## Token Generation

### Python Implementation

```python
# backend/src/core/security.py
import jwt
from datetime import datetime, timedelta
from typing import Dict, Any

from .config import settings


def create_access_token(user_id: int, email: str) -> str:
    """
    Generate JWT access token for authenticated user.

    Args:
        user_id: User ID from database
        email: User email address

    Returns:
        JWT token string
    """
    now = datetime.utcnow()
    payload: Dict[str, Any] = {
        "sub": user_id,
        "email": email,
        "iat": now,
        "exp": now + timedelta(hours=settings.JWT_EXPIRATION_HOURS)
    }

    token = jwt.encode(
        payload,
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM
    )

    return token


def verify_access_token(token: str) -> Dict[str, Any]:
    """
    Verify JWT token and extract payload.

    Args:
        token: JWT token string

    Returns:
        Decoded payload dictionary

    Raises:
        jwt.ExpiredSignatureError: Token has expired
        jwt.InvalidTokenError: Token is invalid
    """
    payload = jwt.decode(
        token,
        settings.JWT_SECRET,
        algorithms=[settings.JWT_ALGORITHM]
    )

    return payload
```

### Token Lifecycle

```
┌─────────────────────────────────────────────────────────────┐
│                     Token Lifecycle                          │
└─────────────────────────────────────────────────────────────┘

1. User signs in
   ↓
2. Backend verifies credentials
   ↓
3. Backend generates JWT token
   - Set sub = user_id
   - Set email = user.email
   - Set iat = now()
   - Set exp = now() + 24 hours
   - Sign with JWT_SECRET
   ↓
4. Backend returns token to frontend
   ↓
5. Frontend stores token (localStorage)
   ↓
6. Frontend includes token in API requests
   - Header: Authorization: Bearer <token>
   ↓
7. Backend verifies token on each request
   - Verify signature with JWT_SECRET
   - Check expiration (exp > now())
   - Extract user_id from sub claim
   ↓
8. Token expires after 24 hours
   ↓
9. User must sign in again
```

---

## Pydantic Schemas

### Authentication Request/Response Schemas

**File**: `backend/src/schemas/auth.py`

```python
from pydantic import BaseModel, EmailStr, Field


class SignupRequest(BaseModel):
    """Request schema for user registration."""

    email: EmailStr = Field(
        description="User email address",
        examples=["user@example.com"]
    )
    password: str = Field(
        min_length=8,
        max_length=128,
        description="User password (minimum 8 characters)",
        examples=["securepassword123"]
    )


class SigninRequest(BaseModel):
    """Request schema for user authentication."""

    email: EmailStr = Field(
        description="User email address",
        examples=["user@example.com"]
    )
    password: str = Field(
        description="User password",
        examples=["securepassword123"]
    )


class TokenResponse(BaseModel):
    """Response schema for successful authentication."""

    access_token: str = Field(
        description="JWT access token",
        examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."]
    )
    token_type: str = Field(
        default="bearer",
        description="Token type (always 'bearer')"
    )
    expires_in: int = Field(
        default=86400,
        description="Token expiration time in seconds (24 hours)"
    )


class SignupResponse(BaseModel):
    """Response schema for successful registration."""

    message: str = Field(
        default="User created successfully",
        description="Success message"
    )
    user_id: int = Field(
        description="ID of the created user",
        examples=[123]
    )
```

---

## Data Validation Rules

### Email Validation

- **Format**: RFC 5322 compliant (validated by Pydantic EmailStr)
- **Max Length**: 255 characters
- **Uniqueness**: Must be unique across all users
- **Case Sensitivity**: Case-insensitive for comparison (lowercase before storage)

**Examples**:
- ✅ Valid: `user@example.com`, `test.user+tag@domain.co.uk`
- ❌ Invalid: `invalid-email`, `@example.com`, `user@`

### Password Validation

- **Min Length**: 8 characters
- **Max Length**: 128 characters (bcrypt limit: 72 bytes, but allow longer for future)
- **Allowed Characters**: Any UTF-8 characters
- **Strength**: No complexity requirements in Spec-2 (future enhancement)

**Examples**:
- ✅ Valid: `password123`, `MySecureP@ssw0rd!`, `こんにちは世界`
- ❌ Invalid: `short`, `<8 chars`

### Password Hashing

- **Algorithm**: bcrypt
- **Work Factor**: 12 (configurable via environment)
- **Salt**: Automatically generated by bcrypt (29 characters)
- **Output Format**: `$2b$12$<salt><hash>` (60 characters total)

**Example Hash**:
```
$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5NU7fXnKJXBvW
```

---

## Security Considerations

### Password Storage

- ✅ **Never store plaintext passwords**
- ✅ **Use bcrypt with work factor 12**
- ✅ **Salt automatically generated per password**
- ✅ **Hash stored in password_hash column (60 chars)**

### JWT Token Security

- ✅ **Signed with HMAC-SHA256**
- ✅ **Secret key minimum 32 characters**
- ✅ **Expiration enforced (24 hours)**
- ✅ **No sensitive data in payload** (only user_id and email)
- ⚠️ **Token not revocable** (stateless design trade-off)

### Database Security

- ✅ **Email index for fast lookups**
- ✅ **Unique constraint prevents duplicates**
- ✅ **Foreign key cascade on user deletion**
- ✅ **Timestamps for audit trail**

---

## Performance Characteristics

### Database Operations

| Operation | Query | Index Used | Estimated Time |
|-----------|-------|------------|----------------|
| Signup (check email) | `SELECT id FROM user WHERE email = ?` | idx_user_email | <5ms |
| Signup (insert user) | `INSERT INTO user (email, password_hash, ...) VALUES (...)` | - | <10ms |
| Signin (lookup user) | `SELECT id, password_hash FROM user WHERE email = ?` | idx_user_email | <5ms |
| Get user tasks | `SELECT * FROM task WHERE user_id = ?` | idx_task_user_id | <10ms |

### Cryptographic Operations

| Operation | Algorithm | Estimated Time |
|-----------|-----------|----------------|
| Password hash (signup) | bcrypt (work factor 12) | ~250ms |
| Password verify (signin) | bcrypt (work factor 12) | ~250ms |
| JWT generation | HMAC-SHA256 | <5ms |
| JWT verification | HMAC-SHA256 | <5ms |

**Total Latency**:
- Signup: ~265ms (hash + DB insert)
- Signin: ~260ms (DB lookup + verify + JWT gen)
- Protected request: <20ms (JWT verify + DB query)

---

## Data Model Summary

### Changes from Spec-1

| Component | Change | Impact |
|-----------|--------|--------|
| User model | Added email, password_hash | Database migration required |
| User table | Added unique index on email | Faster signin lookups |
| JWT tokens | New token structure | Stateless authentication |
| API endpoints | Added Authorization header requirement | All routes now protected |

### Backward Compatibility

- ⚠️ **Breaking change**: Existing Spec-1 users cannot sign in (no email/password)
- ✅ **Task data preserved**: Existing tasks remain linked to user_id
- ✅ **API structure unchanged**: Same endpoints, just added auth requirement
- ⚠️ **Migration required**: Existing users need email/password set

**Recommendation**: For hackathon/demo, start with fresh database (no migration needed).

---

## Next Steps

1. **Implement User model extension** in `backend/src/models/user.py`
2. **Create migration script** for database schema changes
3. **Implement JWT utilities** in `backend/src/core/security.py`
4. **Create Pydantic schemas** in `backend/src/schemas/auth.py`
5. **Test data model** with unit tests

**Ready for**: API contract definition (contracts/auth-api.yaml)
