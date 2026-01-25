"""Security utilities for password hashing and JWT token management."""
import jwt
import bcrypt
from datetime import datetime, timedelta
from typing import Dict, Any

from .config import settings


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.

    Bcrypt has a 72-byte password limit. Passwords are truncated to 72 bytes
    after UTF-8 encoding to comply with this limitation.

    Args:
        password: Plain text password

    Returns:
        Hashed password string
    """
    # Truncate to 72 bytes to comply with bcrypt's limitation
    password_bytes = password.encode('utf-8')[:72]

    # Generate salt and hash the password
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)

    # Return as string
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash.

    Applies the same 72-byte truncation as hash_password for consistency.

    Args:
        plain_password: Plain text password to verify
        hashed_password: Hashed password from database

    Returns:
        True if password matches, False otherwise
    """
    # Apply same truncation as hash_password
    password_bytes = plain_password.encode('utf-8')[:72]
    hashed_bytes = hashed_password.encode('utf-8')

    return bcrypt.checkpw(password_bytes, hashed_bytes)


def create_access_token(user_id: int, email: str) -> str:
    """
    Generate JWT access token for authenticated user.

    Args:
        user_id: User ID from database
        email: User email address

    Returns:
        JWT token string
    """
    now = datetime.utcnow()
    payload: Dict[str, Any] = {
        "sub": str(user_id),  # JWT standard requires sub to be a string
        "email": email,
        "iat": now,
        "exp": now + timedelta(hours=settings.JWT_EXPIRATION_HOURS)
    }

    token = jwt.encode(
        payload,
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM
    )

    return token


def verify_access_token(token: str) -> Dict[str, Any]:
    """
    Verify JWT token and extract payload.

    Args:
        token: JWT token string

    Returns:
        Decoded payload dictionary

    Raises:
        jwt.ExpiredSignatureError: Token has expired
        jwt.InvalidTokenError: Token is invalid
    """
    payload = jwt.decode(
        token,
        settings.JWT_SECRET,
        algorithms=[settings.JWT_ALGORITHM]
    )

    return payload
