<!--
Sync Impact Report:
- Version: 1.0.0 → 1.1.0 (Phase-III: AI-Powered Todo Chatbot Extension)
- Rationale: MINOR version bump - Added new principles for AI agent architecture and MCP tools without removing or redefining existing Phase-II principles
- Modified principles:
  - Principle II: Expanded to include AI agent workflow and MCP tool usage
  - Principle VI: Added OpenAI Agents SDK and Official MCP SDK to technology stack
- Added sections:
  - Principle VIII: Agent-First Architecture (NEW)
  - Principle IX: MCP Tool Design Standards (NEW)
  - Principle X: Stateless Conversation Management (NEW)
  - Principle XI: AI Action Traceability (NEW)
- Removed sections: None
- Templates requiring updates:
  ✅ spec-template.md - Reviewed, aligns with new AI chatbot user stories
  ✅ plan-template.md - Reviewed, Constitution Check will include AI architecture gates
  ✅ tasks-template.md - Reviewed, aligns with MCP tool implementation tasks
- Follow-up TODOs: None
- Date: 2026-01-23
-->

# Todo Full-Stack Web Application Constitution

## Core Principles

### I. Spec-Driven Development (NON-NEGOTIABLE)

All implementation MUST strictly follow approved specifications. No code may be written without:
- An approved feature specification (spec.md)
- A detailed implementation plan (plan.md)
- A task breakdown (tasks.md)

**Rationale**: Ensures all development is intentional, traceable, and aligned with requirements. Prevents scope creep and undocumented changes.

### II. Agentic Workflow Compliance (NON-NEGOTIABLE)

Development MUST follow the strict workflow: **spec → plan → tasks → implement**

- No manual coding allowed; all code generated via Claude Code
- Each phase must be completed and approved before proceeding to the next
- Use specialized agents for their domains:
  - **Database Agent** for schema design and SQLModel models
  - **Auth Agent** for Better Auth integration and JWT handling
  - **Backend Agent** for FastAPI endpoints and business logic
  - **Frontend Agent** for Next.js pages and React components
  - **AI Agents** (OpenAI Agents SDK) for natural language task management via MCP tools

**Rationale**: Ensures consistent, high-quality output through specialized expertise. Makes the development process reviewable and reproducible for hackathon evaluation.

### III. Security-First Design (NON-NEGOTIABLE)

Security is enforced by default at every layer:

- **Authentication**: Better Auth with JWT tokens for all user sessions
- **Authorization**: All API endpoints (except signup/signin) MUST validate JWT tokens
- **User Isolation**: Every database query MUST be user-scoped; users can only access their own data
- **Task Ownership**: Backend MUST enforce task ownership on every CRUD operation
- **Conversation Isolation**: AI conversations MUST be user-scoped; users can only access their own chat history
- **Secrets Management**: No hardcoded secrets; environment variables only (.env files)
- **Password Security**: Passwords MUST be hashed using bcrypt or equivalent
- **Stateless Auth**: JWT tokens are self-contained; no server-side session storage

**Rationale**: Multi-user applications require strict isolation to prevent data leaks and unauthorized access. Security violations are unacceptable and will fail hackathon evaluation.

### IV. Deterministic Behavior

APIs and UI MUST behave consistently across users, sessions, and environments:

- REST APIs follow HTTP semantics and standard status codes (200, 201, 400, 401, 404, 500)
- Errors are explicit, predictable, and documented
- Same input produces same output regardless of user or session
- No race conditions or non-deterministic state changes
- Request/response validation with Pydantic models
- AI agent responses are deterministic given the same conversation context and tools

**Rationale**: Predictable behavior is essential for debugging, testing, and user trust. Non-deterministic systems are impossible to reason about and maintain.

### V. Full-Stack Coherence

Frontend, backend, database, and AI agents MUST integrate seamlessly without mismatches:

- API contracts defined explicitly in specs before implementation
- Frontend consumes APIs exactly as specified (no assumptions)
- Database schema matches backend models (SQLModel ensures this)
- MCP tool schemas match database operations exactly
- Data types consistent across all layers (UI → API → Agent → MCP Tools → Database)
- Error handling coordinated between frontend, backend, and AI agents

**Rationale**: Mismatches between layers cause integration failures, data corruption, and poor user experience. Coherence must be designed upfront, not fixed later.

### VI. Technology Stack Adherence (NON-NEGOTIABLE)

The technology stack is fixed and non-negotiable:

