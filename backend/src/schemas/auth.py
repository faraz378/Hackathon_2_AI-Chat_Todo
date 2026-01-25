"""Authentication request and response schemas."""
from pydantic import BaseModel, EmailStr, Field


class SignupRequest(BaseModel):
    """Request schema for user registration."""

    email: EmailStr = Field(
        description="User email address",
        examples=["user@example.com"]
    )
    password: str = Field(
        min_length=8,
        max_length=128,
        description="User password (minimum 8 characters)",
        examples=["securepassword123"]
    )


class SigninRequest(BaseModel):
    """Request schema for user authentication."""

    email: EmailStr = Field(
        description="User email address",
        examples=["user@example.com"]
    )
    password: str = Field(
        description="User password",
        examples=["securepassword123"]
    )


class TokenResponse(BaseModel):
    """Response schema for successful authentication."""

    access_token: str = Field(
        description="JWT access token",
        examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."]
    )
    token_type: str = Field(
        default="bearer",
        description="Token type (always 'bearer')"
    )
    expires_in: int = Field(
        default=86400,
        description="Token expiration time in seconds (24 hours)"
    )


class SignupResponse(BaseModel):
    """Response schema for successful registration."""

    message: str = Field(
        default="User created successfully",
        description="Success message"
    )
    user_id: int = Field(
        description="ID of the created user",
        examples=[123]
    )
