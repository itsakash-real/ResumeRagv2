
import logging

from fastapi import HTTPException, status
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from models.user import User

logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain: str) -> str:
    """
    Hashes a plaintext password using bcrypt.

    Args:
        plain: Raw password string from the user.

    Returns:
        Bcrypt-hashed password string safe for storage.
    """
    return pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    """
    Compares a plaintext password against a stored bcrypt hash.

    Args:
        plain: Raw password from login attempt.
        hashed: Stored bcrypt hash from DB.

    Returns:
        True if they match, False otherwise.
    """
    return pwd_context.verify(plain, hashed)


async def create_user(db: AsyncSession, email: str, password: str) -> User:
    """
    Creates a new user after checking for duplicate email.

    Args:
        db: Async SQLAlchemy session.
        email: User's email address (already validated by Pydantic).
        password: Plaintext password (will be hashed before storage).

    Returns:
        Newly created User ORM instance.

    Raises:
        HTTPException 400: If a user with this email already exists.
    """
    result = await db.execute(select(User).where(User.email == email))
    existing = result.scalar_one_or_none()

    if existing is not None:
        logger.info("Signup attempted with existing email: %s", email)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists.",
        )

    user = User(
        email=email,
        hashed_password=hash_password(password),
    )
    db.add(user)
    await db.flush()   # Flush to get the generated UUID before commit
    await db.refresh(user)

    logger.info("New user created: %s (id=%s)", email, user.id)
    return user


async def authenticate_user(
    db: AsyncSession,
    email: str,
    password: str,
) -> User | None:
    """
    Looks up a user by email and verifies their password.

    Args:
        db: Async SQLAlchemy session.
        email: Email from login request.
        password: Plaintext password from login request.

    Returns:
        User ORM instance if credentials are valid, None otherwise.
    """
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if user is None:
        logger.info("Login attempted for non-existent email: %s", email)
        return None

    if not verify_password(password, user.hashed_password):
        logger.info("Invalid password for email: %s", email)
        return None

    return user