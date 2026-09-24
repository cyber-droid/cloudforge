"""
Learning Progress, Activity, and Dashboard Pydantic Schemas.
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.user import UserResponse


class LessonProgressUpdate(BaseModel):
    """Payload for updating incremental study time on a lesson."""

    time_spent_seconds: int = Field(
        default=0,
        ge=0,
        le=86400,
        description="Elapsed study duration in seconds (must be >= 0 and <= 24 hours per ping)",
    )
    status: Optional[str] = Field(
        default=None, description="Optional status update: 'in_progress' or 'completed'"
    )


class LessonProgressResponse(BaseModel):
    """Granular lesson completion status and timestamp payload."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    lesson_id: str
    status: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    time_spent_seconds: int
    last_accessed_at: datetime


class CourseProgressResponse(BaseModel):
    """Course completion stats derived from real lesson records."""

    model_config = ConfigDict(from_attributes=True)

    course_id: str
    course_slug: str
    course_title: str
    total_lessons: int
    completed_lessons: int
    in_progress_lessons: int
    progress_percentage: float
    status: str
    started_at: Optional[datetime] = None
    last_accessed_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class LearningActivityResponse(BaseModel):
    """Formatted activity item for recent event feed."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    activity_type: str
    title: str
    course_slug: Optional[str] = None
    course_title: Optional[str] = None
    lesson_slug: Optional[str] = None
    lesson_title: Optional[str] = None
    duration_seconds: Optional[int] = 0
    created_at: datetime


class DailyActivityItem(BaseModel):
    """Daily aggregated study activity for heatmaps and charts."""

    date: str
    count: int = 0
    lessons_completed: int = 0
    time_spent_seconds: int = 0


class WeeklyHoursItem(BaseModel):
    """Day of week hours distribution for weekly chart."""

    day: str
    hours: float


class OverallProgressResponse(BaseModel):
    """Student aggregate progress metrics."""

    overall_progress_percentage: float
    enrolled_courses: int
    completed_courses: int
    in_progress_courses: int
    completed_lessons: int
    total_lessons: int
    learning_hours: float
    current_streak: int
    longest_streak: int


class ContinueLearningResponse(BaseModel):
    """Active resume checkpoint for the student dashboard."""

    course_id: str
    course_slug: str
    course_title: str
    module_id: str
    module_title: str
    module_number: str
    lesson_id: str
    lesson_slug: str
    lesson_title: str
    progress_percentage: float
    estimated_time_remaining: str
    last_accessed_at: datetime


class DashboardStatsResponse(BaseModel):
    """Top-level metrics for dashboard cards."""

    overall_progress: float
    learning_hours: float
    current_streak: int
    longest_streak: int
    courses_completed: int
    courses_enrolled: int
    lessons_completed: int


class DashboardResponse(BaseModel):
    """Unified single-call dashboard payload for high frontend performance."""

    user: UserResponse
    stats: DashboardStatsResponse
    continue_learning: Optional[ContinueLearningResponse] = None
    recent_activity: List[LearningActivityResponse] = Field(default_factory=list)
    weekly_activity: List[DailyActivityItem] = Field(default_factory=list)
    weekly_hours: List[WeeklyHoursItem] = Field(default_factory=list)
    course_progress: List[CourseProgressResponse] = Field(default_factory=list)
