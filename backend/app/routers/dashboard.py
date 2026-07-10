"""Dashboard API routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from backend.app.dependencies import get_repository
from backend.app.db.repository import AnalyticsRepository
from backend.app.schemas import (
    CustomerAnalyticsResponse,
    DashboardOverview,
    FraudAnalyticsResponse,
    RevenueResponse,
    TransactionAnalyticsResponse,
)


router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/overview", response_model=DashboardOverview)
def get_dashboard_overview(
    repository: AnalyticsRepository = Depends(get_repository),
) -> dict:
    return repository.dashboard_overview()


@router.get("/revenue", response_model=RevenueResponse)
def get_revenue_trend(
    limit: int = Query(default=90, ge=1, le=365),
    repository: AnalyticsRepository = Depends(get_repository),
) -> dict:
    return {"items": repository.revenue_trend(limit=limit)}


@router.get("/fraud", response_model=FraudAnalyticsResponse)
def get_fraud_analytics(
    limit: int = Query(default=90, ge=1, le=365),
    heatmap_limit: int = Query(default=500, ge=1, le=5_000),
    repository: AnalyticsRepository = Depends(get_repository),
) -> dict:
    return {
        "trend": repository.fraud_trend(limit=limit),
        "distribution": repository.fraud_distribution(),
        "histogram": repository.transaction_histogram(),
        "heatmap": repository.fraud_heatmap(limit=heatmap_limit),
    }


@router.get("/customers", response_model=CustomerAnalyticsResponse)
def get_customer_analytics(
    limit: int = Query(default=25, ge=1, le=100),
    repository: AnalyticsRepository = Depends(get_repository),
) -> dict:
    return {
        "segments": repository.customer_segments(),
        "top_customers": repository.top_customers(limit=limit),
    }


@router.get("/transactions", response_model=TransactionAnalyticsResponse)
def get_transaction_analytics(
    limit: int = Query(default=25, ge=1, le=100),
    repository: AnalyticsRepository = Depends(get_repository),
) -> dict:
    return {
        "latest_transactions": repository.latest_transactions(limit=limit),
        "high_risk_transactions": repository.high_risk_transactions(limit=limit),
        "top_merchants": repository.top_merchants(limit=limit),
        "merchant_categories": repository.merchant_categories(),
    }
