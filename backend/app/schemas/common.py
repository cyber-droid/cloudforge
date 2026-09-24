"""
Common Reusable Pydantic Schemas.

Provides standardized models for health probes, readiness checks, and unified error/success payloads.
"""

from typing import Any, Generic, Optional, TypeVar

from pydantic import BaseModel, ConfigDict, Field


class HealthResponse(BaseModel):
    """
    Health / Liveness probe response schema.
    Indicates whether the application process is running and accepting requests.
    """

    status: str = Field(
        default="ok", description="Process health status ('ok', 'degraded')"
    )
    environment: str = Field(
        ...,
        description="Current deployment environment (development, staging, production)",
    )
    version: str = Field(default="0.1.0", description="Backend service version")


class ReadinessResponse(BaseModel):
    """
    Readiness probe response schema.
    Indicates whether external dependencies (PostgreSQL database) are reachable and ready.
    """

    status: str = Field(
        default="ready", description="Readiness status ('ready', 'unhealthy')"
    )
    environment: str = Field(..., description="Current deployment environment")
    version: str = Field(default="0.1.0", description="Backend service version")
    database: str = Field(
        ..., description="Database connectivity status ('connected', 'error message')"
    )


class ErrorResponse(BaseModel):
    """Unified API error response payload schema."""

    success: bool = False
    error: str = Field(..., description="Machine-readable error classification")
    message: str = Field(..., description="Human-readable error description")
    details: Optional[Any] = Field(
        default=None, description="Detailed validation error list or trace context"
    )


class MessageResponse(BaseModel):
    """Generic message response."""

    message: str
    detail: Optional[str] = None


T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    """Standardized generic API wrapper for domain responses."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    success: bool = True
    data: Optional[T] = None
    message: Optional[str] = None
