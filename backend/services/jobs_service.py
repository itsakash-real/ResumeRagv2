

import logging
import os
import re
import time

import httpx
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

ADZUNA_APP_ID = os.getenv("ADZUNA_APP_ID", "")
ADZUNA_APP_KEY = os.getenv("ADZUNA_APP_KEY", "")
ADZUNA_BASE_URL = os.getenv("ADZUNA_BASE_URL", "https://api.adzuna.com/v1/api/jobs")
ADZUNA_COUNTRY = os.getenv("ADZUNA_COUNTRY", "us")

_HTML_TAG_RE = re.compile(r"<[^>]+>")


def _strip_html(text: str) -> str:
    """Removes HTML tags from a string using a compiled regex."""
    return _HTML_TAG_RE.sub("", text).strip()


def _normalize_job(raw: dict) -> dict:
    """
    Transforms a raw Adzuna job object into the canonical internal format.

    Args:
        raw: Single job dict from Adzuna API response.

    Returns:
        Dict with keys: title, company, location, url, description,
        salary_min, salary_max.
    """
    return {
        "title": raw.get("title", ""),
        "company": raw.get("company", {}).get("display_name", ""),
        "location": raw.get("location", {}).get("display_name", ""),
        "url": raw.get("redirect_url", ""),
        "description": _strip_html(raw.get("description", "")),
        "salary_min": raw.get("salary_min"),
        "salary_max": raw.get("salary_max"),
    }


async def fetch_jobs(skills: list[str]) -> list[dict]:
    """
    Fetches up to 20 job listings from Adzuna using the top 3 skills as query.

    Design decision: this function never raises on Adzuna errors. A failed
    external API call returns an empty list so the rest of the match pipeline
    can still run gracefully (with no jobs to rank).

    Args:
        skills: List of skill strings from the extracted profile.

    Returns:
        List of normalized job dicts (may be empty on API failure).
    """
    if not ADZUNA_APP_ID or not ADZUNA_APP_KEY:
        logger.error("Adzuna credentials are not configured — returning empty job list.")
        return []

    query = " ".join(skills[:3])
    url = f"{ADZUNA_BASE_URL}/{ADZUNA_COUNTRY}/search/1"
    params = {
        "results_per_page": 20,
        "what": query,
        "app_id": ADZUNA_APP_ID,
        "app_key": ADZUNA_APP_KEY,
        "content-type": "application/json",
    }

    start = time.perf_counter()

    try:
        async with httpx.AsyncClient(timeout=10.0) as http:
            response = await http.get(url, params=params)
            response.raise_for_status()
            data = response.json()
    except httpx.TimeoutException:
        logger.warning("Adzuna API timed out for query: %r", query)
        return []
    except httpx.HTTPStatusError as exc:
        logger.warning(
            "Adzuna API returned HTTP %d for query: %r",
            exc.response.status_code,
            query,
        )
        return []
    except Exception as exc:
        logger.exception("Unexpected error fetching Adzuna jobs: %s", exc)
        return []

    elapsed = time.perf_counter() - start
    raw_jobs: list[dict] = data.get("results", [])
    jobs = [_normalize_job(j) for j in raw_jobs]

    logger.info(
        "Adzuna fetch — query=%r, returned=%d jobs, elapsed=%.3fs",
        query,
        len(jobs),
        elapsed,
    )

    return jobs