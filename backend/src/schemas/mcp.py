"""MCP tool input/output schemas."""
from typing import Optional
from pydantic import BaseModel, Field


class CreateTaskInput(BaseModel):
    """Input schema for create_task MCP tool."""

    title: str = Field(
        min_length=1,
        max_length=500,
        description="The task title (1-500 characters)"
    )
    description: Optional[str] = Field(
        default=None,
        max_length=5000,
        description="Optional detailed description of the task"
    )
    user_id: int = Field(
        description="The user ID (automatically provided by the system)"
    )


class ListTasksInput(BaseModel):
    """Input schema for list_tasks MCP tool."""

    user_id: int = Field(
        description="The user ID (automatically provided by the system)"
    )
    completed: Optional[bool] = Field(
        default=None,
        description="Filter by completion status. If null, return all tasks."
    )


class UpdateTaskInput(BaseModel):
    """Input schema for update_task MCP tool."""

    task_id: int = Field(
        description="The ID of the task to update"
    )
    user_id: int = Field(
        description="The user ID (automatically provided by the system)"
    )
    title: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=500,
        description="New task title (only if changing)"
    )
    description: Optional[str] = Field(
        default=None,
        max_length=5000,
        description="New task description (only if changing)"
    )
    completed: Optional[bool] = Field(
        default=None,
        description="New completion status (only if changing)"
    )


class DeleteTaskInput(BaseModel):
    """Input schema for delete_task MCP tool."""

    task_id: int = Field(
        description="The ID of the task to delete"
    )
    user_id: int = Field(
        description="The user ID (automatically provided by the system)"
    )
