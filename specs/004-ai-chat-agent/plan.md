# Implementation Plan: AI Chat Agent & Integration

**Branch**: `004-ai-chat-agent` | **Date**: 2026-01-23 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/004-ai-chat-agent/spec.md`

## Summary

Build an AI-powered chat interface that enables users to manage tasks through natural language commands. The system uses OpenAI Agents SDK to interpret user intent and execute task operations via MCP tools, with all conversations persisted in the database for stateless operation. The chat endpoint reconstructs conversation context from the database on every request, ensuring conversations can resume after server restarts.

**Key Technical Approach**:
- Stateless FastAPI chat endpoint with JWT authentication
- OpenAI Agents SDK for natural language understanding and tool orchestration
- MCP tools as the exclusive interface between agent and database
- Conversation and message persistence in Neon PostgreSQL
- Chatkit frontend integration for chat UI
- Tool invocation logging for audit trail and debugging

## Technical Context

**Language/Version**: Python 3.13 (backend), TypeScript/Next.js 16 (frontend)
**Primary Dependencies**:
- Backend: FastAPI, SQLModel, OpenAI Agents SDK, Official MCP SDK, asyncpg
- Frontend: Next.js 16 (App Router), React 18, Chatkit UI library
**Storage**: Neon Serverless PostgreSQL (existing database extended with new tables)
**Testing**: pytest (backend), Jest/React Testing Library (frontend)
**Target Platform**: Linux server (backend), Web browsers (frontend)
**Project Type**: Web application (backend + frontend)
**Performance Goals**:
- Agent responses within 5 seconds for 95% of requests
- Support 100 concurrent users
- Database queries for conversation history < 1 second
**Constraints**:
- Stateless operation (no in-memory conversation state)
- Agent must use MCP tools exclusively (no direct database access)
- All conversations and messages must persist to database
- JWT authentication required for all chat requests
**Scale/Scope**:
- Support for 100+ concurrent users
- Conversation history up to 1000 messages per user
- 4 core MCP tools (create_task, list_tasks, update_task, delete_task)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle I: Spec-Driven Development ✅
- Feature specification approved: `specs/004-ai-chat-agent/spec.md`
- Implementation plan in progress: `specs/004-ai-chat-agent/plan.md`
- Task breakdown will follow: `specs/004-ai-chat-agent/tasks.md`

### Principle II: Agentic Workflow Compliance ✅
- Following spec → plan → tasks → implement workflow
- Will use specialized agents:
  - Database Agent for conversation/message models
  - Backend Agent for chat API and MCP tool integration
  - Frontend Agent for Chatkit UI integration

### Principle III: Security-First Design ✅
- JWT authentication enforced on chat endpoint
- User isolation at conversation and message level (user_id foreign keys)
- Tool invocations scoped to authenticated user
- No hardcoded secrets (OpenAI API key in .env)
- Conversation access restricted to owner only

### Principle IV: Deterministic Behavior ✅
- Chat endpoint follows REST semantics (POST /chat)
- Consistent error responses with proper status codes
- Agent behavior deterministic given same conversation context
- Request/response validation with Pydantic models

### Principle V: Full-Stack Coherence ✅
- Chat API contract defined in Phase 1 (contracts/)
- Frontend consumes chat API exactly as specified
- Database schema matches SQLModel models
- MCP tool schemas align with database operations
- Error handling coordinated between frontend, backend, and agent

### Principle VI: Technology Stack Adherence ✅
- Backend: FastAPI (existing)
- Frontend: Next.js 16 App Router (existing)
- Database: Neon PostgreSQL (existing)
- Auth: JWT (existing)
- AI Agent: OpenAI Agents SDK (new, required)
- Tool Protocol: Official MCP SDK (new, required)

### Principle VII: Multi-User Data Isolation ✅
- Conversation table includes user_id foreign key
- Message table includes user_id (via conversation relationship)
- All queries filter by user_id from JWT token
- Tool invocations include user_id for scoping
- Backend verifies JWT user_id matches request user_id

### Principle VIII: Agent-First Architecture ✅
- Clear separation: UI → Chat API → Agent → MCP Tools → Database
- OpenAI Agents SDK handles natural language understanding
- All task operations executed via MCP tools
- Agent does not access database directly
- Stateless design with context reconstruction

### Principle IX: MCP Tool Design Standards ✅
- Tools are stateless (no state between invocations)
- Each tool has JSON schema (inputs, outputs, errors)
- Single responsibility per tool (create_task, list_tasks, etc.)
- Tools enforce user isolation via user_id parameter
- Tools validate inputs before database operations
- Structured error responses for agent interpretation

### Principle X: Stateless Conversation Management ✅
- Conversations and messages persisted in PostgreSQL
- Chat endpoint does not maintain state in memory
- Context reconstructed from database on every request
- Users can resume conversations after server restart
- Messages stored with timestamps and sequence numbers

### Principle XI: AI Action Traceability ✅
- Tool invocations logged with user_id, tool name, inputs, outputs, timestamp
- All messages persisted (user and assistant)
- Failed tool invocations logged with error details
- Audit trail supports reconstructing agent actions
- Logs contain sufficient information for debugging

**Gate Status**: ✅ PASSED - All constitution principles satisfied

## Project Structure

### Documentation (this feature)

```text
specs/004-ai-chat-agent/
├── spec.md              # Feature specification (completed)
├── plan.md              # This file (in progress)
├── research.md          # Phase 0 output (to be generated)
├── data-model.md        # Phase 1 output (to be generated)
├── quickstart.md        # Phase 1 output (to be generated)
├── contracts/           # Phase 1 output (to be generated)
│   ├── chat-api.yaml    # OpenAPI spec for chat endpoint
│   └── mcp-tools.json   # MCP tool schemas
├── checklists/
│   └── requirements.md  # Spec quality checklist (completed)
└── tasks.md             # Phase 2 output (/sp.tasks command)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── models/
│   │   ├── user.py              # Existing
│   │   ├── task.py              # Existing
│   │   ├── conversation.py      # NEW: Conversation model
│   │   ├── message.py           # NEW: Message model
│   │   └── tool_invocation.py   # NEW: Tool invocation log model
│   ├── schemas/
│   │   ├── auth.py              # Existing
│   │   ├── task.py              # Existing
│   │   ├── chat.py              # NEW: Chat request/response schemas
│   │   └── mcp.py               # NEW: MCP tool schemas
│   ├── api/
│   │   ├── routes/
│   │   │   ├── auth.py          # Existing
│   │   │   ├── tasks.py         # Existing
│   │   │   └── chat.py          # NEW: Chat endpoint
│   │   └── deps.py              # Existing (may need updates)
│   ├── services/
│   │   ├── agent.py             # NEW: OpenAI Agent service
│   │   ├── mcp_tools.py         # NEW: MCP tool implementations
│   │   └── conversation.py      # NEW: Conversation management service
│   ├── core/
│   │   ├── config.py            # Existing (add OpenAI API key)
│   │   ├── database.py          # Existing
│   │   └── security.py          # Existing
│   └── main.py                  # Existing (register chat router)
└── tests/
    ├── test_chat_api.py         # NEW: Chat endpoint tests
    ├── test_agent.py            # NEW: Agent service tests
    └── test_mcp_tools.py        # NEW: MCP tool tests

