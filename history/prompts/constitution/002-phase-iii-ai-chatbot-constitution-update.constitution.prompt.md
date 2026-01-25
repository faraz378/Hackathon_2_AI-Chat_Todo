---
id: 002
title: Phase-III AI Chatbot Constitution Update
stage: constitution
date: 2026-01-23
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: main
user: user
command: /sp.constitution
labels: ["constitution", "phase-iii", "ai-chatbot", "mcp-tools", "openai-agents"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
  - N/A (constitution document)
---

## Prompt

```text
 (Phase-III Update)

Project Extension: AI-Powered Todo Chatbot

Core additions:
- Agent-first design using OpenAI Agents SDK
- Stateless chat and tool execution
- All task actions executed only via MCP tools
- Clear separation: UI → Agent → MCP Tools → Database

Key standards:
- Agents must not access the database directly
- MCP tools must be stateless and schema-defined
- Conversation context rebuilt from database each request
- All AI actions traceable and persisted
- Phase-II auth and user isolation rules remain enforced

Constraints:
- Use OpenAI Agents SDK and Official MCP SDK
- Stateless FastAPI chat endpoint
- Persist conversations and messages in Neon PostgreSQL
- No manual coding; Claude Code only

Success criteria:
- Users manage todos via natural language
- Agent correctly invokes MCP tools
- Conversation resumes after restart
- System remains secure and stateless
```

## Response snapshot

Updated constitution from v1.0.0 to v1.1.0 with Phase-III AI-Powered Todo Chatbot requirements.

**Added 4 new principles:**
- Principle VIII: Agent-First Architecture - Enforces UI → Agent → MCP Tools → Database separation
- Principle IX: MCP Tool Design Standards - Defines stateless, schema-driven tool requirements
- Principle X: Stateless Conversation Management - Requires database persistence and context reconstruction
- Principle XI: AI Action Traceability - Mandates logging and audit trails for all AI actions

**Modified existing principles:**
- Principle II: Expanded to include OpenAI Agents SDK in agentic workflow
- Principle III: Added conversation isolation to security requirements
- Principle VI: Added OpenAI Agents SDK and Official MCP SDK to technology stack
- Principle VII: Extended user isolation to include AI conversations

**Key architectural decisions:**
1. AI agents MUST use MCP tools exclusively (no direct database access)
2. All conversations persisted in Neon PostgreSQL for stateless operation
3. Context rebuilt from database on every request
4. All tool invocations logged for traceability and debugging
5. User isolation enforced at conversation and message level

**Quality standards added:**
- MCP Tool Design section with schema, validation, and error handling requirements
- Chat endpoint must be stateless and reconstruct context from database
- Testing requirements for MCP tools, agent behavior, and conversation resume

**Success criteria updated:**
- Users can manage tasks via natural language through AI chatbot
- AI agent correctly invokes MCP tools for all task operations
- Conversations persist and resume correctly after restart
- All AI actions are traceable and auditable

## Outcome

- ✅ Impact: Constitution successfully updated to v1.1.0 with comprehensive Phase-III AI chatbot requirements
- 🧪 Tests: N/A (constitution is a governance document)
- 📁 Files: Updated .specify/memory/constitution.md with 4 new principles and expanded existing principles
- 🔁 Next prompts: Create feature spec for AI chatbot using /sp.specify, then plan with /sp.plan
- 🧠 Reflection: MINOR version bump appropriate as new principles were added without removing or redefining existing Phase-II principles. All Phase-II security and isolation requirements remain enforced and are extended to AI conversations.

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A (constitution update)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Proceed to feature specification phase for AI chatbot implementation
