"""SQLAlchemy engine management."""

from __future__ import annotations

from functools import lru_cache

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

from backend.app.core.config import get_settings


def normalize_database_url(database_url: str) -> str:
    """Normalize SQLAlchemy driver aliases to an installed psycopg2 URL."""

    if database_url.startswith("postgres://"):
        return database_url.replace("postgres://", "postgresql+psycopg2://", 1)
    if database_url.startswith("postgresql+psycopg://"):
        return database_url.replace(
            "postgresql+psycopg://",
            "postgresql+psycopg2://",
            1,
        )
    return database_url


@lru_cache(maxsize=1)
def get_engine() -> Engine:
    """Create and cache the database engine."""

    settings = get_settings()
    return create_engine(
        normalize_database_url(settings.database_url),
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10,
        future=True,
    )
