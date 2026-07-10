"""Load the processed ETL output into the normalized PostgreSQL schema."""

from __future__ import annotations

import argparse
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

import pandas as pd
import psycopg2
from psycopg2.extras import execute_values


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PROCESSED_PATH = (
    PROJECT_ROOT / "data" / "processed" / "transactions_enriched.csv"
)
SCHEMA_DIR = PROJECT_ROOT / "database" / "schema"
ANALYTICS_SQL_DIR = PROJECT_ROOT / "database" / "sql"

FEATURE_COLUMNS = [f"V{index}" for index in range(1, 29)]
PROCESSED_REQUIRED_COLUMNS = [
    "transaction_id",
    "source_row_number",
    "transaction_date",
    "customer_id",
    "merchant_id",
    "merchant_name",
    "merchant_category",
    "transaction_channel",
    "card_type",
    "city",
    "state",
    "customer_segment",
    "risk_score",
    "approval_status",
    "Time",
    "Amount",
    "Class",
    "is_fraud",
    *FEATURE_COLUMNS,
]

CUSTOMER_COLUMNS = [
    "customer_id",
    "customer_segment",
    "card_type",
    "city",
    "state",
]
MERCHANT_COLUMNS = [
    "merchant_id",
    "merchant_name",
    "merchant_category",
]
TRANSACTION_COLUMNS = [
    "transaction_id",
    "source_row_number",
    "transaction_date",
    "customer_id",
    "merchant_id",
    "transaction_channel",
    "amount",
    "class_label",
    "is_fraud",
    "time_seconds",
    "approval_status",
    "risk_score",
    *[f"v{index}" for index in range(1, 29)],
]


@dataclass(frozen=True)
class LoadSummary:
    """Summary returned after loading processed transactions."""

    processed_path: Path
    rows_loaded: int
    chunks_loaded: int
    schema_applied: bool
    analytics_applied: bool


def default_database_url() -> str:
    return os.getenv(
        "DATABASE_URL",
        "postgresql://risk_admin:change_me_locally@127.0.0.1:55432/financial_risk",
    )


def normalize_database_url(database_url: str) -> str:
    if database_url.startswith("postgres://"):
        return database_url.replace("postgres://", "postgresql://", 1)
    return (
        database_url.replace("postgresql+psycopg://", "postgresql://")
        .replace("postgresql+psycopg2://", "postgresql://")
    )


def apply_sql_directory(cursor, directory: Path) -> list[Path]:
    applied_files: list[Path] = []
    for sql_file in sorted(directory.glob("*.sql")):
        cursor.execute(sql_file.read_text(encoding="utf-8"))
        applied_files.append(sql_file)
    return applied_files


def truncate_core_tables(cursor) -> None:
    cursor.execute(
        """
        TRUNCATE TABLE
            fraud_predictions,
            daily_metrics,
            transactions,
            customers,
            merchants
        RESTART IDENTITY CASCADE;
        """
    )


def validate_processed_columns(columns: Iterable[str]) -> None:
    observed = set(columns)
    missing = [
        column for column in PROCESSED_REQUIRED_COLUMNS if column not in observed
    ]
    if missing:
        raise ValueError(f"Processed dataset is missing required columns: {missing}")


def load_processed_transactions(
    database_url: str | None = None,
    processed_path: Path = DEFAULT_PROCESSED_PATH,
    chunk_size: int = 25_000,
    apply_schema: bool = True,
    apply_analytics: bool = True,
    replace: bool = False,
) -> LoadSummary:
    """Load the enriched transaction CSV into PostgreSQL."""

    if not processed_path.exists():
        raise FileNotFoundError(
            f"Processed dataset not found at {processed_path}. Run `python -m etl` first."
        )

    active_database_url = normalize_database_url(database_url or default_database_url())
    rows_loaded = 0
    chunks_loaded = 0

    with psycopg2.connect(active_database_url) as connection:
        with connection.cursor() as cursor:
            if apply_schema:
                apply_sql_directory(cursor, SCHEMA_DIR)
                connection.commit()

            if replace:
                truncate_core_tables(cursor)
                connection.commit()

            for chunk in pd.read_csv(processed_path, chunksize=chunk_size):
                validate_processed_columns(chunk.columns)
                normalized_chunk = normalize_chunk(chunk)
                upsert_customers(cursor, normalized_chunk)
                upsert_merchants(cursor, normalized_chunk)
                upsert_transactions(cursor, normalized_chunk)
                connection.commit()
                rows_loaded += len(normalized_chunk)
                chunks_loaded += 1

            cursor.execute("SELECT refresh_daily_metrics();")
            connection.commit()

            if apply_analytics:
                apply_sql_directory(cursor, ANALYTICS_SQL_DIR)
                connection.commit()

    return LoadSummary(
        processed_path=processed_path,
        rows_loaded=rows_loaded,
        chunks_loaded=chunks_loaded,
        schema_applied=apply_schema,
        analytics_applied=apply_analytics,
    )


