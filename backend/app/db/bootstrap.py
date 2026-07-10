"""Apply lightweight database bootstrap SQL for deployed API containers."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Iterable

from sqlalchemy import create_engine, text

from backend.app.core.config import get_settings
from backend.app.db.session import normalize_database_url


PROJECT_ROOT = Path(__file__).resolve().parents[3]
BOOTSTRAP_SQL_FILES = (
    PROJECT_ROOT / "database" / "schema" / "001_create_core_schema.sql",
    PROJECT_ROOT / "database" / "sql" / "010_analytics_views.sql",
)


def bootstrap_database(
    database_url: str | None = None,
    sql_files: Iterable[Path] = BOOTSTRAP_SQL_FILES,
) -> list[Path]:
    """Create core schema and analytics views required by the API."""

    active_database_url = normalize_database_url(
        database_url or get_settings().database_url
    )
    engine = create_engine(active_database_url, pool_pre_ping=True, future=True)
    applied_files: list[Path] = []

    try:
        with engine.connect().execution_options(
            isolation_level="AUTOCOMMIT"
        ) as connection:
            for sql_file in sql_files:
                if not sql_file.exists():
                    raise FileNotFoundError(f"Bootstrap SQL file not found: {sql_file}")
                connection.execute(text(sql_file.read_text(encoding="utf-8")))
                applied_files.append(sql_file)
    finally:
        engine.dispose()

    return applied_files


def main() -> int:
    applied_files = bootstrap_database()
    for sql_file in applied_files:
        print(f"applied={sql_file.relative_to(PROJECT_ROOT).as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
