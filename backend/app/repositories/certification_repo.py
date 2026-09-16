"""
Certification and Training Repository.

Handles database queries for certification tracks, linked training curricula, and user enrollments.
"""
from datetime import datetime, timezone
from typing import List, Optional, Tuple
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.certification import (
    Certification,
    CertificationTraining,
    EnrollmentStatus,
    UserCertificationEnrollment,
)


class CertificationRepository:
    """Repository handling Certification and Training entity operations."""

    async def get_all(
        self,
        db: AsyncSession,
        *,
        provider: Optional[str] = None,
        level: Optional[str] = None,
        category: Optional[str] = None,
        search: Optional[str] = None,
        published_only: bool = True,
        skip: int = 0,
        limit: int = 50,
    ) -> Tuple[List[Certification], int]:
        """Fetch filtered and paginated certifications catalog."""
        query = select(Certification).options(
            selectinload(Certification.trainings),
        )

        if published_only:
            query = query.where(Certification.is_published.is_(True))

        if provider and provider != "All":
            query = query.where(func.lower(Certification.provider) == provider.lower())

        if level and level != "All":
            query = query.where(func.lower(Certification.level) == level.lower())

        if category and category != "All":
            query = query.where(func.lower(Certification.category) == category.lower())

        if search:
            search_filter = f"%{search.lower()}%"
            query = query.where(
                func.lower(Certification.title).like(search_filter)
                | func.lower(Certification.description).like(search_filter)
                | func.lower(Certification.code).like(search_filter)
            )

        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total_res = await db.execute(count_query)
        total = total_res.scalar() or 0

        # Fetch page
        query = query.order_by(Certification.created_at.asc()).offset(skip).limit(limit)
        result = await db.execute(query)
        items = list(result.scalars().all())

        return items, total

    async def get_by_id_or_slug(
        self,
        db: AsyncSession,
        *,
        identifier: str,
        published_only: bool = True,
    ) -> Optional[Certification]:
        """Fetch single certification by UUID or unique slug."""
        query = select(Certification).options(
            selectinload(Certification.trainings).selectinload(CertificationTraining.course),
            selectinload(Certification.questions),
        ).where(
            (Certification.id == identifier) | (Certification.slug == identifier)
        )

        if published_only:
            query = query.where(Certification.is_published.is_(True))

        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def get_training_by_id_or_slug(
        self,
        db: AsyncSession,
        *,
        identifier: str,
        published_only: bool = True,
    ) -> Optional[CertificationTraining]:
        """Fetch single training program by UUID or slug."""
        query = select(CertificationTraining).options(
            selectinload(CertificationTraining.certification),
            selectinload(CertificationTraining.course),
        ).where(
            (CertificationTraining.id == identifier) | (CertificationTraining.slug == identifier)
        )

        if published_only:
            query = query.where(CertificationTraining.is_published.is_(True))

        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def get_trainings_for_cert(
        self,
        db: AsyncSession,
        *,
        certification_id: str,
        published_only: bool = True,
    ) -> List[CertificationTraining]:
        """Fetch all training programs belonging to a certification."""
        query = select(CertificationTraining).options(
            selectinload(CertificationTraining.course),
        ).where(CertificationTraining.certification_id == certification_id)

        if published_only:
            query = query.where(CertificationTraining.is_published.is_(True))

        result = await db.execute(query.order_by(CertificationTraining.created_at.asc()))
        return list(result.scalars().all())

    async def get_user_enrollment(
        self,
        db: AsyncSession,
        *,
        user_id: str,
        training_id: str,
    ) -> Optional[UserCertificationEnrollment]:
        """Fetch enrollment record for a specific user and training track."""
        query = select(UserCertificationEnrollment).where(
            UserCertificationEnrollment.user_id == user_id,
            UserCertificationEnrollment.training_id == training_id,
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def get_user_enrollments_for_cert(
        self,
        db: AsyncSession,
        *,
        user_id: str,
        certification_id: str,
    ) -> List[UserCertificationEnrollment]:
        """Fetch all user enrollments under a certification."""
        query = select(UserCertificationEnrollment).where(
            UserCertificationEnrollment.user_id == user_id,
            UserCertificationEnrollment.certification_id == certification_id,
        )
        result = await db.execute(query)
        return list(result.scalars().all())

    async def enroll_user_in_training(
        self,
        db: AsyncSession,
        *,
        user_id: str,
        certification_id: str,
        training_id: str,
    ) -> UserCertificationEnrollment:
        """Enroll user in training track idempotently."""
        existing = await self.get_user_enrollment(db, user_id=user_id, training_id=training_id)
        if existing:
            return existing

        enrollment = UserCertificationEnrollment(
            user_id=user_id,
            certification_id=certification_id,
            training_id=training_id,
            status=EnrollmentStatus.ENROLLED.value,
            enrolled_at=datetime.now(timezone.utc),
            started_at=datetime.now(timezone.utc),
        )
        db.add(enrollment)
        await db.flush()
        await db.refresh(enrollment)
        return enrollment

    async def update_enrollment_status(
        self,
        db: AsyncSession,
        *,
        enrollment: UserCertificationEnrollment,
        status: str,
        completed_at: Optional[datetime] = None,
    ) -> UserCertificationEnrollment:
        """Update student training enrollment status."""
        enrollment.status = status
        if completed_at:
            enrollment.completed_at = completed_at
        elif status == EnrollmentStatus.COMPLETED.value and not enrollment.completed_at:
            enrollment.completed_at = datetime.now(timezone.utc)

        await db.flush()
        await db.refresh(enrollment)
        return enrollment


certification_repo = CertificationRepository()
