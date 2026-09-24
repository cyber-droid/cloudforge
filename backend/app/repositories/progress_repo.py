"""
Lesson Progress and Learning Activity Repository Layer.

Encapsulates transactional upserts, activity streaming, and aggregated metrics queries.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.course import (
    CourseModule,
    Lesson,
)
from app.models.progress import (
    ActivityType,
    LearningActivity,
    LessonProgress,
    LessonProgressStatus,
)


class ProgressRepository:
    """Data access methods for LessonProgress."""

    async def get_progress(
        self, db: AsyncSession, *, user_id: str, lesson_id: str
    ) -> Optional[LessonProgress]:
        """Fetch a specific lesson progress record."""
        result = await db.execute(
            select(LessonProgress)
            .options(selectinload(LessonProgress.lesson))
            .where(
                LessonProgress.user_id == user_id, LessonProgress.lesson_id == lesson_id
            )
        )
        return result.scalars().first()

    async def upsert_start(
        self, db: AsyncSession, *, user_id: str, lesson_id: str
    ) -> LessonProgress:
        """Create or update lesson progress to in_progress."""
        now = datetime.now(timezone.utc)
        record = await self.get_progress(db, user_id=user_id, lesson_id=lesson_id)

        if not record:
            record = LessonProgress(
                user_id=user_id,
                lesson_id=lesson_id,
                status=LessonProgressStatus.IN_PROGRESS.value,
                started_at=now,
                last_accessed_at=now,
                time_spent_seconds=0,
            )
            db.add(record)
        else:
            record.last_accessed_at = now
            if record.status == LessonProgressStatus.NOT_STARTED.value:
                record.status = LessonProgressStatus.IN_PROGRESS.value

        await db.commit()
        await db.refresh(record)
        return record

    async def record_time(
        self,
        db: AsyncSession,
        *,
        user_id: str,
        lesson_id: str,
        additional_seconds: int,
        new_status: Optional[str] = None,
    ) -> LessonProgress:
        """Increment study duration on a lesson."""
        now = datetime.now(timezone.utc)
        record = await self.get_progress(db, user_id=user_id, lesson_id=lesson_id)

        if not record:
            record = LessonProgress(
                user_id=user_id,
                lesson_id=lesson_id,
                status=new_status or LessonProgressStatus.IN_PROGRESS.value,
                started_at=now,
                last_accessed_at=now,
                time_spent_seconds=additional_seconds,
            )
            db.add(record)
        else:
            record.time_spent_seconds += additional_seconds
            record.last_accessed_at = now
            if new_status:
                record.status = new_status
                if (
                    new_status == LessonProgressStatus.COMPLETED.value
                    and not record.completed_at
                ):
                    record.completed_at = now

        await db.commit()
        await db.refresh(record)
        return record

    async def complete_lesson(
        self,
        db: AsyncSession,
        *,
        user_id: str,
        lesson_id: str,
        additional_seconds: int = 0,
    ) -> LessonProgress:
        """Mark lesson as completed and set completed_at timestamp."""
        now = datetime.now(timezone.utc)
        record = await self.get_progress(db, user_id=user_id, lesson_id=lesson_id)

        if not record:
            record = LessonProgress(
                user_id=user_id,
                lesson_id=lesson_id,
                status=LessonProgressStatus.COMPLETED.value,
                started_at=now,
                completed_at=now,
                last_accessed_at=now,
                time_spent_seconds=additional_seconds,
            )
            db.add(record)
        else:
            record.status = LessonProgressStatus.COMPLETED.value
            record.completed_at = now
            record.last_accessed_at = now
            record.time_spent_seconds += additional_seconds

        await db.commit()
        await db.refresh(record)
        return record

    async def get_course_lesson_progress(
        self, db: AsyncSession, *, user_id: str, course_id: str
    ) -> List[LessonProgress]:
        """Fetch all lesson progress records for a user within a specific course."""
        query = (
            select(LessonProgress)
            .join(Lesson, LessonProgress.lesson_id == Lesson.id)
            .join(CourseModule, Lesson.module_id == CourseModule.id)
            .where(
                LessonProgress.user_id == user_id, CourseModule.course_id == course_id
            )
        )
        result = await db.execute(query)
        return list(result.scalars().all())

    async def get_user_completed_lesson_count(
        self, db: AsyncSession, *, user_id: str
    ) -> int:
        """Count total lessons completed by user across all courses."""
        query = select(func.count(LessonProgress.id)).where(
            LessonProgress.user_id == user_id,
            LessonProgress.status == LessonProgressStatus.COMPLETED.value,
        )
        result = await db.execute(query)
        return result.scalar() or 0

    async def get_total_study_seconds(self, db: AsyncSession, *, user_id: str) -> int:
        """Sum total learning seconds recorded across all user lesson progress."""
        query = select(
            func.coalesce(func.sum(LessonProgress.time_spent_seconds), 0)
        ).where(LessonProgress.user_id == user_id)
        result = await db.execute(query)
        return result.scalar() or 0

    async def get_recently_accessed_incomplete_lesson(
        self, db: AsyncSession, *, user_id: str
    ) -> Optional[LessonProgress]:
        """Find the most recently accessed incomplete lesson for continue learning."""
        query = (
            select(LessonProgress)
            .options(
                selectinload(LessonProgress.lesson)
                .selectinload(Lesson.module)
                .selectinload(CourseModule.course)
            )
            .where(
                LessonProgress.user_id == user_id,
                LessonProgress.status == LessonProgressStatus.IN_PROGRESS.value,
            )
            .order_by(desc(LessonProgress.last_accessed_at))
            .limit(1)
        )
        result = await db.execute(query)
        return result.scalars().first()


class ActivityRepository:
    """Data access methods for LearningActivity stream."""

    async def log_activity(
        self,
        db: AsyncSession,
        *,
        user_id: str,
        activity_type: str,
        course_id: Optional[str] = None,
        lesson_id: Optional[str] = None,
        duration_seconds: int = 0,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> LearningActivity:
        """Record an append-only learning event."""
        activity = LearningActivity(
            user_id=user_id,
            activity_type=activity_type,
            course_id=course_id,
            lesson_id=lesson_id,
            duration_seconds=duration_seconds,
            activity_metadata=metadata or {},
        )
        db.add(activity)
        await db.commit()
        await db.refresh(activity)
        return activity

    async def get_recent_activities(
        self, db: AsyncSession, *, user_id: str, limit: int = 10
    ) -> List[LearningActivity]:
        """Fetch the most recent learning activities for student dashboard."""
        query = (
            select(LearningActivity)
            .options(
                selectinload(LearningActivity.course),
                selectinload(LearningActivity.lesson),
            )
            .where(LearningActivity.user_id == user_id)
            .order_by(desc(LearningActivity.created_at))
            .limit(limit)
        )
        result = await db.execute(query)
        return list(result.scalars().all())

    async def get_distinct_activity_dates(
        self, db: AsyncSession, *, user_id: str
    ) -> List[datetime]:
        """
        Fetch distinct UTC dates where qualifying learning activities occurred.
        Authoritative source for streak calculation.
        """
        query = (
            select(LearningActivity.created_at)
            .where(LearningActivity.user_id == user_id)
            .order_by(desc(LearningActivity.created_at))
        )
        result = await db.execute(query)
        rows = result.scalars().all()
        # Extract unique dates while preserving datetime type
        seen = set()
        unique_dates = []
        for dt in rows:
            d = dt.date()
            if d not in seen:
                seen.add(d)
                unique_dates.append(dt)
        return unique_dates

    async def get_daily_activity_aggregates(
        self, db: AsyncSession, *, user_id: str, since_date: datetime
    ) -> List[Dict[str, Any]]:
        """
        Aggregate learning events grouped by calendar date.
        Returns [{'date': 'YYYY-MM-DD', 'count': int, 'lessons_completed': int, 'time_spent_seconds': int}]
        """
        query = (
            select(LearningActivity)
            .where(
                LearningActivity.user_id == user_id,
                LearningActivity.created_at >= since_date,
            )
            .order_by(LearningActivity.created_at.asc())
        )
        result = await db.execute(query)
        activities = result.scalars().all()

        daily_dict: Dict[str, Dict[str, Any]] = {}
        for a in activities:
            day_str = a.created_at.strftime("%Y-%m-%d")
            if day_str not in daily_dict:
                daily_dict[day_str] = {
                    "date": day_str,
                    "count": 0,
                    "lessons_completed": 0,
                    "time_spent_seconds": 0,
                }
            daily_dict[day_str]["count"] += 1
            if a.activity_type == ActivityType.LESSON_COMPLETED.value:
                daily_dict[day_str]["lessons_completed"] += 1
            daily_dict[day_str]["time_spent_seconds"] += a.duration_seconds or 0

        return sorted(daily_dict.values(), key=lambda x: x["date"])


progress_repo = ProgressRepository()
activity_repo = ActivityRepository()
