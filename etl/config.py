"""Configuration primitives for the ETL pipeline."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RANDOM_SEED = int(os.getenv("RISK_ANALYTICS_RANDOM_SEED", "42"))


@dataclass(frozen=True)
class ETLConfig:
    """Runtime configuration for deterministic dataset processing."""

    raw_data_path: Path = PROJECT_ROOT / "data" / "raw" / "creditcard.csv"
    processed_data_path: Path = (
        PROJECT_ROOT / "data" / "processed" / "transactions_enriched.csv"
    )
    quality_report_path: Path = (
        PROJECT_ROOT / "data" / "processed" / "etl_quality_report.json"
    )
    random_seed: int = DEFAULT_RANDOM_SEED
    base_transaction_datetime: str = "2024-01-01T00:00:00"
