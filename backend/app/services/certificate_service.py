"""
Certificate Service.

Handles formative certificate issuance upon verified training completion and public verification lookups.
"""
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.certificate import Certificate, CertificateStatus
from app.models.certification import CertificationTraining
from app.repositories.certificate_repo import certificate_repo
from app.schemas.certificate import CertificateResponse, CertificateVerifyResponse


class CertificateService:
    """Service managing CloudForge training completion certificates."""

    async def issue_certificate(
        self,
        db: AsyncSession,
        *,
        user_id: str,
        training: CertificationTraining,
        recipient_name: str,
    ) -> Certificate:
        """Issue certificate idempotently with formatted prefix."""
        # Determine prefix based on provider/code
        prefix = "CF"
        if training.certification and training.certification.code:
            prefix = f"CF-{training.certification.code.replace(' ', '')}"
        elif training.certification and training.certification.provider:
            prefix = f"CF-{training.certification.provider[:3].upper()}"

        return await certificate_repo.issue_certificate(
            db,
            user_id=user_id,
            training_id=training.id,
            certification_id=training.certification_id,
            recipient_name=recipient_name,
            training_title=training.certification.training_certificate_name if training.certification else training.title,
            prefix=prefix,
        )

    async def get_certificate(
        self,
        db: AsyncSession,
        *,
        identifier: str,
        user_id: Optional[str] = None,
    ) -> CertificateResponse:
        """Fetch certificate by UUID or certificate number."""
        cert = await certificate_repo.get_by_id_or_number(db, identifier=identifier)
        if not cert:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Certificate '{identifier}' not found.",
            )

        if user_id and cert.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to view this certificate.",
            )

        return CertificateResponse(
            id=cert.id,
            certificate_number=cert.certificate_number,
            verification_code=cert.verification_code,
            training_id=cert.training_id,
            training_title=cert.training_title_snapshot,
            certification_id=cert.certification_id,
            recipient_name=cert.recipient_name_snapshot,
            issued_at=cert.issued_at,
            status=cert.status,
            completion_percentage=cert.completion_percentage,
            verification_url=f"/certificates/verify/{cert.verification_code}",
        )

    async def list_user_certificates(
        self,
        db: AsyncSession,
        *,
        user_id: str,
    ) -> List[CertificateResponse]:
        """List all certificates issued to a student."""
        items, _ = await certificate_repo.list_user_certificates(db, user_id=user_id)
        return [
            CertificateResponse(
                id=c.id,
                certificate_number=c.certificate_number,
                verification_code=c.verification_code,
                training_id=c.training_id,
                training_title=c.training_title_snapshot,
                certification_id=c.certification_id,
                recipient_name=c.recipient_name_snapshot,
                issued_at=c.issued_at,
                status=c.status,
                completion_percentage=c.completion_percentage,
                verification_url=f"/certificates/verify/{c.verification_code}",
            )
            for c in items
        ]

    async def verify_certificate(
        self,
        db: AsyncSession,
        *,
        verification_code: str,
    ) -> CertificateVerifyResponse:
        """
        Public verification lookup.
        Strictly returns non-sensitive metadata (no email, user ID, passwords, or activity history).
        """
        cert = await certificate_repo.get_by_verification_code(db, verification_code=verification_code)
        if not cert:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Certificate verification failed. Invalid or unrecognized verification code.",
            )

        if cert.status == CertificateStatus.REVOKED.value:
            return CertificateVerifyResponse(
                is_valid=False,
                certificate_number=cert.certificate_number,
                recipient_name=cert.recipient_name_snapshot,
                training_title=cert.training_title_snapshot,
                issued_at=cert.issued_at,
                status=CertificateStatus.REVOKED.value,
                completion_percentage=cert.completion_percentage,
                message="This certificate has been revoked by CloudForge administration.",
            )

        return CertificateVerifyResponse(
            is_valid=True,
            certificate_number=cert.certificate_number,
            recipient_name=cert.recipient_name_snapshot,
            training_title=cert.training_title_snapshot,
            issued_at=cert.issued_at,
            status=cert.status,
            completion_percentage=cert.completion_percentage,
            message="Certificate is authentic and verified by CloudForge Certification Registry.",
        )


certificate_service = CertificateService()
