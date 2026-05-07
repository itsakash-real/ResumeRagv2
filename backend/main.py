

import os
import logging
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from dotenv import load_dotenv
from fastapi import FastAPI, Request, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from database.db import async_engine, Base
from middleware.rate_limit import limiter

# Import all models so Base.metadata knows about all tables
import models  # noqa: F401

from routers import auth as auth_router
from routers import resume as resume_router
from routers import jobs as jobs_router

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manages startup and shutdown events.
    On startup: creates all tables (dev convenience — use Alembic in production).
    """
    logger.info("ResumeRAG v2 starting up...")
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables verified/created.")
    yield
    logger.info("ResumeRAG v2 shutting down.")


app = FastAPI(
    title="ResumeRAG v2",
    version="2.0.0",
    description="AI-powered resume-to-job matching platform.",
    lifespan=lifespan,
)

# ── Rate limiting ──────────────────────────────────────────────────────────────
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# ── CORS ───────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        FRONTEND_URL,
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:5175",
        "http://localhost:5176"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ────────────────────────────────────────────────────────────────────
app.include_router(auth_router.router)
app.include_router(resume_router.router)
app.include_router(jobs_router.router)


# ── Health check ───────────────────────────────────────────────────────────────
@app.get("/health", tags=["Health"])
async def health_check(request: Request) -> JSONResponse:
    """
    Liveness probe. Returns service status, UTC timestamp, and version.
    """
    return JSONResponse(
        content={
            "status": "ok",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "version": "2.0.0",
        }
    )


# ── WebSockets (Phase 5 Stub) ──────────────────────────────────────────────────

# In-memory store: resume_id → WebSocket connection
# Phase 5 will wire this into the pipeline services
active_connections: dict[str, WebSocket] = {}


@app.websocket("/ws/progress/{resume_id}")
async def progress_ws(websocket: WebSocket, resume_id: str) -> None:
    """
    WebSocket endpoint for real-time pipeline progress.
    Clients connect after upload and receive JSON: { step, percent }.
    Pipeline services call send_progress() to push updates.
    """
    await websocket.accept()
    active_connections[resume_id] = websocket
    try:
        # Hold connection open until client disconnects or pipeline closes it
        while True:
            await websocket.receive_text()
    except Exception:
        pass
    finally:
        active_connections.pop(resume_id, None)


async def send_progress(resume_id: str, step: str, percent: int) -> None:
    """
    Called by pipeline services to push progress to the connected client.
    Safe to call even if no client is connected.
    """
    ws = active_connections.get(resume_id)
    if ws:
        try:
            await ws.send_json({"step": step, "percent": percent})
            if percent >= 100:
                await ws.close()
                active_connections.pop(resume_id, None)
        except Exception:
            active_connections.pop(resume_id, None)