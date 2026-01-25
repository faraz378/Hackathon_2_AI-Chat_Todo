# Tasks: AI Chat Agent & Integration

**Input**: Design documents from `/specs/004-ai-chat-agent/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `backend/src/`
- **Frontend**: `frontend/`
- All paths are relative to repository root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization, environment configuration, and dependency installation

- [x] T001 Add OpenAI API key configuration to backend/.env (OPENAI_API_KEY, OPENAI_MODEL, OPENAI_TEMPERATURE, OPENAI_MAX_TOKENS)
- [x] T002 Install OpenAI Python SDK in backend (pip install openai)
- [x] T003 [P] Update backend/src/core/config.py to load OpenAI configuration from environment variables
- [x] T004 [P] Verify existing JWT authentication and database connection are working

**Checkpoint**: Environment configured, dependencies installed

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core database models and infrastructure that ALL user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T005 Create Conversation model in backend/src/models/conversation.py with user_id FK, timestamps, and relationship to User
- [x] T006 [P] Create Message model in backend/src/models/message.py with conversation_id FK, role, content, sequence_number, timestamps
- [x] T007 [P] Create ToolInvocationLog model in backend/src/models/tool_invocation.py with user_id FK, tool_name, inputs, outputs, success, error_message
- [x] T008 Update backend/src/models/__init__.py to export new models (Conversation, Message, ToolInvocationLog)
- [x] T009 Run database migration to create conversation, message, and tool_invocation_logs tables with indexes
- [x] T010 [P] Create chat request/response schemas in backend/src/schemas/chat.py (ChatRequest, ChatResponse, ToolInvocation)
- [x] T011 [P] Create MCP tool schemas in backend/src/schemas/mcp.py (CreateTaskInput, ListTasksInput, UpdateTaskInput, DeleteTaskInput)
- [x] T012 Verify database tables created successfully and indexes exist (user_id, conversation_id, sequence_number)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Natural Language Task Management (Priority: P1) 🎯 MVP

**Goal**: Enable users to create, view, update, and delete tasks using natural language commands through a chat interface

**Independent Test**: Send messages like "Create a task to buy groceries", "Show my tasks", "Mark groceries as done", "Delete groceries task" and verify agent correctly interprets intent and executes operations via MCP tools

### Backend Implementation for User Story 1

- [x] T013 [P] [US1] Implement create_task MCP tool in backend/src/services/mcp_tools.py with user_id scoping and validation
- [x] T014 [P] [US1] Implement list_tasks MCP tool in backend/src/services/mcp_tools.py with user_id filtering and optional completion filter
- [x] T015 [P] [US1] Implement update_task MCP tool in backend/src/services/mcp_tools.py with task_id lookup and user_id verification
- [x] T016 [P] [US1] Implement delete_task MCP tool in backend/src/services/mcp_tools.py with task_id lookup and user_id verification
- [x] T017 [US1] Create AgentService in backend/src/services/agent.py with OpenAI client initialization and system prompt configuration
- [x] T018 [US1] Implement tool registration in AgentService with JSON schemas for all 4 MCP tools (create_task, list_tasks, update_task, delete_task)
- [x] T019 [US1] Implement chat method in AgentService that sends messages to OpenAI with conversation context and handles tool calls
- [x] T020 [US1] Implement tool execution logic in AgentService that invokes MCP tools and returns results to agent
- [x] T021 [US1] Create ConversationService in backend/src/services/conversation.py with create_conversation method
- [x] T022 [US1] Implement add_message method in ConversationService with sequence number calculation and conversation timestamp update
- [x] T023 [US1] Implement log_tool_invocation method in ConversationService to persist tool calls to tool_invocation_logs table
- [x] T024 [US1] Create chat endpoint POST /chat in backend/src/api/routes/chat.py with JWT authentication dependency
- [x] T025 [US1] Implement chat endpoint logic: extract user_id from JWT, create/load conversation, add user message, call AgentService
- [x] T026 [US1] Implement chat endpoint response: add assistant message, log tool invocations, return ChatResponse with conversation_id and message_id
- [x] T027 [US1] Add error handling in chat endpoint for OpenAI API errors, database errors, and tool execution failures
- [x] T028 [US1] Register chat router in backend/src/main.py with proper CORS configuration
- [x] T029 [US1] Add input validation in chat endpoint (message length max 10000 chars, conversation_id ownership verification)

### Frontend Implementation for User Story 1

- [x] T030 [P] [US1] Create chat page in frontend/app/chat/page.tsx with authentication check and layout
- [x] T031 [P] [US1] Create ChatInterface component in frontend/components/chat/ChatInterface.tsx with state management for messages and conversation_id
- [x] T032 [P] [US1] Create MessageList component in frontend/components/chat/MessageList.tsx with scrollable message display
- [x] T033 [P] [US1] Create MessageBubble component in frontend/components/chat/MessageBubble.tsx with role-based styling (user vs assistant)
- [x] T034 [P] [US1] Create MessageInput component in frontend/components/chat/MessageInput.tsx with textarea and send button
- [x] T035 [US1] Implement sendMessage API call in frontend/lib/api.ts that POSTs to /chat endpoint with JWT token
- [x] T036 [US1] Integrate sendMessage in ChatInterface with optimistic UI updates (add user message immediately, update with response)
- [x] T037 [US1] Add error handling in ChatInterface for failed API calls with user-friendly error messages
- [x] T038 [US1] Add loading state in ChatInterface while waiting for agent response
- [x] T039 [US1] Style chat components with Tailwind CSS to match existing design system

**Checkpoint**: At this point, User Story 1 should be fully functional - users can manage tasks via natural language

---

## Phase 4: User Story 2 - Conversation Persistence and Resume (Priority: P2)

**Goal**: Enable users to see conversation history and continue conversations after closing browser or server restart

**Independent Test**: Have a conversation, close browser, reopen, verify full history is displayed and user can continue chatting with context

### Backend Implementation for User Story 2

- [x] T040 [US2] Implement load_conversation_messages method in ConversationService that queries messages ordered by sequence_number
- [x] T041 [US2] Implement get_user_conversations method in ConversationService that lists all conversations for a user with message counts
- [x] T042 [US2] Update chat endpoint to load conversation history from database when conversation_id is provided
- [x] T043 [US2] Implement conversation context reconstruction in AgentService that converts database messages to OpenAI format
- [x] T044 [US2] Add pagination support in load_conversation_messages (limit to most recent 50 messages for performance)
- [x] T045 [US2] Create GET /conversations endpoint in backend/src/api/routes/chat.py to list user's conversations
- [x] T046 [US2] Create GET /conversations/{conversation_id}/messages endpoint to retrieve full message history with pagination
- [x] T047 [US2] Add conversation ownership verification in all conversation endpoints (user_id from JWT must match conversation.user_id)

### Frontend Implementation for User Story 2

- [x] T048 [P] [US2] Implement loadConversationHistory API call in frontend/lib/api/chat.ts that GETs /conversations/{id}/messages
- [x] T049 [P] [US2] Implement listConversations API call in frontend/lib/api/chat.ts that GETs /conversations
- [x] T050 [US2] Update ChatInterface to load conversation history on mount when conversation_id exists
- [x] T051 [US2] Add conversation list sidebar in frontend/app/chat/page.tsx showing user's conversations with last message preview
- [x] T052 [US2] Implement conversation selection in sidebar that loads selected conversation's messages
- [x] T053 [US2] Add "New Conversation" button that clears current conversation and starts fresh
- [x] T054 [US2] Persist conversation_id in URL query parameter for shareable/bookmarkable conversations
- [x] T055 [US2] Add auto-scroll to bottom when new messages arrive in MessageList component

**Checkpoint**: At this point, User Story 2 should be fully functional - conversations persist and resume correctly

---

## Phase 5: User Story 3 - AI Agent Feedback and Confirmations (Priority: P3)

**Goal**: Provide clear, helpful agent responses with confirmations, error explanations, and guidance

**Independent Test**: Send various commands (successful, ambiguous, failing) and verify agent provides appropriate confirmations, clarifying questions, and helpful error messages

### Backend Implementation for User Story 3

- [x] T056 [US3] Enhance system prompt in AgentService with detailed guidelines for confirmations, clarifying questions, and error explanations
- [x] T057 [US3] Add examples to system prompt showing good agent responses for common scenarios (task created, task not found, ambiguous reference)
- [x] T058 [US3] Implement help command handling in AgentService that provides examples of supported commands
- [x] T059 [US3] Enhance error handling in MCP tools to return structured error messages with user-friendly descriptions
- [x] T060 [US3] Update tool execution logic in AgentService to pass tool errors back to agent for explanation to user
- [x] T061 [US3] Add ambiguity detection in AgentService (e.g., when user says "complete the task" but has multiple tasks)
- [x] T062 [US3] Implement clarifying question flow where agent asks user to specify which task they mean

### Frontend Implementation for User Story 3

- [x] T063 [P] [US3] Add tool invocation display in MessageBubble to show which tools were called (optional, for transparency)
- [x] T064 [P] [US3] Add typing indicator in ChatInterface while agent is processing
- [x] T065 [P] [US3] Add timestamp display in MessageBubble for each message
- [x] T066 [US3] Improve error message display in ChatInterface with retry button for failed messages
- [x] T067 [US3] Add welcome message when user first opens chat explaining what the agent can do

**Checkpoint**: At this point, User Story 3 should be fully functional - agent provides excellent UX with clear feedback

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final improvements, documentation, and deployment preparation

- [x] T068 [P] Add comprehensive logging throughout chat flow (request received, agent called, tools invoked, response sent)
- [x] T069 [P] Add rate limiting middleware to chat endpoint (e.g., 60 requests per minute per user)
- [x] T070 [P] Update API documentation in backend/src/main.py to include chat endpoints
- [x] T071 [P] Add link to chat page in frontend dashboard navigation
- [x] T072 [P] Create user guide documentation explaining how to use the chat interface
- [x] T073 Verify all tool invocations are being logged correctly in tool_invocation_logs table
- [x] T074 Verify user isolation - test that users cannot access other users' conversations
- [x] T075 Verify conversation persistence - restart backend server and confirm conversations resume correctly
- [x] T076 Performance test - verify agent responses within 5 seconds for 95% of requests
- [x] T077 Load test - verify system handles 100 concurrent users without degradation
- [x] T078 Security audit - verify JWT validation, user isolation, and input validation are working correctly
- [x] T079 Update README.md with chat feature setup instructions and usage examples
- [x] T080 Create deployment checklist for production environment (OpenAI API key, database migration, CORS config)

**Checkpoint**: Feature complete, tested, documented, and ready for deployment

---

## Dependencies & Execution Strategy

### User Story Dependencies

```
Phase 1 (Setup) → Phase 2 (Foundational)
                      ↓
    ┌─────────────────┼─────────────────┐
    ↓                 ↓                 ↓
