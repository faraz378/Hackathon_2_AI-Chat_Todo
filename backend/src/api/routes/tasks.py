"""Task API routes."""
import logging
from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from ...models.task import Task
from ...schemas.error import ErrorDetail, ErrorResponse
from ...schemas.task import TaskCreate, TaskResponse, TaskUpdate
from ..deps import get_db_session, verify_user_access

# Configure logger
logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/users/{user_id}/tasks",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": ErrorResponse, "description": "Validation error"},
        500: {"model": ErrorResponse, "description": "Database error"},
    },
)
async def create_task(
    user_id: int,
    task_data: TaskCreate,
    db: AsyncSession = Depends(get_db_session),
    verified_user_id: int = Depends(verify_user_access),
) -> TaskResponse:
    """
    Create a new task for a specific user.

    Args:
        user_id: The ID of the user who owns the task
        task_data: Task creation data (title, description)
        db: Database session

    Returns:
        TaskResponse: The created task with all fields

    Raises:
        HTTPException 400: Validation error (title empty, too long, etc.)
        HTTPException 500: Database error
    """
    logger.info(f"Creating task for user_id={user_id}, title='{task_data.title}'")

    try:
        # Create new task with user_id scoping
        new_task = Task(
            title=task_data.title,
            description=task_data.description,
            user_id=user_id,
            completed=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        db.add(new_task)
        await db.commit()
        await db.refresh(new_task)

        logger.info(f"Task created successfully: task_id={new_task.id}, user_id={user_id}")
        return TaskResponse.model_validate(new_task)

    except IntegrityError as e:
        await db.rollback()
        logger.error(f"IntegrityError creating task for user_id={user_id}: {str(e)}")
        # Foreign key constraint violation (user doesn't exist)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": {
                    "code": "INVALID_USER",
                    "message": f"User with ID {user_id} does not exist"
                }
            }
        )
    except ValueError as e:
        # Validation error from Pydantic
        await db.rollback()
        logger.error(f"Validation error creating task for user_id={user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": str(e)
                }
            }
        )
    except Exception as e:
        # Unexpected database or server error
        await db.rollback()
        logger.error(f"Unexpected error creating task for user_id={user_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "An unexpected error occurred while creating the task"
                }
            }
        )


@router.get(
    "/users/{user_id}/tasks",
    response_model=List[TaskResponse],
    status_code=status.HTTP_200_OK,
)
async def get_tasks(
    user_id: int,
    db: AsyncSession = Depends(get_db_session),
    verified_user_id: int = Depends(verify_user_access),
) -> List[TaskResponse]:
    """
    Retrieve all tasks for a specific user.

    Args:
        user_id: The ID of the user
        db: Database session

    Returns:
        List[TaskResponse]: List of tasks (empty list if user has no tasks)
    """
    logger.info(f"Retrieving all tasks for user_id={user_id}")

    try:
        # Query tasks with user_id filtering
        result = await db.execute(
            select(Task).where(Task.user_id == user_id)
        )
        tasks = result.scalars().all()

        logger.info(f"Retrieved {len(tasks)} tasks for user_id={user_id}")
        return [TaskResponse.model_validate(task) for task in tasks]

    except Exception as e:
        logger.error(f"Error retrieving tasks for user_id={user_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "An unexpected error occurred while retrieving tasks"
                }
            }
        )


@router.get(
    "/users/{user_id}/tasks/{task_id}",
    response_model=TaskResponse,
    status_code=status.HTTP_200_OK,
    responses={
        404: {"model": ErrorResponse, "description": "Task not found"},
    },
)
async def get_task(
    user_id: int,
    task_id: int,
    db: AsyncSession = Depends(get_db_session),
    verified_user_id: int = Depends(verify_user_access),
) -> TaskResponse:
    """
    Retrieve a specific task by ID for a user.

    Args:
        user_id: The ID of the user
        task_id: The ID of the task
        db: Database session

    Returns:
        TaskResponse: The requested task

    Raises:
        HTTPException 404: Task not found or belongs to different user
    """
    logger.info(f"Retrieving task_id={task_id} for user_id={user_id}")

    try:
        # Query with user_id filtering for isolation
        result = await db.execute(
            select(Task).where(Task.id == task_id, Task.user_id == user_id)
        )
        task = result.scalar_one_or_none()

        if task is None:
            logger.warning(f"Task not found: task_id={task_id}, user_id={user_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": {
                        "code": "NOT_FOUND",
                        "message": "Task not found"
                    }
                }
            )

        logger.info(f"Task retrieved successfully: task_id={task_id}, user_id={user_id}")
        return TaskResponse.model_validate(task)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving task_id={task_id} for user_id={user_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "An unexpected error occurred while retrieving the task"
                }
            }
        )


