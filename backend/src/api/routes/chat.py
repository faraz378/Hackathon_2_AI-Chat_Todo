"""Chat API routes."""
import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ...schemas.chat import ChatRequest, ChatResponse, ToolInvocation
from ...schemas.error import ErrorCode
from ...services.agent import AgentService
from ...services.conversation import ConversationService
from ..deps import get_db_session, get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse, status_code=status.HTTP_200_OK)
async def chat(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db_session),
    user_id: int = Depends(get_current_user)
) -> ChatResponse:
    """
    Send a message to the AI agent and get a response.

    Args:
        request: Chat request with conversation_id and message
        db: Database session
        user_id: Authenticated user ID from JWT

    Returns:
        ChatResponse with conversation_id, message_id, response, and tool_invocations

    Raises:
        HTTPException 400: Invalid input (empty message, message too long)
        HTTPException 404: Conversation not found or doesn't belong to user
        HTTPException 500: Internal error (OpenAI API, database, tool execution)
    """
    try:
        # Validate message
        if not request.message or len(request.message.strip()) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": {
                        "code": "VALIDATION_ERROR",
                        "message": "Message cannot be empty"
                    }
                }
            )

        if len(request.message) > 10000:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": {
                        "code": "VALIDATION_ERROR",
                        "message": "Message must be less than 10000 characters"
                    }
                }
            )

        logger.info(f"Chat request from user {user_id}, conversation_id={request.conversation_id}")

        # Create or load conversation
        if request.conversation_id is None:
            # Create new conversation
            conversation = await ConversationService.create_conversation(user_id, db)
            conversation_id = conversation.id
            conversation_history = []
        else:
            # Load existing conversation
            conversation_id = request.conversation_id
            try:
                conversation_history = await ConversationService.load_conversation_messages(
                    conversation_id, user_id, db
                )
            except ValueError as e:
                # Conversation not found or doesn't belong to user
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail={
                        "error": {
                            "code": "NOT_FOUND",
                            "message": "Conversation not found"
                        }
                    }
                )

        # Add user message to conversation
        user_message = await ConversationService.add_message(
            conversation_id=conversation_id,
            role="user",
            content=request.message,
            db=db
        )

        # Add user message to conversation history for agent
        conversation_history.append({
            "role": "user",
            "content": request.message
        })

        # Call AI agent
        agent = AgentService()
        try:
            response_text, tool_invocations = await agent.chat(
                messages=conversation_history,
                user_id=user_id,
                db=db
            )
        except Exception as e:
            logger.error(f"Error calling AI agent: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "error": {
                        "code": "AGENT_ERROR",
                        "message": "Failed to get response from AI agent"
                    }
                }
            )

        # Add assistant message to conversation
        assistant_message = await ConversationService.add_message(
            conversation_id=conversation_id,
            role="assistant",
            content=response_text,
            db=db,
            tool_invocations=tool_invocations
        )

        # Log tool invocations
        for tool_inv in tool_invocations:
            await ConversationService.log_tool_invocation(
                user_id=user_id,
                tool_name=tool_inv["tool"],
                inputs=tool_inv["inputs"],
                outputs=tool_inv.get("outputs"),
                success=tool_inv.get("error") is None,
                error_message=tool_inv.get("error"),
                db=db,
                message_id=assistant_message.id
            )

        logger.info(f"Chat response sent to user {user_id}, conversation_id={conversation_id}")

        # Return response
        return ChatResponse(
            conversation_id=conversation_id,
            message_id=assistant_message.id,
            response=response_text,
            tool_invocations=[
                ToolInvocation(
                    tool=inv["tool"],
                    inputs=inv["inputs"],
                    outputs=inv.get("outputs"),
                    error=inv.get("error")
                )
                for inv in tool_invocations
            ]
        )

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Log unexpected errors
        logger.error(f"Unexpected error in chat endpoint: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": {
                    "code": ErrorCode.INTERNAL_ERROR,
                    "message": "An unexpected error occurred while processing your message"
                }
            }
        )


@router.get("/conversations", status_code=status.HTTP_200_OK)
async def list_conversations(
    db: AsyncSession = Depends(get_db_session),
    user_id: int = Depends(get_current_user)
):
    """
    Get list of user's conversations.

    Args:
        db: Database session
        user_id: Authenticated user ID from JWT

    Returns:
        List of conversation summaries
    """
    try:
        conversations = await ConversationService.get_user_conversations(user_id, db)
        return conversations
    except Exception as e:
        logger.error(f"Error listing conversations for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": {
                    "code": ErrorCode.INTERNAL_ERROR,
                    "message": "Failed to retrieve conversations"
                }
            }
        )


@router.get("/conversations/{conversation_id}/messages", status_code=status.HTTP_200_OK)
async def get_conversation_messages(
    conversation_id: int,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db_session),
    user_id: int = Depends(get_current_user)
):
    """
    Get messages from a specific conversation.

    Args:
        conversation_id: Conversation ID
        limit: Maximum number of messages to return
        offset: Number of messages to skip
        db: Database session
        user_id: Authenticated user ID from JWT

    Returns:
        Dict with messages list and total count
    """
    try:
        # Verify conversation belongs to user
        from sqlalchemy import select
        from ...models.conversation import Conversation
        from ...models.message import Message

        result = await db.execute(
            select(Conversation).where(Conversation.id == conversation_id)
        )
        conversation = result.scalar_one_or_none()

        if not conversation or conversation.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": {
                        "code": "NOT_FOUND",
                        "message": "Conversation not found"
                    }
                }
            )

        # Get messages with pagination
        result = await db.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.sequence_number)
            .offset(offset)
            .limit(limit)
        )
        messages = result.scalars().all()

        # Get total count
        from sqlalchemy import func
        count_result = await db.execute(
            select(func.count(Message.id))
            .where(Message.conversation_id == conversation_id)
        )
        total = count_result.scalar() or 0

        return {
            "messages": [
                {
                    "id": msg.id,
                    "role": msg.role,
                    "content": msg.content,
                    "sequence_number": msg.sequence_number,
                    "created_at": msg.created_at.isoformat(),
                    "tool_invocations": msg.tool_invocations
                }
                for msg in messages
            ],
            "total": total
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting messages for conversation {conversation_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": {
                    "code": ErrorCode.INTERNAL_ERROR,
                    "message": "Failed to retrieve messages"
                }
            }
        )
