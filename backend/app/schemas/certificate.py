"""
CloudForge Certificate Pydantic v2 Schemas.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class CertificateResponse(BaseModel):
    """Student view of an earned CloudForge training certificate."""
    model_config = ConfigDict(from_attributes=True)

    id: str
    certificate_number: str
    verification_code: str
    training_id: str
    training_title: str
    certification_id: Optional[str] = None
    recipient_name: str
    issued_at: datetime
    status: str
    completion_percentage: float
    verification_url: str


class CertificateVerifyResponse(BaseModel):
    """Public verification payload (strictly omits private student data)."""
    model_config = ConfigDict(from_attributes=True)

    is_valid: bool
    certificate_number: str
    recipient_name: str
    training_title: str
    issued_at: datetime
    status: str
    completion_percentage: float
    message: str