- **Frontend**: Next.js 16+ (App Router only)
- **Backend**: Python FastAPI
- **ORM**: SQLModel
- **Database**: Neon Serverless PostgreSQL
- **Authentication**: Better Auth (JWT-based)
- **AI Agents**: OpenAI Agents SDK (for natural language task management)
- **Tool Protocol**: Official MCP SDK (Model Context Protocol)
- **Development**: Claude Code + Spec-Kit Plus

No substitutions, alternatives, or additional frameworks allowed without explicit approval.

**Rationale**: Stack consistency ensures all team members work with the same tools and patterns. Deviations create integration problems and evaluation difficulties.

### VII. Multi-User Data Isolation

Every user has completely isolated data:

- All database tables with user data MUST include a `user_id` foreign key
- All queries MUST filter by `user_id` extracted from JWT token
- Backend MUST verify JWT token user_id matches URL/request user_id
- AI conversations and messages MUST be scoped to the authenticated user
- Unauthorized access attempts MUST return 401 status consistently
- No shared data between users unless explicitly designed (e.g., public resources)

**Rationale**: Data leaks between users are critical security failures. Isolation must be enforced at the database and API level, not just the UI.

### VIII. Agent-First Architecture (NON-NEGOTIABLE - Phase III)

AI agents are the primary interface for task management via natural language:

- **Clear Separation**: UI → Agent → MCP Tools → Database (no layer skipping)
- **Agent Responsibility**: OpenAI Agents SDK handles natural language understanding and tool orchestration
- **Tool Execution**: All task actions (create, read, update, delete) MUST be executed via MCP tools
- **No Direct Database Access**: AI agents MUST NOT access the database directly; only through MCP tools
- **Stateless Design**: Agents do not maintain state between requests; context rebuilt from database each time
- **Tool-Only Actions**: Agents cannot perform task operations through any mechanism other than MCP tools

**Rationale**: Agent-first design ensures all AI actions are traceable, auditable, and follow the same security rules as direct API calls. Direct database access by agents would bypass security checks and create audit gaps.

### IX. MCP Tool Design Standards (NON-NEGOTIABLE - Phase III)

MCP tools are the bridge between AI agents and the database:

- **Stateless**: Tools MUST NOT maintain state between invocations
- **Schema-Defined**: Every tool MUST have an explicit JSON schema defining inputs and outputs
- **Single Responsibility**: Each tool performs one atomic operation (e.g., create_task, list_tasks, update_task)
- **User-Scoped**: Tools MUST enforce user isolation by accepting user_id and filtering all queries
- **Idempotent**: Where possible, tools should be idempotent (same input produces same result)
- **Error Handling**: Tools MUST return structured errors that agents can interpret and communicate to users
- **Validation**: Tools MUST validate all inputs before database operations

**Rationale**: Well-designed MCP tools ensure AI agents can reliably perform operations while maintaining security, traceability, and data integrity.

### X. Stateless Conversation Management (NON-NEGOTIABLE - Phase III)

Conversations are persisted and reconstructed on every request:

- **Persistence**: All conversations and messages MUST be stored in Neon PostgreSQL
- **Stateless Backend**: FastAPI chat endpoint MUST NOT maintain conversation state in memory
- **Context Reconstruction**: On each request, conversation history is loaded from database and passed to agent
- **Resume Capability**: Users MUST be able to resume conversations after server restart or session timeout
- **Message Ordering**: Messages MUST be stored with timestamps and sequence numbers for correct ordering
- **User Isolation**: Conversations MUST be scoped to authenticated users (user_id foreign key)

**Rationale**: Stateless design ensures scalability, reliability, and the ability to resume conversations across sessions. Persisting conversations enables audit trails and debugging.

### XI. AI Action Traceability (NON-NEGOTIABLE - Phase III)

Every AI action MUST be traceable and auditable:

- **Tool Invocation Logging**: Every MCP tool call MUST be logged with user_id, tool name, inputs, outputs, and timestamp
- **Conversation History**: All user messages and agent responses MUST be persisted in the database
- **Error Tracking**: Failed tool invocations MUST be logged with error details
- **Audit Trail**: System MUST support reconstructing what actions an agent took and why
- **Debugging Support**: Logs MUST contain enough information to debug agent behavior and tool failures

**Rationale**: AI systems can behave unpredictably; traceability ensures accountability, enables debugging, and builds user trust. Without audit trails, diagnosing issues is impossible.

## Development Workflow

### Workflow Stages

1. **Specification**: Define requirements, user stories, acceptance criteria
2. **Planning**: Design architecture, API contracts, data models, MCP tool schemas
3. **Task Breakdown**: Create ordered, testable tasks with dependencies
4. **Implementation**: Execute tasks via Claude Code and specialized agents
5. **Validation**: Verify each user story works independently

### Agent Usage

