"""Authentication routes for signup and signin."""
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.security import hash_password, create_access_token, verify_password
from ...models.user import User
from ...schemas.auth import SignupRequest, SignupResponse, SigninRequest, TokenResponse
from ...schemas.error import ErrorCode
from ..deps import get_db_session

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/signup", response_model=SignupResponse, status_code=status.HTTP_201_CREATED)
async def signup(
    request: SignupRequest,
    db: AsyncSession = Depends(get_db_session)
) -> SignupResponse:
    """
    Register a new user with email and password.

    Args:
        request: Signup request with email and password
        db: Database session

    Returns:
        SignupResponse with user_id and success message

    Raises:
        HTTPException: 400 if email already exists or validation fails
        HTTPException: 500 if internal error occurs
    """
    try:
        # Normalize email to lowercase for case-insensitive comparison
        email = request.email.lower()

        logger.info(f"Signup attempt for email: {email}")

        # Check if email already exists
        result = await db.execute(
            select(User).where(User.email == email)
        )
        existing_user = result.scalar_one_or_none()

        if existing_user:
            logger.warning(f"Signup failed: Email already exists - {email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": {
                        "code": ErrorCode.EMAIL_EXISTS,
                        "message": "Email already registered"
                    }
                }
            )

        # Hash password
        password_hash = hash_password(request.password)

        # Create new user
        new_user = User(
            email=email,
            password_hash=password_hash
        )

        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)

        logger.info(f"User created successfully: user_id={new_user.id}, email={email}")

        return SignupResponse(
            message="User created successfully",
            user_id=new_user.id
        )

    except HTTPException:
        # Re-raise HTTP exceptions (EMAIL_EXISTS, etc.)
        raise
    except Exception as e:
        # Log the error and return generic internal error
        logger.error(f"Signup error for email {request.email.lower()}: {str(e)}", exc_info=True)
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": {
                    "code": ErrorCode.INTERNAL_ERROR,
                    "message": "An internal error occurred during signup"
                }
            }
        )


@router.post("/signin", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def signin(
    request: SigninRequest,
    db: AsyncSession = Depends(get_db_session)
) -> TokenResponse:
    """
    Authenticate user and return JWT token.

    Args:
        request: Signin request with email and password
        db: Database session

    Returns:
        TokenResponse with JWT access token

    Raises:
        HTTPException: 401 if credentials are invalid
        HTTPException: 500 if internal error occurs
    """
    try:
        # Normalize email to lowercase
        email = request.email.lower()

        logger.info(f"Signin attempt for email: {email}")

        # Look up user by email
        result = await db.execute(
            select(User).where(User.email == email)
        )
        user = result.scalar_one_or_none()

        # Verify user exists and password is correct
        if not user or not verify_password(request.password, user.password_hash):
            logger.warning(f"Signin failed: Invalid credentials for email - {email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "error": {
                        "code": ErrorCode.INVALID_CREDENTIALS,
                        "message": "Invalid email or password"
                    }
                }
            )

        # Generate JWT token
        access_token = create_access_token(user_id=user.id, email=user.email)

        logger.info(f"Signin successful: user_id={user.id}, email={email}")

        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=86400  # 24 hours in seconds
        )

    except HTTPException:
        # Re-raise HTTP exceptions (INVALID_CREDENTIALS, etc.)
        raise
    except Exception as e:
        # Log the error and return generic internal error
        logger.error(f"Signin error for email {request.email.lower()}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": {
                    "code": ErrorCode.INTERNAL_ERROR,
                    "message": "An internal error occurred during signin"
                }
            }
        )
