"""Tests for raw dataset schema validation."""

from __future__ import annotations

import unittest

import pandas as pd

from etl.schema import (
    EXPECTED_RAW_COLUMNS,
    FEATURE_COLUMNS,
    SchemaValidationError,
    validate_raw_schema,
)


def make_raw_frame() -> pd.DataFrame:
    frame = pd.DataFrame(
        {
            "Time": [0, 1, 2],
            "Amount": [10.25, 20.00, 31.50],
            "Class": [0, 1, 0],
        }
    )
    for column in FEATURE_COLUMNS:
        frame[column] = 0.0
    return frame[EXPECTED_RAW_COLUMNS]


class RawSchemaValidationTest(unittest.TestCase):
    def test_valid_raw_schema_passes(self) -> None:
        summary = validate_raw_schema(make_raw_frame())

        self.assertEqual(summary.row_count, 3)
        self.assertEqual(summary.column_count, len(EXPECTED_RAW_COLUMNS))
        self.assertEqual(summary.columns, tuple(EXPECTED_RAW_COLUMNS))

    def test_missing_column_fails(self) -> None:
        frame = make_raw_frame().drop(columns=["V7"])

        with self.assertRaises(SchemaValidationError):
            validate_raw_schema(frame)

    def test_unexpected_class_label_fails(self) -> None:
        frame = make_raw_frame()
        frame.loc[1, "Class"] = 2

        with self.assertRaises(SchemaValidationError):
            validate_raw_schema(frame)

    def test_fractional_class_label_fails(self) -> None:
        frame = make_raw_frame()
        frame["Class"] = frame["Class"].astype(float)
        frame.loc[1, "Class"] = 0.5

        with self.assertRaises(SchemaValidationError):
            validate_raw_schema(frame)

    def test_negative_amount_fails(self) -> None:
        frame = make_raw_frame()
        frame.loc[0, "Amount"] = -1.0

        with self.assertRaises(SchemaValidationError):
            validate_raw_schema(frame)


if __name__ == "__main__":
    unittest.main()
