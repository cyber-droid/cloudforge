"""
Certificate Repository.

Handles querying and persisting CloudForge formative training completion certificates.
"""
from datetime import datetime, timezone
from typing import List, Optional, Tuple
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.certificate import (
    Certificate,
    CertificateStatus,
    generate_certificate_number,
    generate_verification_code,
)


class CertificateRepository:
    """Repository handling Certificate entity operations."""

    async def get_by_id_or_number(
        self,
        db: AsyncSession,
        *,
        identifier: str,
    ) -> Optional[Certificate]:
        """Fetch certificate by UUID or serial certificate_number."""
        query = select(Certificate).options(
            selectinload(Certificate.training),
            selectinload(Certificate.certification),
        ).where(
            (Certificate.id == identifier) | (Certificate.certificate_number == identifier)
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_verification_code(
        self,
        db: AsyncSession,
        *,
        verification_code: str,
    ) -> Optional[Certificate]:
        """Fetch certificate by public verification code."""
        query = select(Certificate).options(
            selectinload(Certificate.training),
            selectinload(Certificate.certification),
        ).where(Certificate.verification_code == verification_code)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def get_user_certificate_for_training(
        self,
        db: AsyncSession,
        *,
        user_id: str,
        training_id: str,
    ) -> Optional[Certificate]:
        """Fetch existing certificate for user and training track."""
        query = select(Certificate).options(
            selectinload(Certificate.training),
            selectinload(Certificate.certification),
        ).where(
            Certificate.user_id == user_id,
            Certificate.training_id == training_id,
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def list_user_certificates(
        self,
        db: AsyncSession,
        *,
        user_id: str,
        skip: int = 0,
        limit: int = 50,
    ) -> Tuple[List[Certificate], int]:
        """List all certificates issued to a student."""
        query = select(Certificate).options(
            selectinload(Certificate.training),
            selectinload(Certificate.certification),
        ).where(Certificate.user_id == user_id)

        count_query = select(func.count()).select_from(query.subquery())
        total_res = await db.execute(count_query)
        total = total_res.scalar() or 0

        query = query.order_by(Certificate.issued_at.desc()).offset(skip).limit(limit)
        result = await db.execute(query)
        items = list(result.scalars().all())

        return items, total

    async def issue_certificate(
        self,
        db: AsyncSession,
        *,
        user_id: str,
        training_id: str,
        certification_id: Optional[str],
        recipient_name: str,
        training_title: str,
        prefix: str = "CF",
    ) -> Certificate:
        """Create and issue a new CloudForge certificate idempotently."""
        existing = await self.get_user_certificate_for_training(db, user_id=user_id, training_id=training_id)
        if existing:
            return existing

        cert_num = generate_certificate_number(prefix=prefix)
        verify_code = generate_verification_code()

        certificate = Certificate(
            user_id=user_id,
            training_id=training_id,
            certification_id=certification_id,
            certificate_number=cert_num,
            verification_code=verify_code,
            issued_at=datetime.now(timezone.utc),
            status=CertificateStatus.ISSUED.value,
            completion_percentage=100.0,
            recipient_name_snapshot=recipient_name,
            training_title_snapshot=training_title,
        )
        db.add(certificate)
        await db.flush()
        await db.refresh(certificate)
        return certificate


certificate_repo = CertificateRepository()