frontend/
├── app/
│   ├── dashboard/
│   │   └── page.tsx             # Existing (add chat link)
│   ├── chat/
│   │   └── page.tsx             # NEW: Chat interface page
│   ├── signin/
│   │   └── page.tsx             # Existing
│   └── signup/
│       └── page.tsx             # Existing
├── components/
│   ├── auth/                    # Existing
│   └── chat/                    # NEW: Chat UI components
│       ├── ChatInterface.tsx    # Main chat component
│       ├── MessageList.tsx      # Message display
│       ├── MessageInput.tsx     # Input field
│       └── MessageBubble.tsx    # Individual message
└── lib/
    ├── api.ts                   # Existing (add chat API calls)
    └── types.ts                 # Existing (add chat types)
```

**Structure Decision**: Web application structure (Option 2) with backend and frontend directories. Extending existing FastAPI backend with new chat routes and services. Extending existing Next.js frontend with new chat pages and components. All new code follows existing patterns and conventions.

## Complexity Tracking

> No constitution violations - this section is not needed.

## Phase 0: Research & Technology Decisions

### Research Tasks

1. **OpenAI Agents SDK Integration**
   - Research: How to initialize and configure OpenAI Agents SDK in FastAPI
   - Research: Agent prompt design best practices for task management
   - Research: Tool calling patterns and error handling
   - Research: Async/await compatibility with FastAPI

2. **MCP SDK Integration**
   - Research: Official MCP SDK installation and setup
   - Research: Tool schema definition format (JSON Schema)
   - Research: Tool registration and invocation patterns
   - Research: Error handling and validation in MCP tools

3. **Stateless Conversation Management**
   - Research: Efficient conversation history loading from database
   - Research: Context window management for large conversations
   - Research: Message ordering and pagination strategies
   - Research: Database indexing for fast conversation retrieval

4. **Chatkit Frontend Integration**
   - Research: Chatkit library installation and configuration
   - Research: Message rendering and styling patterns
   - Research: Real-time vs polling for message updates
   - Research: Error handling and retry logic in chat UI

### Technology Decisions

**Decision 1: OpenAI Agents SDK**
- **Chosen**: OpenAI Agents SDK (official Python library)
- **Rationale**: Required by constitution, official support, robust tool calling
- **Alternatives Considered**: LangChain (more complex), custom implementation (too much work)

**Decision 2: MCP Tool Protocol**
- **Chosen**: Official MCP SDK
- **Rationale**: Required by constitution, standardized protocol, good documentation
- **Alternatives Considered**: Custom tool protocol (not standardized), function calling (less structured)

**Decision 3: Conversation Storage Strategy**
- **Chosen**: Full conversation history in database with pagination
- **Rationale**: Stateless requirement, enables resume after restart, supports audit trail
- **Alternatives Considered**: In-memory cache (violates stateless), Redis (adds complexity)

**Decision 4: Frontend Chat Library**
- **Chosen**: Chatkit (or similar React chat UI library)
- **Rationale**: Pre-built components, consistent styling, faster development
- **Alternatives Considered**: Custom components (more work), third-party chat service (overkill)

**Decision 5: Agent Prompt Strategy**
- **Chosen**: System prompt with tool descriptions and examples
- **Rationale**: Clear instructions, consistent behavior, easy to iterate
- **Alternatives Considered**: Few-shot learning (more complex), fine-tuning (not needed)

## Phase 1: Design & Contracts

### Data Model Design

See `data-model.md` for complete entity definitions, relationships, and validation rules.

**Summary of New Entities**:
1. **Conversation**: Represents a chat session (user_id, created_at, updated_at)
2. **Message**: Individual messages in a conversation (conversation_id, role, content, sequence_number, timestamp)
3. **ToolInvocationLog**: Audit trail for MCP tool calls (user_id, tool_name, inputs, outputs, timestamp, success)

**Key Relationships**:
- User → Conversations (one-to-many)
- Conversation → Messages (one-to-many)
- User → ToolInvocationLogs (one-to-many)
- Message → ToolInvocationLog (optional one-to-one for messages that triggered tools)

### API Contracts

See `contracts/` directory for complete OpenAPI and MCP schemas.

**Chat API Endpoint**:
```
POST /chat
Authorization: Bearer <jwt_token>
Content-Type: application/json