@router.put(
    "/users/{user_id}/tasks/{task_id}",
    response_model=TaskResponse,
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": ErrorResponse, "description": "Validation error"},
        404: {"model": ErrorResponse, "description": "Task not found"},
    },
)
async def update_task(
    user_id: int,
    task_id: int,
    task_data: TaskUpdate,
    db: AsyncSession = Depends(get_db_session),
    verified_user_id: int = Depends(verify_user_access),
) -> TaskResponse:
    """
    Update an existing task for a user.

    Args:
        user_id: The ID of the user
        task_id: The ID of the task to update
        task_data: Task update data (partial updates supported)
        db: Database session

    Returns:
        TaskResponse: The updated task

    Raises:
        HTTPException 404: Task not found or belongs to different user
        HTTPException 400: Validation error
    """
    logger.info(f"Updating task_id={task_id} for user_id={user_id}")

    try:
        # Query with user_id filtering for isolation
        result = await db.execute(
            select(Task).where(Task.id == task_id, Task.user_id == user_id)
        )
        task = result.scalar_one_or_none()

        if task is None:
            logger.warning(f"Task not found for update: task_id={task_id}, user_id={user_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": {
                        "code": "NOT_FOUND",
                        "message": "Task not found"
                    }
                }
            )

        # Partial update - only update provided fields
        update_data = task_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(task, field, value)

        # Update timestamp
        task.updated_at = datetime.utcnow()

        await db.commit()
        await db.refresh(task)

        logger.info(f"Task updated successfully: task_id={task_id}, user_id={user_id}, fields={list(update_data.keys())}")
        return TaskResponse.model_validate(task)

    except HTTPException:
        raise
    except ValueError as e:
        await db.rollback()
        logger.error(f"Validation error updating task_id={task_id} for user_id={user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": str(e)
                }
            }
        )
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating task_id={task_id} for user_id={user_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "An unexpected error occurred while updating the task"
                }
            }
        )


@router.delete(
    "/users/{user_id}/tasks/{task_id}",
    status_code=status.HTTP_200_OK,
    responses={
        404: {"model": ErrorResponse, "description": "Task not found"},
    },
)
async def delete_task(
    user_id: int,
    task_id: int,
    db: AsyncSession = Depends(get_db_session),
    verified_user_id: int = Depends(verify_user_access),
) -> dict:
    """
    Delete a task for a user.

    Args:
        user_id: The ID of the user
        task_id: The ID of the task to delete
        db: Database session

    Returns:
        dict: Success message

    Raises:
        HTTPException 404: Task not found or belongs to different user
    """
    logger.info(f"Deleting task_id={task_id} for user_id={user_id}")

    try:
        # Query with user_id filtering for isolation
        result = await db.execute(
            select(Task).where(Task.id == task_id, Task.user_id == user_id)
        )
        task = result.scalar_one_or_none()

        if task is None:
            logger.warning(f"Task not found for deletion: task_id={task_id}, user_id={user_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": {
                        "code": "NOT_FOUND",
                        "message": "Task not found"
                    }
                }
            )

        await db.delete(task)
        await db.commit()

        logger.info(f"Task deleted successfully: task_id={task_id}, user_id={user_id}")
        return {"message": "Task deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error deleting task_id={task_id} for user_id={user_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "An unexpected error occurred while deleting the task"
                }
            }
        )
