"""Tool invocation log database model."""
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .user import User


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
