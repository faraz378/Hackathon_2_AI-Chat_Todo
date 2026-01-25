"""Message database model."""
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .conversation import Conversation


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
    conversation: "Conversation" = Relationship(back_populates="messages")
