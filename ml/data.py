"""Dataset preparation utilities for fraud detection models."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd


PCA_FEATURE_COLUMNS = [f"V{index}" for index in range(1, 29)]
BASE_MODEL_FEATURE_COLUMNS = ["Time", "Amount", *PCA_FEATURE_COLUMNS]
ENGINEERED_MODEL_FEATURE_COLUMNS = [
    "amount_log",
    "hour_of_day",
    "is_night_transaction",
]
MODEL_FEATURE_COLUMNS = [
    *BASE_MODEL_FEATURE_COLUMNS,
    *ENGINEERED_MODEL_FEATURE_COLUMNS,
]
TARGET_COLUMN = "Class"
IDENTIFIER_COLUMN = "transaction_id"
REQUIRED_PROCESSED_COLUMNS = [
    IDENTIFIER_COLUMN,
    TARGET_COLUMN,
    *BASE_MODEL_FEATURE_COLUMNS,
]


@dataclass(frozen=True)
class ModelingDataset:
    """Prepared fraud modeling dataset."""

    features: pd.DataFrame
    target: pd.Series
    transaction_ids: pd.Series
    feature_columns: tuple[str, ...]


def load_modeling_dataset(processed_data_path: Path) -> ModelingDataset:
    """Load the processed ETL artifact and prepare model-safe features."""

    if not processed_data_path.exists():
        raise FileNotFoundError(
            f"Processed dataset not found at {processed_data_path}. Run `python -m etl` first."
        )

    frame = pd.read_csv(processed_data_path, usecols=REQUIRED_PROCESSED_COLUMNS)
    validate_processed_modeling_frame(frame)
    features = build_features(frame)

    return ModelingDataset(
        features=features,
        target=frame[TARGET_COLUMN].astype(int),
        transaction_ids=frame[IDENTIFIER_COLUMN].astype(str),
        feature_columns=tuple(features.columns),
    )


def validate_processed_modeling_frame(frame: pd.DataFrame) -> None:
    """Validate the minimum processed dataset columns needed for ML."""

    missing_columns = [
        column for column in REQUIRED_PROCESSED_COLUMNS if column not in frame.columns
    ]
    if missing_columns:
        raise ValueError(
            f"Processed dataset is missing required ML columns: {missing_columns}"
        )

    invalid_classes = sorted(set(frame[TARGET_COLUMN].dropna().unique()) - {0, 1})
    if invalid_classes:
        raise ValueError(f"Target column contains unsupported labels: {invalid_classes}")

    if frame[REQUIRED_PROCESSED_COLUMNS].isna().any().any():
        missing_summary = frame[REQUIRED_PROCESSED_COLUMNS].isna().sum()
        missing_summary = missing_summary[missing_summary > 0].to_dict()
        raise ValueError(f"Processed dataset contains missing ML values: {missing_summary}")


def build_features(frame: pd.DataFrame) -> pd.DataFrame:
    """Create model features without using post-label business risk fields."""

    features = frame[BASE_MODEL_FEATURE_COLUMNS].copy()
    features["amount_log"] = np.log1p(features["Amount"].astype(float))
    features["hour_of_day"] = (
        (features["Time"].astype(int) // 3600) % 24
    ).astype(float)
    features["is_night_transaction"] = features["hour_of_day"].between(
        0,
        5,
        inclusive="both",
    ).astype(int)
    return features[MODEL_FEATURE_COLUMNS].astype(float)
