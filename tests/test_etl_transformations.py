"""Tests for deterministic cleaning and enrichment."""

from __future__ import annotations

import unittest

import pandas as pd
from pandas.testing import assert_frame_equal

from etl.config import ETLConfig
from etl.schema import EXPECTED_RAW_COLUMNS, FEATURE_COLUMNS
from etl.transformations import clean_transactions, enrich_transactions


def make_raw_frame() -> pd.DataFrame:
    records = [
        {"Time": 0, "Amount": 10.25, "Class": 0},
        {"Time": 1, "Amount": 250.00, "Class": 1},
        {"Time": 1, "Amount": 250.00, "Class": 1},
        {"Time": 2, "Amount": None, "Class": 0},
        {"Time": 3, "Amount": 75.50, "Class": 0},
    ]
    frame = pd.DataFrame(records)
    for index, column in enumerate(FEATURE_COLUMNS, start=1):
        frame[column] = index / 100.0
    return frame[EXPECTED_RAW_COLUMNS]


class ETLTransformationsTest(unittest.TestCase):
    def test_clean_transactions_drops_missing_and_duplicate_rows(self) -> None:
        cleaned_frame, summary = clean_transactions(make_raw_frame())

        self.assertEqual(summary.raw_rows, 5)
        self.assertEqual(summary.rows_dropped_for_missing_values, 1)
        self.assertEqual(summary.duplicate_rows_detected, 1)
        self.assertEqual(summary.rows_dropped_as_duplicates, 1)
        self.assertEqual(len(cleaned_frame), 3)
        self.assertIn("source_row_number", cleaned_frame.columns)

    def test_enrichment_is_deterministic_for_same_seed(self) -> None:
        cleaned_frame, _summary = clean_transactions(make_raw_frame())
        config = ETLConfig(random_seed=7)

        first = enrich_transactions(cleaned_frame, config)
        second = enrich_transactions(cleaned_frame, config)

        assert_frame_equal(first, second)

    def test_enrichment_adds_required_business_columns(self) -> None:
        cleaned_frame, _summary = clean_transactions(make_raw_frame())
        enriched = enrich_transactions(cleaned_frame, ETLConfig(random_seed=7))

        required_columns = {
            "transaction_id",
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
            "transaction_date",
        }

        self.assertTrue(required_columns.issubset(set(enriched.columns)))
        self.assertEqual(enriched["transaction_id"].nunique(), len(enriched))
        self.assertTrue(enriched["risk_score"].between(0, 100).all())
        self.assertEqual(enriched.loc[0, "transaction_date"], "2024-01-01 00:00:00")


if __name__ == "__main__":
    unittest.main()
