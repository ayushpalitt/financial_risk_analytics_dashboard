"""Machine learning API routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from backend.app.dependencies import get_repository
from backend.app.db.repository import AnalyticsRepository
from backend.app.schemas import (
    FraudDistributionPoint,
    ModelPerformanceResponse,
)


router = APIRouter(prefix="/ml", tags=["machine-learning"])


@router.get("/model-performance", response_model=ModelPerformanceResponse)
def get_model_performance(
    repository: AnalyticsRepository = Depends(get_repository),
) -> dict:
    return {"items": repository.model_performance()}


@router.get("/fraud-distribution", response_model=list[FraudDistributionPoint])
def get_fraud_distribution(
    repository: AnalyticsRepository = Depends(get_repository),
) -> list[dict]:
    return repository.fraud_distribution()
