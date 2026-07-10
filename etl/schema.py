"""Schema contracts and validation for the raw fraud dataset."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
from pandas.api.types import is_numeric_dtype


FEATURE_COLUMNS = [f"V{index}" for index in range(1, 29)]
EXPECTED_RAW_COLUMNS = ["Time", *FEATURE_COLUMNS, "Amount", "Class"]
CLASS_LABELS = {0, 1}


class SchemaValidationError(ValueError):
    """Raised when a dataset does not match the expected fraud schema."""


@dataclass(frozen=True)
class SchemaValidationSummary:
    """Machine-readable result of a successful schema validation."""

    row_count: int
    column_count: int
    columns: tuple[str, ...]


def validate_raw_schema(frame: pd.DataFrame) -> SchemaValidationSummary:
    """Validate the raw Kaggle credit card fraud dataset schema."""

    actual_columns = list(frame.columns)
    missing_columns = [
        column for column in EXPECTED_RAW_COLUMNS if column not in actual_columns
    ]
    unexpected_columns = [
        column for column in actual_columns if column not in EXPECTED_RAW_COLUMNS
    ]

    if missing_columns or unexpected_columns:
        raise SchemaValidationError(
            "Raw dataset schema mismatch. "
            f"Missing columns: {missing_columns}. "
            f"Unexpected columns: {unexpected_columns}."
        )

    if actual_columns != EXPECTED_RAW_COLUMNS:
        raise SchemaValidationError(
            "Raw dataset columns are present but not in the expected order. "
            f"Expected {EXPECTED_RAW_COLUMNS}; received {actual_columns}."
        )

    non_numeric_columns = [
        column for column in EXPECTED_RAW_COLUMNS if not is_numeric_dtype(frame[column])
    ]
    if non_numeric_columns:
        raise SchemaValidationError(
            f"Raw dataset columns must be numeric: {non_numeric_columns}."
        )

    observed_classes = set(frame["Class"].dropna().astype(float).unique().tolist())
    invalid_classes = sorted(
        value for value in observed_classes if value not in {float(label) for label in CLASS_LABELS}
    )
    if invalid_classes:
        raise SchemaValidationError(
            f"Class column contains unsupported labels: {invalid_classes}."
        )

    if (frame["Time"].dropna() < 0).any():
        raise SchemaValidationError("Time column contains negative values.")

    if (frame["Amount"].dropna() < 0).any():
        raise SchemaValidationError("Amount column contains negative values.")

    return SchemaValidationSummary(
        row_count=int(len(frame)),
        column_count=int(len(frame.columns)),
        columns=tuple(actual_columns),
    )
