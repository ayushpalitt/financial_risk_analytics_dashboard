"""FastAPI dependencies."""

from __future__ import annotations

from backend.app.db.repository import AnalyticsRepository
from backend.app.db.session import get_engine


def get_repository() -> AnalyticsRepository:
    """Return a database-backed analytics repository."""

    return AnalyticsRepository(get_engine())
