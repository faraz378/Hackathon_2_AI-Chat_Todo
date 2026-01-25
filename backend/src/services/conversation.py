"""Conversation management service."""
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.conversation import Conversation
from ..models.message import Message
from ..models.tool_invocation import ToolInvocationLog

logger = logging.getLogger(__name__)


class ConversationService:
    """Service for managing conversations and messages."""

    @staticmethod
    async def create_conversation(
        user_id: int,
        db: AsyncSession
    ) -> Conversation:
        """
        Create a new conversation for a user.

        Args:
            user_id: User ID
            db: Database session

        Returns:
            Created Conversation object
        """
        try:
            conversation = Conversation(
                user_id=user_id,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )

            db.add(conversation)
            await db.commit()
            await db.refresh(conversation)

            logger.info(f"Created conversation {conversation.id} for user {user_id}")
            return conversation

        except Exception as e:
            await db.rollback()
            logger.error(f"Error creating conversation for user {user_id}: {str(e)}")
            raise

    @staticmethod
    async def add_message(
        conversation_id: int,
        role: str,
        content: str,
        db: AsyncSession,
        tool_invocations: Optional[List[Dict]] = None
    ) -> Message:
        """
        Add a message to a conversation.

        Args:
            conversation_id: Conversation ID
            role: Message role ('user' or 'assistant')
            content: Message content
            db: Database session
            tool_invocations: Optional list of tool invocations (for assistant messages)

        Returns:
            Created Message object
        """
        try:
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
                created_at=datetime.utcnow(),
                tool_invocations=json.dumps(tool_invocations) if tool_invocations else None
            )
            db.add(message)

            # Update conversation timestamp
            conversation = await db.get(Conversation, conversation_id)
            if conversation:
                conversation.updated_at = datetime.utcnow()

            await db.commit()
            await db.refresh(message)

            logger.info(f"Added {role} message {message.id} to conversation {conversation_id}")
            return message

        except Exception as e:
            await db.rollback()
            logger.error(f"Error adding message to conversation {conversation_id}: {str(e)}")
            raise

    @staticmethod
    async def log_tool_invocation(
        user_id: int,
        tool_name: str,
        inputs: Dict,
        outputs: Optional[Dict],
        success: bool,
        error_message: Optional[str],
        db: AsyncSession,
        message_id: Optional[int] = None
    ) -> ToolInvocationLog:
        """
        Log an MCP tool invocation for audit trail.

        Args:
            user_id: User ID
            tool_name: Name of the tool invoked
            inputs: Tool input parameters
            outputs: Tool output (None if failed)
            success: Whether the tool call succeeded
            error_message: Error message if failed
            db: Database session
            message_id: Optional message ID that triggered this tool call

        Returns:
            Created ToolInvocationLog object
        """
        try:
            log = ToolInvocationLog(
                user_id=user_id,
                message_id=message_id,
                tool_name=tool_name,
                inputs=json.dumps(inputs),
                outputs=json.dumps(outputs) if outputs else None,
                success=success,
                error_message=error_message,
                created_at=datetime.utcnow()
            )

            db.add(log)
            await db.commit()
            await db.refresh(log)

            logger.info(f"Logged tool invocation: {tool_name} for user {user_id}, success={success}")
            return log

        except Exception as e:
            await db.rollback()
            logger.error(f"Error logging tool invocation: {str(e)}")
            raise

    @staticmethod
    async def load_conversation_messages(
        conversation_id: int,
        user_id: int,
        db: AsyncSession,
        limit: int = 50
    ) -> List[Dict[str, str]]:
        """
        Load conversation history from database in OpenAI format.

        Args:
            conversation_id: Conversation ID
            user_id: User ID (for ownership verification)
            db: Database session
            limit: Maximum number of messages to load

        Returns:
            List of messages in OpenAI format [{"role": "user", "content": "..."}]
        """
        try:
            # Verify conversation belongs to user
            conversation = await db.get(Conversation, conversation_id)
            if not conversation or conversation.user_id != user_id:
                raise ValueError("Conversation not found or does not belong to user")

            # Load messages ordered by sequence
            result = await db.execute(
                select(Message)
                .where(Message.conversation_id == conversation_id)
                .order_by(Message.sequence_number.desc())
                .limit(limit)
            )
            messages = result.scalars().all()

            # Reverse to get chronological order
            messages = list(reversed(messages))

            # Convert to OpenAI format
            openai_messages = [
                {"role": msg.role, "content": msg.content}
                for msg in messages
            ]

            logger.info(f"Loaded {len(openai_messages)} messages from conversation {conversation_id}")
            return openai_messages

        except Exception as e:
            logger.error(f"Error loading conversation {conversation_id}: {str(e)}")
            raise

    @staticmethod
    async def get_user_conversations(
        user_id: int,
        db: AsyncSession
    ) -> List[Dict]:
        """
        Get all conversations for a user with summary information.

        Args:
            user_id: User ID
            db: Database session

        Returns:
            List of conversation summaries
        """
        try:
            # Load user's conversations
            result = await db.execute(
                select(Conversation)
                .where(Conversation.user_id == user_id)
                .order_by(Conversation.updated_at.desc())
            )
            conversations = result.scalars().all()

            # Build summaries
            summaries = []
            for conv in conversations:
                # Get message count
                msg_result = await db.execute(
                    select(func.count(Message.id))
                    .where(Message.conversation_id == conv.id)
                )
                message_count = msg_result.scalar() or 0

                # Get last message preview
                last_msg_result = await db.execute(
                    select(Message)
                    .where(Message.conversation_id == conv.id)
                    .order_by(Message.sequence_number.desc())
                    .limit(1)
                )
                last_message = last_msg_result.scalar_one_or_none()
                last_message_preview = last_message.content[:100] if last_message else None

                summaries.append({
                    "id": conv.id,
                    "created_at": conv.created_at.isoformat(),
                    "updated_at": conv.updated_at.isoformat(),
                    "message_count": message_count,
                    "last_message_preview": last_message_preview
                })

            logger.info(f"Retrieved {len(summaries)} conversations for user {user_id}")
            return summaries

        except Exception as e:
            logger.error(f"Error getting conversations for user {user_id}: {str(e)}")
            raise
