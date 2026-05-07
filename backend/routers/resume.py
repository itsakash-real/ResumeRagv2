

import logging
import uuid
import asyncio

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, Request, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.db import get_db
from middleware.rate_limit import limiter
from models.resume import Resume
from models.user import User
from utils.jwt import get_current_user
from utils.file_validator import validate_pdf
from schemas.resume import ResumeIDRequest
from services.parser_service import parse_pdf
from services.extractor_service import extract_profile
from services.embeddings_service import embed_text, embed_batch
from services.faiss_service import build_index, query_index
from services.jobs_service import fetch_jobs
from background.tasks import save_match_results

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/resume", tags=["Resume"])


# ── POST /resume/upload ────────────────────────────────────────────────────────

@router.post(
    "/upload",
    status_code=status.HTTP_201_CREATED,
    summary="Upload a PDF resume and extract raw text",
)
async def upload_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Accepts a PDF upload, validates it, extracts text, and persists a Resume row.

    Returns:
        resume_id: UUID of the created Resume record.
        char_count: Number of characters extracted from the PDF.
    """
    file_bytes = await file.read()

    # Step 1: Validate magic bytes + size (raises HTTPException on failure)
    validate_pdf(file_bytes)

    # Step 2: Extract text
    try:
        raw_text = await asyncio.to_thread(parse_pdf, file_bytes)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    # Step 3: Persist Resume row (profile_json is null until /analyze is called)
    resume = Resume(
        user_id=current_user.id,
        filename=file.filename or "resume.pdf",
        raw_text=raw_text,
        profile_json=None,
    )
    db.add(resume)
    await db.flush()
    await db.refresh(resume)

    logger.info(
        "Resume uploaded — resume_id=%s, user_id=%s, chars=%d",
        resume.id,
        current_user.id,
        len(raw_text),
    )

    return {
        "resume_id": str(resume.id),
        "char_count": len(raw_text),
    }


# ── POST /resume/analyze ───────────────────────────────────────────────────────

@router.post(
    "/analyze",
    status_code=status.HTTP_200_OK,
    summary="Extract structured profile from an uploaded resume via Groq",
)
async def analyze_resume(
    body: ResumeIDRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Calls Groq to extract a structured JSON profile from stored resume text.
    Updates Resume.profile_json in the database.

    Request body:
        { "resume_id": "<uuid>" }

    Returns:
        The structured profile dict (skills, experience_years, job_titles, summary).
    """
    resume_id: str = body.resume_id

    resume = await _get_resume_for_user(db, resume_id, current_user.id)

    profile = await asyncio.to_thread(extract_profile, resume.raw_text)

    # Persist the profile so /match can use cached version
    resume.profile_json = profile
    db.add(resume)
    await db.flush()

    logger.info("Profile extracted and cached — resume_id=%s", resume_id)

    return profile


# ── POST /resume/match ─────────────────────────────────────────────────────────

@router.post(
    "/match",
    status_code=status.HTTP_200_OK,
    summary="Match resume against live job listings (rate limited: 10/hour)",
)
@limiter.limit("10/hour")
async def match_resume(
    request: Request,
    body: ResumeIDRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Full AI matching pipeline:
      1. Load resume + profile (or extract fresh if not cached).
      2. Fetch live jobs from Adzuna.
      3. Embed resume summary + job descriptions.
      4. Build FAISS index, query for top matches.
      5. Return ranked matches with 0–100 scores.
      6. Persist results asynchronously via BackgroundTasks.

    Request body:
        { "resume_id": "<uuid>" }

    Returns:
        profile: Structured resume profile.
        matches: List of ranked jobs with scores.
    """
    resume_id: str = body.resume_id

    resume = await _get_resume_for_user(db, resume_id, current_user.id)

    # ── Step 1: Profile (use cache if available) ───────────────────────────────
    if resume.profile_json:
        profile = resume.profile_json
        logger.info("Using cached profile for resume_id=%s", resume_id)
    else:
        profile = await asyncio.to_thread(extract_profile, resume.raw_text)
        resume.profile_json = profile
        db.add(resume)
        await db.commit()  # Commit immediately to release SQLite write-lock before slow AI steps!
        logger.info("Fresh profile extracted for resume_id=%s", resume_id)

    # ── Step 2: Fetch live jobs ────────────────────────────────────────────────
    jobs: list[dict] = await fetch_jobs(profile["skills"])

    if not jobs:
        logger.warning("No jobs returned from Adzuna for resume_id=%s", resume_id)
        return {"profile": profile, "matches": []}

    # ── Step 3: Embed resume summary ──────────────────────────────────────────
    resume_vector = await asyncio.to_thread(embed_text, profile["summary"])       # shape (384,)

    # ── Step 4: Embed job descriptions ────────────────────────────────────────
    descriptions = [j["description"] or j["title"] for j in jobs]
    job_vectors = await asyncio.to_thread(embed_batch, descriptions)              # shape (N, 384)

    # ── Step 5: FAISS — build index + query ───────────────────────────────────
    index = await asyncio.to_thread(build_index, job_vectors)
    ranked = await asyncio.to_thread(query_index, index, resume_vector, k=len(jobs))

    # ── Step 6: Assemble scored matches ───────────────────────────────────────
    matches: list[dict] = []
    for job_idx, raw_score in ranked:
        job = jobs[job_idx].copy()
        job["score"] = round(raw_score * 100, 1)  # Convert [0,1] → [0,100]
        matches.append(job)

    # Already sorted descending by query_index, enforce explicitly
    matches.sort(key=lambda x: x["score"], reverse=True)

    # ── Step 7: Persist in background (after response is sent) ────────────────
    background_tasks.add_task(
        save_match_results,
        str(resume.id),
        matches,
    )

    logger.info(
        "Match complete — resume_id=%s, jobs_ranked=%d, top_score=%.1f",
        resume_id,
        len(matches),
        matches[0]["score"] if matches else 0.0,
    )

    return {"profile": profile, "matches": matches}


# ── Shared helper ─────────────────────────────────────────────────────────────

async def _get_resume_for_user(
    db: AsyncSession,
    resume_id: str,
    user_id: uuid.UUID,
) -> Resume:
    """
    Fetches a Resume by ID and verifies ownership.

    Args:
        db: Async database session.
        resume_id: UUID string of the resume.
        user_id: UUID of the authenticated user.

    Returns:
        Resume ORM instance.

    Raises:
        HTTPException 404: If the resume does not exist.
        HTTPException 403: If the resume belongs to a different user.
    """
    try:
        parsed_id = uuid.UUID(resume_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid resume_id format.",
        ) from exc

    result = await db.execute(select(Resume).where(Resume.id == parsed_id))
    resume = result.scalar_one_or_none()

    if resume is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found.",
        )

    if resume.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this resume.",
        )

    return resume