# Quickstart Guide: AI Chat Agent & Integration

**Feature**: 004-ai-chat-agent
**Date**: 2026-01-23
**Audience**: Developers setting up and testing the AI chat agent feature

## Overview

This guide walks you through setting up the AI chat agent feature, from environment configuration to testing the complete chat flow. Follow these steps in order to get the system running.

## Prerequisites

Before starting, ensure you have:
- ✅ Python 3.13+ installed
- ✅ Node.js 18+ and npm installed
- ✅ PostgreSQL database (Neon) accessible
- ✅ OpenAI API account and API key
- ✅ Existing Phase-II backend and frontend running

## Step 1: Environment Configuration

### Backend Environment Variables

Add the following to `backend/.env`:

```bash
# Existing variables (from Phase-II)
DATABASE_URL=postgresql+asyncpg://user:password@host/database
JWT_SECRET=your-jwt-secret-key
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# NEW: OpenAI API Configuration
OPENAI_API_KEY=sk-your-openai-api-key-here
OPENAI_MODEL=gpt-4
OPENAI_TEMPERATURE=0.7
OPENAI_MAX_TOKENS=500
```

**How to get OpenAI API key**:
1. Go to https://platform.openai.com/api-keys
2. Sign in or create an account
3. Click "Create new secret key"
4. Copy the key and add it to `.env`
5. **Important**: Never commit this key to version control

### Frontend Environment Variables

No new environment variables needed for frontend. Existing `.env.local` should work:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8001
```

## Step 2: Install Dependencies

### Backend Dependencies

```bash
cd backend

# Install new dependencies
pip install openai  # OpenAI Python SDK

# Verify installation
python -c "import openai; print('OpenAI SDK installed successfully')"
```

### Frontend Dependencies

```bash
cd frontend

# Install new dependencies (if using a chat UI library)
npm install react-chat-elements  # Optional: pre-built chat components

# Or just use existing dependencies (Tailwind CSS for custom components)
```

## Step 3: Database Migration

Run the migration to create new tables for conversations, messages, and tool invocation logs.

### Option A: Using SQLModel (Automatic)

The new models will be automatically created when the backend starts (via `init_db()` in `main.py`).

```bash
cd backend
python -m src.main
```

Check logs for:
```
INFO: Database tables initialized successfully
```

### Option B: Manual SQL Migration

If you prefer manual control, run this SQL:

```sql
-- Create conversations table
CREATE TABLE conversation (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_conversation_user_id ON conversation(user_id);

-- Create messages table
CREATE TABLE message (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER NOT NULL REFERENCES conversation(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL CHECK (content <> ''),
    sequence_number INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    tool_invocations TEXT,
    UNIQUE (conversation_id, sequence_number)
);

CREATE INDEX idx_message_conversation_id ON message(conversation_id);
CREATE INDEX idx_message_conversation_sequence ON message(conversation_id, sequence_number);

-- Create tool_invocation_logs table
CREATE TABLE tool_invocation_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
    message_id INTEGER REFERENCES message(id) ON DELETE SET NULL,
    tool_name VARCHAR(100) NOT NULL,
    inputs TEXT NOT NULL,
    outputs TEXT,
    success BOOLEAN NOT NULL,
    error_message VARCHAR(1000),
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_tool_invocation_user_id ON tool_invocation_logs(user_id);
CREATE INDEX idx_tool_invocation_created_at ON tool_invocation_logs(created_at);
CREATE INDEX idx_tool_invocation_tool_name ON tool_invocation_logs(tool_name);
```

### Verify Migration

```bash
# Connect to your database
psql $DATABASE_URL

# Check tables exist
\dt

# Should see: conversation, message, tool_invocation_logs

# Check indexes
\di

# Should see all the idx_* indexes listed above
```

## Step 4: Start Backend Server

```bash
cd backend

# Start with auto-reload for development
uvicorn src.main:app --reload --port 8001

# Or use the existing startup script if you have one
python -m src.main
```

**Expected output**:
```
INFO:     Uvicorn running on http://127.0.0.1:8001
INFO:     Application startup complete
INFO:     Database tables initialized successfully
```

**Verify backend is running**:
```bash
curl http://localhost:8001/
# Should return: {"status": "ok", "message": "Task Management API is running"}
```

## Step 5: Start Frontend Server

```bash
cd frontend

# Start Next.js development server
npm run dev
```

**Expected output**:
```
▲ Next.js 16.1.1 (Turbopack)
- Local:        http://localhost:3000
✓ Ready in 2.5s
```

## Step 6: Test the Chat Flow

### 6.1 Create a Test User

If you don't have a test user, create one:

```bash
curl -X POST http://localhost:8001/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPassword123"
  }'
```

**Expected response**:
```json
{
  "message": "User created successfully",
  "user_id": 1
}
```

### 6.2 Sign In and Get JWT Token

```bash
curl -X POST http://localhost:8001/auth/signin \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPassword123"
  }'
