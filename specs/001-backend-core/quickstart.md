# Quickstart Guide: Backend Core & Data Layer

**Feature**: Backend Core & Data Layer
**Date**: 2026-01-12
**Purpose**: Setup instructions, testing guide, and API usage examples

## Prerequisites

- Python 3.11 or higher
- Neon PostgreSQL account (free tier available at https://neon.tech)
- Git (for cloning repository)
- curl or Postman (for API testing)

## Environment Setup

### 1. Clone Repository and Navigate to Backend

```bash
git clone <repository-url>
cd hackathon-2-phase2
git checkout 001-backend-core
cd backend
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

**requirements.txt contents**:
```
fastapi==0.104.1
sqlmodel==0.0.14
pydantic==2.5.0
uvicorn[standard]==0.24.0
asyncpg==0.29.0
python-dotenv==1.0.0
pytest==7.4.3
pytest-asyncio==0.21.1
httpx==0.25.2
```

### 4. Configure Database Connection

Create `.env` file in `backend/` directory:

```bash
# .env
DATABASE_URL=postgresql+asyncpg://user:password@ep-xxx.region.aws.neon.tech/dbname?sslmode=require
```

**Getting Neon Connection String**:
1. Sign up at https://neon.tech
2. Create a new project
3. Copy the connection string from the dashboard
4. Replace `postgresql://` with `postgresql+asyncpg://` for async support
5. Add `?sslmode=require` at the end

### 5. Initialize Database

```bash
# Run database initialization script
python -m src.core.database init

# Or use SQLModel's automatic table creation (development only)
# Tables will be created on first app startup
```

## Running the Application

### Development Server

```bash
# Start FastAPI development server with auto-reload
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

**Expected Output**:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using StatReload
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### Verify Server is Running

```bash
curl http://localhost:8000/docs
```

This opens the interactive API documentation (Swagger UI).

## API Usage Examples

### 1. Create a Task

```bash
curl -X POST http://localhost:8000/users/123/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Buy groceries",
    "description": "Milk and eggs"
  }'
```

**Expected Response** (201 Created):
```json
{
  "id": 1,
  "title": "Buy groceries",
  "description": "Milk and eggs",
  "completed": false,
  "user_id": 123,
  "created_at": "2026-01-12T10:00:00Z",
  "updated_at": "2026-01-12T10:00:00Z"
}
```

### 2. Get All Tasks for a User

```bash
curl http://localhost:8000/users/123/tasks
```

**Expected Response** (200 OK):
```json
[
  {
    "id": 1,
    "title": "Buy groceries",
    "description": "Milk and eggs",
    "completed": false,
    "user_id": 123,
    "created_at": "2026-01-12T10:00:00Z",
    "updated_at": "2026-01-12T10:00:00Z"
  }
]
```

### 3. Get a Specific Task

```bash
curl http://localhost:8000/users/123/tasks/1
```

**Expected Response** (200 OK):
```json
{
  "id": 1,
  "title": "Buy groceries",
  "description": "Milk and eggs",
  "completed": false,
  "user_id": 123,
  "created_at": "2026-01-12T10:00:00Z",
  "updated_at": "2026-01-12T10:00:00Z"
}
```

### 4. Update a Task (Mark as Complete)

```bash
curl -X PUT http://localhost:8000/users/123/tasks/1 \
  -H "Content-Type: application/json" \
  -d '{
    "completed": true
  }'
```

**Expected Response** (200 OK):
```json
{
  "id": 1,
  "title": "Buy groceries",
  "description": "Milk and eggs",
  "completed": true,
  "user_id": 123,
  "created_at": "2026-01-12T10:00:00Z",
  "updated_at": "2026-01-12T15:00:00Z"
}
```

### 5. Delete a Task

```bash
curl -X DELETE http://localhost:8000/users/123/tasks/1
```

**Expected Response** (200 OK):
```json
{
  "message": "Task deleted successfully"
}
```

## Testing User Isolation

### Verify User Cannot Access Another User's Tasks

```bash
# Create task for user 123
curl -X POST http://localhost:8000/users/123/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "User 123 task"}'

# Try to access as user 456 (should return 404)
curl http://localhost:8000/users/456/tasks/1
```

**Expected Response** (404 Not Found):
```json
{
  "error": {
    "code": "NOT_FOUND",
    "message": "Task not found"
  }
}
```

## Running Tests

### Run All Tests

```bash
# From backend/ directory
pytest

# With verbose output
pytest -v

# With coverage report
pytest --cov=src --cov-report=html
```

**Expected Output**:
```
============================= test session starts ==============================
collected 15 items

tests/test_tasks_api.py ........                                         [ 53%]
tests/test_user_isolation.py .......                                     [100%]

