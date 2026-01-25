# Data Model: AI Chat Agent & Integration

**Feature**: 004-ai-chat-agent
**Date**: 2026-01-23
**Phase**: 1 (Design & Contracts)

## Overview

This document defines the database schema for the AI chat agent feature, including new entities for conversations, messages, and tool invocation logs. All entities follow the existing SQLModel patterns and maintain user isolation through foreign key relationships.

## Entity Definitions

### 1. Conversation

Represents a chat session between a user and the AI agent.

**Purpose**: Group related messages together and track conversation metadata.

**SQLModel Definition**:
```python
from datetime import datetime
from typing import Optional, List
from sqlmodel import Field, Relationship, SQLModel

class Conversation(SQLModel, table=True):
    """
    Conversation model for chat sessions.

    Each conversation belongs to a single user and contains multiple messages.
    Conversations persist across sessions to enable resume functionality.
    """

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(
        foreign_key="user.id",
        nullable=False,
        index=True,
        description="Owner of this conversation"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="When the conversation was started"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Last message timestamp"
    )

    # Relationships
    user: "User" = Relationship(back_populates="conversations")
    messages: List["Message"] = Relationship(
        back_populates="conversation",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
```

**Attributes**:
- `id` (int, PK): Auto-incrementing primary key
- `user_id` (int, FK, indexed): References user.id, enforces ownership
- `created_at` (datetime): Timestamp when conversation started
- `updated_at` (datetime): Timestamp of last message (updated on each message)

**Relationships**:
- `user`: Many-to-one with User (one user has many conversations)
- `messages`: One-to-many with Message (one conversation has many messages)

**Indexes**:
- Primary key on `id`
- Index on `user_id` for fast user-scoped queries

**Constraints**:
- `user_id` must reference valid user (foreign key constraint)
- `created_at` and `updated_at` cannot be null

**Validation Rules**:
- User must exist before creating conversation
- `updated_at` must be >= `created_at`

---

### 2. Message

Represents a single message in a conversation (from user or assistant).

**Purpose**: Store conversation history with proper ordering and metadata.

**SQLModel Definition**:
```python
class Message(SQLModel, table=True):
    """
    Message model for chat messages.

    Messages belong to a conversation and are ordered by sequence_number.
    Role indicates whether the message is from the user or the assistant.
    """

    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: int = Field(
        foreign_key="conversation.id",
        nullable=False,
        index=True,
        description="Parent conversation"
    )
    role: str = Field(
        max_length=20,
        nullable=False,
        description="Message sender: 'user' or 'assistant'"
    )
    content: str = Field(
        nullable=False,
        description="Message text content"
    )
    sequence_number: int = Field(
        nullable=False,
        description="Order of message in conversation (0-indexed)"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="When the message was created"
    )
    tool_invocations: Optional[str] = Field(
        default=None,
        description="JSON string of tool calls (if assistant message)"
    )

    # Relationships
    conversation: Conversation = Relationship(back_populates="messages")
```

**Attributes**:
- `id` (int, PK): Auto-incrementing primary key
- `conversation_id` (int, FK, indexed): References conversation.id
- `role` (str, max 20 chars): Either "user" or "assistant"
- `content` (str): The message text (no length limit for flexibility)
- `sequence_number` (int): Order within conversation (0, 1, 2, ...)
- `created_at` (datetime): Timestamp when message was created
- `tool_invocations` (str, optional): JSON string of tool calls made by assistant

**Relationships**:
- `conversation`: Many-to-one with Conversation

**Indexes**:
- Primary key on `id`
- Index on `conversation_id` for fast conversation queries
- Composite index on `(conversation_id, sequence_number)` for ordered retrieval

**Constraints**:
- `conversation_id` must reference valid conversation (foreign key constraint)
- `role` must be either "user" or "assistant"
- `content` cannot be empty
- `sequence_number` must be unique within a conversation

