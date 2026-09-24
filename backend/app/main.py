"""
CloudForge FastAPI Application Entry Point.

Configures:
1. Application lifespan hooks (logging startup / shutdown)
2. CORS middleware for frontend communication
3. Global structured error handling (HTTP exceptions, Pydantic validation errors, unexpected crashes)
4. Health (/health) and Readiness (/ready) diagnostic probes
5. API versioning router mounting (/api/v1)

Why this architecture exists:
- Separation of Concerns: Application configuration, routing, and error formatting are cleanly decoupled.
- Observability: Structured logging ensures every lifecycle phase and error is visible.
- Consistent Error Envelope: Clients and frontend state managers receive uniform JSON error objects.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import Depends, FastAPI, Request, Response, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.v1.api import api_router
from app.api.v1.endpoints.health import health_check, readiness_check
from app.core.config import settings
from app.core.database import get_db
from app.core.logging import logger
from app.schemas.common import HealthResponse, ReadinessResponse


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan manager.
    Handles startup configuration checks and graceful connection pool shutdown.
    """
    logger.info(
        f"Initializing {settings.PROJECT_NAME} in [{settings.ENVIRONMENT}] mode..."
    )
    logger.info(
        f"Database target: {settings.POSTGRES_SERVER}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
    )
    yield
    logger.info(f"Gracefully shutting down {settings.PROJECT_NAME}...")


def create_application() -> FastAPI:
    """FastAPI Application Factory."""
    app = FastAPI(
        title=settings.PROJECT_NAME,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        docs_url=f"{settings.API_V1_STR}/docs",
        redoc_url=f"{settings.API_V1_STR}/redoc",
        description="Backend API for CloudForge - AI-Assisted Cloud & DevOps Learning Platform",
        version="0.1.0",
        lifespan=lifespan,
    )

    # --------------------------------------------------------------------------
    # 1. CORS Middleware Configuration
    # --------------------------------------------------------------------------
    # Crucial for SPA architectures (Vite + React frontend running on port 5173 / 3000)
    if settings.BACKEND_CORS_ORIGINS:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[
                str(origin).rstrip("/") for origin in settings.BACKEND_CORS_ORIGINS
            ],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # --------------------------------------------------------------------------
    # 2. Global Error Handling
    # --------------------------------------------------------------------------
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        """Uniform JSON structure for deliberate HTTP exceptions (404, 403, 401, etc.)."""
        logger.warning(
            f"HTTP {exc.status_code} on {request.method} {request.url.path}: {exc.detail}"
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error": "HTTPException",
                "message": exc.detail
                if isinstance(exc.detail, str)
                else "An HTTP error occurred",
                "details": exc.detail if not isinstance(exc.detail, str) else None,
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ):
        """Structured JSON error format for Pydantic input validation failures (422)."""
        logger.warning(
            f"Validation error on {request.method} {request.url.path}: {exc.errors()}"
        )
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "success": False,
                "error": "ValidationError",
                "message": "Input validation failed for the requested resource.",
                "details": exc.errors(),
            },
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        """Catch-all handler for unexpected internal server errors (500)."""
        logger.error(
            f"Unhandled exception on {request.method} {request.url.path}: {exc}",
            exc_info=True,
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "error": "InternalServerError",
                "message": "An unexpected server error occurred. Please try again later.",
                "details": str(exc) if settings.DEBUG else None,
            },
        )

    # --------------------------------------------------------------------------
    # 3. Root Level Health & Diagnostic Endpoints
    # --------------------------------------------------------------------------
    @app.get(
        "/health",
        response_model=HealthResponse,
        tags=["System Diagnostics"],
        summary="Root Application Health Check",
    )
    async def root_health():
        """Root-level liveness probe."""
        return await health_check()

    @app.get(
        "/ready",
        response_model=ReadinessResponse,
        tags=["System Diagnostics"],
        summary="Root Database Readiness Check",
    )
    async def root_ready(response: Response, db: AsyncSession = Depends(get_db)):
        """Root-level database readiness probe."""
        return await readiness_check(response=response, db=db)

    @app.get("/", tags=["Root"], summary="Service Information")
    async def root():
        """Root endpoint returning service identity, documentation, and diagnostics URLs."""
        return {
            "name": settings.PROJECT_NAME,
            "version": "0.1.0",
            "environment": settings.ENVIRONMENT,
            "health": "/health",
            "ready": "/ready",
            "docs": f"{settings.API_V1_STR}/docs",
        }

    # --------------------------------------------------------------------------
    # 4. Mount Versioned API Routes
    # --------------------------------------------------------------------------
    app.include_router(api_router, prefix=settings.API_V1_STR)

    return app


app = create_application()
