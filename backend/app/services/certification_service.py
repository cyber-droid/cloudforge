"""
Certification Service.

Coordinates certification catalog browsing, exam domain structures, and authentic readiness calculation.
"""
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.certification import Certification
from app.repositories.certification_repo import certification_repo
from app.repositories.course_repo import enrollment_repo
from app.repositories.practice_repo import practice_repo
from app.schemas.certification import (
    CertificationDetailResponse,
    CertificationListResponse,
    CertificationSummaryResponse,
    TrainingSummaryResponse,
)


class CertificationService:
    """Service handling certification listings and preparation readiness calculations."""

    async def list_certifications(
        self,
        db: AsyncSession,
        *,
        user_id: Optional[str] = None,
        provider: Optional[str] = None,
        level: Optional[str] = None,
        category: Optional[str] = None,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> CertificationListResponse:
        """List certifications with filter criteria and readiness score if user is authenticated."""
        items, total = await certification_repo.get_all(
            db,
            provider=provider,
            level=level,
            category=category,
            search=search,
            skip=skip,
            limit=limit,
        )

        summaries: List[CertificationSummaryResponse] = []
        for cert in items:
            readiness = 0.0
            if user_id:
                readiness = await self.calculate_readiness(db, user_id=user_id, certification=cert)

            summaries.append(
                CertificationSummaryResponse(
                    id=cert.id,
                    code=cert.code,
                    title=cert.title,
                    name=cert.name,
                    slug=cert.slug,
                    provider=cert.provider,
                    vendor=cert.vendor,
                    level=cert.level,
                    category=cert.category,
                    badge_icon=cert.badge_icon,
                    duration=cert.duration,
                    training_title=cert.training_title,
                    description=cert.description,
                    training_certificate_name=cert.training_certificate_name,
                    official_url=cert.official_url,
                    is_official_certification=cert.is_official_certification,
                    is_published=cert.is_published,
                    exam_domains=cert.exam_domains or cert.domains or [],
                    domains=cert.exam_domains or cert.domains or [],
                    skills_gained=cert.skills_gained or [],
                    practice_questions_count=cert.practice_questions_count,
                    mock_exams_count=cert.mock_exams_count,
                    progress=readiness,
                    created_at=cert.created_at,
                )
            )

        return CertificationListResponse(items=summaries, total=total)

    async def get_certification_detail(
        self,
        db: AsyncSession,
        *,
        identifier: str,
        user_id: Optional[str] = None,
    ) -> CertificationDetailResponse:
        """Fetch full certification detail with training tracks and readiness score."""
        cert = await certification_repo.get_by_id_or_slug(db, identifier=identifier)
        if not cert:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Certification '{identifier}' not found.",
            )

        readiness = 0.0
        if user_id:
            readiness = await self.calculate_readiness(db, user_id=user_id, certification=cert)

        # Build training responses with user status if available
        trainings_summary: List[TrainingSummaryResponse] = []
        for tr in (cert.trainings or []):
            prog = 0.0
            st = "not_enrolled"
            if user_id:
                enr = await certification_repo.get_user_enrollment(db, user_id=user_id, training_id=tr.id)
                if enr:
                    st = enr.status
                    if tr.course_id:
                        c_enr = await enrollment_repo.get_by_user_and_course(db, user_id=user_id, course_id=tr.course_id)
                        if c_enr:
                            prog = c_enr.progress_percentage

            trainings_summary.append(
                TrainingSummaryResponse(
                    id=tr.id,
                    certification_id=tr.certification_id,
                    title=tr.title,
                    slug=tr.slug,
                    description=tr.description,
                    level=tr.level,
                    estimated_hours=tr.estimated_hours,
                    course_id=tr.course_id,
                    modules=tr.modules or [],
                    is_published=tr.is_published,
                    progress_percentage=prog,
                    status=st,
                    created_at=tr.created_at,
                )
            )

        return CertificationDetailResponse(
            id=cert.id,
            code=cert.code,
            title=cert.title,
            name=cert.name,
            slug=cert.slug,
            provider=cert.provider,
            vendor=cert.vendor,
            level=cert.level,
            category=cert.category,
            badge_icon=cert.badge_icon,
            duration=cert.duration,
            training_title=cert.training_title,
            description=cert.description,
            training_certificate_name=cert.training_certificate_name,
            official_url=cert.official_url,
            is_official_certification=cert.is_official_certification,
            is_published=cert.is_published,
            exam_domains=cert.exam_domains or cert.domains or [],
            domains=cert.exam_domains or cert.domains or [],
            skills_gained=cert.skills_gained or [],
            practice_questions_count=cert.practice_questions_count,
            mock_exams_count=cert.mock_exams_count,
            progress=readiness,
            trainings=trainings_summary,
            created_at=cert.created_at,
        )

    async def calculate_readiness(
        self,
        db: AsyncSession,
        *,
        user_id: str,
        certification: Certification,
    ) -> float:
        """
        Calculate realistic preparation readiness score (0-100%).
        Weights:
        - 60% based on linked curriculum course completion
        - 40% based on mock exam passing scores
        """
        course_component = 0.0
        trainings = certification.trainings or []
        if trainings:
            total_course_prog = 0.0
            counted_trainings = 0
            for tr in trainings:
                if tr.course_id:
                    c_enr = await enrollment_repo.get_by_user_and_course(db, user_id=user_id, course_id=tr.course_id)
                    if c_enr:
                        total_course_prog += c_enr.progress_percentage
                    counted_trainings += 1
            if counted_trainings > 0:
                course_component = (total_course_prog / counted_trainings) * 0.60

        # Exam component
        exam_component = 0.0
        attempts, _ = await practice_repo.list_user_attempts(
            db,
            user_id=user_id,
            certification_id=certification.id,
            limit=10,
        )
        if attempts:
            best_score = max((a.percentage for a in attempts), default=0.0)
            exam_component = (best_score / 100.0) * 40.0

        total_readiness = course_component + exam_component
        return min(100.0, max(0.0, round(total_readiness, 1)))


certification_service = CertificationService()