def normalize_chunk(chunk: pd.DataFrame) -> pd.DataFrame:
    normalized = chunk.copy()
    normalized["transaction_date"] = pd.to_datetime(normalized["transaction_date"])
    normalized["source_row_number"] = normalized["source_row_number"].astype(int)
    normalized["Amount"] = normalized["Amount"].astype(float)
    normalized["Class"] = normalized["Class"].astype(int)
    normalized["is_fraud"] = normalized["Class"].eq(1)
    normalized["Time"] = normalized["Time"].astype(int)
    normalized["risk_score"] = normalized["risk_score"].astype(float)
    return normalized


def upsert_customers(cursor, chunk: pd.DataFrame) -> None:
    customers = chunk[CUSTOMER_COLUMNS].drop_duplicates(subset=["customer_id"])
    execute_upsert(
        cursor=cursor,
        table_name="customers",
        columns=CUSTOMER_COLUMNS,
        records=records_from_frame(customers[CUSTOMER_COLUMNS]),
        conflict_columns=["customer_id"],
        update_columns=["customer_segment", "card_type", "city", "state"],
    )


def upsert_merchants(cursor, chunk: pd.DataFrame) -> None:
    merchants = chunk[MERCHANT_COLUMNS].drop_duplicates(subset=["merchant_id"])
    execute_upsert(
        cursor=cursor,
        table_name="merchants",
        columns=MERCHANT_COLUMNS,
        records=records_from_frame(merchants[MERCHANT_COLUMNS]),
        conflict_columns=["merchant_id"],
        update_columns=["merchant_name", "merchant_category"],
    )


def upsert_transactions(cursor, chunk: pd.DataFrame) -> None:
    transactions = pd.DataFrame(
        {
            "transaction_id": chunk["transaction_id"],
            "source_row_number": chunk["source_row_number"],
            "transaction_date": chunk["transaction_date"],
            "customer_id": chunk["customer_id"],
            "merchant_id": chunk["merchant_id"],
            "transaction_channel": chunk["transaction_channel"],
            "amount": chunk["Amount"],
            "class_label": chunk["Class"],
            "is_fraud": chunk["is_fraud"],
            "time_seconds": chunk["Time"],
            "approval_status": chunk["approval_status"],
            "risk_score": chunk["risk_score"],
            **{f"v{index}": chunk[f"V{index}"] for index in range(1, 29)},
        }
    )
    execute_upsert(
        cursor=cursor,
        table_name="transactions",
        columns=TRANSACTION_COLUMNS,
        records=records_from_frame(transactions[TRANSACTION_COLUMNS]),
        conflict_columns=["transaction_id"],
        update_columns=[
            column for column in TRANSACTION_COLUMNS if column != "transaction_id"
        ],
        page_size=5_000,
    )


def execute_upsert(
    cursor,
    table_name: str,
    columns: Sequence[str],
    records: list[tuple],
    conflict_columns: Sequence[str],
    update_columns: Sequence[str],
    page_size: int = 10_000,
) -> None:
    if not records:
        return

    column_sql = ", ".join(columns)
    conflict_sql = ", ".join(conflict_columns)
    if update_columns:
        update_sql = ", ".join(
            f"{column} = EXCLUDED.{column}" for column in update_columns
        )
        conflict_action = f"DO UPDATE SET {update_sql}"
    else:
        conflict_action = "DO NOTHING"

    sql = (
        f"INSERT INTO {table_name} ({column_sql}) VALUES %s "
        f"ON CONFLICT ({conflict_sql}) {conflict_action};"
    )
    execute_values(cursor, sql, records, page_size=page_size)


def records_from_frame(frame: pd.DataFrame) -> list[tuple]:
    return [
        tuple(to_python_scalar(value) for value in row)
        for row in frame.itertuples(index=False, name=None)
    ]


def to_python_scalar(value):
    if pd.isna(value):
        return None
    if isinstance(value, pd.Timestamp):
        return value.to_pydatetime()
    if hasattr(value, "item"):
        return value.item()
    return value


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Load processed financial risk transactions into PostgreSQL."
    )
    parser.add_argument(
        "--database-url",
        default=default_database_url(),
        help="PostgreSQL connection URL.",
    )
    parser.add_argument(
        "--processed-path",
        type=Path,
        default=DEFAULT_PROCESSED_PATH,
        help="Path to data/processed/transactions_enriched.csv.",
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=25_000,
        help="Number of processed rows to load per database batch.",
    )
    parser.add_argument(
        "--skip-schema",
        action="store_true",
        help="Skip applying database/schema SQL files before loading.",
    )
    parser.add_argument(
        "--skip-analytics",
        action="store_true",
        help="Skip applying database/sql analytics files after loading.",
    )
    parser.add_argument(
        "--replace",
        action="store_true",
        help="Truncate normalized tables before loading the processed dataset.",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    summary = load_processed_transactions(
        database_url=args.database_url,
        processed_path=args.processed_path,
        chunk_size=args.chunk_size,
        apply_schema=not args.skip_schema,
        apply_analytics=not args.skip_analytics,
        replace=args.replace,
    )
    print(
        "\n".join(
            [
                f"processed_path={summary.processed_path}",
                f"rows_loaded={summary.rows_loaded}",
                f"chunks_loaded={summary.chunks_loaded}",
                f"schema_applied={summary.schema_applied}",
                f"analytics_applied={summary.analytics_applied}",
            ]
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