**Validation Rules**:
- Role must be "user" or "assistant" (enum validation)
- Content must not be empty string
- Sequence number must be >= 0
- Sequence numbers must be consecutive within a conversation (0, 1, 2, ...)
- Tool invocations must be valid JSON if provided

---

### 3. ToolInvocationLog

Represents an audit log entry for MCP tool invocations.

**Purpose**: Track all tool calls for debugging, auditing, and analytics.

**SQLModel Definition**:
```python
class ToolInvocationLog(SQLModel, table=True):
    """
    Tool invocation log for audit trail.

    Records every MCP tool call with inputs, outputs, and success status.
    Enables debugging and ensures all AI actions are traceable.
    """

    __tablename__ = "tool_invocation_logs"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(
        foreign_key="user.id",
        nullable=False,
        index=True,
        description="User who triggered the tool call"
    )
    message_id: Optional[int] = Field(
        foreign_key="message.id",
        nullable=True,
        description="Message that triggered this tool call"
    )
    tool_name: str = Field(
        max_length=100,
        nullable=False,
        description="Name of the tool invoked"
    )
    inputs: str = Field(
        nullable=False,
        description="JSON string of tool input parameters"
    )
    outputs: Optional[str] = Field(
        default=None,
        description="JSON string of tool output (null if failed)"
    )
    success: bool = Field(
        nullable=False,
        description="Whether the tool call succeeded"
    )
    error_message: Optional[str] = Field(
        default=None,
        max_length=1000,
        description="Error message if tool call failed"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="When the tool was invoked"
    )

    # Relationships
    user: "User" = Relationship()
```

**Attributes**:
- `id` (int, PK): Auto-incrementing primary key
- `user_id` (int, FK, indexed): References user.id, tracks who triggered the call
- `message_id` (int, FK, optional): References message.id, links to conversation
- `tool_name` (str, max 100 chars): Name of the MCP tool (e.g., "create_task")
- `inputs` (str): JSON string of input parameters
- `outputs` (str, optional): JSON string of output data (null if failed)
- `success` (bool): True if tool executed successfully, False if error
- `error_message` (str, optional, max 1000 chars): Error description if failed
- `created_at` (datetime): Timestamp of tool invocation

**Relationships**:
- `user`: Many-to-one with User

**Indexes**:
- Primary key on `id`
- Index on `user_id` for user-scoped queries
- Index on `created_at` for time-based queries
- Index on `tool_name` for analytics

**Constraints**:
- `user_id` must reference valid user (foreign key constraint)
- `tool_name` cannot be empty
- `inputs` must be valid JSON
- If `success` is True, `outputs` should be provided
- If `success` is False, `error_message` should be provided

**Validation Rules**:
- Tool name must match one of the registered MCP tools
- Inputs must be valid JSON string
- Outputs must be valid JSON string if provided
- Error message required when success is False

---

## Relationships Diagram

```
User (existing)
  |
  +-- 1:N --> Conversation
  |             |
  |             +-- 1:N --> Message
  |
  +-- 1:N --> ToolInvocationLog
                  |
                  +-- N:1 --> Message (optional)
```

**Relationship Details**:
1. **User → Conversations**: One user can have many conversations
2. **Conversation → Messages**: One conversation contains many messages
3. **User → ToolInvocationLogs**: One user can trigger many tool invocations
4. **Message → ToolInvocationLog**: One message can trigger multiple tool calls (optional link)

---

## Database Migrations

### Migration Script

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

### Rollback Script

```sql
DROP TABLE IF EXISTS tool_invocation_logs CASCADE;
DROP TABLE IF EXISTS message CASCADE;
DROP TABLE IF EXISTS conversation CASCADE;
```

---

## Data Access Patterns

### 1. Create New Conversation

```python
async def create_conversation(user_id: int, db: AsyncSession) -> Conversation:
    """Create a new conversation for a user."""
    conversation = Conversation(user_id=user_id)
    db.add(conversation)
    await db.commit()
    await db.refresh(conversation)
    return conversation
```

