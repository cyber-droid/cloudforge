"""
Certification Training Service.

Manages training track enrollment, real lesson progress derivation from courses, and training completion verification.
"""

from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.certification import EnrollmentStatus
from app.models.progress import LessonProgressStatus
from app.repositories.certificate_repo import certificate_repo
from app.repositories.certification_repo import certification_repo
from app.repositories.course_repo import course_repo, enrollment_repo
from app.repositories.progress_repo import progress_repo
from app.repositories.user_repo import user_repo
from app.schemas.certificate import CertificateResponse
from app.schemas.certification import (
    TrainingDetailResponse,
    TrainingProgressResponse,
    TrainingSummaryResponse,
)
from app.services.certificate_service import certificate_service


class TrainingService:
    """Service managing training programs, progress evaluation, and verified completion."""

    async def get_training_detail(
        self,
        db: AsyncSession,
        *,
        identifier: str,
        user_id: Optional[str] = None,
    ) -> TrainingDetailResponse:
        """Fetch details of a training track with linked course information."""
        training = await certification_repo.get_training_by_id_or_slug(
            db, identifier=identifier
        )
        if not training:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Training track '{identifier}' not found.",
            )

        course_title = training.course.title if training.course else None
        course_slug = training.course.slug if training.course else None

        total_lessons = 0
        completed_lessons = 0
        prog = 0.0
        st = "not_enrolled"

        if training.course_id:
            course = await course_repo.get_by_id_or_slug(
                db, identifier=training.course_id
            )
            if course:
                pub_modules = [m for m in (course.modules or []) if m.published]
                pub_lessons = [
                    lesson for m in pub_modules for lesson in (m.lessons or []) if lesson.published
                ]
                total_lessons = len(pub_lessons)

                if user_id:
                    enr = await certification_repo.get_user_enrollment(
                        db, user_id=user_id, training_id=training.id
                    )
                    if enr:
                        st = enr.status
                    progs = await progress_repo.get_course_lesson_progress(
                        db, user_id=user_id, course_id=training.course_id
                    )
                    completed_lesson_ids = {
                        p.lesson_id
                        for p in progs
                        if (
                            getattr(p, "completed", False)
                            or getattr(p, "status", None) == "completed"
                            or getattr(p, "status", None)
                            == LessonProgressStatus.COMPLETED.value
                        )
                    }
                    completed_lessons = len(
                        [lesson for lesson in pub_lessons if lesson.id in completed_lesson_ids]
                    )
                    if total_lessons > 0:
                        prog = round((completed_lessons / total_lessons) * 100.0, 1)

        return TrainingDetailResponse(
            id=training.id,
            certification_id=training.certification_id,
            title=training.title,
            slug=training.slug,
            description=training.description,
            level=training.level,
            estimated_hours=training.estimated_hours,
            course_id=training.course_id,
            course_title=course_title,
            course_slug=course_slug,
            modules=training.modules or [],
            is_published=training.is_published,
            progress_percentage=prog,
            status=st,
            total_lessons=total_lessons,
            completed_lessons=completed_lessons,
            created_at=training.created_at,
        )

    async def enroll_training(
        self,
        db: AsyncSession,
        *,
        user_id: str,
        identifier: str,
    ) -> TrainingSummaryResponse:
        """Enroll user in certification training track and auto-enroll in linked course."""
        training = await certification_repo.get_training_by_id_or_slug(
            db, identifier=identifier
        )
        if not training:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Training track '{identifier}' not found.",
            )

        enrollment = await certification_repo.enroll_user_in_training(
            db,
            user_id=user_id,
            certification_id=training.certification_id,
            training_id=training.id,
        )

        # Also enroll in mapped course if present
        if training.course_id:
            c_enr = await enrollment_repo.get_by_user_and_course(
                db, user_id=user_id, course_id=training.course_id
            )
            if not c_enr:
                await enrollment_repo.create(
                    db, user_id=user_id, course_id=training.course_id
                )

        prog_data = await self.get_training_progress(
            db, user_id=user_id, identifier=training.id
        )

        return TrainingSummaryResponse(
            id=training.id,
            certification_id=training.certification_id,
            title=training.title,
            slug=training.slug,
            description=training.description,
            level=training.level,
            estimated_hours=training.estimated_hours,
            course_id=training.course_id,
            modules=training.modules or [],
            is_published=training.is_published,
            progress_percentage=prog_data.progress_percentage,
            status=enrollment.status,
            created_at=training.created_at,
        )

    async def get_training_progress(
        self,
        db: AsyncSession,
        *,
        user_id: str,
        identifier: str,
    ) -> TrainingProgressResponse:
        """Calculate real progress for training from underlying lesson progress."""
        training = await certification_repo.get_training_by_id_or_slug(
            db, identifier=identifier
        )
        if not training:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Training track '{identifier}' not found.",
            )

        enrollment = await certification_repo.get_user_enrollment(
            db, user_id=user_id, training_id=training.id
        )
        current_status = enrollment.status if enrollment else "not_enrolled"

        total_lessons = 0
        completed_lessons = 0
        total_modules = 0
        completed_modules = 0
        prog_pct = 0.0

        if training.course_id:
            course = await course_repo.get_by_id_or_slug(
                db, identifier=training.course_id
            )
            if course:
                pub_modules = [m for m in (course.modules or []) if m.published]
                pub_lessons = [
                    lesson for m in pub_modules for lesson in (m.lessons or []) if lesson.published
                ]
                total_modules = len(pub_modules)
                total_lessons = len(pub_lessons)

                lesson_progress_records = (
                    await progress_repo.get_course_lesson_progress(
                        db, user_id=user_id, course_id=training.course_id
                    )
                )
                completed_lesson_ids = {
                    p.lesson_id
                    for p in lesson_progress_records
                    if (
                        getattr(p, "completed", False)
                        or getattr(p, "status", None) == "completed"
                        or getattr(p, "status", None)
                        == LessonProgressStatus.COMPLETED.value
                    )
                }
                completed_lessons = len(
                    [lesson for lesson in pub_lessons if lesson.id in completed_lesson_ids]
                )

                # Check completed modules
                for mod in pub_modules:
                    mod_lessons = [lesson for lesson in (mod.lessons or []) if lesson.published]
                    if mod_lessons and all(
                        lesson.id in completed_lesson_ids for lesson in mod_lessons
                    ):
                        completed_modules += 1

                if total_lessons > 0:
                    prog_pct = round((completed_lessons / total_lessons) * 100.0, 1)

        is_eligible = total_lessons > 0 and completed_lessons >= total_lessons
        existing_cert = await certificate_repo.get_user_certificate_for_training(
            db, user_id=user_id, training_id=training.id
        )

        return TrainingProgressResponse(
            training_id=training.id,
            certification_id=training.certification_id,
            status=current_status,
            progress_percentage=prog_pct,
            completed_lessons=completed_lessons,
            total_lessons=total_lessons,
            completed_modules=completed_modules,
            total_modules=total_modules,
            is_eligible_for_certificate=is_eligible,
            certificate_id=existing_cert.id if existing_cert else None,
        )

    async def complete_training(
        self,
        db: AsyncSession,
        *,
        user_id: str,
        identifier: str,
    ) -> CertificateResponse:
        """
        Verify all required content is completed, mark training complete, and issue certificate idempotently.
        """
        training = await certification_repo.get_training_by_id_or_slug(
            db, identifier=identifier
        )
        if not training:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Training track '{identifier}' not found.",
            )

        prog_data = await self.get_training_progress(
            db, user_id=user_id, identifier=training.id
        )
        if not prog_data.is_eligible_for_certificate:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Cannot complete training. {prog_data.completed_lessons} of {prog_data.total_lessons} "
                    "required lessons completed."
                ),
            )

        enrollment = await certification_repo.get_user_enrollment(
            db, user_id=user_id, training_id=training.id
        )
        if not enrollment:
            enrollment = await certification_repo.enroll_user_in_training(
                db,
                user_id=user_id,
                certification_id=training.certification_id,
                training_id=training.id,
            )

        await certification_repo.update_enrollment_status(
            db,
            enrollment=enrollment,
            status=EnrollmentStatus.COMPLETED.value,
        )

        # Issue CloudForge certificate idempotently
        user = await user_repo.get_by_id(db, id=user_id)
        recipient_name = user.name if user else "CloudForge Engineer"
        cert = await certificate_service.issue_certificate(
            db,
            user_id=user_id,
            training=training,
            recipient_name=recipient_name,
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


training_service = TrainingService()
