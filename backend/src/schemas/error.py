"""Error response schemas."""
from enum import Enum
from pydantic import BaseModel


class ErrorCode(str, Enum):
    """Standard error codes used across the API."""

    # General errors
    NOT_FOUND = "NOT_FOUND"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    INTERNAL_ERROR = "INTERNAL_ERROR"

    # Authentication errors
    EMAIL_EXISTS = "EMAIL_EXISTS"
    INVALID_CREDENTIALS = "INVALID_CREDENTIALS"
    MISSING_TOKEN = "MISSING_TOKEN"
    INVALID_TOKEN = "INVALID_TOKEN"
    EXPIRED_TOKEN = "EXPIRED_TOKEN"
    FORBIDDEN = "FORBIDDEN"


class ErrorDetail(BaseModel):
    """Error detail structure."""

    code: str
    message: str


class ErrorResponse(BaseModel):
    """
    Standard error response format for all API endpoints.

    Example:
        {
            "error": {
                "code": "NOT_FOUND",
                "message": "Task not found"
            }
        }
    """

    error: ErrorDetail
