

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from database.db import get_db
from schemas.auth import SignupRequest, LoginRequest, TokenResponse
from services.auth_service import create_user, authenticate_user
from utils.jwt import create_access_token, create_refresh_token

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/signup",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user account",
)
async def signup(
    payload: SignupRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """
    Creates a new user and returns JWT access + refresh tokens.
    Returns HTTP 400 if the email is already registered.
    """
    try:
        user = await create_user(db, payload.email, payload.password)
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Unexpected error during signup: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred. Please try again.",
        ) from exc

    token_data = {"sub": str(user.id)}
    return TokenResponse(
        access_token=create_access_token(token_data),
        refresh_token=create_refresh_token(token_data),
    )


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Authenticate and receive JWT tokens",
)
async def login(
    payload: LoginRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """
    Validates credentials and returns JWT access + refresh tokens.
    Returns HTTP 401 for invalid email or password (intentionally vague).
    """
    try:
        user = await authenticate_user(db, payload.email, payload.password)
    except Exception as exc:
        logger.exception("Unexpected error during login: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred. Please try again.",
        ) from exc

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token_data = {"sub": str(user.id)}
    return TokenResponse(
        access_token=create_access_token(token_data),
        refresh_token=create_refresh_token(token_data),
    )