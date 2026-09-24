"""
Courses, Curriculum, Modules, and Lessons API Endpoints.
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.common import MessageResponse
from app.schemas.course import (
    CourseCurriculumResponse,
    CourseDetailResponse,
    CourseEnrollmentResponse,
    CourseListResponse,
    LessonDetailResponse,
    ModuleDetailResponse,
)
from app.services.course_service import course_service

router = APIRouter()


@router.get(
    "",
    response_model=CourseListResponse,
    status_code=status.HTTP_200_OK,
    summary="List and Filter Courses",
    description="Query paginated courses with category, difficulty, search keyword, and technology filters.",
)
async def list_courses(
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=12, ge=1, le=50, description="Items per page"),
    category: Optional[str] = Query(default=None, description="Course domain category"),
    difficulty: Optional[str] = Query(default=None, description="Experience level"),
    technology: Optional[str] = Query(
        default=None, description="Technology tag filter"
    ),
    search: Optional[str] = Query(
        default=None,
        description="Search term across title, description, and technologies",
    ),
    certificate_available: Optional[bool] = Query(
        default=None, description="Filter courses with certification vouchers"
    ),
    db: AsyncSession = Depends(get_db),
) -> CourseListResponse:
    """Fetch paginated course catalog."""
    return await course_service.list_courses(
        db,
        page=page,
        page_size=page_size,
        category=category,
        difficulty=difficulty,
        technology=technology,
        search=search,
        certificate_available=certificate_available,
    )


@router.get(
    "/{course_id}",
    response_model=CourseDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Course Detail",
    description="Retrieve full course syllabus, outcomes, and instructor details by UUID or slug.",
)
async def get_course(
    course_id: str, db: AsyncSession = Depends(get_db)
) -> CourseDetailResponse:
    """Fetch single course details."""
    return await course_service.get_course(db, identifier=course_id)


@router.get(
    "/{course_id}/curriculum",
    response_model=CourseCurriculumResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Course Curriculum Tree",
    description="Fetch nested ordered modules and lessons for curriculum navigation.",
)
async def get_curriculum(
    course_id: str, db: AsyncSession = Depends(get_db)
) -> CourseCurriculumResponse:
    """Fetch ordered syllabus tree."""
    return await course_service.get_curriculum(db, course_id=course_id)


@router.get(
    "/{course_id}/modules/{module_id}",
    response_model=ModuleDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Module Detail",
    description="Retrieve module information and its associated lessons.",
)
async def get_module(
    course_id: str, module_id: str, db: AsyncSession = Depends(get_db)
) -> ModuleDetailResponse:
    """Fetch single module with lessons."""
    return await course_service.get_module(db, course_id=course_id, module_id=module_id)


@router.get(
    "/{course_id}/lessons/{lesson_id}",
    response_model=LessonDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Lesson Content & Resources",
    description="Retrieve markdown lesson content, video URL, and attached resources.",
)
async def get_lesson(
    course_id: str, lesson_id: str, db: AsyncSession = Depends(get_db)
) -> LessonDetailResponse:
    """Fetch single lesson."""
    return await course_service.get_lesson(db, course_id=course_id, lesson_id=lesson_id)


@router.post(
    "/{course_id}/enroll",
    response_model=CourseEnrollmentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Enroll in Course",
    description="Enroll the authenticated student into a course.",
)
async def enroll_course(
    course_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> CourseEnrollmentResponse:
    """Enroll logged-in student in course."""
    return await course_service.enroll_user(
        db,
        user_id=current_user.id,
        course_identifier=course_id,
    )


@router.delete(
    "/{course_id}/enroll",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Cancel Course Enrollment",
    description="Unenroll the authenticated student from a course.",
)
async def unenroll_course(
    course_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    """Cancel course enrollment."""
    await course_service.unenroll_user(
        db,
        user_id=current_user.id,
        course_identifier=course_id,
    )
    return MessageResponse(message="Successfully unenrolled from course.")
