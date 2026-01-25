# Research: AI Chat Agent & Integration

**Feature**: 004-ai-chat-agent
**Date**: 2026-01-23
**Phase**: 0 (Research & Technology Decisions)

## Overview

This document captures research findings and technology decisions for implementing an AI-powered chat interface for task management. The research focuses on OpenAI Agents SDK integration, MCP tool protocol, stateless conversation management, and frontend chat UI patterns.

## 1. OpenAI Agents SDK Integration

### Research Question
How to integrate OpenAI Agents SDK with FastAPI for stateless, tool-enabled chat?

### Findings

**Installation**:
```bash
pip install openai
```

**Basic Integration Pattern**:
```python
from openai import AsyncOpenAI
import os

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def chat_with_agent(messages: list, tools: list):
    response = await client.chat.completions.create(
        model="gpt-4",
        messages=messages,
        tools=tools,
        temperature=0.7
    )
    return response
```

**Key Considerations**:
- Use async client for FastAPI compatibility
- Pass full conversation history as messages array
- Register tools with JSON schema format
- Handle tool calls in response and execute them
- Return tool results back to agent for final response

**Error Handling**:
- Rate limit errors: Implement exponential backoff
- Invalid tool calls: Validate before execution
- API timeouts: Set reasonable timeout (30s)
- Token limit exceeded: Truncate conversation history

**Best Practices**:
- Store API key in environment variable
- Use structured logging for all API calls
- Implement retry logic with exponential backoff
- Monitor token usage and costs
- Cache agent responses where appropriate

### Decision
**Chosen**: OpenAI Python SDK with async client
**Rationale**: Official SDK, excellent async support, robust tool calling, well-documented
**Implementation**: Create `services/agent.py` with AgentService class

---

## 2. MCP Tool Protocol Integration

### Research Question
How to implement MCP tools that the OpenAI agent can invoke for task operations?

### Findings

**MCP Tool Schema Format**:
```json
{
  "type": "function",
  "function": {
    "name": "create_task",
    "description": "Create a new task for the user",
    "parameters": {
      "type": "object",
      "properties": {
        "title": {
          "type": "string",
          "description": "The task title"
        },
        "description": {
          "type": "string",
          "description": "Optional task description"
        },
        "user_id": {
          "type": "integer",
          "description": "The user ID (automatically provided)"
        }
      },
      "required": ["title", "user_id"]
    }
  }
}
```

**Tool Implementation Pattern**:
```python
async def create_task_tool(title: str, description: str | None, user_id: int, db: AsyncSession):
    """MCP tool: Create a new task"""
    # Validate inputs
    if not title or len(title) > 500:
        return {"error": "Invalid title"}

    # Execute database operation
    task = Task(title=title, description=description, user_id=user_id)
    db.add(task)
    await db.commit()
    await db.refresh(task)

    # Return structured result
    return {
        "task_id": task.id,
        "title": task.title,
        "completed": task.completed
    }
```

**Tool Invocation Flow**:
1. Agent receives user message
2. Agent decides to call a tool
3. Backend extracts tool name and arguments
4. Backend executes tool with user_id from JWT
5. Backend returns tool result to agent
6. Agent generates final response with tool result

**Key Considerations**:
- Tools must be stateless (no shared state)
- Always include user_id for isolation
- Validate all inputs before database operations
- Return structured data (JSON serializable)
- Handle errors gracefully with error objects

### Decision
**Chosen**: OpenAI function calling format (compatible with MCP)
**Rationale**: Native OpenAI support, JSON schema validation, structured responses
**Implementation**: Create `services/mcp_tools.py` with 4 tool functions

---

## 3. Stateless Conversation Management

### Research Question
How to manage conversation state in a stateless FastAPI application with database persistence?

### Findings

**Database Schema**:
```sql
CREATE TABLE conversations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);

CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER NOT NULL REFERENCES conversations(id),
    role VARCHAR(20) NOT NULL,  -- 'user' or 'assistant'
    content TEXT NOT NULL,
    sequence_number INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL,
    tool_invocations JSONB  -- Optional: store tool calls
);

CREATE INDEX idx_messages_conversation ON messages(conversation_id, sequence_number);
CREATE INDEX idx_conversations_user ON conversations(user_id);
```