Phase 3 (US1)    Phase 4 (US2)    Phase 5 (US3)
    ↓                 ↓                 ↓
    └─────────────────┼─────────────────┘
                      ↓
                Phase 6 (Polish)
```

**Key Insights**:
- Phase 1 and 2 are sequential and blocking
- Phase 3, 4, 5 (user stories) can be implemented in parallel after Phase 2 completes
- However, US2 and US3 build on US1, so sequential implementation (US1 → US2 → US3) is recommended for MVP approach
- Phase 6 can only start after all user stories are complete

### Parallel Execution Opportunities

**Within Phase 2 (Foundational)**:
- T006, T007 can run in parallel (different model files)
- T010, T011 can run in parallel (different schema files)

**Within Phase 3 (US1)**:
- Backend: T013-T016 (MCP tools) can all run in parallel (same file but independent functions)
- Frontend: T030-T034 (components) can all run in parallel (different files)
- Backend and Frontend can run in parallel after T029 completes

**Within Phase 4 (US2)**:
- T048, T049 can run in parallel (different API calls)
- Backend and Frontend can run in parallel

**Within Phase 5 (US3)**:
- T063-T065 can run in parallel (different frontend components)
- Backend and Frontend can run in parallel

**Within Phase 6 (Polish)**:
- T068-T072 can all run in parallel (different concerns)

### MVP Scope Recommendation

**Minimum Viable Product (MVP)**: Phase 1 + Phase 2 + Phase 3 (User Story 1 only)

This delivers:
- ✅ Natural language task management via chat
- ✅ Agent correctly interprets commands and uses MCP tools
- ✅ Basic chat UI with message display and input
- ✅ User authentication and isolation
- ✅ Tool invocation logging

**MVP excludes**:
- ❌ Conversation persistence (US2) - users start fresh each time
- ❌ Enhanced agent feedback (US3) - basic responses only
- ❌ Polish features (rate limiting, comprehensive docs)

**MVP Task Count**: 39 tasks (T001-T039)
**Full Feature Task Count**: 80 tasks

### Implementation Timeline Estimate

**Note**: Time estimates are provided for planning purposes only, not as commitments

- Phase 1 (Setup): 4 tasks - ~1 hour
- Phase 2 (Foundational): 8 tasks - ~4 hours
- Phase 3 (US1 - MVP): 27 tasks - ~12 hours
- Phase 4 (US2): 16 tasks - ~6 hours
- Phase 5 (US3): 12 tasks - ~4 hours
- Phase 6 (Polish): 13 tasks - ~4 hours

**Total**: 80 tasks - ~31 hours (with parallelization, can be reduced significantly)

---

## Task Validation Checklist

✅ All tasks follow format: `- [ ] [TaskID] [P?] [Story?] Description with file path`
✅ Tasks organized by user story for independent implementation
✅ Each user story has clear goal and independent test criteria
✅ Foundational phase clearly marked as blocking
✅ Parallel opportunities identified with [P] marker
✅ File paths included in all implementation tasks
✅ Dependencies documented in execution strategy
✅ MVP scope clearly defined (Phase 1 + 2 + 3)
✅ No test tasks included (tests not requested in spec)

---

**Tasks Status**: ✅ Complete - 80 tasks generated, organized by user story, ready for implementation
