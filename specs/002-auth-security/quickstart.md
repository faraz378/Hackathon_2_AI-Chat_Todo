# Quickstart Guide: Authentication & Security

**Feature**: 002-auth-security | **Date**: 2026-01-13
**Phase**: 1 (Design) | **Plan**: [plan.md](plan.md)

## Overview

This guide provides step-by-step instructions for setting up and testing the authentication system. Follow these instructions to get the backend and frontend running with JWT-based authentication.

---

## Prerequisites

### System Requirements

- **Python**: 3.11 or higher
- **Node.js**: 18.x or higher
- **PostgreSQL**: Neon Serverless account (free tier available)
- **Git**: For version control
- **curl** or **Postman**: For API testing

### Knowledge Requirements

- Basic understanding of REST APIs
- Familiarity with JWT tokens
- Basic command line usage

---

## Backend Setup

### Step 1: Install Python Dependencies

```bash
cd backend

# Activate virtual environment (if not already active)
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install new dependencies for authentication
pip install PyJWT==2.8.0 passlib[bcrypt]==1.7.4 python-multipart==0.0.6

# Verify installation
pip list | grep -E "(PyJWT|passlib)"
```

**Expected Output**:
```
passlib                1.7.4
PyJWT                  2.8.0
```

### Step 2: Configure Environment Variables

Create or update `backend/.env` file:

```bash
# Database connection (from Spec-1)
DATABASE_URL=postgresql+asyncpg://user:password@ep-xxx.region.aws.neon.tech/dbname?sslmode=require

# JWT Configuration (NEW for Spec-2)
JWT_SECRET=your-super-secret-key-must-be-at-least-32-characters-long-for-security
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24
```

**Important**:
- `JWT_SECRET` must be at least 32 characters
- Use a cryptographically secure random string in production
- Generate with: `python -c "import secrets; print(secrets.token_urlsafe(32))"`

### Step 3: Update Configuration

Verify `backend/src/core/config.py` includes JWT settings:

```python
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    DATABASE_URL: str
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
```

### Step 4: Run Database Migration

```bash
# Generate migration for User model changes
alembic revision --autogenerate -m "Add authentication fields to user model"

# Review the generated migration file in backend/migrations/versions/
# Ensure it adds email and password_hash columns

# Apply migration
alembic upgrade head

# Verify migration
alembic current
```

**Expected Output**:
```
INFO  [alembic.runtime.migration] Running upgrade 001 -> 002, Add authentication fields to user model
```

### Step 5: Start Backend Server

```bash
# Start development server with auto-reload
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Or with logging
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000 --log-level debug
```

**Expected Output**:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using StatReload
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### Step 6: Verify Backend Health

```bash
# Test health endpoint
curl http://localhost:8000/

# Expected response:
# {"status":"ok","message":"Task Management API is running","version":"1.0.0"}

# View API documentation
# Open browser: http://localhost:8000/docs
```

---

## Frontend Setup (Optional for Backend Testing)

### Step 1: Initialize Next.js Project

```bash
# Create frontend directory
mkdir -p frontend
cd frontend

# Initialize Next.js with TypeScript
npx create-next-app@latest . --typescript --app --no-src-dir --import-alias "@/*"

# Install Better Auth
npm install better-auth

# Install additional dependencies
npm install axios
```

### Step 2: Configure Environment

Create `frontend/.env.local`:

```bash
# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000

# JWT Secret (same as backend)
JWT_SECRET=your-super-secret-key-must-be-at-least-32-characters-long-for-security
```

### Step 3: Start Frontend Server

```bash
npm run dev
```

**Expected Output**:
```
  ▲ Next.js 16.0.0
  - Local:        http://localhost:3000
  - Ready in 2.3s
```

---

## Testing Authentication Flow

### Test 1: User Registration

**Request**:
```bash
curl -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }'
```

**Expected Response** (201 Created):
```json
{
  "message": "User created successfully",
  "user_id": 1
}
```

**Test Variations**:

1. **Duplicate Email** (should fail):
```bash
# Run same request again
curl -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }'

# Expected: 400 Bad Request
# {"error":{"code":"EMAIL_EXISTS","message":"Email already registered"}}
```

2. **Weak Password** (should fail):
```bash
curl -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test2@example.com",
    "password": "short"
  }'

# Expected: 400 Bad Request
# {"error":{"code":"VALIDATION_ERROR","message":"Password must be at least 8 characters"}}
```

### Test 2: User Sign In

**Request**:
```bash
curl -X POST http://localhost:8000/auth/signin \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }'
```

