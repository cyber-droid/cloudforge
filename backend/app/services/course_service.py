"""
Course and Curriculum Business Service.

Coordinates course catalogs, syllabus tree transformations, and student enrollment lifecycles.
"""

from math import ceil
from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import logger
from app.models.course import Course
from app.repositories.course_repo import (
    course_repo,
    enrollment_repo,
    lesson_repo,
    module_repo,
)
from app.schemas.course import (
    CourseCurriculumResponse,
    CourseDetailResponse,
    CourseEnrollmentResponse,
    CourseListResponse,
    CourseSummaryResponse,
    LessonDetailResponse,
    LessonResourceResponse,
    LessonSummaryResponse,
    ModuleDetailResponse,
    ModuleSummaryResponse,
)


class CourseService:
    """Service handling Course, Module, Lesson, and Enrollment operations."""

    def _to_course_summary(self, course: Course) -> CourseSummaryResponse:
        """Helper to transform Course ORM entity to summary schema with computed counts."""
        modules = course.modules or []
        lessons_count = sum(len(m.lessons or []) for m in modules)

        return CourseSummaryResponse(
            id=course.id,
            slug=course.slug,
            title=course.title,
            description=course.description,
            category=course.category,
            difficulty=course.difficulty,
            duration_minutes=course.duration_minutes,
            thumbnail_url=course.thumbnail_url,
            rating=course.rating,
            students_count=course.students_count,
            certificate_available=course.certificate_available,
            published=course.published,
            technologies=course.technologies or [],
            learning_outcomes=course.learning_outcomes or [],
            instructor_name=course.instructor_name,
            instructor_role=course.instructor_role,
            instructor_avatar=course.instructor_avatar,
            instructor_verified=course.instructor_verified,
            modules_count=len(modules),
            lessons_count=lessons_count,
            created_at=course.created_at,
        )

    def _to_course_detail(self, course: Course) -> CourseDetailResponse:
        """Helper to transform Course ORM entity into full detail schema with nested syllabus."""
        summary = self._to_course_summary(course)

        module_responses: List[ModuleSummaryResponse] = []
        for mod in course.modules or []:
            lesson_summaries = [
                LessonSummaryResponse(
                    id=les.id,
                    title=les.title,
                    slug=les.slug,
                    lesson_type=les.lesson_type,
                    estimated_minutes=les.estimated_minutes,
                    order_index=les.order_index,
                    published=les.published,
                )
                for les in (mod.lessons or [])
            ]
            module_responses.append(
                ModuleSummaryResponse(
                    id=mod.id,
                    course_id=mod.course_id,
                    module_number=mod.module_number,
                    title=mod.title,
                    description=mod.description,
                    order_index=mod.order_index,
                    published=mod.published,
                    lessons_count=len(lesson_summaries),
                    lessons=lesson_summaries,
                )
            )

        return CourseDetailResponse(
            **summary.model_dump(),
            long_description=course.long_description,
            modules=module_responses,
        )

    async def list_courses(
        self,
        db: AsyncSession,
        *,
        page: int = 1,
        page_size: int = 12,
        category: Optional[str] = None,
        difficulty: Optional[str] = None,
        technology: Optional[str] = None,
        search: Optional[str] = None,
        certificate_available: Optional[bool] = None,
    ) -> CourseListResponse:
        """Query and paginate courses with SQL filters."""
        courses, total = await course_repo.get_paginated(
            db,
            page=page,
            page_size=page_size,
            category=category,
            difficulty=difficulty,
            technology=technology,
            search=search,
            certificate_available=certificate_available,
        )

        items = [self._to_course_summary(c) for c in courses]
        total_pages = ceil(total / page_size) if total > 0 else 1

        return CourseListResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    async def get_course(
        self, db: AsyncSession, *, identifier: str
    ) -> CourseDetailResponse:
        """Fetch course details by UUID or slug."""
        course = await course_repo.get_by_id_or_slug(db, identifier=identifier)
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Course '{identifier}' not found.",
            )
        return self._to_course_detail(course)

    async def get_curriculum(
        self, db: AsyncSession, *, course_id: str
    ) -> CourseCurriculumResponse:
        """Fetch full ordered syllabus tree for a course."""
        course = await course_repo.get_by_id_or_slug(db, identifier=course_id)
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Course '{course_id}' not found.",
            )
        detail = self._to_course_detail(course)
        return CourseCurriculumResponse(
            course_id=course.id,
            course_title=course.title,
            course_slug=course.slug,
            modules=detail.modules,
        )

    async def get_module(
        self, db: AsyncSession, *, course_id: str, module_id: str
    ) -> ModuleDetailResponse:
        """Fetch a specific module with full lesson details."""
        module = await module_repo.get_by_id(db, module_id=module_id)
        if not module or (
            module.course_id != course_id and module.course.slug != course_id
        ):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Module not found for this course.",
            )

        lesson_details = [
            LessonDetailResponse(
                id=lesson.id,
                module_id=lesson.module_id,
                title=lesson.title,
                slug=lesson.slug,
                description=lesson.description,
                content=lesson.content,
                lesson_type=lesson.lesson_type,
                estimated_minutes=lesson.estimated_minutes,
                order_index=lesson.order_index,
                video_url=lesson.video_url,
                published=lesson.published,
                resources=[
                    LessonResourceResponse.model_validate(r)
                    for r in (lesson.resources or [])
                ],
                created_at=lesson.created_at,
                updated_at=lesson.updated_at,
            )
            for lesson in (module.lessons or [])
        ]

        return ModuleDetailResponse(
            id=module.id,
            course_id=module.course_id,
            module_number=module.module_number,
            title=module.title,
            description=module.description,
            order_index=module.order_index,
            published=module.published,
            lessons=lesson_details,
        )

    async def get_lesson(
        self, db: AsyncSession, *, course_id: str, lesson_id: str
    ) -> LessonDetailResponse:
        """Fetch a specific lesson with content and resources."""
        lesson = await lesson_repo.get_by_id(db, lesson_id=lesson_id)
        if not lesson:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Lesson '{lesson_id}' not found.",
            )

        return LessonDetailResponse(
            id=lesson.id,
            module_id=lesson.module_id,
            title=lesson.title,
            slug=lesson.slug,
            description=lesson.description,
            content=lesson.content,
            lesson_type=lesson.lesson_type,
            estimated_minutes=lesson.estimated_minutes,
            order_index=lesson.order_index,
            video_url=lesson.video_url,
            published=lesson.published,
            resources=[
                LessonResourceResponse.model_validate(r)
                for r in (lesson.resources or [])
            ],
            created_at=lesson.created_at,
            updated_at=lesson.updated_at,
        )

    async def enroll_user(
        self, db: AsyncSession, *, user_id: str, course_identifier: str
    ) -> CourseEnrollmentResponse:
        """Enroll student in a course with duplicate prevention."""
        course = await course_repo.get_by_id_or_slug(db, identifier=course_identifier)
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Course '{course_identifier}' not found.",
            )

        existing = await enrollment_repo.get_by_user_and_course(
            db, user_id=user_id, course_id=course.id
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is already enrolled in this course.",
            )

        enrollment = await enrollment_repo.create(
            db, user_id=user_id, course_id=course.id
        )
        # Increment student count
        course.students_count += 1
        await db.commit()

        # Log enrollment activity event for streak and timeline calculation
        from app.models.progress import ActivityType
        from app.repositories.progress_repo import activity_repo

        await activity_repo.log_activity(
            db,
            user_id=user_id,
            activity_type=ActivityType.COURSE_ENROLLED.value,
            course_id=course.id,
            metadata={"course_title": course.title},
        )

        logger.info(f"Student {user_id} enrolled in course {course.id} ({course.slug})")
        return CourseEnrollmentResponse(
            id=enrollment.id,
            user_id=enrollment.user_id,
            course_id=enrollment.course_id,
            status=enrollment.status,
            enrolled_at=enrollment.enrolled_at,
            completed_at=enrollment.completed_at,
            course=self._to_course_summary(course),
        )

    async def get_user_courses(
        self, db: AsyncSession, *, user_id: str
    ) -> List[CourseEnrollmentResponse]:
        """Fetch all course enrollments for the current student."""
        enrollments = await enrollment_repo.get_user_enrollments(db, user_id=user_id)
        return [
            CourseEnrollmentResponse(
                id=e.id,
                user_id=e.user_id,
                course_id=e.course_id,
                status=e.status,
                enrolled_at=e.enrolled_at,
                completed_at=e.completed_at,
                course=self._to_course_summary(e.course) if e.course else None,
            )
            for e in enrollments
        ]

    async def get_user_course_enrollment(
        self, db: AsyncSession, *, user_id: str, course_identifier: str
    ) -> CourseEnrollmentResponse:
        """Get single course enrollment status for student."""
        course = await course_repo.get_by_id_or_slug(db, identifier=course_identifier)
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found.",
            )

        enrollment = await enrollment_repo.get_by_user_and_course(
            db, user_id=user_id, course_id=course.id
        )
        if not enrollment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User is not enrolled in this course.",
            )

        return CourseEnrollmentResponse(
            id=enrollment.id,
            user_id=enrollment.user_id,
            course_id=enrollment.course_id,
            status=enrollment.status,
            enrolled_at=enrollment.enrolled_at,
            completed_at=enrollment.completed_at,
            course=self._to_course_summary(course),
        )

    async def unenroll_user(
        self, db: AsyncSession, *, user_id: str, course_identifier: str
    ) -> bool:
        """Cancel/delete user course enrollment."""
        course = await course_repo.get_by_id_or_slug(db, identifier=course_identifier)
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found.",
            )

        success = await enrollment_repo.delete(db, user_id=user_id, course_id=course.id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Enrollment not found.",
            )
        if course.students_count > 0:
            course.students_count -= 1
            await db.commit()
        return True


course_service = CourseService()
