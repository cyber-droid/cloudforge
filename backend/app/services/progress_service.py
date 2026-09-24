"""
Learning Progress, Streaks, Study Hours, and Dashboard Aggregation Service.

Why this architecture exists:
1. Deterministic Progress Calculation:
   Course and overall progress percentages are strictly computed from actual completed lesson records
   against published curriculum totals, preventing out-of-sync or fake numbers.

2. True Calendar-Day Streak Algorithm:
   Computes consecutive learning days from distinct UTC event dates. A qualifying activity on
   consecutive calendar days maintains the streak without double-counting multiple events on the same day.

3. Single-Roundtrip Dashboard Assembly:
   Consolidates all metrics required by the frontend student workbench in one clean asynchronous query batch.
"""

from datetime import datetime, timedelta, timezone
from typing import List, Optional, Tuple

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import logger
from app.models.course import (
    EnrollmentStatus,
    Lesson,
)
from app.models.progress import (
    ActivityType,
    LessonProgressStatus,
)
from app.models.user import User
from app.repositories.course_repo import (
    course_repo,
    enrollment_repo,
    lesson_repo,
    module_repo,
)
from app.repositories.progress_repo import activity_repo, progress_repo
from app.schemas.progress import (
    ContinueLearningResponse,
    CourseProgressResponse,
    DailyActivityItem,
    DashboardResponse,
    DashboardStatsResponse,
    LearningActivityResponse,
    LessonProgressResponse,
    OverallProgressResponse,
    WeeklyHoursItem,
)
from app.schemas.user import UserResponse


