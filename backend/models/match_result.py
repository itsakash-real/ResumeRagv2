

import uuid
from datetime import datetime
from sqlalchemy import String, Float, DateTime, ForeignKey, func, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.db import Base


class MatchResult(Base):
    __tablename__ = "match_results"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    resume_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("resumes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    job_title: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )
    company: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    url: Mapped[str] = mapped_column(
        String(2048),
        nullable=False,
    )
    score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    resume: Mapped["Resume"] = relationship(  # noqa: F821
        "Resume",
        back_populates="match_results",
    )