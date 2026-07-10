"""Static validation for PostgreSQL schema, analytics SQL, and loader contracts."""

from __future__ import annotations

import unittest
from pathlib import Path

import pandas as pd

from scripts.load_processed_to_postgres import (
    DEFAULT_PROCESSED_PATH,
    PROCESSED_REQUIRED_COLUMNS,
    TRANSACTION_COLUMNS,
    normalize_database_url,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_FILE = PROJECT_ROOT / "database" / "schema" / "001_create_core_schema.sql"
MIGRATION_FILE = (
    PROJECT_ROOT / "database" / "migrations" / "001_create_core_schema.sql"
)
ANALYTICS_DIR = PROJECT_ROOT / "database" / "sql"


class DatabaseArtifactsTest(unittest.TestCase):
    def test_core_schema_contains_required_tables_and_constraints(self) -> None:
        schema_sql = SCHEMA_FILE.read_text(encoding="utf-8")

        for table_name in [
            "customers",
            "merchants",
            "transactions",
            "fraud_predictions",
            "daily_metrics",
        ]:
            self.assertIn(f"CREATE TABLE IF NOT EXISTS {table_name}", schema_sql)

        self.assertIn("PRIMARY KEY", schema_sql)
        self.assertIn("REFERENCES customers(customer_id)", schema_sql)
        self.assertIn("REFERENCES merchants(merchant_id)", schema_sql)
        self.assertIn("REFERENCES transactions(transaction_id)", schema_sql)
        self.assertIn("CHECK", schema_sql)
        self.assertIn("CREATE INDEX IF NOT EXISTS", schema_sql)
        self.assertIn("CREATE OR REPLACE FUNCTION refresh_daily_metrics", schema_sql)

    def test_schema_and_initial_migration_match(self) -> None:
        self.assertEqual(
            SCHEMA_FILE.read_text(encoding="utf-8"),
            MIGRATION_FILE.read_text(encoding="utf-8"),
        )

    def test_analytics_sql_contains_advanced_reporting_constructs(self) -> None:
        analytics_sql = "\n".join(
            path.read_text(encoding="utf-8")
            for path in sorted(ANALYTICS_DIR.glob("*.sql"))
        )
        analytics_sql_upper = analytics_sql.upper()

        for view_name in [
            "vw_dashboard_overview",
            "vw_revenue_trend_daily",
            "vw_fraud_trend_daily",
            "vw_monthly_revenue",
            "vw_top_customers",
            "vw_top_merchants",
            "vw_customer_running_totals",
            "vw_transaction_risk_rankings",
            "vw_fraud_heatmap",
        ]:
            self.assertIn(view_name, analytics_sql)

        for materialized_view_name in [
            "mv_daily_metrics",
            "mv_monthly_revenue",
            "mv_rolling_fraud_rate",
            "mv_top_customers_90d",
            "mv_top_merchants_90d",
        ]:
            self.assertIn(materialized_view_name, analytics_sql)

        for construct in [
            "WITH ",
            " OVER (",
            "DENSE_RANK()",
            "ROW_NUMBER()",
            "ROWS BETWEEN",
            "CREATE MATERIALIZED VIEW",
            "REFRESH MATERIALIZED VIEW",
        ]:
            self.assertIn(construct, analytics_sql_upper)

    def test_sql_files_terminate_statements(self) -> None:
        for sql_file in [SCHEMA_FILE, MIGRATION_FILE, *ANALYTICS_DIR.glob("*.sql")]:
            sql = sql_file.read_text(encoding="utf-8").strip()
            self.assertTrue(sql.endswith(";"), f"{sql_file} must end with semicolon")

    def test_loader_contract_matches_processed_dataset(self) -> None:
        if not DEFAULT_PROCESSED_PATH.exists():
            self.skipTest("Processed ETL output is not present.")

        processed_header = pd.read_csv(DEFAULT_PROCESSED_PATH, nrows=0).columns
        missing = [
            column
            for column in PROCESSED_REQUIRED_COLUMNS
            if column not in processed_header
        ]

        self.assertEqual(missing, [])
        self.assertIn("class_label", TRANSACTION_COLUMNS)
        self.assertIn("time_seconds", TRANSACTION_COLUMNS)
        self.assertIn("v28", TRANSACTION_COLUMNS)

    def test_database_url_normalization_supports_sqlalchemy_driver_names(self) -> None:
        normalized = normalize_database_url(
            "postgresql+psycopg://user:pass@localhost:5432/db"
        )

        self.assertEqual(normalized, "postgresql://user:pass@localhost:5432/db")


if __name__ == "__main__":
    unittest.main()
