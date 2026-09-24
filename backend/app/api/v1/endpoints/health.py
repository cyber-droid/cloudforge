"""
Health and Readiness Diagnostic Endpoints.

Why these exist:
1. /health (Liveness):
   Allows container orchestrators (Kubernetes / Docker Compose) and load balancers to detect
   if the FastAPI process is alive and responding. If this fails, the container should be restarted.

2. /ready (Readiness):
   Verifies that the application's underlying dependencies (PostgreSQL async engine) are operational
   before routing user traffic to the pod or service instance.
"""

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.logging import logger
from app.schemas.common import HealthResponse, ReadinessResponse

router = APIRouter()


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Application Health / Liveness Check",
    description="Returns the immediate liveness status of the FastAPI backend application process.",
    tags=["System Diagnostics"],
)
@router.get(
    "/livez",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    include_in_schema=False,
)
async def health_check() -> HealthResponse:
    """
    Lightweight health check probe.
    Does not query downstream databases to minimize overhead.
    """
    return HealthResponse(
        status="ok",
        environment=settings.ENVIRONMENT,
        version="0.1.0",
    )


@router.get(
    "/ready",
    response_model=ReadinessResponse,
    status_code=status.HTTP_200_OK,
    summary="Database Readiness Check",
    description="Verifies that the PostgreSQL database connection pool is active and responding to queries.",
    responses={
        200: {"description": "Service and database are healthy and ready."},
        503: {
            "description": "Service is unhealthy or database is unreachable.",
            "model": ReadinessResponse,
        },
    },
    tags=["System Diagnostics"],
)
@router.get(
    "/healthz",
    response_model=ReadinessResponse,
    status_code=status.HTTP_200_OK,
    include_in_schema=False,
)
async def readiness_check(
    response: Response, db: AsyncSession = Depends(get_db)
) -> ReadinessResponse:
    """
    Readiness probe with live database ping.
    Executes 'SELECT 1' via the injected asynchronous SQLAlchemy session.
    """
    try:
        await db.execute(text("SELECT 1"))
        return ReadinessResponse(
            status="ready",
            environment=settings.ENVIRONMENT,
            version="0.1.0",
            database="connected",
        )
    except Exception as exc:
        logger.error(f"Readiness probe database check failed: {exc}", exc_info=True)
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return ReadinessResponse(
            status="unhealthy",
            environment=settings.ENVIRONMENT,
            version="0.1.0",
            database=f"error: {str(exc)}",
        )
