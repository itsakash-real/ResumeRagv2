

import logging

# Import your session maker (adjust 'database' to match your actual file)
from database.db import SyncSessionLocal

from models.match_result import MatchResult

logger = logging.getLogger(__name__)


def save_match_results(
    resume_id: str,
    matches: list[dict],
) -> None:
    """
    Bulk-inserts MatchResult rows for a completed match operation.

    This function is intentionally synchronous and receives a regular
    (non-async) SQLAlchemy Session because FastAPI BackgroundTasks execute
    in a threadpool executor, not the async event loop.

    Args:
        resume_id: UUID string of the parent Resume row.
        matches: List of dicts, each containing:
                 title, company, url, score (0–100 float).
    """
    if not matches:
        logger.info("save_match_results called with empty matches — nothing to save.")
        return

    import uuid
    try:
        parsed_resume_id = uuid.UUID(resume_id)
    except ValueError:
        logger.error("Invalid resume_id provided to save_match_results: %s", resume_id)
        return

    rows = [
        MatchResult(
            resume_id=parsed_resume_id,
            job_title=match.get("title", ""),
            company=match.get("company", ""),
            url=match.get("url", ""),
            score=match.get("score", 0.0),
        )
        for match in matches
    ]

    # Create a fresh database session uniquely for this background thread
    db = SyncSessionLocal()
    try:
        db.add_all(rows)
        db.commit()
        logger.info(
            "Saved %d match results for resume_id=%s", len(rows), resume_id
        )
    except Exception as exc:
        db.rollback()
        logger.exception(
            "Failed to save match results for resume_id=%s: %s", resume_id, exc
        )
    finally:
        db.close()