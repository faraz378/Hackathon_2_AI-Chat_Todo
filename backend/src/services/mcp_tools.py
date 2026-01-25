"""MCP tool implementations for task management."""
import logging
from datetime import datetime
from typing import Dict, List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.task import Task

logger = logging.getLogger(__name__)


async def create_task(
    title: str,
    user_id: int,
    db: AsyncSession,
    description: Optional[str] = None
) -> Dict:
    """
    MCP tool: Create a new task for the user.

    Args:
        title: Task title (1-500 characters)
        user_id: User ID (from JWT token)
        db: Database session
        description: Optional task description

    Returns:
        Dict with task details (task_id, title, description, completed, created_at)

    Raises:
        ValueError: If validation fails
    """
    try:
        # Validate inputs
        if not title or len(title) > 500:
            raise ValueError("Title must be between 1 and 500 characters")

        if description and len(description) > 5000:
            raise ValueError("Description must be less than 5000 characters")

        # Create task
        task = Task(
            title=title,
            description=description,
            user_id=user_id,
            completed=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        db.add(task)
        await db.commit()
        await db.refresh(task)

        logger.info(f"Created task {task.id} for user {user_id}")

        return {
            "task_id": task.id,
            "title": task.title,
            "description": task.description,
            "completed": task.completed,
            "created_at": task.created_at.isoformat()
        }

    except ValueError as e:
        logger.error(f"Validation error in create_task: {str(e)}")
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating task for user {user_id}: {str(e)}")
        raise ValueError(f"Failed to create task: {str(e)}")


async def list_tasks(
    user_id: int,
    db: AsyncSession,
    completed: Optional[bool] = None
) -> Dict:
    """
    MCP tool: List all tasks for the user.

    Args:
        user_id: User ID (from JWT token)
        db: Database session
        completed: Optional filter by completion status

    Returns:
        Dict with tasks list and total count
    """
    try:
        # Build query with user_id filter
        query = select(Task).where(Task.user_id == user_id)

        # Add completion filter if specified
        if completed is not None:
            query = query.where(Task.completed == completed)

        # Execute query
        result = await db.execute(query)
        tasks = result.scalars().all()

        logger.info(f"Retrieved {len(tasks)} tasks for user {user_id}")

        # Format tasks
        task_list = [
            {
                "task_id": task.id,
                "title": task.title,
                "description": task.description,
                "completed": task.completed,
                "created_at": task.created_at.isoformat(),
                "updated_at": task.updated_at.isoformat()
            }
            for task in tasks
        ]

        return {
            "tasks": task_list,
            "total_count": len(task_list)
        }

    except Exception as e:
        logger.error(f"Error listing tasks for user {user_id}: {str(e)}")
        raise ValueError(f"Failed to list tasks: {str(e)}")


async def update_task(
    task_id: int,
    user_id: int,
    db: AsyncSession,
    title: Optional[str] = None,
    description: Optional[str] = None,
    completed: Optional[bool] = None
) -> Dict:
    """
    MCP tool: Update an existing task.

    Args:
        task_id: Task ID to update
        user_id: User ID (from JWT token)
        db: Database session
        title: New title (optional)
        description: New description (optional)
        completed: New completion status (optional)

    Returns:
        Dict with updated task details

    Raises:
        ValueError: If task not found or validation fails
    """
    try:
        # Find task with user_id verification
        result = await db.execute(
            select(Task).where(Task.id == task_id, Task.user_id == user_id)
        )
        task = result.scalar_one_or_none()

        if not task:
            raise ValueError(f"Task {task_id} not found or does not belong to user")

        # Validate and update fields
        if title is not None:
            if not title or len(title) > 500:
                raise ValueError("Title must be between 1 and 500 characters")
            task.title = title

        if description is not None:
            if len(description) > 5000:
                raise ValueError("Description must be less than 5000 characters")
            task.description = description

        if completed is not None:
            task.completed = completed

        # Update timestamp
        task.updated_at = datetime.utcnow()

        await db.commit()
        await db.refresh(task)

        logger.info(f"Updated task {task_id} for user {user_id}")

        return {
            "task_id": task.id,
            "title": task.title,
            "description": task.description,
            "completed": task.completed,
            "updated_at": task.updated_at.isoformat()
        }

    except ValueError as e:
        logger.error(f"Error updating task {task_id}: {str(e)}")
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating task {task_id} for user {user_id}: {str(e)}")
        raise ValueError(f"Failed to update task: {str(e)}")


async def delete_task(
    task_id: int,
    user_id: int,
    db: AsyncSession
) -> Dict:
    """
    MCP tool: Delete a task.

    Args:
        task_id: Task ID to delete
        user_id: User ID (from JWT token)
        db: Database session

    Returns:
        Dict with success status and deleted task ID

    Raises:
        ValueError: If task not found
    """
    try:
        # Find task with user_id verification
        result = await db.execute(
            select(Task).where(Task.id == task_id, Task.user_id == user_id)
        )
        task = result.scalar_one_or_none()

        if not task:
            raise ValueError(f"Task {task_id} not found or does not belong to user")

        # Delete task
        await db.delete(task)
        await db.commit()

        logger.info(f"Deleted task {task_id} for user {user_id}")

        return {
            "success": True,
            "message": "Task deleted successfully",
            "deleted_task_id": task_id
        }

    except ValueError as e:
        logger.error(f"Error deleting task {task_id}: {str(e)}")
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error deleting task {task_id} for user {user_id}: {str(e)}")
        raise ValueError(f"Failed to delete task: {str(e)}")
