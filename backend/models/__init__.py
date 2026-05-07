# models/__init__.py
# Imports all models so Alembic and Base.metadata.create_all() can discover them.

from .user import User
from .resume import Resume
from .match_result import MatchResult

__all__ = ["User", "Resume", "MatchResult"]