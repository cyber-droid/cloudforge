"""
Lesson Execution and Study Progress Tracking Endpoints.
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.progress import LessonProgressResponse, LessonProgressUpdate
from app.services.progress_service import progress_service

router = APIRouter()


@router.post(
    "/{lesson_id}/start",
    response_model=LessonProgressResponse,
    status_code=status.HTTP_200_OK,
    summary="Start Lesson Study",
    description="Mark lesson as in_progress, update last_accessed_at, and record learning activity event."
)
async def start_lesson(
    lesson_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> LessonProgressResponse:
    """Record student opening/starting a lesson."""
    return await progress_service.start_lesson(
        db,
        user_id=current_user.id,
        lesson_id=lesson_id,
    )


@router.post(
    "/{lesson_id}/progress",
    response_model=LessonProgressResponse,
    status_code=status.HTTP_200_OK,
    summary="Record Lesson Study Time",
    description="Incrementally log study duration seconds with strict boundary validation (0 <= time <= 86400s)."
)
async def record_lesson_progress(
    lesson_id: str,
    payload: LessonProgressUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> LessonProgressResponse:
    """Increment study time spent on a lesson."""
    return await progress_service.record_study_time(
        db,
        user_id=current_user.id,
        lesson_id=lesson_id,
        time_spent_seconds=payload.time_spent_seconds,
        status_update=payload.status,
    )


@router.post(
    "/{lesson_id}/complete",
    response_model=LessonProgressResponse,
    status_code=status.HTTP_200_OK,
    summary="Complete Lesson",
    description="Mark lesson as completed, calculate course progress, and trigger course graduation if all lessons are finished."
)
async def complete_lesson(
    lesson_id: str,
    payload: LessonProgressUpdate = LessonProgressUpdate(),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> LessonProgressResponse:
    """Mark lesson completed and check course completion."""
    return await progress_service.complete_lesson(
        db,
        user_id=current_user.id,
        lesson_id=lesson_id,
        time_spent_seconds=payload.time_spent_seconds,
    )
