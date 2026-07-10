"""FastAPI application entry point."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from backend.app.core.config import get_settings
from backend.app.routers import ai, dashboard, ml
from backend.app.schemas import HealthResponse


def create_app() -> FastAPI:
    settings = get_settings()
    application = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description=(
            "Enterprise financial risk analytics API for dashboard, "
            "fraud analytics, model performance, and executive reporting."
        ),
    )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=list(settings.cors_origins),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    application.include_router(dashboard.router)
    application.include_router(ml.router)
    application.include_router(ai.router)

    @application.exception_handler(SQLAlchemyError)
    def database_exception_handler(_request, exc: SQLAlchemyError) -> JSONResponse:
        return JSONResponse(
            status_code=503,
            content={
                "detail": "Database service is unavailable.",
                "error": exc.__class__.__name__,
            },
        )

    @application.get("/health", response_model=HealthResponse, tags=["health"])
    def health() -> dict:
        return {
            "status": "ok",
            "app_name": settings.app_name,
            "version": settings.app_version,
            "environment": settings.environment,
        }

    return application


app = create_app()