### 2. Load Conversation History

```python
async def load_conversation_messages(
    conversation_id: int,
    user_id: int,
    db: AsyncSession,
    limit: int = 50
) -> List[Message]:
    """Load recent messages from a conversation."""
    # Verify ownership
    conversation = await db.get(Conversation, conversation_id)
    if not conversation or conversation.user_id != user_id:
        raise ValueError("Conversation not found")

    # Load messages ordered by sequence
    result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.sequence_number.desc())
        .limit(limit)
    )
    messages = result.scalars().all()
    return list(reversed(messages))  # Return in chronological order
```

### 3. Add Message to Conversation

```python
async def add_message(
    conversation_id: int,
    role: str,
    content: str,
    db: AsyncSession,
    tool_invocations: Optional[str] = None
) -> Message:
    """Add a new message to a conversation."""
    # Get next sequence number
    result = await db.execute(
        select(func.max(Message.sequence_number))
        .where(Message.conversation_id == conversation_id)
    )
    max_seq = result.scalar() or -1
    next_seq = max_seq + 1

    # Create message
    message = Message(
        conversation_id=conversation_id,
        role=role,
        content=content,
        sequence_number=next_seq,
        tool_invocations=tool_invocations
    )
    db.add(message)

    # Update conversation timestamp
    conversation = await db.get(Conversation, conversation_id)
    conversation.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(message)
    return message
```

### 4. Log Tool Invocation

```python
async def log_tool_invocation(
    user_id: int,
    tool_name: str,
    inputs: dict,
    outputs: Optional[dict],
    success: bool,
    error_message: Optional[str],
    db: AsyncSession,
    message_id: Optional[int] = None
) -> ToolInvocationLog:
    """Log an MCP tool invocation."""
    log = ToolInvocationLog(
        user_id=user_id,
        message_id=message_id,
        tool_name=tool_name,
        inputs=json.dumps(inputs),
        outputs=json.dumps(outputs) if outputs else None,
        success=success,
        error_message=error_message
    )
    db.add(log)
    await db.commit()
    await db.refresh(log)
    return log
```

---

## Performance Considerations

### Indexes
- **conversation.user_id**: Fast user-scoped conversation queries
- **message.conversation_id**: Fast message retrieval for a conversation
- **message.(conversation_id, sequence_number)**: Ordered message retrieval
- **tool_invocation_logs.user_id**: User-scoped audit queries
- **tool_invocation_logs.created_at**: Time-based analytics
- **tool_invocation_logs.tool_name**: Tool usage analytics

### Query Optimization
- Use `LIMIT` when loading conversation history (pagination)
- Use `ORDER BY sequence_number` for chronological message order
- Batch insert messages when possible
- Use connection pooling (already configured)

### Storage Estimates
- Conversation: ~50 bytes per row
- Message: ~500 bytes per row (average)
- ToolInvocationLog: ~300 bytes per row
- For 1000 users with 10 conversations each and 100 messages per conversation:
  - Conversations: 10,000 rows × 50 bytes = 500 KB
  - Messages: 1,000,000 rows × 500 bytes = 500 MB
  - Tool logs: ~500,000 rows × 300 bytes = 150 MB
  - Total: ~650 MB (very manageable)

---

## Data Integrity Rules

### Cascade Deletes
- When a user is deleted → all conversations, messages, and tool logs are deleted
- When a conversation is deleted → all messages are deleted
- When a message is deleted → tool invocation log message_id is set to NULL

### Constraints
- Conversation must belong to a valid user
- Message must belong to a valid conversation
- Message role must be "user" or "assistant"
- Message content cannot be empty
- Sequence numbers must be unique within a conversation
- Tool invocation must belong to a valid user

### Validation
- Validate JSON format for tool_invocations, inputs, and outputs
- Validate role enum before insert
- Validate sequence number uniqueness before insert
- Validate user ownership before queries

---

**Data Model Status**: ✅ Complete - All entities defined with relationships, constraints, and access patterns
