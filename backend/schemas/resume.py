

from pydantic import BaseModel, field_validator


class ResumeIDRequest(BaseModel):
    """
    Shared request body for /analyze and /match — just a resume UUID string.
    """
    resume_id: str

    @field_validator("resume_id", mode="before")
    @classmethod
    def strip_resume_id(cls, value: str) -> str:
        """Strip whitespace. UUID format validation happens in the router."""
        if not isinstance(value, str):
            raise ValueError("resume_id must be a string.")
        value = value.strip()
        if not value:
            raise ValueError("resume_id cannot be empty.")
        return value


class ProfileOut(BaseModel):
    """
    Structured profile extracted from a resume by the Groq service.
    """
    skills: list[str]
    experience_years: int
    job_titles: list[str]
    summary: str

    @field_validator("skills", mode="before")
    @classmethod
    def validate_skills(cls, value: list) -> list[str]:
        """Enforce max 20 skills, each max 50 chars, strip whitespace."""
        if not isinstance(value, list):
            raise ValueError("skills must be a list.")
        cleaned = [str(s).strip()[:50] for s in value[:20] if str(s).strip()]
        return cleaned

    @field_validator("summary", mode="before")
    @classmethod
    def strip_summary(cls, value: str) -> str:
        if not isinstance(value, str):
            raise ValueError("summary must be a string.")
        return value.strip()

    @field_validator("job_titles", mode="before")
    @classmethod
    def validate_job_titles(cls, value: list) -> list[str]:
        if not isinstance(value, list):
            raise ValueError("job_titles must be a list.")
        return [str(t).strip() for t in value if str(t).strip()]


class UploadResponse(BaseModel):
    resume_id: str
    char_count: int


class MatchJobOut(BaseModel):
    """Single ranked job in a /match response."""
    title: str
    company: str
    location: str
    url: str
    description: str
    salary_min: float | None
    salary_max: float | None
    score: float

    @field_validator("score")
    @classmethod
    def clamp_score(cls, value: float) -> float:
        """Ensure score stays in [0.0, 100.0] regardless of floating-point drift."""
        return round(max(0.0, min(100.0, value)), 1)


class MatchResponse(BaseModel):
    profile: ProfileOut
    matches: list[MatchJobOut]