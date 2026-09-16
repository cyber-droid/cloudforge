"""
Certificate Endpoints.
"""
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.certificate import CertificateResponse, CertificateVerifyResponse
from app.services.certificate_service import certificate_service

router = APIRouter()


@router.get(
    "",
    response_model=List[CertificateResponse],
    status_code=status.HTTP_200_OK,
    summary="List User Certificates",
    description="Fetch all formative training completion certificates earned by the authenticated student.",
)
async def list_my_certificates(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[CertificateResponse]:
    """List certificates for student."""
    return await certificate_service.list_user_certificates(
        db,
        user_id=current_user.id,
    )


@router.get(
    "/verify/{verification_code}",
    response_model=CertificateVerifyResponse,
    status_code=status.HTTP_200_OK,
    summary="Public Certificate Verification",
    description="Publicly verifies authenticity of a CloudForge certificate by verification code. Strictly omits private student data.",
)
async def verify_certificate(
    verification_code: str,
    db: AsyncSession = Depends(get_db),
) -> CertificateVerifyResponse:
    """Verify certificate publicly."""
    return await certificate_service.verify_certificate(
        db,
        verification_code=verification_code,
    )


@router.get(
    "/{identifier}",
    response_model=CertificateResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Certificate Details",
    description="Fetch certificate details by certificate UUID or serial certificate number.",
)
async def get_certificate(
    identifier: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> CertificateResponse:
    """Get single certificate."""
    return await certificate_service.get_certificate(
        db,
        identifier=identifier,
        user_id=current_user.id,
    )
