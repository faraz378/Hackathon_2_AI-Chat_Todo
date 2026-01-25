"""AI Agent service using OpenAI SDK."""
import json
import logging
from typing import Dict, List, Optional

from openai import AsyncOpenAI
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.config import settings
from . import mcp_tools

logger = logging.getLogger(__name__)


class AgentService:
    """
    AI Agent service for natural language task management.

    Uses OpenAI Agents SDK to interpret user intent and execute
    task operations via MCP tools.
    """

    # System prompt for the agent
    SYSTEM_PROMPT = """You are a helpful task management assistant. Users can ask you to create, view, update, or delete their tasks using natural language.

Available tools:
- create_task(title, description): Create a new task with a title and optional description
- list_tasks(completed): Show all tasks for the user (optionally filter by completion status)
- update_task(task_id, title, description, completed): Update a task's properties
- delete_task(task_id): Remove a task

Guidelines:
- Be concise and friendly in your responses
- Always confirm actions after executing them (e.g., "I've created a task 'buy groceries' for you")
- If the user's intent is unclear, ask clarifying questions
- If a task reference is ambiguous (e.g., "complete the task" when multiple tasks exist), ask which task they mean
- Always use tools to perform task operations - never make up data or pretend to complete actions
- If a tool call fails, explain the error to the user in simple terms

Examples:
User: "Create a task to buy groceries"
Assistant: [calls create_task] "I've created a task 'buy groceries' for you."

User: "Show my tasks"
Assistant: [calls list_tasks] "You have 3 tasks: 1. Buy groceries, 2. Call dentist, 3. Finish report"

User: "Mark the groceries task as done"
Assistant: [calls update_task] "I've marked 'buy groceries' as completed. Great job!"
"""

    # Tool schemas for OpenAI function calling
    TOOLS = [
        {
            "type": "function",
            "function": {
                "name": "create_task",
                "description": "Create a new task for the user. Use this when the user asks to create, add, or make a new task.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "The task title (1-500 characters). Extract the main task description from the user's message."
                        },
                        "description": {
                            "type": "string",
                            "description": "Optional detailed description of the task. Include any additional context or details mentioned by the user."
                        }
                    },
                    "required": ["title"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "list_tasks",
                "description": "List all tasks for the user. Use this when the user asks to see, show, list, or view their tasks.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "completed": {
                            "type": "boolean",
                            "description": "Filter by completion status. If null, return all tasks."
                        }
                    },
                    "required": []
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "update_task",
                "description": "Update an existing task. Use this when the user asks to update, modify, change, complete, or mark a task as done.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "task_id": {
                            "type": "integer",
                            "description": "The ID of the task to update. If the user refers to a task by title, you must first call list_tasks to find the task_id."
                        },
                        "title": {
                            "type": "string",
                            "description": "New task title (1-500 characters). Only provide if the user wants to change the title."
                        },
                        "description": {
                            "type": "string",
                            "description": "New task description. Only provide if the user wants to change the description."
                        },
                        "completed": {
                            "type": "boolean",
                            "description": "New completion status. Set to true when user says 'complete', 'done', 'finish', or 'mark as done'."
                        }
                    },
                    "required": ["task_id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "delete_task",
                "description": "Delete a task. Use this when the user asks to delete, remove, or get rid of a task.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "task_id": {
                            "type": "integer",
                            "description": "The ID of the task to delete. If the user refers to a task by title, you must first call list_tasks to find the task_id."
                        }
                    },
                    "required": ["task_id"]
                }
            }
        }
    ]

    def __init__(self):
        """Initialize the AgentService with OpenAI client."""
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL
        self.temperature = settings.OPENAI_TEMPERATURE
        self.max_tokens = settings.OPENAI_MAX_TOKENS

    async def chat(
        self,
        messages: List[Dict[str, str]],
        user_id: int,
        db: AsyncSession
    ) -> tuple[str, List[Dict]]:
        """
        Send messages to the AI agent and get a response.

        Args:
            messages: Conversation history in OpenAI format
            user_id: User ID for tool execution
            db: Database session for tool execution

        Returns:
            Tuple of (response_text, tool_invocations)
        """
        # Add system prompt
        full_messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT}
        ] + messages

        # Try to call OpenAI API
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=full_messages,
                tools=self.TOOLS,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )

            assistant_message = response.choices[0].message
            tool_invocations = []

            # Check if agent wants to call tools
            if assistant_message.tool_calls:
                # Execute all tool calls
                for tool_call in assistant_message.tool_calls:
                    tool_name = tool_call.function.name
                    tool_args = json.loads(tool_call.function.arguments)

                    logger.info(f"Agent calling tool: {tool_name} with args: {tool_args}")

                    # Execute tool and get result
                    tool_result = await self._execute_tool(
                        tool_name, tool_args, user_id, db
                    )

                    tool_invocations.append({
                        "tool": tool_name,
                        "inputs": {**tool_args, "user_id": user_id},
                        "outputs": tool_result.get("outputs"),
                        "error": tool_result.get("error")
                    })

                # Send tool results back to agent for final response
                messages_with_tools = full_messages + [
                    {
                        "role": "assistant",
                        "content": assistant_message.content or "",
                        "tool_calls": [
                            {
                                "id": tc.id,
                                "type": "function",
                                "function": {
                                    "name": tc.function.name,
                                    "arguments": tc.function.arguments
                                }
                            }
                            for tc in assistant_message.tool_calls
                        ]
                    }
                ] + [
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(tool_invocations[i].get("outputs") or {"error": tool_invocations[i].get("error")})
                    }
                    for i, tool_call in enumerate(assistant_message.tool_calls)
                ]

                # Get final response from agent
                final_response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=messages_with_tools,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens
                )

                response_text = final_response.choices[0].message.content

            else:
                # No tool calls, just return the response
                response_text = assistant_message.content

            return response_text, tool_invocations

        except Exception as openai_error:
            # Log the specific error
            logger.warning(f"OpenAI API error: {str(openai_error)} (Type: {type(openai_error).__name__}). Falling back to direct tool execution.")

            # When OpenAI API is unavailable, parse intent and call tools directly
            message_content = messages[-1]['content'].lower() if messages else ""

            if 'hello' in message_content or 'hi' in message_content or 'hey' in message_content:
                response_text = "Hello! I'm your AI task assistant. You can ask me to create, list, update, or delete tasks."
                tool_invocations = []
            elif any(word in message_content for word in ['create', 'add', 'make', 'new']):
                # Extract task title from message (simple heuristic)
                import re
                title = "sample task"  # default
                try:
                    # Look for "create/add/make [task description]" - more flexible pattern
                    pattern = r'(?:create|add|make|new)\s+(?:a\s+)?(?:task\s+(?:to|called|for)\s+|to\s+)?(.+?)(?:\.|$)'
                    match = re.search(pattern, message_content)

                    if match:
                        title = match.group(1).strip()
                        # Clean up title - remove common phrases
                        title = re.sub(r'\s*(please|now|today|tomorrow)\s*$', '', title).strip()

                        # Ensure we have a valid title
                        if not title or len(title.strip()) == 0:
                            title = "sample task"

                except Exception as e:
                    logger.warning(f"Error parsing task title from message '{message_content}': {str(e)}")
                    title = "sample task"

                try:
                    # Call the actual create_task function directly
                    from .mcp_tools import create_task
                    task_result = await create_task(
                        title=title,
                        user_id=user_id,
                        db=db,
                        description=None
                    )

                    response_text = f"I've created a task '{title}' for you."
                    tool_invocations = [{
                        "tool": "create_task",
                        "inputs": {"title": title, "user_id": user_id},
                        "outputs": task_result,
                        "error": None
                    }]
                except Exception as e:
                    logger.error(f"Error creating task '{title}' for user {user_id}: {str(e)}")
                    response_text = f"I had trouble creating the task '{title}': {str(e)}"
                    tool_invocations = [{
                        "tool": "create_task",
                        "inputs": {"title": title, "user_id": user_id},
                        "outputs": None,
                        "error": str(e)
                    }]
            elif any(word in message_content for word in ['show', 'list', 'view', 'see', 'my tasks']):
                # Call the actual list_tasks function directly
                try:
                    from .mcp_tools import list_tasks
                    tasks_result = await list_tasks(
                        user_id=user_id,
                        db=db,
                        completed=None
                    )

                    task_count = len(tasks_result.get('tasks', []))
                    if task_count == 0:
                        response_text = "You don't have any tasks yet. You can create one by asking me to create a task."
                    else:
                        response_text = f"You have {task_count} tasks:"
                        for i, task in enumerate(tasks_result['tasks'], 1):
                            status = "completed" if task['completed'] else "not completed"
                            response_text += f"\n{i}. {task['title']} ({status})"

                    tool_invocations = [{
                        "tool": "list_tasks",
                        "inputs": {"user_id": user_id},
                        "outputs": tasks_result,
                        "error": None
                    }]
                except Exception as e:
                    logger.error(f"Error listing tasks directly: {str(e)}")
                    response_text = f"I had trouble listing your tasks: {str(e)}"
                    tool_invocations = [{
                        "tool": "list_tasks",
                        "inputs": {"user_id": user_id},
                        "outputs": None,
                        "error": str(e)
                    }]
            elif any(word in message_content for word in ['update', 'complete', 'done', 'finish']):
                # For update tasks, we'd need to identify the task_id, which requires listing first
                # For simplicity in this fallback, we'll return a message
                response_text = "I can help you update tasks. Please specify which task you'd like to update and what changes to make."
                tool_invocations = []
            elif any(word in message_content for word in ['delete', 'remove']):
                # For delete tasks, we'd need to identify the task_id
                response_text = "I can help you delete tasks. Please specify which task you'd like to delete."
                tool_invocations = []
            else:
                response_text = f"I received your message: '{messages[-1]['content']}' and I'm ready to help you manage your tasks."
                tool_invocations = []

            return response_text, tool_invocations

    async def _execute_tool(
        self,
        tool_name: str,
        tool_args: Dict,
        user_id: int,
        db: AsyncSession
    ) -> Dict:
        """
        Execute an MCP tool and return the result.

        Args:
            tool_name: Name of the tool to execute
            tool_args: Tool arguments
            user_id: User ID for scoping
            db: Database session

        Returns:
            Dict with outputs or error
        """
        try:
            # Map tool names to functions
            tool_map = {
                "create_task": mcp_tools.create_task,
                "list_tasks": mcp_tools.list_tasks,
                "update_task": mcp_tools.update_task,
                "delete_task": mcp_tools.delete_task
            }

            if tool_name not in tool_map:
                raise ValueError(f"Unknown tool: {tool_name}")

            # Execute tool with user_id
            tool_func = tool_map[tool_name]
            result = await tool_func(user_id=user_id, db=db, **tool_args)

            return {"outputs": result, "error": None}

        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {str(e)}")
            return {"outputs": None, "error": str(e)}
