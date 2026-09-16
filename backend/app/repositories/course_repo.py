"""
Course, Module, Lesson, and Enrollment Repository Layer.

Encapsulates all PostgreSQL queries with eager-loading strategies to eliminate N+1 query overhead.
"""
from typing import List, Optional, Tuple
from sqlalchemy import cast, func, or_, select, String, Text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.course import Course, CourseEnrollment, CourseModule, EnrollmentStatus, Lesson, LessonResource


class CourseRepository:
    """Data access methods for Course entities."""

    async def get_by_id_or_slug(self, db: AsyncSession, *, identifier: str) -> Optional[Course]:
        """Fetch a course by either UUID or slug, eager-loading modules and lessons."""
        query = (
            select(Course)
            .options(
                selectinload(Course.modules).selectinload(CourseModule.lessons)
            )
            .where(or_(Course.id == identifier, Course.slug == identifier))
        )
        result = await db.execute(query)
        return result.scalars().first()

    async def get_paginated(
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
        published_only: bool = True
    ) -> Tuple[List[Course], int]:
        """
        Query courses with SQL-level filtering, ILIKE search, and pagination.
        Returns (list_of_courses, total_count).
        """
        query = select(Course).options(
            selectinload(Course.modules).selectinload(CourseModule.lessons)
        )
        count_query = select(func.count(Course.id))

        filters = []
        if published_only:
            filters.append(Course.published.is_(True))

        if category and category != "All":
            if category == "Security":
                filters.append(or_(Course.category == "Security", Course.category == "Cloud Security"))
            elif category == "AI":
                filters.append(or_(Course.category == "AI", Course.category == "AI Engineering"))
            else:
                filters.append(Course.category.ilike(f"%{category}%"))

        if difficulty and difficulty != "All":
            filters.append(Course.difficulty.ilike(f"%{difficulty}%"))

        if certificate_available is not None:
            filters.append(Course.certificate_available.is_(certificate_available))

        if search and search.strip():
            search_pattern = f"%{search.strip().lower()}%"
            filters.append(
                or_(
                    func.lower(Course.title).ilike(search_pattern),
                    func.lower(Course.description).ilike(search_pattern),
                    cast(Course.technologies, String).ilike(search_pattern),
                )
            )

        if technology and technology.strip():
            tech_pattern = f"%{technology.strip().lower()}%"
            filters.append(cast(Course.technologies, String).ilike(tech_pattern))

        if filters:
            query = query.where(*filters)
            count_query = count_query.where(*filters)

        # Count total matching records
        count_res = await db.execute(count_query)
        total = count_res.scalar() or 0

        # Apply ordering and pagination
        offset = (page - 1) * page_size
        query = query.order_by(Course.created_at.asc()).offset(offset).limit(page_size)

        result = await db.execute(query)
        courses = list(result.scalars().all())

        return courses, total


class ModuleRepository:
    """Data access methods for Course Modules."""

    async def get_by_id(self, db: AsyncSession, *, module_id: str) -> Optional[CourseModule]:
        """Fetch module with all ordered lessons."""
        query = (
            select(CourseModule)
            .options(selectinload(CourseModule.lessons))
            .where(CourseModule.id == module_id)
        )
        result = await db.execute(query)
        return result.scalars().first()


class LessonRepository:
    """Data access methods for Lessons."""

    async def get_by_id(self, db: AsyncSession, *, lesson_id: str) -> Optional[Lesson]:
        """Fetch lesson with attached resources."""
        query = (
            select(Lesson)
            .options(selectinload(Lesson.resources))
            .where(or_(Lesson.id == lesson_id, Lesson.slug == lesson_id))
        )
        result = await db.execute(query)
        return result.scalars().first()


class EnrollmentRepository:
    """Data access methods for Course Enrollments."""

    async def get_by_user_and_course(
        self,
        db: AsyncSession,
        *,
        user_id: str,
        course_id: str
    ) -> Optional[CourseEnrollment]:
        """Check if user has an existing enrollment for a course."""
        query = (
            select(CourseEnrollment)
            .options(selectinload(CourseEnrollment.course))
            .where(
                CourseEnrollment.user_id == user_id,
                CourseEnrollment.course_id == course_id,
            )
        )
        result = await db.execute(query)
        return result.scalars().first()

    async def create(
        self,
        db: AsyncSession,
        *,
        user_id: str,
        course_id: str
    ) -> CourseEnrollment:
        """Create a new active course enrollment."""
        enrollment = CourseEnrollment(
            user_id=user_id,
            course_id=course_id,
            status=EnrollmentStatus.ACTIVE.value,
        )
        db.add(enrollment)
        await db.commit()
        await db.refresh(enrollment)
        return enrollment

    async def get_user_enrollments(
        self,
        db: AsyncSession,
        *,
        user_id: str
    ) -> List[CourseEnrollment]:
        """Fetch all course enrollments for a user."""
        query = (
            select(CourseEnrollment)
            .options(selectinload(CourseEnrollment.course))
            .where(CourseEnrollment.user_id == user_id)
            .order_by(CourseEnrollment.enrolled_at.desc())
        )
        result = await db.execute(query)
        return list(result.scalars().all())

    async def delete(
        self,
        db: AsyncSession,
        *,
        user_id: str,
        course_id: str
    ) -> bool:
        """Cancel/delete a course enrollment."""
        enrollment = await self.get_by_user_and_course(db, user_id=user_id, course_id=course_id)
        if enrollment:
            await db.delete(enrollment)
            await db.commit()
            return True
        return False


course_repo = CourseRepository()
module_repo = ModuleRepository()
lesson_repo = LessonRepository()
enrollment_repo = EnrollmentRepository()
