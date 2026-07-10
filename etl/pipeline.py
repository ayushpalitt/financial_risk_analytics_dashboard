"""Executable ETL pipeline for the financial risk analytics dataset."""

from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

import pandas as pd

from etl.config import ETLConfig
from etl.transformations import (
    build_quality_report,
    clean_transactions,
    enrich_transactions,
)


@dataclass(frozen=True)
class ETLResult:
    """Outcome returned by a completed ETL run."""

    processed_data_path: Path
    quality_report_path: Path
    rows_written: int
    raw_file_sha256: str
    processed_file_sha256: str
    duplicate_rows_detected: int
    rows_dropped_for_missing_values: int
    rows_dropped_as_duplicates: int


def run_etl(config: ETLConfig | None = None) -> ETLResult:
    """Run the deterministic extract, transform, and load workflow."""

    active_config = config or ETLConfig()
    if not active_config.raw_data_path.exists():
        raise FileNotFoundError(
            f"Raw dataset not found at {active_config.raw_data_path}."
        )

    raw_file_sha256 = file_sha256(active_config.raw_data_path)
    raw_frame = pd.read_csv(active_config.raw_data_path)

    cleaned_frame, cleaning_summary = clean_transactions(raw_frame)
    processed_frame = enrich_transactions(cleaned_frame, active_config)

    active_config.processed_data_path.parent.mkdir(parents=True, exist_ok=True)
    processed_frame.to_csv(active_config.processed_data_path, index=False)
    processed_file_sha256 = file_sha256(active_config.processed_data_path)

    report = build_quality_report(
        raw_frame=raw_frame,
        processed_frame=processed_frame,
        cleaning_summary=cleaning_summary,
        config=active_config,
        raw_file_sha256=raw_file_sha256,
        processed_file_sha256=processed_file_sha256,
    )

    active_config.quality_report_path.parent.mkdir(parents=True, exist_ok=True)
    active_config.quality_report_path.write_text(
        json.dumps(report, indent=2, sort_keys=True),
        encoding="utf-8",
    )

    return ETLResult(
        processed_data_path=active_config.processed_data_path,
        quality_report_path=active_config.quality_report_path,
        rows_written=int(len(processed_frame)),
        raw_file_sha256=raw_file_sha256,
        processed_file_sha256=processed_file_sha256,
        duplicate_rows_detected=cleaning_summary.duplicate_rows_detected,
        rows_dropped_for_missing_values=(
            cleaning_summary.rows_dropped_for_missing_values
        ),
        rows_dropped_as_duplicates=cleaning_summary.rows_dropped_as_duplicates,
    )


def file_sha256(path: Path, chunk_size: int = 1024 * 1024) -> str:
    """Return a SHA-256 hash for an on-disk file."""

    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the Financial Risk Analytics deterministic ETL pipeline."
    )
    parser.add_argument(
        "--raw-path",
        type=Path,
        default=ETLConfig.raw_data_path,
        help="Path to the raw creditcard.csv dataset.",
    )
    parser.add_argument(
        "--processed-path",
        type=Path,
        default=ETLConfig.processed_data_path,
        help="Path where the enriched processed CSV will be written.",
    )
    parser.add_argument(
        "--report-path",
        type=Path,
        default=ETLConfig.quality_report_path,
        help="Path where the ETL quality report JSON will be written.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=ETLConfig.random_seed,
        help="Fixed random seed used for deterministic enrichment.",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    result = run_etl(
        ETLConfig(
            raw_data_path=args.raw_path,
            processed_data_path=args.processed_path,
            quality_report_path=args.report_path,
            random_seed=args.seed,
        )
    )
    print(
        json.dumps(
            {
                "processed_data_path": str(result.processed_data_path),
                "quality_report_path": str(result.quality_report_path),
                "rows_written": result.rows_written,
                "raw_file_sha256": result.raw_file_sha256,
                "processed_file_sha256": result.processed_file_sha256,
                "duplicate_rows_detected": result.duplicate_rows_detected,
                "rows_dropped_for_missing_values": (
                    result.rows_dropped_for_missing_values
                ),
                "rows_dropped_as_duplicates": result.rows_dropped_as_duplicates,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