============================== 15 passed in 2.34s ==============================
```

### Run Specific Test File

```bash
pytest tests/test_tasks_api.py
pytest tests/test_user_isolation.py
```

### Run Specific Test

```bash
pytest tests/test_tasks_api.py::test_create_task
pytest tests/test_user_isolation.py::test_user_cannot_access_other_user_tasks
```

## Validation Checklist

Use this checklist to verify the backend is working correctly:

### ✅ Basic Functionality
- [ ] Server starts without errors
- [ ] API documentation accessible at http://localhost:8000/docs
- [ ] Can create a task with title only
- [ ] Can create a task with title and description
- [ ] Can retrieve all tasks for a user
- [ ] Can retrieve a specific task by ID
- [ ] Can update task title
- [ ] Can update task description
- [ ] Can mark task as complete
- [ ] Can mark task as incomplete
- [ ] Can delete a task

### ✅ Validation
- [ ] Cannot create task with empty title (400 error)
- [ ] Cannot create task with title > 500 characters (400 error)
- [ ] Cannot create task with description > 5000 characters (400 error)
- [ ] Cannot update task with empty title (400 error)

### ✅ User Isolation
- [ ] User A cannot retrieve User B's tasks
- [ ] User A cannot retrieve User B's specific task (404 error)
- [ ] User A cannot update User B's task (404 error)
- [ ] User A cannot delete User B's task (404 error)
- [ ] Empty list returned for user with no tasks (not error)

### ✅ HTTP Status Codes
- [ ] POST /tasks returns 201 on success
- [ ] GET /tasks returns 200 on success
- [ ] GET /tasks/{id} returns 200 on success
- [ ] GET /tasks/{id} returns 404 when not found
- [ ] PUT /tasks/{id} returns 200 on success
- [ ] PUT /tasks/{id} returns 404 when not found
- [ ] DELETE /tasks/{id} returns 200 on success
- [ ] DELETE /tasks/{id} returns 404 when not found
- [ ] Validation errors return 400

### ✅ Data Persistence
- [ ] Tasks persist after server restart
- [ ] Task data is correct after restart (title, description, completed)
- [ ] Timestamps are preserved after restart

### ✅ Concurrent Operations
- [ ] Multiple tasks can be created simultaneously
- [ ] No data corruption with concurrent requests
- [ ] Database handles concurrent reads/writes

## Troubleshooting

### Database Connection Errors

**Problem**: `asyncpg.exceptions.InvalidPasswordError`
**Solution**: Verify DATABASE_URL in .env file, check Neon dashboard for correct credentials

**Problem**: `asyncpg.exceptions.ConnectionDoesNotExistError`
**Solution**: Ensure Neon project is active (not suspended), check network connectivity

### Import Errors

**Problem**: `ModuleNotFoundError: No module named 'fastapi'`
**Solution**: Activate virtual environment and run `pip install -r requirements.txt`

### Port Already in Use

**Problem**: `OSError: [Errno 48] Address already in use`
**Solution**: Kill existing process on port 8000 or use different port:
```bash
uvicorn src.main:app --reload --port 8001
```

### Tests Failing

**Problem**: Tests fail with database errors
**Solution**: Ensure test database is configured, or use SQLite for tests:
```python
# In conftest.py
DATABASE_URL = "sqlite:///./test.db"
```

## Next Steps

After verifying the backend works correctly:

1. **Proceed to /sp.tasks**: Generate task breakdown for implementation
2. **Implement with agents**: Use Database Agent for models, Backend Agent for API routes
3. **Integration with Spec-2**: Add JWT authentication (user_id from token instead of path parameter)
4. **Integration with Spec-3**: Frontend will consume these API endpoints

## API Documentation

- **Interactive Docs**: http://localhost:8000/docs (Swagger UI)
- **ReDoc**: http://localhost:8000/redoc (Alternative documentation)
- **OpenAPI Spec**: http://localhost:8000/openapi.json (Machine-readable)
- **Contract File**: `specs/001-backend-core/contracts/openapi.yaml`

## Development Tips

### Enable Debug Logging

```python
# In src/main.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Database Query Logging

```python
# In src/core/database.py
engine = create_async_engine(DATABASE_URL, echo=True)  # Logs all SQL queries
```

### Hot Reload

FastAPI with `--reload` automatically restarts on code changes. No need to manually restart server during development.

### Testing with Postman

Import the OpenAPI spec into Postman:
1. Open Postman
2. Import → Link → http://localhost:8000/openapi.json
3. Collection created with all endpoints

## Performance Benchmarking

### Load Testing with Apache Bench

```bash
# Test create endpoint (100 requests, 10 concurrent)
ab -n 100 -c 10 -p task.json -T application/json \
  http://localhost:8000/users/123/tasks

# task.json content:
# {"title": "Load test task"}
```

**Expected Results**:
- Requests per second: > 100
- Mean response time: < 100ms
- No failed requests

### Verify Concurrent Request Handling

```bash
# Create 100 tasks concurrently
for i in {1..100}; do
  curl -X POST http://localhost:8000/users/123/tasks \
    -H "Content-Type: application/json" \
    -d "{\"title\": \"Task $i\"}" &
done
wait

# Verify all 100 tasks were created
curl http://localhost:8000/users/123/tasks | jq 'length'
# Should output: 100
```

## Security Notes

**⚠️ Important for Spec-1**:
- user_id is passed as path parameter (not authenticated)
- No JWT validation in this spec
- Suitable for development/testing only
- **DO NOT deploy to production without Spec-2 authentication**

**Spec-2 will add**:
- JWT token validation
- user_id extracted from token (not path parameter)
- Secure authentication endpoints
- Password hashing

## Support

For issues or questions:
- Check troubleshooting section above
- Review API documentation at /docs
- Consult data-model.md for schema details
- Review research.md for technical decisions
