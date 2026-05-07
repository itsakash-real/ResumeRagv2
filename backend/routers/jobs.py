

import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from database.db import get_db
from models.match_result import MatchResult
from models.resume import Resume
from models.user import User
from schemas.match import MatchResultOut, PaginatedMatchResponse
from utils.jwt import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/matches", tags=["Matches"])


# ── GET /matches ───────────────────────────────────────────────────────────────

@router.get(
    "",
    response_model=PaginatedMatchResponse,
    status_code=status.HTTP_200_OK,
    summary="Retrieve paginated match history for the authenticated user",
)
async def get_matches(
    page: int = Query(default=1, ge=1, description="Page number (1-indexed)"),
    limit: int = Query(default=10, ge=1, le=50, description="Results per page (max 50)"),
    min_score: float = Query(default=0.0, ge=0.0, le=100.0, description="Minimum match score filter"),
    sort: str = Query(
        default="score_desc",
        pattern=r"^(score_desc|score_asc|date_desc)$",
        description="Sort order: score_desc | score_asc | date_desc",
    ),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> PaginatedMatchResponse:
    """
    Returns paginated MatchResult records belonging to the current user.

    Filtering:
        - min_score: only results with score >= this value are returned.

    Sorting options:
        - score_desc: highest score first (default).
        - score_asc:  lowest score first.
        - date_desc:  most recently created first.

    Pagination:
        - total reflects the filtered count (not the raw table count).
        - offset = (page - 1) * limit.
    """
    # ── Base filter: MatchResult → Resume → User ownership ───────────────────
    base_query = (
        select(MatchResult)
        .join(Resume, MatchResult.resume_id == Resume.id)
        .where(Resume.user_id == current_user.id)
        .where(MatchResult.score >= min_score)
    )

    # ── Total count (filtered, pre-pagination) ────────────────────────────────
    count_result = await db.execute(
        select(func.count()).select_from(base_query.subquery())
    )
    total: int = count_result.scalar_one()

    # ── Sorting ───────────────────────────────────────────────────────────────
    sort_map = {
        "score_desc": MatchResult.score.desc(),
        "score_asc":  MatchResult.score.asc(),
        "date_desc":  MatchResult.created_at.desc(),
    }
    ordered_query = base_query.order_by(sort_map[sort])

    # ── Pagination ────────────────────────────────────────────────────────────
    offset = (page - 1) * limit
    paginated_query = ordered_query.offset(offset).limit(limit)

    result = await db.execute(paginated_query)
    rows = result.scalars().all()

    logger.info(
        "GET /matches — user=%s, page=%d, limit=%d, min_score=%.1f, "
        "sort=%s, total=%d, returned=%d",
        current_user.id, page, limit, min_score, sort, total, len(rows),
    )

    return PaginatedMatchResponse(
        total=total,
        page=page,
        limit=limit,
        results=[MatchResultOut.model_validate(row) for row in rows],
    )


# ── DELETE /matches/{match_id} ─────────────────────────────────────────────────

@router.delete(
    "/{match_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a specific match result (must belong to authenticated user)",
)
async def delete_match(
    match_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """
    Permanently deletes a MatchResult row after verifying ownership.

    Ownership is verified by tracing:
        MatchResult → Resume → User (must equal current_user.id)

    Raises:
        HTTPException 400: If match_id is not a valid UUID.
        HTTPException 404: If the match does not exist.
        HTTPException 403: If the match belongs to a different user.
    """
    try:
        parsed_match_id = uuid.UUID(match_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid match_id format.",
        ) from exc

    # Fetch the match with its parent resume in one join
    result = await db.execute(
        select(MatchResult)
        .join(Resume, MatchResult.resume_id == Resume.id)
        .where(MatchResult.id == parsed_match_id)
    )
    match = result.scalar_one_or_none()

    if match is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Match result not found.",
        )

    # Verify ownership by checking the parent resume's user_id
    resume_result = await db.execute(
        select(Resume).where(Resume.id == match.resume_id)
    )
    resume = resume_result.scalar_one_or_none()

    if resume is None or resume.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete this match result.",
        )

    await db.delete(match)

    logger.info(
        "Match result deleted — match_id=%s, user=%s", match_id, current_user.id
    )

    # 204 No Content — return nothing