```

**Expected response**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 86400
}
```

**Save the token** for the next steps:
```bash
export TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### 6.3 Send First Chat Message (Create Task)

```bash
curl -X POST http://localhost:8001/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "conversation_id": null,
    "message": "Create a task to buy groceries tomorrow"
  }'
```

**Expected response**:
```json
{
  "conversation_id": 1,
  "message_id": 2,
  "response": "I've created a task 'buy groceries tomorrow' for you. It's been added to your task list.",
  "tool_invocations": [
    {
      "tool": "create_task",
      "inputs": {
        "title": "buy groceries tomorrow",
        "user_id": 1
      },
      "outputs": {
        "task_id": 1,
        "title": "buy groceries tomorrow",
        "completed": false
      }
    }
  ]
}
```

### 6.4 Continue Conversation (List Tasks)

```bash
curl -X POST http://localhost:8001/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "conversation_id": 1,
    "message": "Show me all my tasks"
  }'
```

**Expected response**:
```json
{
  "conversation_id": 1,
  "message_id": 4,
  "response": "You have 1 task:\n1. Buy groceries tomorrow (not completed)",
  "tool_invocations": [
    {
      "tool": "list_tasks",
      "inputs": {
        "user_id": 1
      },
      "outputs": {
        "tasks": [
          {
            "task_id": 1,
            "title": "buy groceries tomorrow",
            "completed": false
          }
        ]
      }
    }
  ]
}
```

### 6.5 Test Frontend Chat UI

1. Open browser to http://localhost:3000
2. Sign in with test@example.com / TestPassword123
3. Navigate to /chat (or click "Chat" link in dashboard)
4. Type a message: "Create a task to call dentist"
5. Verify agent responds and task is created
6. Type another message: "Show my tasks"
7. Verify agent lists both tasks

## Step 7: Verify Tool Invocation Logging

Check that tool invocations are being logged:

```bash
# Connect to database
psql $DATABASE_URL

# Query tool invocation logs
SELECT
  id,
  user_id,
  tool_name,
  success,
  created_at
FROM tool_invocation_logs
ORDER BY created_at DESC
LIMIT 10;
```

**Expected output**:
```
 id | user_id | tool_name   | success | created_at
----+---------+-------------+---------+----------------------------
  2 |       1 | list_tasks  | t       | 2026-01-23 11:45:00
  1 |       1 | create_task | t       | 2026-01-23 11:30:00
```

## Step 8: Test Conversation Resume

Test that conversations persist across sessions:

1. Close the browser tab
2. Restart the backend server (Ctrl+C, then restart)
3. Open browser again to http://localhost:3000/chat
4. Sign in
5. Verify previous conversation is displayed
6. Send a new message
7. Verify agent has context from previous messages

## Troubleshooting

### Issue: "OpenAI API key not found"

**Solution**: Verify `OPENAI_API_KEY` is set in `backend/.env` and restart the backend server.

```bash
# Check if key is set
cd backend
grep OPENAI_API_KEY .env

