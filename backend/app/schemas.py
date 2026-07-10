"""Pydantic response schemas for API endpoints."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class APIModel(BaseModel):
    """Base schema configured for API serialization."""

    model_config = ConfigDict(extra="ignore")


class HealthResponse(APIModel):
    status: str
    app_name: str
    version: str
    environment: str


class DashboardOverview(APIModel):
    total_transactions: int = 0
    fraud_rate: float = 0
    revenue: float = 0
    fraud_loss: float = 0
    average_transaction_value: float = 0
    high_risk_transactions: int = 0
    average_fraud_amount: float = 0


class RevenueTrendPoint(APIModel):
    metric_date: str
    transaction_count: int
    revenue: float
    fraud_loss: float
    running_total_revenue: float
    revenue_delta: float | None = None


class RevenueResponse(APIModel):
    items: list[RevenueTrendPoint]


class FraudTrendPoint(APIModel):
    metric_date: str
    transaction_count: int
    fraud_transactions: int
    fraud_loss: float
    fraud_rate: float
    rolling_7_day_fraud_rate: float


class FraudDistributionPoint(APIModel):
    class_label: int
    class_name: str
    transactions: int
    revenue: float
    fraud_loss: float
    transaction_share: float


class TransactionHistogramBucket(APIModel):
    amount_bucket: str
    transactions: int
    fraud_transactions: int
    revenue: float


class FraudHeatmapPoint(APIModel):
    iso_day_of_week: int
    hour_of_day: int
    state: str
    transactions: int
    fraud_transactions: int
    fraud_rate: float
    average_risk_score: float


class FraudAnalyticsResponse(APIModel):
    trend: list[FraudTrendPoint]
    distribution: list[FraudDistributionPoint]
    histogram: list[TransactionHistogramBucket]
    heatmap: list[FraudHeatmapPoint]


class CustomerSegmentPoint(APIModel):
    customer_segment: str
    customers: int
    transactions: int
    revenue: float
    fraud_loss: float
    fraud_transactions: int
    fraud_rate: float


class TopCustomer(APIModel):
    customer_id: str
    customer_segment: str
    city: str
    state: str
    transactions: int
    total_spend: float
    average_transaction_value: float
    fraud_loss: float
    fraud_transactions: int
    fraud_rate: float
    latest_transaction_at: str
    spend_rank: int
    fraud_exposure_rank: int


class CustomerAnalyticsResponse(APIModel):
    segments: list[CustomerSegmentPoint]
    top_customers: list[TopCustomer]


class MerchantCategoryPoint(APIModel):
    merchant_category: str
    merchants: int
    transactions: int
    revenue: float
    fraud_loss: float
    average_risk_score: float
    fraud_transactions: int
    fraud_rate: float


class TopMerchant(APIModel):
    merchant_id: str
    merchant_name: str
    merchant_category: str
    transactions: int
    revenue: float
    average_transaction_value: float
    average_risk_score: float
    fraud_loss: float
    fraud_transactions: int
    fraud_rate: float
    latest_transaction_at: str
    revenue_rank: int
    fraud_risk_rank: int


class TransactionRecord(APIModel):
    transaction_id: str
    transaction_date: str
    amount: float
    class_label: int
    is_fraud: bool
    risk_score: float
    approval_status: str
    transaction_channel: str
    customer_segment: str | None = None
    customer_id: str | None = None
    city: str | None = None
    state: str | None = None
    merchant_id: str | None = None
    merchant_name: str
    merchant_category: str
    latest_rank: int | None = None
    risk_rank: int | None = None


class TransactionAnalyticsResponse(APIModel):
    latest_transactions: list[TransactionRecord]
    high_risk_transactions: list[TransactionRecord]
    top_merchants: list[TopMerchant]
    merchant_categories: list[MerchantCategoryPoint]


class ModelPerformance(APIModel):
    model_name: str
    model_version: str
    predictions: int
    true_positive: int
    false_positive: int
    true_negative: int
    false_negative: int
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    average_fraud_probability: float
    latest_prediction_at: str | None = None


class ModelPerformanceResponse(APIModel):
    items: list[ModelPerformance]


class ExecutiveReportRequest(APIModel):
    audience: str = Field(default="executive leadership", max_length=80)
    include_recommendations: bool = True


class ExecutiveReportResponse(APIModel):
    report_markdown: str
    generated_with_ai: bool
    model: str | None = None
    inputs: dict[str, Any]
