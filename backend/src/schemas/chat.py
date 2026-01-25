"""Chat API request/response schemas."""
from typing import List, Optional
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Request schema for chat endpoint."""

    conversation_id: Optional[int] = Field(
        default=None,
        description="ID of existing conversation, or null to start a new one"
    )
    message: str = Field(
        min_length=1,
        max_length=10000,
        description="User's message to the agent"
    )


class ToolInvocation(BaseModel):
    """Schema for tool invocation details."""

    tool: str = Field(description="Name of the MCP tool invoked")
    inputs: dict = Field(description="Input parameters passed to the tool")
    outputs: Optional[dict] = Field(
        default=None,
        description="Output returned by the tool (null if failed)"
    )
    error: Optional[str] = Field(
        default=None,
        description="Error message if tool invocation failed"
    )


class ChatResponse(BaseModel):
    """Response schema for chat endpoint."""

    conversation_id: int = Field(
        description="ID of the conversation (new or existing)"
    )
    message_id: int = Field(
        description="ID of the assistant's response message"
    )
    response: str = Field(
        description="Agent's text response to the user"
    )
    tool_invocations: List[ToolInvocation] = Field(
        default_factory=list,
        description="List of tools invoked by the agent (if any)"
    )
