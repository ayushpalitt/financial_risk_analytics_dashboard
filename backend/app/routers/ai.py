"""AI reporting API routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from backend.app.core.config import Settings, get_settings
from backend.app.dependencies import get_repository
from backend.app.db.repository import AnalyticsRepository
from backend.app.schemas import ExecutiveReportRequest, ExecutiveReportResponse
from backend.app.services.ai_report import ExecutiveReportService


router = APIRouter(prefix="/ai", tags=["ai-reporting"])


@router.post("/report", response_model=ExecutiveReportResponse)
def generate_executive_report(
    request: ExecutiveReportRequest,
    repository: AnalyticsRepository = Depends(get_repository),
    settings: Settings = Depends(get_settings),
) -> dict:
    service = ExecutiveReportService(repository=repository, settings=settings)
    return service.generate_report(
        audience=request.audience,
        include_recommendations=request.include_recommendations,
    )


@router.get("/report", response_model=ExecutiveReportResponse)
def get_executive_report(
    repository: AnalyticsRepository = Depends(get_repository),
    settings: Settings = Depends(get_settings),
) -> dict:
    service = ExecutiveReportService(repository=repository, settings=settings)
    return service.generate_report(
        audience="executive leadership",
        include_recommendations=True,
    )
