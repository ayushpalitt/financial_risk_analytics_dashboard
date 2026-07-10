"""Tests for FastAPI backend routes using dependency overrides."""

from __future__ import annotations

import unittest

from fastapi.testclient import TestClient

from backend.app.core.config import Settings
from backend.app.dependencies import get_repository
from backend.app.main import app
from backend.app.routers.ai import get_settings


class FakeRepository:
    def dashboard_overview(self) -> dict:
        return {
            "total_transactions": 1000,
            "fraud_rate": 0.012,
            "revenue": 125000.50,
            "fraud_loss": 2100.25,
            "average_transaction_value": 125.0,
            "high_risk_transactions": 18,
            "average_fraud_amount": 175.0,
        }

    def revenue_trend(self, limit: int = 90) -> list[dict]:
        return [
            {
                "metric_date": "2024-01-02",
                "transaction_count": 500,
                "revenue": 62500.25,
                "fraud_loss": 1000.0,
                "running_total_revenue": 125000.5,
                "revenue_delta": 100.0,
            }
        ][:limit]

    def fraud_trend(self, limit: int = 90) -> list[dict]:
        return [
            {
                "metric_date": "2024-01-02",
                "transaction_count": 500,
                "fraud_transactions": 6,
                "fraud_loss": 1000.0,
                "fraud_rate": 0.012,
                "rolling_7_day_fraud_rate": 0.011,
            }
        ][:limit]

    def fraud_distribution(self) -> list[dict]:
        return [
            {
                "class_label": 0,
                "class_name": "Genuine",
                "transactions": 988,
                "revenue": 122900.25,
                "fraud_loss": 0.0,
                "transaction_share": 0.988,
            },
            {
                "class_label": 1,
                "class_name": "Fraud",
                "transactions": 12,
                "revenue": 2100.25,
                "fraud_loss": 2100.25,
                "transaction_share": 0.012,
            },
        ]

    def transaction_histogram(self) -> list[dict]:
        return [
            {
                "amount_bucket": "0100-0249",
                "transactions": 100,
                "fraud_transactions": 3,
                "revenue": 15000.0,
            }
        ]

    def fraud_heatmap(self, limit: int = 500) -> list[dict]:
        return [
            {
                "iso_day_of_week": 2,
                "hour_of_day": 14,
                "state": "NY",
                "transactions": 100,
                "fraud_transactions": 3,
                "fraud_rate": 0.03,
                "average_risk_score": 42.5,
            }
        ][:limit]

    def customer_segments(self) -> list[dict]:
        return [
            {
                "customer_segment": "Mass Market",
                "customers": 100,
                "transactions": 700,
                "revenue": 80000.0,
                "fraud_loss": 1000.0,
                "fraud_transactions": 6,
                "fraud_rate": 0.008571,
            }
        ]

    def top_customers(self, limit: int = 25) -> list[dict]:
        return [
            {
                "customer_id": "CUST-0000001",
                "customer_segment": "Premium",
                "city": "New York",
                "state": "NY",
                "transactions": 20,
                "total_spend": 5000.0,
                "average_transaction_value": 250.0,
                "fraud_loss": 100.0,
                "fraud_transactions": 1,
                "fraud_rate": 0.05,
                "latest_transaction_at": "2024-01-02T12:00:00",
                "spend_rank": 1,
                "fraud_exposure_rank": 1,
            }
        ][:limit]

    def merchant_categories(self) -> list[dict]:
        return [
            {
                "merchant_category": "E-commerce",
                "merchants": 10,
                "transactions": 250,
                "revenue": 40000.0,
                "fraud_loss": 750.0,
                "average_risk_score": 38.4,
                "fraud_transactions": 4,
                "fraud_rate": 0.016,
            }
        ]

    def top_merchants(self, limit: int = 25) -> list[dict]:
        return [
            {
                "merchant_id": "MRCH-000001",
                "merchant_name": "Aster Online Marketplace #001",
                "merchant_category": "E-commerce",
                "transactions": 80,
                "revenue": 20000.0,
                "average_transaction_value": 250.0,
                "average_risk_score": 39.0,
                "fraud_loss": 500.0,
                "fraud_transactions": 2,
                "fraud_rate": 0.025,
                "latest_transaction_at": "2024-01-02T11:00:00",
                "revenue_rank": 1,
                "fraud_risk_rank": 1,
            }
        ][:limit]

    def latest_transactions(self, limit: int = 25) -> list[dict]:
        return [
            {
                "latest_rank": 1,
                "transaction_id": "TXN-1",
                "transaction_date": "2024-01-02T12:00:00",
                "amount": 125.0,
                "class_label": 0,
                "is_fraud": False,
                "risk_score": 24.2,
                "approval_status": "Approved",
                "transaction_channel": "E-commerce",
                "customer_id": "CUST-0000001",
                "customer_segment": "Premium",
                "city": "New York",
                "state": "NY",
                "merchant_id": "MRCH-000001",
                "merchant_name": "Aster Online Marketplace #001",
                "merchant_category": "E-commerce",
            }
        ][:limit]

    def high_risk_transactions(self, limit: int = 25) -> list[dict]:
        return [
            {
                "risk_rank": 1,
                "transaction_id": "TXN-2",
                "transaction_date": "2024-01-02T13:00:00",
                "amount": 500.0,
                "class_label": 1,
                "is_fraud": True,
                "risk_score": 94.2,
                "approval_status": "Declined",
                "transaction_channel": "ATM",
                "customer_segment": "Premium",
                "city": "New York",
                "state": "NY",
                "merchant_name": "Aster Online Marketplace #001",
                "merchant_category": "E-commerce",
            }
        ][:limit]

    def model_performance(self) -> list[dict]:
        return [
            {
                "model_name": "fraud_detection_classifier",
                "model_version": "1.0.0",
                "predictions": 1000,
                "true_positive": 10,
                "false_positive": 1,
                "true_negative": 987,
                "false_negative": 2,
                "accuracy": 0.997,
                "precision": 0.909,
                "recall": 0.833,
                "f1_score": 0.87,
                "average_fraud_probability": 0.02,
                "latest_prediction_at": "2024-01-02T14:00:00",
            }
        ]


