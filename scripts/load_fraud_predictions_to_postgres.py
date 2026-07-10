"""Load model prediction exports into PostgreSQL fraud_predictions."""

from __future__ import annotations

import argparse
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

import pandas as pd
import psycopg2
from psycopg2.extras import execute_values


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PREDICTIONS_PATH = PROJECT_ROOT / "data" / "exports" / "fraud_predictions.csv"
REQUIRED_COLUMNS = [
    "transaction_id",
    "model_name",
    "model_version",
    "fraud_probability",
    "predicted_class",
    "prediction_threshold",
]


@dataclass(frozen=True)
class PredictionLoadSummary:
    """Summary returned after loading fraud predictions."""

    predictions_path: Path
    rows_loaded: int
    chunks_loaded: int


def default_database_url() -> str:
    return os.getenv(
        "DATABASE_URL",
        "postgresql://risk_admin:change_me_locally@127.0.0.1:55432/financial_risk",
    )


def normalize_database_url(database_url: str) -> str:
    return (
        database_url.replace("postgresql+psycopg://", "postgresql://")
        .replace("postgresql+psycopg2://", "postgresql://")
    )


def load_fraud_predictions(
    database_url: str | None = None,
    predictions_path: Path = DEFAULT_PREDICTIONS_PATH,
    chunk_size: int = 25_000,
) -> PredictionLoadSummary:
    """Upsert fraud prediction rows into PostgreSQL."""

    if not predictions_path.exists():
        raise FileNotFoundError(
            f"Prediction export not found at {predictions_path}. Run `python -m ml` first."
        )

    active_database_url = normalize_database_url(database_url or default_database_url())
    rows_loaded = 0
    chunks_loaded = 0

    with psycopg2.connect(active_database_url) as connection:
        with connection.cursor() as cursor:
            for chunk in pd.read_csv(predictions_path, chunksize=chunk_size):
                validate_prediction_chunk(chunk)
                records = [
                    tuple(to_python_scalar(value) for value in row)
                    for row in chunk[REQUIRED_COLUMNS].itertuples(index=False, name=None)
                ]
                execute_values(
                    cursor,
                    """
                    INSERT INTO fraud_predictions (
                        transaction_id,
                        model_name,
                        model_version,
                        fraud_probability,
                        predicted_class,
                        prediction_threshold
                    )
                    VALUES %s
                    ON CONFLICT (
                        transaction_id,
                        model_name,
                        model_version
                    )
                    DO UPDATE SET
                        fraud_probability = EXCLUDED.fraud_probability,
                        predicted_class = EXCLUDED.predicted_class,
                        prediction_threshold = EXCLUDED.prediction_threshold,
                        prediction_date = NOW();
                    """,
                    records,
                    page_size=5_000,
                )
                connection.commit()
                rows_loaded += len(chunk)
                chunks_loaded += 1

    return PredictionLoadSummary(
        predictions_path=predictions_path,
        rows_loaded=rows_loaded,
        chunks_loaded=chunks_loaded,
    )


def validate_prediction_chunk(chunk: pd.DataFrame) -> None:
    missing = [column for column in REQUIRED_COLUMNS if column not in chunk.columns]
    if missing:
        raise ValueError(f"Prediction export is missing columns: {missing}")

    if chunk[REQUIRED_COLUMNS].isna().any().any():
        raise ValueError("Prediction export contains missing values.")

    if not chunk["fraud_probability"].between(0, 1).all():
        raise ValueError("fraud_probability must be between 0 and 1.")

    if not chunk["prediction_threshold"].between(0, 1).all():
        raise ValueError("prediction_threshold must be between 0 and 1.")

    invalid_classes = sorted(set(chunk["predicted_class"].unique()) - {0, 1})
    if invalid_classes:
        raise ValueError(f"predicted_class contains invalid labels: {invalid_classes}")


def to_python_scalar(value):
    if pd.isna(value):
        return None
    if hasattr(value, "item"):
        return value.item()
    return value


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Load fraud prediction exports into PostgreSQL."
    )
    parser.add_argument(
        "--database-url",
        default=default_database_url(),
        help="PostgreSQL connection URL.",
    )
    parser.add_argument(
        "--predictions-path",
        type=Path,
        default=DEFAULT_PREDICTIONS_PATH,
        help="Path to data/exports/fraud_predictions.csv.",
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=25_000,
        help="Prediction rows to load per batch.",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    summary = load_fraud_predictions(
        database_url=args.database_url,
        predictions_path=args.predictions_path,
        chunk_size=args.chunk_size,
    )
    print(
        "\n".join(
            [
                f"predictions_path={summary.predictions_path}",
                f"rows_loaded={summary.rows_loaded}",
                f"chunks_loaded={summary.chunks_loaded}",
            ]
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