**Expected Response** (200 OK):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOjEsImVtYWlsIjoidGVzdEBleGFtcGxlLmNvbSIsImlhdCI6MTcwNTEwNDAwMCwiZXhwIjoxNzA1MTkwNDAwfQ.signature_here",
  "token_type": "bearer",
  "expires_in": 86400
}
```

**Save the token** for subsequent requests:
```bash
# Extract token (Linux/macOS)
TOKEN=$(curl -s -X POST http://localhost:8000/auth/signin \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}' \
  | jq -r '.access_token')

echo $TOKEN

# Windows PowerShell
$response = Invoke-RestMethod -Uri "http://localhost:8000/auth/signin" -Method Post -ContentType "application/json" -Body '{"email":"test@example.com","password":"password123"}'
$TOKEN = $response.access_token
Write-Output $TOKEN
```

**Test Variations**:

1. **Invalid Credentials** (should fail):
```bash
curl -X POST http://localhost:8000/auth/signin \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "wrongpassword"
  }'

# Expected: 401 Unauthorized
# {"error":{"code":"INVALID_CREDENTIALS","message":"Invalid email or password"}}
```

### Test 3: Create Task (Protected Endpoint)

**Request with Token**:
```bash
curl -X POST http://localhost:8000/users/1/tasks \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "title": "Buy groceries",
    "description": "Milk, eggs, bread"
  }'
```

**Expected Response** (201 Created):
```json
{
  "id": 1,
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "completed": false,
  "user_id": 1,
  "created_at": "2026-01-13T10:30:00Z",
  "updated_at": "2026-01-13T10:30:00Z"
}
```

**Test Variations**:

1. **Missing Token** (should fail):
```bash
curl -X POST http://localhost:8000/users/1/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Buy groceries"
  }'

# Expected: 401 Unauthorized
# {"error":{"code":"MISSING_TOKEN","message":"Authorization header required"}}
```

2. **Invalid Token** (should fail):
```bash
curl -X POST http://localhost:8000/users/1/tasks \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer invalid_token_here" \
  -d '{
    "title": "Buy groceries"
  }'

# Expected: 401 Unauthorized
# {"error":{"code":"INVALID_TOKEN","message":"Invalid or expired token"}}
```

3. **Access Another User's Resources** (should fail):
```bash
# Try to create task for user_id=999 with token for user_id=1
curl -X POST http://localhost:8000/users/999/tasks \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "title": "Unauthorized task"
  }'

# Expected: 403 Forbidden
# {"error":{"code":"FORBIDDEN","message":"Cannot access another user's resources"}}
```

### Test 4: Get All Tasks (Protected Endpoint)

**Request**:
```bash
curl -X GET http://localhost:8000/users/1/tasks \
  -H "Authorization: Bearer $TOKEN"
```

**Expected Response** (200 OK):
```json
[
  {
    "id": 1,
    "title": "Buy groceries",
    "description": "Milk, eggs, bread",
    "completed": false,
    "user_id": 1,
    "created_at": "2026-01-13T10:30:00Z",
    "updated_at": "2026-01-13T10:30:00Z"
  }
]
```

### Test 5: Update Task (Protected Endpoint)

**Request**:
```bash
curl -X PUT http://localhost:8000/users/1/tasks/1 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "completed": true
  }'
```

**Expected Response** (200 OK):
```json
{
  "id": 1,
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "completed": true,
  "user_id": 1,
  "created_at": "2026-01-13T10:30:00Z",
  "updated_at": "2026-01-13T11:00:00Z"
}
```

### Test 6: Delete Task (Protected Endpoint)

**Request**:
```bash
curl -X DELETE http://localhost:8000/users/1/tasks/1 \
  -H "Authorization: Bearer $TOKEN"