**Context Reconstruction Pattern**:
```python
async def load_conversation_context(conversation_id: int, user_id: int, db: AsyncSession):
    """Load conversation history from database"""
    # Verify conversation belongs to user
    conversation = await db.get(Conversation, conversation_id)
    if not conversation or conversation.user_id != user_id:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Load messages ordered by sequence
    result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.sequence_number)
    )
    messages = result.scalars().all()

    # Convert to OpenAI format
    return [
        {"role": msg.role, "content": msg.content}
        for msg in messages
    ]
```

**Pagination Strategy**:
- Load most recent N messages (e.g., 50) for context
- Implement "load more" for older messages
- Summarize very old messages if context window exceeded

**Performance Optimization**:
- Add database indexes on conversation_id and sequence_number
- Use connection pooling (already configured)
- Cache recent conversations in Redis (optional, future enhancement)

### Decision
**Chosen**: Full conversation history in PostgreSQL with indexed queries
**Rationale**: Meets stateless requirement, enables resume, supports audit trail, good performance with indexes
**Implementation**: Create `services/conversation.py` with ConversationService class

---

## 4. Chatkit Frontend Integration

### Research Question
How to build a chat UI in Next.js that integrates with the chat API?

### Findings

**Chat UI Library Options**:
1. **react-chat-elements**: Lightweight, customizable, good TypeScript support
2. **stream-chat-react**: Full-featured but heavy, overkill for our needs
3. **Custom components**: More control but more work

**Recommended Approach**: Use react-chat-elements or build custom components with Tailwind CSS

**Component Structure**:
```tsx
// ChatInterface.tsx - Main container
<div className="chat-container">
  <MessageList messages={messages} />
  <MessageInput onSend={handleSend} />
</div>

// MessageList.tsx - Scrollable message display
{messages.map(msg => (
  <MessageBubble
    key={msg.id}
    role={msg.role}
    content={msg.content}
    timestamp={msg.created_at}
  />
))}

// MessageInput.tsx - Input field with send button
<form onSubmit={handleSubmit}>
  <textarea value={input} onChange={handleChange} />
  <button type="submit">Send</button>
</form>
```

**API Integration Pattern**:
```typescript
async function sendMessage(conversationId: number | null, message: string) {
  const token = localStorage.getItem('token');

  const response = await fetch('http://localhost:8001/chat', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({
      conversation_id: conversationId,
      message: message
    })
  });

  if (!response.ok) {
    throw new Error('Failed to send message');
  }

  return await response.json();
}
```

**State Management**:
- Use React useState for messages array
- Use useEffect to load conversation history on mount
- Optimistic updates: Add user message immediately, update with response
- Error handling: Show error message, allow retry

**Real-time Updates**:
- Not required for MVP (polling or manual refresh acceptable)
- Future enhancement: WebSocket or Server-Sent Events

### Decision
**Chosen**: Custom React components with Tailwind CSS
**Rationale**: Full control, matches existing design system, no heavy dependencies
**Implementation**: Create `components/chat/` directory with ChatInterface, MessageList, MessageInput, MessageBubble

---

## 5. Agent Prompt Engineering

### Research Question
What system prompt will guide the agent to correctly interpret user intent and use tools?

### Findings

**Effective Prompt Structure**:
1. Role definition: "You are a helpful task management assistant"
2. Capabilities: List available tools and their purposes
3. Guidelines: How to behave (concise, friendly, ask clarifying questions)
4. Examples: Few-shot examples of good interactions (optional)

**Recommended System Prompt**:
```
You are a helpful task management assistant. Users can ask you to create, view, update, or delete their tasks using natural language.

Available tools:
- create_task(title, description): Create a new task with a title and optional description
- list_tasks(): Show all tasks for the user
- update_task(task_id, title, description, completed): Update a task's properties
- delete_task(task_id): Remove a task

Guidelines:
- Be concise and friendly in your responses
- Always confirm actions after executing them (e.g., "I've created a task 'buy groceries' for you")
- If the user's intent is unclear, ask clarifying questions
- If a task reference is ambiguous (e.g., "complete the task" when multiple tasks exist), ask which task they mean
- Always use tools to perform task operations - never make up data or pretend to complete actions
- If a tool call fails, explain the error to the user in simple terms

Examples:
User: "Create a task to buy groceries"
Assistant: [calls create_task] "I've created a task 'buy groceries' for you."

User: "Show my tasks"
Assistant: [calls list_tasks] "You have 3 tasks: 1. Buy groceries, 2. Call dentist, 3. Finish report"

User: "Mark the groceries task as done"
Assistant: [calls update_task] "I've marked 'buy groceries' as completed. Great job!"
```

