"""Task database model."""
from datetime import datetime
from typing import Optional

from sqlmodel import Field, Relationship, SQLModel

from .user import User


class Task(SQLModel, table=True):
    """
    Task model with user ownership and CRUD operations.

    Constraints:
    - title: required, max 500 characters, non-empty
    - description: optional, max 5000 characters
    - completed: boolean flag, defaults to False
    - user_id: required foreign key to User
    """

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(
        max_length=500,
        min_length=1,
        nullable=False,
        description="Task title (1-500 characters)"
    )
    description: Optional[str] = Field(
        default=None,
        max_length=5000,
        description="Task description (max 5000 characters)"
    )
    completed: bool = Field(default=False, nullable=False)
    user_id: int = Field(foreign_key="user.id", nullable=False, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationships
    user: User = Relationship(back_populates="tasks")
