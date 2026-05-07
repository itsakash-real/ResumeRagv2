import logging

from database.db import SyncSessionLocal, sync_engine
from models.match_result import MatchResult

logger = logging.getLogger(__name__)


def _can_save_history() -> bool:
    """Returns True only if the configured DB is reachable."""
    try:
        from sqlalchemy import text

        # Lightweight connectivity check
        with sync_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as exc:
        logger.warning(
            "Database not available; skipping match history save: %s",
            exc,
        )
        return False


def save_match_results(resume_id: str, matches: list[dict]) -> None:
    """Persist match results.

    This is executed as a FastAPI BackgroundTasks threadpool job.

    Requirement:
      - If PostgreSQL (DB) is not reachable/unavailable, DO NOT save history.
    """
    if not matches:
        logger.info("save_match_results called with empty matches — nothing to save.")
        return

    if not _can_save_history():
        logger.info("Skipping match history save due to missing/unreachable DB.")
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

    db = SyncSessionLocal()
    try:
        db.add_all(rows)
        db.commit()
        logger.info("Saved %d match results for resume_id=%s", len(rows), resume_id)
    except Exception as exc:
        db.rollback()
        logger.exception(
            "Failed to save match results for resume_id=%s: %s",
            resume_id,
            exc,
        )
    finally:
        db.close()

