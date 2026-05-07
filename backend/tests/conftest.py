

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

from database.db import Base, get_db
from main import app

# ── In-memory async SQLite engine ─────────────────────────────────────────────
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,  # Single connection shared across the session
    echo=False,
)

TestSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


# ── Session-scoped: create tables once per test session ───────────────────────
@pytest_asyncio.fixture(scope="session", autouse=True)
async def create_test_tables():
    """Creates all tables in the in-memory SQLite DB once per test session."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# ── Function-scoped: fresh DB session per test ────────────────────────────────
@pytest_asyncio.fixture
async def db_session():
    """Yields an async session and rolls back after each test for isolation."""
    async with TestSessionLocal() as session:
        yield session
        await session.rollback()


# ── Override get_db dependency ────────────────────────────────────────────────
@pytest_asyncio.fixture(autouse=True)
async def override_get_db(db_session: AsyncSession):
    """
    Replaces the real get_db FastAPI dependency with the test session.
    Applied automatically to every test via autouse=True.
    """
    async def _get_test_db():
        yield db_session

    app.dependency_overrides[get_db] = _get_test_db
    yield
    app.dependency_overrides.clear()


# ── HTTP client fixture ────────────────────────────────────────────────────────
@pytest_asyncio.fixture
async def client():
    """Yields an httpx AsyncClient wired to the FastAPI app."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac


# ── Test user fixture ──────────────────────────────────────────────────────────
@pytest_asyncio.fixture
async def test_user(client: AsyncClient) -> dict:
    """
    Creates a user via POST /auth/signup and returns their credentials
    alongside an access token ready for use in Authorization headers.

    Returns:
        {
            "email": str,
            "password": str,
            "access_token": str,
        }
    """
    email = "testuser@resumerag.dev"
    password = "securepassword99"

    response = await client.post(
        "/auth/signup",
        json={"email": email, "password": password},
    )
    assert response.status_code == 201, f"test_user fixture failed: {response.text}"

    return {
        "email": email,
        "password": password,
        "access_token": response.json()["access_token"],
    }