def fake_settings() -> Settings:
    return Settings(
        openai_api_key="",
        ai_reports_enabled=True,
        openai_model="gpt-5.5",
    )


class BackendAPITest(unittest.TestCase):
    def setUp(self) -> None:
        app.dependency_overrides[get_repository] = lambda: FakeRepository()
        app.dependency_overrides[get_settings] = fake_settings
        self.client = TestClient(app)

    def tearDown(self) -> None:
        app.dependency_overrides.clear()

    def test_health_endpoint(self) -> None:
        response = self.client.get("/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")

    def test_dashboard_overview_endpoint(self) -> None:
        response = self.client.get("/dashboard/overview")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["total_transactions"], 1000)
        self.assertEqual(response.json()["high_risk_transactions"], 18)

    def test_fraud_endpoint_returns_composite_payload(self) -> None:
        response = self.client.get("/dashboard/fraud?limit=1&heatmap_limit=1")

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(len(body["trend"]), 1)
        self.assertEqual(len(body["distribution"]), 2)
        self.assertEqual(len(body["histogram"]), 1)
        self.assertEqual(len(body["heatmap"]), 1)

    def test_transactions_endpoint_returns_tables(self) -> None:
        response = self.client.get("/dashboard/transactions?limit=1")

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["latest_transactions"][0]["transaction_id"], "TXN-1")
        self.assertEqual(body["high_risk_transactions"][0]["transaction_id"], "TXN-2")
        self.assertEqual(body["top_merchants"][0]["merchant_id"], "MRCH-000001")

    def test_model_performance_endpoint(self) -> None:
        response = self.client.get("/ml/model-performance")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["items"][0]["model_name"], "fraud_detection_classifier")

    def test_ai_report_falls_back_without_openai_key(self) -> None:
        response = self.client.post(
            "/ai/report",
            json={"audience": "risk committee", "include_recommendations": True},
        )

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertFalse(body["generated_with_ai"])
        self.assertIn("Executive Risk Report", body["report_markdown"])
        self.assertIn("Recommendations", body["report_markdown"])


if __name__ == "__main__":
    unittest.main()
