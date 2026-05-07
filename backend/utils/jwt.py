

import os
import logging
from datetime import datetime, timedelta, timezone
from typing import Any
import uuid

from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database.db import get_db

load_dotenv()

logger = logging.getLogger(__name__)

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY is not set in environment variables.")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def create_access_token(
    data: dict[str, Any],
    expires_delta: timedelta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
) -> str:
    """
    Creates a signed JWT access token.

    Args:
        data: Payload to encode (must include 'sub' key with user identifier).
        expires_delta: Token lifetime. Defaults to 15 minutes.

    Returns:
        Encoded JWT string.
    """
    payload = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    payload.update({"exp": expire, "type": "access"})
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(
    data: dict[str, Any],
    expires_delta: timedelta = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
) -> str:
    """
    Creates a signed JWT refresh token with a longer TTL.

    Args:
        data: Payload to encode (must include 'sub' key with user identifier).
        expires_delta: Token lifetime. Defaults to 7 days.

    Returns:
        Encoded JWT string.
    """
    payload = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    payload.update({"exp": expire, "type": "refresh"})
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str) -> dict[str, Any]:
    """
    Decodes and validates a JWT token.

    Args:
        token: Raw JWT string.

    Returns:
        Decoded payload dict.

    Raises:
        HTTPException 401: If the token is expired, malformed, or invalid.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as exc:
        logger.warning("JWT verification failed: %s", exc)
        raise credentials_exception from exc


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    FastAPI dependency. Verifies the bearer token and returns the User ORM object.

    Args:
        token: JWT extracted from Authorization header by oauth2_scheme.
        db: Injected async database session.

    Returns:
        User ORM instance for the authenticated request.

    Raises:
        HTTPException 401: If token is invalid or user no longer exists.
    """
    # Import here to avoid circular imports between utils and models
    from models.user import User

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = verify_token(token)

    user_id: str | None = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    try:
        parsed_user_id = uuid.UUID(user_id)
    except ValueError:
        raise credentials_exception

    result = await db.execute(select(User).where(User.id == parsed_user_id))
    user = result.scalar_one_or_none()

    if user is None:
        raise credentials_exception

    return user