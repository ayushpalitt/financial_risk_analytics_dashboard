"""Read repository for dashboard and analytics queries."""

from __future__ import annotations

from collections.abc import Sequence
from datetime import date, datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import text
from sqlalchemy.engine import Engine


class AnalyticsRepository:
    """Query facade over PostgreSQL analytics views."""

    def __init__(self, engine: Engine) -> None:
        self._engine = engine

    def dashboard_overview(self) -> dict[str, Any]:
        return self._fetch_one(
            """
            SELECT
                total_transactions,
                fraud_rate,
                revenue,
                fraud_loss,
                average_transaction_value,
                high_risk_transactions,
                average_fraud_amount
            FROM vw_dashboard_overview;
            """
        )

    def revenue_trend(self, limit: int = 90) -> list[dict[str, Any]]:
        return self._fetch_all(
            """
            SELECT
                metric_date,
                transaction_count,
                revenue,
                fraud_loss,
                running_total_revenue,
                revenue_delta
            FROM vw_revenue_trend_daily
            ORDER BY metric_date DESC
            LIMIT :limit;
            """,
            {"limit": limit},
        )

    def fraud_trend(self, limit: int = 90) -> list[dict[str, Any]]:
        return self._fetch_all(
            """
            SELECT
                metric_date,
                transaction_count,
                fraud_transactions,
                fraud_loss,
                fraud_rate,
                rolling_7_day_fraud_rate
            FROM vw_fraud_trend_daily
            ORDER BY metric_date DESC
            LIMIT :limit;
            """,
            {"limit": limit},
        )

    def fraud_distribution(self) -> list[dict[str, Any]]:
        return self._fetch_all(
            """
            SELECT
                class_label,
                class_name,
                transactions,
                revenue,
                fraud_loss,
                transaction_share
            FROM vw_fraud_distribution
            ORDER BY class_label;
            """
        )

    def transaction_histogram(self) -> list[dict[str, Any]]:
        return self._fetch_all(
            """
            SELECT amount_bucket, transactions, fraud_transactions, revenue
            FROM vw_transaction_histogram
            ORDER BY amount_bucket;
            """
        )

    def fraud_heatmap(self, limit: int = 500) -> list[dict[str, Any]]:
        return self._fetch_all(
            """
            SELECT
                iso_day_of_week,
                hour_of_day,
                state,
                transactions,
                fraud_transactions,
                fraud_rate,
                average_risk_score
            FROM vw_fraud_heatmap
            ORDER BY fraud_transactions DESC, transactions DESC
            LIMIT :limit;
            """,
            {"limit": limit},
        )

    def customer_segments(self) -> list[dict[str, Any]]:
        return self._fetch_all(
            """
            SELECT
                customer_segment,
                customers,
                transactions,
                revenue,
                fraud_loss,
                fraud_transactions,
                fraud_rate
            FROM vw_customer_segments
            ORDER BY revenue DESC;
            """
        )

    def top_customers(self, limit: int = 25) -> list[dict[str, Any]]:
        return self._fetch_all(
            """
            SELECT
                customer_id,
                customer_segment,
                city,
                state,
                transactions,
                total_spend,
                average_transaction_value,
                fraud_loss,
                fraud_transactions,
                fraud_rate,
                latest_transaction_at,
                spend_rank,
                fraud_exposure_rank
            FROM vw_top_customers
            ORDER BY spend_rank
            LIMIT :limit;
            """,
            {"limit": limit},
        )

    def merchant_categories(self) -> list[dict[str, Any]]:
        return self._fetch_all(
            """
            SELECT
                merchant_category,
                merchants,
                transactions,
                revenue,
                fraud_loss,
                average_risk_score,
                fraud_transactions,
                fraud_rate
            FROM vw_merchant_categories
            ORDER BY revenue DESC;
            """
        )

    def top_merchants(self, limit: int = 25) -> list[dict[str, Any]]:
        return self._fetch_all(
            """
            SELECT
                merchant_id,
                merchant_name,
                merchant_category,
                transactions,
                revenue,
                average_transaction_value,
                average_risk_score,
                fraud_loss,
                fraud_transactions,
                fraud_rate,
                latest_transaction_at,
                revenue_rank,
                fraud_risk_rank
            FROM vw_top_merchants
            ORDER BY revenue_rank
            LIMIT :limit;
            """,
            {"limit": limit},
        )

    def latest_transactions(self, limit: int = 25) -> list[dict[str, Any]]:
        return self._fetch_all(
            """
            SELECT
                latest_rank,
                transaction_id,
                transaction_date,
                amount,
                class_label,
                is_fraud,
                risk_score,
                approval_status,
                transaction_channel,
                customer_id,
                customer_segment,
                city,
                state,
                merchant_id,
                merchant_name,
                merchant_category
            FROM vw_latest_transactions
            ORDER BY latest_rank
            LIMIT :limit;
            """,
            {"limit": limit},
        )

    def high_risk_transactions(self, limit: int = 25) -> list[dict[str, Any]]:
        return self._fetch_all(
            """
            SELECT
                risk_rank,
                transaction_id,
                transaction_date,
                amount,
                class_label,
                is_fraud,
                risk_score,
                approval_status,
                transaction_channel,
                customer_segment,
                city,
                state,
                merchant_name,
                merchant_category
            FROM vw_high_risk_transactions
            ORDER BY risk_rank
            LIMIT :limit;
            """,
            {"limit": limit},
        )

    def model_performance(self) -> list[dict[str, Any]]:
        return self._fetch_all(
            """
            SELECT
                model_name,
                model_version,
                predictions,
                true_positive,
                false_positive,
                true_negative,
                false_negative,
                accuracy,
                precision,
                recall,
                f1_score,
                average_fraud_probability,
                latest_prediction_at
            FROM vw_model_performance_by_version
            ORDER BY latest_prediction_at DESC NULLS LAST;
            """
        )

    def _fetch_one(
        self,
        sql: str,
        parameters: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        with self._engine.connect() as connection:
            row = connection.execute(text(sql), parameters or {}).mappings().first()
        return normalize_mapping(row or {})

    def _fetch_all(
        self,
        sql: str,
        parameters: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        with self._engine.connect() as connection:
            rows: Sequence[Any] = (
                connection.execute(text(sql), parameters or {}).mappings().all()
            )
        return [normalize_mapping(row) for row in rows]


def normalize_mapping(row: Any) -> dict[str, Any]:
    """Convert database-native scalar types into JSON-friendly values."""

    normalized: dict[str, Any] = {}
    for key, value in dict(row).items():
        if isinstance(value, Decimal):
            normalized[key] = float(value)
        elif isinstance(value, (datetime, date)):
            normalized[key] = value.isoformat()
        else:
            normalized[key] = value
    return normalized
