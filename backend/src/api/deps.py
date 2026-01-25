"""API dependency injection functions."""
import logging
from typing import AsyncGenerator

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import get_session
from ..core.security import verify_access_token
from ..schemas.error import ErrorCode

# Configure logger
logger = logging.getLogger(__name__)

# Re-export get_session for convenience
get_db = get_session

# HTTP Bearer token security scheme
security = HTTPBearer()


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Database session dependency for API endpoints.

    Usage:
        @router.get("/endpoint")
        async def endpoint(db: AsyncSession = Depends(get_db_session)):
            ...
    """
    async for session in get_session():
        yield session


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> int:
    """
    Extract and verify JWT token, return user_id.

    Args:
        credentials: HTTP Bearer token from Authorization header

    Returns:
        User ID from token

    Raises:
        HTTPException: 401 if token is missing, invalid, or expired
    """
    token = credentials.credentials

    try:
        logger.debug("Verifying JWT token")
        payload = verify_access_token(token)
        user_id_str = payload.get("sub")
        if user_id_str is None:
            logger.warning("JWT token missing 'sub' claim")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "error": {
                        "code": ErrorCode.INVALID_TOKEN,
                        "message": "Invalid or expired token"
                    }
                }
            )
        # Convert string sub claim to integer
        user_id = int(user_id_str)
        logger.info(f"JWT verification successful: user_id={user_id}")
        return user_id
    except jwt.ExpiredSignatureError:
        logger.warning("JWT token expired")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": {
                    "code": ErrorCode.EXPIRED_TOKEN,
                    "message": "Token has expired"
                }
            }
        )
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid JWT token: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": {
                    "code": ErrorCode.INVALID_TOKEN,
                    "message": "Invalid or expired token"
                }
            }
        )


async def verify_user_access(
    user_id: int,
    current_user_id: int = Depends(get_current_user)
) -> int:
    """
    Verify current user can access resources for user_id.

    Args:
        user_id: User ID from route parameter
        current_user_id: User ID from JWT token

    Returns:
        Verified user ID

    Raises:
        HTTPException: 403 if user IDs don't match
    """
    logger.debug(f"Verifying user access: route_user_id={user_id}, token_user_id={current_user_id}")

    if current_user_id != user_id:
        logger.warning(f"Access denied: user_id={current_user_id} attempted to access resources for user_id={user_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": {
                    "code": ErrorCode.FORBIDDEN,
                    "message": "Cannot access another user's resources"
                }
            }
        )

    logger.debug(f"User access verified: user_id={user_id}")
    return current_user_id
