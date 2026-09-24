"""
Lesson Progress and Learning Activity Models.

Why these entities exist:
1. LessonProgress:
   Represents the user's granular learning state per lesson with time tracking and completion timestamps.
   Unique constraint on (user_id, lesson_id) prevents race-condition duplicate completions.

2. LearningActivity:
   Append-only event stream logging key learning events (lesson_started, lesson_completed,
   course_enrolled, course_completed). Authoritative ledger used for calculating authentic
   learning streaks, daily activity heatmaps, and weekly study hours.
"""
import enum
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from sqlalchemy import (
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Integer,
    JSON,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class LessonProgressStatus(str, enum.Enum):
    """Status of a lesson for a specific user."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class ActivityType(str, enum.Enum):
    """Learning activity events."""
    LESSON_STARTED = "lesson_started"
    LESSON_COMPLETED = "lesson_completed"
    COURSE_ENROLLED = "course_enrolled"
    COURSE_COMPLETED = "course_completed"
    LESSON_TIME_RECORDED = "lesson_time_recorded"
    PROJECT_STARTED = "project_started"
    PROJECT_STEP_COMPLETED = "project_step_completed"
    PROJECT_COMPLETED = "project_completed"


class LessonProgress(Base, TimestampMixin):
    """User progress through a single lesson."""
    __tablename__ = "lesson_progress"
    __table_args__ = (
        UniqueConstraint("user_id", "lesson_id", name="uq_user_lesson_progress"),
    )

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        index=True,
    )
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    lesson_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("lessons.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    status: Mapped[str] = mapped_column(
        String(20),
        default=LessonProgressStatus.NOT_STARTED.value,
        nullable=False,
        index=True,
    )
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    time_spent_seconds: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    last_accessed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )

    # Relationships
    lesson: Mapped["Lesson"] = relationship(
        "Lesson",
        lazy="joined",
    )


class LearningActivity(Base, TimestampMixin):
    """Append-only learning event stream for streak, hours, and heatmap calculations."""
    __tablename__ = "learning_activities"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        index=True,
    )
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    activity_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )
    course_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("courses.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    lesson_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("lessons.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    duration_seconds: Mapped[Optional[int]] = mapped_column(
        Integer,
        default=0,
        nullable=True,
    )
    activity_metadata: Mapped[Dict[str, Any]] = mapped_column(
        JSON,
        default=dict,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )

    # Relationships
    course: Mapped[Optional["Course"]] = relationship(
        "Course",
        lazy="joined",
    )
    lesson: Mapped[Optional["Lesson"]] = relationship(
        "Lesson",
        lazy="joined",
    )