- **Database Agent**: Schema design, SQLModel models, migrations, query optimization
- **Auth Agent**: Better Auth setup, JWT generation/validation, authentication middleware
- **Backend Agent**: FastAPI routes, business logic, error handling, CORS, MCP tool implementation
- **Frontend Agent**: Next.js pages, React components, state management, API integration, chat UI
- **OpenAI Agents**: Natural language understanding, tool orchestration, conversation management

Agents MUST be used for their specialized domains. Do not implement features manually.

### Quality Gates

Before proceeding to the next stage:
- All placeholders in specs/plans/tasks must be filled
- All "NEEDS CLARIFICATION" items must be resolved
- Constitution compliance must be verified
- MCP tool schemas must be validated
- User approval must be obtained

## Quality Standards

### API Design

- RESTful endpoints following HTTP semantics
- Proper status codes: 200 (OK), 201 (Created), 400 (Bad Request), 401 (Unauthorized), 404 (Not Found), 500 (Internal Server Error)
- JWT required in `Authorization: Bearer <token>` header for all protected endpoints
- Request/response validation with Pydantic models
- Explicit error messages with consistent structure
- Chat endpoint MUST be stateless and reconstruct context from database

### MCP Tool Design

- JSON schema for every tool defining inputs, outputs, and errors
- Tools MUST be stateless and idempotent where possible
- Tools MUST enforce user isolation via user_id parameter
- Tools MUST validate inputs before database operations
- Tools MUST return structured errors for agent interpretation
- Tool names MUST be descriptive and follow naming conventions (e.g., create_task, list_tasks)

### Data Persistence

- All data stored in Neon Serverless PostgreSQL
- Database connection pooling configured
- Graceful error handling for database failures
- Transactions used for multi-step operations
- No data loss on server restart
- Conversations and messages persisted with proper indexing for fast retrieval

### Testing Requirements

- Each user story must be independently testable
- Test that unauthorized requests return 401
- Test that users cannot access other users' data or conversations
- Test all CRUD operations for task ownership enforcement
- Test JWT token validation and expiration
- Test MCP tools in isolation with mock data
- Test agent behavior with various natural language inputs
- Test conversation resume after simulated restart

## Constraints

### Non-Negotiable Constraints

- No manual coding; all code generated via Claude Code
- Technology stack cannot be changed
- All endpoints require valid JWT after authentication
- Stateless backend authentication (JWT only, no sessions)
- Stateless conversation management (no in-memory state)
- Multi-user support is mandatory
- Data persistence required across sessions
- AI agents MUST use MCP tools exclusively for task operations
- MCP tools MUST be stateless and schema-defined

### Prohibited Practices

- Hardcoding secrets or tokens in code
- Implementing features without approved specs
- Skipping workflow stages (spec → plan → tasks → implement)
- Using different technologies than specified
- Allowing users to access other users' data or conversations
- Manual coding or editing generated code
- AI agents accessing database directly (bypassing MCP tools)
- Maintaining conversation state in memory (must persist to database)
- MCP tools with stateful behavior or side effects beyond database operations

## Governance

### Constitution Authority

This constitution supersedes all other practices and guidelines. In case of conflict, constitution principles take precedence.

### Amendment Process

1. Propose amendment with rationale and impact analysis
2. Document affected templates and code
3. Obtain user approval
4. Update constitution with version bump (semantic versioning)
5. Propagate changes to dependent templates
6. Create ADR for significant changes

### Version Semantics

- **MAJOR**: Backward incompatible principle removals or redefinitions
- **MINOR**: New principles added or materially expanded guidance
- **PATCH**: Clarifications, wording fixes, non-semantic refinements

### Compliance Verification

- All specs must reference constitution principles
- All plans must include "Constitution Check" section
- All PRs must verify compliance with security and isolation requirements
- MCP tool implementations must be validated against design standards
- AI agent behavior must be auditable and traceable
- Complexity violations must be explicitly justified

### Success Criteria

The project succeeds when:
- All specs (Backend, Auth, Frontend, AI Chatbot) are fully implemented and integrated
- Users can sign up, sign in, and manage only their own tasks
- Users can manage tasks via natural language through AI chatbot
- AI agent correctly invokes MCP tools for all task operations
- Conversations persist and resume correctly after restart
- Unauthorized requests return 401 consistently
- Task ownership is enforced on every CRUD operation (direct API and MCP tools)
- All AI actions are traceable and auditable
- Application works end-to-end as a full-stack system with AI capabilities
- Specs, plans, and iterations are reviewable and traceable
- Project passes hackathon evaluation based on process and correctness

**Version**: 1.1.0 | **Ratified**: 2026-01-12 | **Last Amended**: 2026-01-23