```

**Expected Response** (200 OK):
```json
{
  "message": "Task deleted successfully"
}
```

---

## Validation Checklist

Use this checklist to verify the authentication system is working correctly:

### Backend Validation

- [ ] **Environment configured**: JWT_SECRET set in .env (minimum 32 characters)
- [ ] **Dependencies installed**: PyJWT and passlib installed
- [ ] **Database migrated**: User table has email and password_hash columns
- [ ] **Server running**: Backend accessible at http://localhost:8000
- [ ] **API docs accessible**: http://localhost:8000/docs loads successfully

### Authentication Flow

- [ ] **Signup works**: Can create new user with valid email/password
- [ ] **Duplicate email rejected**: Cannot register same email twice
- [ ] **Weak password rejected**: Passwords under 8 characters rejected
- [ ] **Signin works**: Can authenticate with correct credentials
- [ ] **Invalid credentials rejected**: Wrong password returns 401
- [ ] **Token received**: Signin returns valid JWT token

### Authorization Flow

- [ ] **Protected endpoints require token**: Requests without token return 401
- [ ] **Valid token accepted**: Requests with valid token succeed
- [ ] **Invalid token rejected**: Malformed tokens return 401
- [ ] **User isolation enforced**: Cannot access other users' resources (403)
- [ ] **Token expiration works**: Expired tokens return 401 (test after 24 hours)

### CRUD Operations

- [ ] **Create task**: Can create task with valid token
- [ ] **Read tasks**: Can retrieve own tasks with valid token
- [ ] **Update task**: Can update own task with valid token
- [ ] **Delete task**: Can delete own task with valid token
- [ ] **Cross-user access blocked**: Cannot CRUD other users' tasks

---

## Troubleshooting

### Issue: "JWT_SECRET not found"

**Symptom**: Server fails to start with configuration error

**Solution**:
1. Verify `.env` file exists in `backend/` directory
2. Check `JWT_SECRET` is set and at least 32 characters
3. Restart server after updating `.env`

```bash
# Generate secure secret
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Add to .env
echo "JWT_SECRET=<generated-secret>" >> .env
```

### Issue: "Invalid token" on valid requests

**Symptom**: All authenticated requests return 401 INVALID_TOKEN

**Solution**:
1. Verify JWT_SECRET is identical in frontend and backend
2. Check token is not expired (24-hour limit)
3. Ensure Authorization header format: `Bearer <token>` (note the space)

```bash
# Debug: Decode token to check expiration
python -c "
import jwt
token = 'your-token-here'
print(jwt.decode(token, options={'verify_signature': False}))
"
```

### Issue: "Cannot access another user's resources"

**Symptom**: Getting 403 FORBIDDEN on own resources

**Solution**:
1. Verify user_id in URL matches user_id in token
2. Check token was generated for correct user
3. Ensure signin returns correct user_id

```bash
# Debug: Check token claims
python -c "
import jwt
token = 'your-token-here'
payload = jwt.decode(token, options={'verify_signature': False})
print(f\"Token user_id: {payload['sub']}\")
"
```

### Issue: Database migration fails

**Symptom**: Alembic migration errors

**Solution**:
1. Check database connection string is correct
2. Verify database is accessible
3. Review migration file for conflicts

```bash
# Test database connection
python -c "
from sqlalchemy import create_engine
from backend.src.core.config import settings
engine = create_engine(settings.DATABASE_URL.replace('+asyncpg', ''))
conn = engine.connect()
print('Database connection successful')
conn.close()
"

# Reset migrations (CAUTION: destroys data)
alembic downgrade base
alembic upgrade head
```

### Issue: Password verification fails

**Symptom**: Correct password returns INVALID_CREDENTIALS

**Solution**:
1. Verify passlib[bcrypt] is installed
2. Check password hashing is working during signup
3. Ensure password is not being modified before hashing

```bash
# Test password hashing
python -c "
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
hash = pwd_context.hash('password123')
print(f'Hash: {hash}')
print(f'Verify: {pwd_context.verify(\"password123\", hash)}')
"
```

---

## Performance Testing

### Measure JWT Verification Latency

```bash
# Install Apache Bench (if not installed)
# Ubuntu: sudo apt-get install apache2-utils
# macOS: brew install ab

# Test protected endpoint performance
ab -n 1000 -c 10 \
  -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/users/1/tasks

# Expected: <50ms average response time
```

### Measure Password Hashing Time

```python
# Run in Python shell
import time
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Test hashing performance
start = time.time()
hash = pwd_context.hash("password123")
elapsed = (time.time() - start) * 1000
print(f"Hash time: {elapsed:.2f}ms")

# Expected: ~250ms with work factor 12
```

---

## Next Steps

After completing this quickstart:

1. **Run `/sp.tasks`** to generate task breakdown
2. **Run `/sp.implement`** to execute implementation
3. **Write tests** for authentication endpoints
4. **Deploy** to staging environment
5. **Security audit** before production

---

## Additional Resources

### Documentation

- **Spec**: [spec.md](spec.md) - Feature requirements
- **Plan**: [plan.md](plan.md) - Implementation plan
- **Research**: [research.md](research.md) - Technology decisions
- **Data Model**: [data-model.md](data-model.md) - Database schema
- **API Contracts**: [contracts/auth-api.yaml](contracts/auth-api.yaml) - OpenAPI spec

### External Resources

- **PyJWT Documentation**: https://pyjwt.readthedocs.io/
- **FastAPI Security**: https://fastapi.tiangolo.com/tutorial/security/
- **Better Auth**: https://better-auth.com/docs
- **Neon PostgreSQL**: https://neon.tech/docs

### Support

For issues or questions:
1. Check troubleshooting section above
2. Review error logs in terminal
3. Consult API documentation at http://localhost:8000/docs
4. Review specification documents in `specs/002-auth-security/`
