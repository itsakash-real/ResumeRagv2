
import os
from dotenv import load_dotenv

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
)
from sqlalchemy.orm import DeclarativeBase, sessionmaker

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set in environment variables.")

# PostgreSQL async compatibility
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace(
        "postgresql://",
        "postgresql+asyncpg://",
        1,
    )

elif DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace(
        "postgres://",
        "postgresql+asyncpg://",
        1,
    )

# =========================
# ASYNC ENGINE (FastAPI)
# =========================

if "sqlite" in DATABASE_URL:

    async_engine = create_async_engine(
        DATABASE_URL,
        echo=False,
    )

else:

    async_engine = create_async_engine(
        DATABASE_URL,
        echo=False,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
    )

SessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)

# =========================
# SYNC ENGINE (BackgroundTasks)
# =========================

if "sqlite" in DATABASE_URL:

    SYNC_DATABASE_URL = DATABASE_URL.replace(
        "sqlite+aiosqlite",
        "sqlite"
    )

    sync_engine = create_engine(
        SYNC_DATABASE_URL,
        connect_args={
            "check_same_thread": False,
            "timeout": 30,
        },
    )

    # Improve concurrent SQLite access
    from sqlalchemy import text

    with sync_engine.connect() as conn:
        conn.execute(text("PRAGMA journal_mode=WAL"))
        conn.commit()

else:

    SYNC_DATABASE_URL = DATABASE_URL.replace(
        "+asyncpg",
        ""
    )

    sync_engine = create_engine(
        SYNC_DATABASE_URL,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10,
    )

SyncSessionLocal = sessionmaker(
    bind=sync_engine,
    autoflush=False,
    autocommit=False,
)

# =========================
# BASE MODEL
# =========================

class Base(DeclarativeBase):
    pass

# =========================
# FASTAPI DB DEPENDENCY
# =========================

async def get_db():
    async with SessionLocal() as session:
        try:
            yield session
            await session.commit()

        except Exception:
            await session.rollback()
            raise

        finally:
            await session.close()