# If missing, add it
echo "OPENAI_API_KEY=sk-your-key-here" >> .env

# Restart server
uvicorn src.main:app --reload --port 8001
```

### Issue: "Rate limit exceeded" from OpenAI

**Solution**: You've hit OpenAI's rate limit. Wait a few minutes or upgrade your OpenAI plan.

```bash
# Check your OpenAI usage
curl https://api.openai.com/v1/usage \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

### Issue: "Conversation not found"

**Solution**: The conversation_id doesn't exist or doesn't belong to the authenticated user.

```bash
# List all conversations for user
curl http://localhost:8001/conversations \
  -H "Authorization: Bearer $TOKEN"

# Use a valid conversation_id from the response
```

### Issue: "Tool execution failed"

**Solution**: Check the backend logs for detailed error messages.

```bash
# Backend logs will show:
# ERROR: Tool execution failed: <detailed error>

# Common causes:
# - Database connection issue
# - Invalid tool parameters
# - Task not found (for update/delete)
```

### Issue: Frontend shows "Failed to send message"

**Solution**: Check browser console for error details.

```javascript
// Open browser DevTools (F12)
// Check Console tab for errors

// Common causes:
// - Backend not running (check http://localhost:8001/)
// - JWT token expired (sign in again)
// - CORS issue (check backend CORS config)
```

## Testing Checklist

Use this checklist to verify the feature is working correctly:

- [ ] Backend starts without errors
- [ ] Frontend starts without errors
- [ ] Database tables created (conversation, message, tool_invocation_logs)
- [ ] User can sign up and sign in
- [ ] User can send first message (creates new conversation)
- [ ] Agent responds with confirmation
- [ ] Tool invocation logged in database
- [ ] User can continue conversation (uses existing conversation_id)
- [ ] Agent has context from previous messages
- [ ] User can create tasks via natural language
- [ ] User can list tasks via natural language
- [ ] User can update tasks via natural language
- [ ] User can delete tasks via natural language
- [ ] Conversation persists after browser close
- [ ] Conversation persists after server restart
- [ ] Multiple users have isolated conversations
- [ ] Error messages are user-friendly

## Next Steps

After verifying the feature works:

1. **Run Tests**: Execute unit and integration tests
   ```bash
   cd backend
   pytest tests/test_chat_api.py
   pytest tests/test_agent.py
   pytest tests/test_mcp_tools.py
   ```

2. **Performance Testing**: Test with multiple concurrent users
   ```bash
   # Use a load testing tool like locust or k6
   ```

3. **Security Audit**: Verify user isolation and JWT validation
   ```bash
   # Try accessing another user's conversation
   # Should return 404 or 401
   ```

4. **Documentation**: Update README with chat feature instructions

5. **Deployment**: Deploy to production environment

## Useful Commands

### View Backend Logs
```bash
cd backend
tail -f logs/app.log  # If logging to file
# Or just watch the console output
```

### View Database State
```bash
psql $DATABASE_URL

-- Count conversations
SELECT COUNT(*) FROM conversation;

-- Count messages
SELECT COUNT(*) FROM message;

-- Count tool invocations
SELECT COUNT(*) FROM tool_invocation_logs;

-- View recent conversations
SELECT c.id, c.user_id, c.created_at, COUNT(m.id) as message_count
FROM conversation c
LEFT JOIN message m ON m.conversation_id = c.id
GROUP BY c.id
ORDER BY c.created_at DESC
LIMIT 10;
```

### Clear Test Data
```bash
psql $DATABASE_URL

-- Delete all test data (careful!)
DELETE FROM tool_invocation_logs;
DELETE FROM message;
DELETE FROM conversation;
```

## API Documentation

Once the backend is running, view the interactive API documentation:

- **Swagger UI**: http://localhost:8001/docs
- **ReDoc**: http://localhost:8001/redoc

The chat endpoint will be documented there with request/response examples.

---

**Quickstart Status**: ✅ Complete - All setup and testing steps documented