class ProgressService:
    """Service managing student learning progress, activity streams, and dashboard metrics."""

    async def start_lesson(
        self, db: AsyncSession, *, user_id: str, lesson_id: str
    ) -> LessonProgressResponse:
        """
        Record that a student has opened and started a lesson.
        Updates LessonProgress and logs a lesson_started event.
        """
        lesson = await lesson_repo.get_by_id(db, lesson_id=lesson_id)
        if not lesson or not lesson.published:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Lesson '{lesson_id}' not found or is unpublished.",
            )

        module = await module_repo.get_by_id(db, module_id=lesson.module_id)
        course_id = module.course_id if module else None

        progress = await progress_repo.upsert_start(
            db, user_id=user_id, lesson_id=lesson.id
        )

        # Log activity event
        await activity_repo.log_activity(
            db,
            user_id=user_id,
            activity_type=ActivityType.LESSON_STARTED.value,
            course_id=course_id,
            lesson_id=lesson.id,
            metadata={"lesson_title": lesson.title},
        )

        return LessonProgressResponse.model_validate(progress)

    async def record_study_time(
        self,
        db: AsyncSession,
        *,
        user_id: str,
        lesson_id: str,
        time_spent_seconds: int,
        status_update: Optional[str] = None,
    ) -> LessonProgressResponse:
        """
        Increment study time on a lesson with boundary validation.
        """
        if time_spent_seconds < 0 or time_spent_seconds > 86400:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Study duration must be between 0 and 86400 seconds (24 hours).",
            )

        lesson = await lesson_repo.get_by_id(db, lesson_id=lesson_id)
        if not lesson:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lesson not found.",
            )

        progress = await progress_repo.record_time(
            db,
            user_id=user_id,
            lesson_id=lesson.id,
            additional_seconds=time_spent_seconds,
            new_status=status_update,
        )

        if time_spent_seconds > 0:
            module = await module_repo.get_by_id(db, module_id=lesson.module_id)
            await activity_repo.log_activity(
                db,
                user_id=user_id,
                activity_type=ActivityType.LESSON_TIME_RECORDED.value,
                course_id=module.course_id if module else None,
                lesson_id=lesson.id,
                duration_seconds=time_spent_seconds,
                metadata={"lesson_title": lesson.title},
            )

        return LessonProgressResponse.model_validate(progress)

    async def complete_lesson(
        self,
        db: AsyncSession,
        *,
        user_id: str,
        lesson_id: str,
        time_spent_seconds: int = 0,
    ) -> LessonProgressResponse:
        """
        Mark a lesson as completed, calculate course progress, and trigger course completion if all lessons are done.
        """
        if time_spent_seconds < 0 or time_spent_seconds > 86400:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid time spent duration.",
            )

        lesson = await lesson_repo.get_by_id(db, lesson_id=lesson_id)
        if not lesson or not lesson.published:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lesson not found or is unpublished.",
            )

        module = await module_repo.get_by_id(db, module_id=lesson.module_id)
        course_id = module.course_id if module else None

        progress = await progress_repo.complete_lesson(
            db,
            user_id=user_id,
            lesson_id=lesson.id,
            additional_seconds=time_spent_seconds,
        )

        # Log completion activity
        await activity_repo.log_activity(
            db,
            user_id=user_id,
            activity_type=ActivityType.LESSON_COMPLETED.value,
            course_id=course_id,
            lesson_id=lesson.id,
            duration_seconds=time_spent_seconds,
            metadata={"lesson_title": lesson.title},
        )

        # Check if entire course is now completed
        if course_id:
            await self._check_and_update_course_completion(
                db, user_id=user_id, course_id=course_id
            )

        return LessonProgressResponse.model_validate(progress)

    async def _check_and_update_course_completion(
        self, db: AsyncSession, *, user_id: str, course_id: str
    ) -> bool:
        """Helper to mark course enrollment completed when all published lessons are finished."""
        course = await course_repo.get_by_id_or_slug(db, identifier=course_id)
        if not course:
            return False

        all_published_lessons: List[Lesson] = []
        for m in course.modules or []:
            if m.published:
                for lesson in m.lessons or []:
                    if lesson.published:
                        all_published_lessons.append(lesson)

        if not all_published_lessons:
            return False

        progress_records = await progress_repo.get_course_lesson_progress(
            db, user_id=user_id, course_id=course.id
        )
        completed_lesson_ids = {
            p.lesson_id
            for p in progress_records
            if p.status == LessonProgressStatus.COMPLETED.value
        }

        all_completed = all(lesson.id in completed_lesson_ids for lesson in all_published_lessons)
        if all_completed:
            enrollment = await enrollment_repo.get_by_user_and_course(
                db, user_id=user_id, course_id=course.id
            )
            if enrollment and enrollment.status != EnrollmentStatus.COMPLETED.value:
                enrollment.status = EnrollmentStatus.COMPLETED.value
                enrollment.completed_at = datetime.now(timezone.utc)
                await db.commit()

                await activity_repo.log_activity(
                    db,
                    user_id=user_id,
                    activity_type=ActivityType.COURSE_COMPLETED.value,
                    course_id=course.id,
                    metadata={"course_title": course.title},
                )
                logger.info(
                    f"Student {user_id} COMPLETED course {course.id} ({course.title})"
                )
                return True
        return False

    async def get_course_progress(
        self, db: AsyncSession, *, user_id: str, course_identifier: str
    ) -> CourseProgressResponse:
        """
        Calculate progress for a single course based on actual published lessons.
        Formula: completed_lessons / total_published_lessons * 100
        """
        course = await course_repo.get_by_id_or_slug(db, identifier=course_identifier)
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Course '{course_identifier}' not found.",
            )

        published_lessons = [
            lesson
            for m in (course.modules or [])
            if m.published
            for lesson in (m.lessons or [])
            if lesson.published
        ]
        total_lessons = len(published_lessons)

        progress_records = await progress_repo.get_course_lesson_progress(
            db, user_id=user_id, course_id=course.id
        )

        completed_count = sum(
            1
            for p in progress_records
            if p.status == LessonProgressStatus.COMPLETED.value
        )
        in_progress_count = sum(
            1
            for p in progress_records
            if p.status == LessonProgressStatus.IN_PROGRESS.value
        )

        percentage = (
            round((completed_count / total_lessons * 100), 1)
            if total_lessons > 0
            else 0.0
        )

        enrollment = await enrollment_repo.get_by_user_and_course(
            db, user_id=user_id, course_id=course.id
        )

        started_at = progress_records[0].started_at if progress_records else None
        last_accessed_at = max(
            (p.last_accessed_at for p in progress_records), default=None
        )

        return CourseProgressResponse(
            course_id=course.id,
            course_slug=course.slug,
            course_title=course.title,
            total_lessons=total_lessons,
            completed_lessons=completed_count,
            in_progress_lessons=in_progress_count,
            progress_percentage=percentage,
            status=enrollment.status
            if enrollment
            else (
                "completed"
                if percentage >= 100
                else "in_progress"
                if percentage > 0
                else "not_started"
            ),
            started_at=started_at,
            last_accessed_at=last_accessed_at,
            completed_at=enrollment.completed_at if enrollment else None,
        )

    def calculate_streaks(self, activity_dates: List[datetime]) -> Tuple[int, int]:
        """
        Calculate current and longest daily learning streaks.

        Algorithm:
        1. Extract unique calendar date strings (YYYY-MM-DD) sorted descending.
        2. Today or yesterday must be present to have an active current streak.
        3. Step backwards day by day to count current continuous sequence.
        4. Find maximum continuous sequence across all historical activity.
        """
        if not activity_dates:
            return 0, 0

        unique_dates = sorted(list({d.date() for d in activity_dates}), reverse=True)

        if not unique_dates:
            return 0, 0

        today = datetime.now(timezone.utc).date()
        yesterday = today - timedelta(days=1)

        # 1. Current Streak
        current_streak = 0
        if unique_dates[0] in (today, yesterday):
            expected_date = unique_dates[0]
            for d in unique_dates:
                if d == expected_date:
                    current_streak += 1
                    expected_date -= timedelta(days=1)
                else:
                    break

        # 2. Longest Historical Streak
        longest_streak = 0
        temp_streak = 0
        prev_date = None

        for d in sorted(unique_dates):
            if prev_date is None:
                temp_streak = 1
            elif d == prev_date + timedelta(days=1):
                temp_streak += 1
            else:
                temp_streak = 1
            if temp_streak > longest_streak:
                longest_streak = temp_streak
            prev_date = d

        return current_streak, max(current_streak, longest_streak)

    async def get_overall_progress(
        self, db: AsyncSession, *, user_id: str
    ) -> OverallProgressResponse:
        """Calculate high-level learning summary metrics."""
        enrollments = await enrollment_repo.get_user_enrollments(db, user_id=user_id)
        enrolled_count = len(enrollments)
        completed_courses = sum(
            1 for e in enrollments if e.status == EnrollmentStatus.COMPLETED.value
        )
        in_progress_courses = sum(
            1 for e in enrollments if e.status == EnrollmentStatus.ACTIVE.value
        )

        total_completed_lessons = await progress_repo.get_user_completed_lesson_count(
            db, user_id=user_id
        )
        total_seconds = await progress_repo.get_total_study_seconds(db, user_id=user_id)
        learning_hours = round(total_seconds / 3600.0, 1)

        activity_dates = await activity_repo.get_distinct_activity_dates(
            db, user_id=user_id
        )
        current_streak, longest_streak = self.calculate_streaks(activity_dates)

        # Compute total published lessons across enrolled courses
        total_lessons_in_enrolled = 0
        for e in enrollments:
            if e.course and e.course.modules:
                total_lessons_in_enrolled += sum(
                    len(m.lessons or []) for m in e.course.modules if m.published
                )

        overall_pct = (
            round((total_completed_lessons / total_lessons_in_enrolled * 100), 1)
            if total_lessons_in_enrolled > 0
            else 0.0
        )

        return OverallProgressResponse(
            overall_progress_percentage=min(100.0, overall_pct),
            enrolled_courses=enrolled_count,
            completed_courses=completed_courses,
            in_progress_courses=in_progress_courses,
            completed_lessons=total_completed_lessons,
            total_lessons=total_lessons_in_enrolled,
            learning_hours=learning_hours,
            current_streak=current_streak,
            longest_streak=longest_streak,
        )

    async def get_continue_learning(
        self, db: AsyncSession, *, user_id: str
    ) -> Optional[ContinueLearningResponse]:
        """
        Find what the user should continue next:
        1. Recently accessed in_progress lesson.
        2. Else, first uncompleted lesson of the most recently enrolled course.
        """
        recent_prog = await progress_repo.get_recently_accessed_incomplete_lesson(
            db, user_id=user_id
        )
        if recent_prog and recent_prog.lesson:
            lesson = recent_prog.lesson
            module = lesson.module
            course = module.course if module else None
            if course and module:
                course_prog = await self.get_course_progress(
                    db, user_id=user_id, course_identifier=course.id
                )
                return ContinueLearningResponse(
                    course_id=course.id,
                    course_slug=course.slug,
                    course_title=course.title,
                    module_id=module.id,
                    module_title=module.title,
                    module_number=module.module_number,
                    lesson_id=lesson.id,
                    lesson_slug=lesson.slug,
                    lesson_title=lesson.title,
                    progress_percentage=course_prog.progress_percentage,
                    estimated_time_remaining=f"{lesson.estimated_minutes}m remaining",
                    last_accessed_at=recent_prog.last_accessed_at,
                )

        # Fallback to most recent active enrollment
        enrollments = await enrollment_repo.get_user_enrollments(db, user_id=user_id)
        active_enrollments = [
            e for e in enrollments if e.status == EnrollmentStatus.ACTIVE.value
        ]
        if not active_enrollments:
            return None

        target_course = active_enrollments[0].course
        if not target_course or not target_course.modules:
            return None

        # Find first incomplete lesson
        course_progs = await progress_repo.get_course_lesson_progress(
            db, user_id=user_id, course_id=target_course.id
        )
        completed_ids = {
            p.lesson_id
            for p in course_progs
            if p.status == LessonProgressStatus.COMPLETED.value
        }

        for mod in target_course.modules:
            for les in mod.lessons or []:
                if les.id not in completed_ids:
                    prog = await self.get_course_progress(
                        db, user_id=user_id, course_identifier=target_course.id
                    )
                    return ContinueLearningResponse(
                        course_id=target_course.id,
                        course_slug=target_course.slug,
                        course_title=target_course.title,
                        module_id=mod.id,
                        module_title=mod.title,
                        module_number=mod.module_number,
                        lesson_id=les.id,
                        lesson_slug=les.slug,
                        lesson_title=les.title,
                        progress_percentage=prog.progress_percentage,
                        estimated_time_remaining=f"{les.estimated_minutes}m remaining",
                        last_accessed_at=datetime.now(timezone.utc),
                    )

        return None

    async def get_recent_activity(
        self, db: AsyncSession, *, user_id: str, limit: int = 10
    ) -> List[LearningActivityResponse]:
        """Format recent activities into human-readable timeline entries."""
        activities = await activity_repo.get_recent_activities(
            db, user_id=user_id, limit=limit
        )
        results = []
        for a in activities:
            title = ""
            if a.activity_type == ActivityType.LESSON_COMPLETED.value:
                lesson_title = a.lesson.title if a.lesson else "Lesson"
                title = f"Completed {lesson_title}"
            elif a.activity_type == ActivityType.LESSON_STARTED.value:
                lesson_title = a.lesson.title if a.lesson else "Lesson"
                title = f"Started {lesson_title}"
            elif a.activity_type == ActivityType.COURSE_ENROLLED.value:
                course_title = a.course.title if a.course else "Course"
                title = f"Enrolled in {course_title}"
            elif a.activity_type == ActivityType.COURSE_COMPLETED.value:
                course_title = a.course.title if a.course else "Course"
                title = f"Graduated {course_title}"
            else:
                title = f"Studied {a.lesson.title if a.lesson else 'Curriculum'}"

            results.append(
                LearningActivityResponse(
                    id=a.id,
                    activity_type=a.activity_type,
                    title=title,
                    course_slug=a.course.slug if a.course else None,
                    course_title=a.course.title if a.course else None,
                    lesson_slug=a.lesson.slug if a.lesson else None,
                    lesson_title=a.lesson.title if a.lesson else None,
                    duration_seconds=a.duration_seconds or 0,
                    created_at=a.created_at,
                )
            )
        return results

    async def get_daily_activity(
        self, db: AsyncSession, *, user_id: str, period: str = "week"
    ) -> List[DailyActivityItem]:
        """Aggregate daily activity for GitHub-style heatmap."""
        days = 365 if period == "year" else (30 if period == "month" else 7)
        since_date = datetime.now(timezone.utc) - timedelta(days=days)
        aggregates = await activity_repo.get_daily_activity_aggregates(
            db, user_id=user_id, since_date=since_date
        )
        return [DailyActivityItem(**item) for item in aggregates]

    async def get_dashboard(self, db: AsyncSession, *, user: User) -> DashboardResponse:
        """
        Unified student dashboard endpoint consolidating real PostgreSQL metrics.
        """
        overall = await self.get_overall_progress(db, user_id=user.id)
        continue_card = await self.get_continue_learning(db, user_id=user.id)
        recent_events = await self.get_recent_activity(db, user_id=user.id, limit=8)
        daily_activity = await self.get_daily_activity(
            db, user_id=user.id, period="month"
        )

        # Compute weekly hours distribution by day of week
        since_week = datetime.now(timezone.utc) - timedelta(days=7)
        week_aggregates = await activity_repo.get_daily_activity_aggregates(
            db, user_id=user.id, since_date=since_week
        )
        day_map = {
            "Mon": 0.0,
            "Tue": 0.0,
            "Wed": 0.0,
            "Thu": 0.0,
            "Fri": 0.0,
            "Sat": 0.0,
            "Sun": 0.0,
        }
        for item in week_aggregates:
            try:
                dt = datetime.strptime(item["date"], "%Y-%m-%d")
                day_name = dt.strftime("%a")
                if day_name in day_map:
                    day_map[day_name] += round(item["time_spent_seconds"] / 3600.0, 1)
            except Exception:
                pass

        weekly_hours = [WeeklyHoursItem(day=d, hours=h) for d, h in day_map.items()]

        # Enrolled courses progress list
        enrollments = await enrollment_repo.get_user_enrollments(db, user_id=user.id)
        course_progress_list = []
        for e in enrollments:
            if e.course:
                prog = await self.get_course_progress(
                    db, user_id=user.id, course_identifier=e.course.id
                )
                course_progress_list.append(prog)

        stats = DashboardStatsResponse(
            overall_progress=overall.overall_progress_percentage,
            learning_hours=overall.learning_hours,
            current_streak=overall.current_streak,
            longest_streak=overall.longest_streak,
            courses_completed=overall.completed_courses,
            courses_enrolled=overall.enrolled_courses,
            lessons_completed=overall.completed_lessons,
        )

        return DashboardResponse(
            user=UserResponse.model_validate(user),
            stats=stats,
            continue_learning=continue_card,
            recent_activity=recent_events,
            weekly_activity=daily_activity,
            weekly_hours=weekly_hours,
            course_progress=course_progress_list,
        )


progress_service = ProgressService()