**Prompt Iteration Strategy**:
- Start with basic prompt
- Test with various user inputs
- Refine based on agent behavior
- Add examples for common failure cases

### Decision
**Chosen**: Structured system prompt with role, tools, guidelines, and examples
**Rationale**: Clear instructions lead to consistent behavior, examples improve accuracy
**Implementation**: Store prompt in `services/agent.py` as constant, make it configurable

---

## 6. Error Handling Strategy

### Research Question
How to handle errors gracefully across the entire chat flow?

### Findings

**Error Categories**:
1. **User Input Errors**: Invalid message, empty input
2. **Authentication Errors**: Invalid/expired JWT token
3. **Agent Errors**: OpenAI API failure, rate limit, timeout
4. **Tool Errors**: Database error, validation error, not found
5. **System Errors**: Unexpected exceptions

**Error Response Format**:
```json
{
  "error": {
    "code": "TOOL_EXECUTION_FAILED",
    "message": "Failed to create task: Title is required",
    "details": {
      "tool": "create_task",
      "reason": "validation_error"
    }
  }
}
```

**Frontend Error Handling**:
- Display error message in chat as system message
- Allow user to retry failed action
- Log errors for debugging
- Graceful degradation (show error, don't crash)

**Backend Error Handling**:
- Catch all exceptions in chat endpoint
- Log errors with context (user_id, conversation_id, message)
- Return structured error responses
- Don't expose internal details to user

### Decision
**Chosen**: Structured error responses with error codes and user-friendly messages
**Rationale**: Consistent error handling, good UX, debuggable
**Implementation**: Create error schemas in `schemas/chat.py`, handle in chat endpoint

---

## 7. Security Considerations

### Research Question
What security measures are needed for the chat system?

### Findings

**Authentication**:
- Reuse existing JWT authentication
- Verify token on every chat request
- Extract user_id from token for all operations

**Authorization**:
- Verify conversation belongs to authenticated user
- Pass user_id to all MCP tools for scoping
- Never allow cross-user data access

**Input Validation**:
- Validate message length (max 10,000 characters)
- Sanitize user input before storing
- Validate tool arguments before execution

**Rate Limiting**:
- Limit chat requests per user (e.g., 60 per minute)
- Prevent abuse of OpenAI API
- Return 429 status code when limit exceeded

**Data Privacy**:
- Don't log sensitive user data
- Encrypt data at rest (database level)
- Don't send user data to OpenAI beyond necessary context

### Decision
**Chosen**: JWT authentication, user_id scoping, input validation, rate limiting
**Rationale**: Comprehensive security without over-engineering
**Implementation**: Reuse existing auth middleware, add rate limiting middleware

---

## Summary of Decisions

| Area | Decision | Rationale |
|------|----------|-----------|
| AI Agent | OpenAI Python SDK (async) | Official, robust, async-compatible |
| Tool Protocol | OpenAI function calling | Native support, JSON schema validation |
| Conversation Storage | PostgreSQL with indexes | Stateless, persistent, performant |
| Frontend UI | Custom React + Tailwind | Full control, matches design system |
| Agent Prompt | Structured with examples | Clear instructions, consistent behavior |
| Error Handling | Structured error responses | Good UX, debuggable |
| Security | JWT + user_id scoping | Comprehensive, reuses existing auth |

## Next Steps

1. Implement database models (Conversation, Message, ToolInvocationLog)
2. Implement MCP tools with schemas
3. Implement agent service with OpenAI integration
4. Implement chat API endpoint
5. Implement frontend chat components
6. Write tests for all components
7. Document setup and usage

---

**Research Status**: ✅ Complete - All technology decisions made and documented