Request:
{
  "conversation_id": 123,  // optional, null for new conversation
  "message": "Create a task to buy groceries"
}

Response:
{
  "conversation_id": 123,
  "message_id": 456,
  "response": "I've created a task 'buy groceries' for you. It's been added to your task list.",
  "tool_invocations": [
    {
      "tool": "create_task",
      "inputs": {"title": "buy groceries", "user_id": 7},
      "outputs": {"task_id": 89, "title": "buy groceries", "completed": false}
    }
  ]
}
```

**MCP Tool Schemas**:
- `create_task`: Creates a new task for the user
- `list_tasks`: Lists all tasks for the user
- `update_task`: Updates an existing task
- `delete_task`: Deletes a task

### Agent Architecture

**Agent Configuration**:
- Model: GPT-4 (or latest available)
- Temperature: 0.7 (balance between creativity and consistency)
- Max tokens: 500 (concise responses)
- Tools: 4 MCP tools registered

**System Prompt**:
```
You are a helpful task management assistant. Users can ask you to create, view, update,
or delete their tasks using natural language.

Available tools:
- create_task: Create a new task with a title and optional description
- list_tasks: Show all tasks for the user
- update_task: Update a task's title, description, or completion status
- delete_task: Remove a task

Guidelines:
- Be concise and friendly
- Confirm actions after executing them
- Ask clarifying questions if the user's intent is unclear
- If a task reference is ambiguous, ask which task they mean
- Always use tools to perform task operations - never make up data
```

### Integration Points

1. **Backend → Database**: SQLModel async queries for conversations and messages
2. **Backend → OpenAI**: Agent service calls OpenAI API with conversation context
3. **Backend → MCP Tools**: Agent invokes tools which execute database operations
4. **Frontend → Backend**: HTTP POST to /chat endpoint with JWT auth
5. **Frontend → Chatkit**: React components render messages from API responses

### Quickstart Guide

See `quickstart.md` for step-by-step setup instructions including:
- Environment variable configuration (OpenAI API key)
- Database migration for new tables
- Backend service startup
- Frontend development server
- Testing the chat interface

## Phase 2: Task Breakdown

*This phase is handled by the `/sp.tasks` command and will generate `tasks.md`.*

The task breakdown will include:
1. Database schema implementation (Conversation, Message, ToolInvocationLog models)
2. MCP tool implementation (4 tools with schemas and validation)
3. Agent service implementation (OpenAI SDK integration, prompt configuration)
4. Chat API endpoint implementation (stateless, JWT auth, context reconstruction)
5. Conversation management service (load history, persist messages, pagination)
6. Frontend chat page implementation (Chatkit integration, message rendering)
7. Frontend API integration (chat endpoint calls, error handling)
8. Testing (unit tests for tools, integration tests for chat flow)
9. Documentation updates (API docs, README)

## Risk Analysis

### Technical Risks

1. **OpenAI API Rate Limits**
   - Risk: High usage could hit rate limits
   - Mitigation: Implement exponential backoff, queue requests if needed
   - Fallback: Display user-friendly error message, allow retry

2. **Large Conversation Context**
   - Risk: Very long conversations exceed token limits
   - Mitigation: Implement context window management, summarize old messages
   - Fallback: Truncate to most recent N messages

3. **Database Query Performance**
   - Risk: Loading full conversation history could be slow
   - Mitigation: Add database indexes on user_id and conversation_id, implement pagination
   - Fallback: Load only recent messages initially

4. **Agent Misinterpretation**
   - Risk: Agent might misunderstand user intent
   - Mitigation: Clear system prompt, ask clarifying questions, log all interactions
   - Fallback: Allow users to rephrase or use direct task management UI

### Integration Risks

1. **MCP Tool Failures**
   - Risk: Tool invocation could fail (database error, validation error)
   - Mitigation: Comprehensive error handling, structured error responses
   - Fallback: Agent explains error to user, suggests alternatives

2. **Frontend-Backend Mismatch**
   - Risk: Chat API contract changes could break frontend
   - Mitigation: Define contract upfront in OpenAPI spec, version API if needed
   - Fallback: Graceful degradation, show error message

3. **JWT Token Expiration**
   - Risk: Token expires during conversation
   - Mitigation: Frontend refreshes token proactively, handles 401 gracefully
   - Fallback: Redirect to signin, preserve conversation state

## Success Metrics

### Functional Metrics
- ✅ Users can create tasks via natural language (90% success rate target)
- ✅ Conversations persist across sessions (100% message retention)
- ✅ Agent correctly invokes MCP tools (85% accuracy target)
- ✅ User isolation maintained (0% cross-user access)

### Performance Metrics
- ✅ Agent responses within 5 seconds (95th percentile)
- ✅ Database queries < 1 second (conversation history)
- ✅ Support 100 concurrent users without degradation

### Quality Metrics
- ✅ All tool invocations logged for audit trail
- ✅ Zero security violations (user isolation, JWT validation)
- ✅ Graceful error handling (no crashes, user-friendly messages)

## Next Steps

1. **Generate research.md**: Document OpenAI SDK and MCP SDK integration patterns
2. **Generate data-model.md**: Define Conversation, Message, and ToolInvocationLog entities
3. **Generate contracts/**: Create OpenAPI spec for chat endpoint and MCP tool schemas
4. **Generate quickstart.md**: Step-by-step setup and testing guide
5. **Run /sp.tasks**: Generate detailed task breakdown with dependencies and acceptance criteria

---

**Plan Status**: Phase 0 and Phase 1 design complete. Ready for `/sp.tasks` to generate implementation tasks.
