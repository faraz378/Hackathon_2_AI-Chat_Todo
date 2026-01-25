"""Task request/response schemas."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class TaskCreate(BaseModel):
    """
    Schema for creating a new task.

    Validation:
    - title: required, 1-500 characters
    - description: optional, max 5000 characters
    """

    title: str = Field(
        min_length=1,
        max_length=500,
        description="Task title (1-500 characters)"
    )
    description: Optional[str] = Field(
        default=None,
        max_length=5000,
        description="Task description (max 5000 characters)"
    )

    @field_validator('title')
    @classmethod
    def title_not_empty(cls, v: str) -> str:
        """Ensure title is not empty or whitespace only."""
        if not v or not v.strip():
            raise ValueError('Title cannot be empty')
        return v.strip()

    @field_validator('description')
    @classmethod
    def description_length(cls, v: Optional[str]) -> Optional[str]:
        """Validate description length if provided."""
        if v is not None and len(v) > 5000:
            raise ValueError('Description cannot exceed 5000 characters')
        return v.strip() if v else None


class TaskUpdate(BaseModel):
    """
    Schema for updating an existing task.

    All fields are optional for partial updates.
    """

    title: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=500,
        description="Task title (1-500 characters)"
    )
    description: Optional[str] = Field(
        default=None,
        max_length=5000,
        description="Task description (max 5000 characters)"
    )
    completed: Optional[bool] = Field(
        default=None,
        description="Task completion status"
    )

    @field_validator('title')
    @classmethod
    def title_not_empty(cls, v: Optional[str]) -> Optional[str]:
        """Ensure title is not empty or whitespace only if provided."""
        if v is not None:
            if not v or not v.strip():
                raise ValueError('Title cannot be empty')
            return v.strip()
        return v


class TaskResponse(BaseModel):
    """
    Schema for task responses.

    Returns complete task information including metadata.
    """

    id: int
    title: str
    description: Optional[str]
    completed: bool
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic configuration."""
        from_attributes = True
