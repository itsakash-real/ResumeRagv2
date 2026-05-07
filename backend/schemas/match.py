

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class MatchResultOut(BaseModel):
    """
    Serialized representation of a single MatchResult row.
    Used in list and paginated responses.
    """
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    job_title: str
    company: str
    url: str
    score: float
    created_at: datetime


class PaginatedMatchResponse(BaseModel):
    """
    Wrapper for paginated GET /matches responses.

    Attributes:
        total:   Total number of records matching the filter (pre-pagination).
        page:    Current page number (1-indexed).
        limit:   Maximum records per page.
        results: The current page's records.
    """
    total: int
    page: int
    limit: int
    results: list[MatchResultOut]