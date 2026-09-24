"""
User Account, Profile, Enrollment, Learning Progress, Skills, and Roadmap Endpoints.
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.course import CourseEnrollmentResponse
from app.schemas.progress import (
    ContinueLearningResponse,
    CourseProgressResponse,
    DailyActivityItem,
    DashboardResponse,
    LearningActivityResponse,
    OverallProgressResponse,
)
from app.schemas.roadmap import UserRoadmapProgressResponse
from app.schemas.skill import UserSkillMatrixResponse, UserSkillResponse
from app.schemas.user import UserResponse, UserUpdate
from app.services.course_service import course_service
from app.services.progress_service import progress_service
from app.services.roadmap_service import roadmap_service
from app.services.skill_service import skill_service
from app.services.user_service import user_service

router = APIRouter()


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Current User Profile",
    description="Fetch profile and preference details for the currently authenticated user.",
)
async def get_me(current_user: User = Depends(get_current_user)) -> UserResponse:
    """Return current authenticated user object."""
    return UserResponse.model_validate(current_user)


@router.patch(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Current User Profile",
    description="Update user display name, avatar, learning goal, terminal theme/font, and notification preferences.",
)
async def update_me(
    data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """Update profile and preference settings."""
    return await user_service.update_profile(db, current_user=current_user, data=data)


@router.get(
    "/me/courses",
    response_model=List[CourseEnrollmentResponse],
    status_code=status.HTTP_200_OK,
    summary="Get Enrolled Courses",
    description="Fetch list of courses currently enrolled by the authenticated student.",
)
async def get_my_courses(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> List[CourseEnrollmentResponse]:
    """Return student's active enrollments."""
    return await course_service.get_user_courses(db, user_id=current_user.id)


@router.get(
    "/me/courses/{course_id}",
    response_model=CourseEnrollmentResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Course Enrollment Status",
    description="Fetch enrollment details for a specific course by UUID or slug.",
)
async def get_my_course_enrollment(
    course_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> CourseEnrollmentResponse:
    """Return enrollment status for single course."""
    return await course_service.get_user_course_enrollment(
        db,
        user_id=current_user.id,
        course_identifier=course_id,
    )


@router.get(
    "/me/courses/{course_id}/progress",
    response_model=CourseProgressResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Specific Course Progress",
    description="Calculate course progress from actual published lesson records.",
)
async def get_my_course_progress(
    course_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> CourseProgressResponse:
    """Return calculated progress stats for a course."""
    return await progress_service.get_course_progress(
        db,
        user_id=current_user.id,
        course_identifier=course_id,
    )


@router.get(
    "/me/progress",
    response_model=OverallProgressResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Overall Learning Progress",
    description="Fetch student's overall progress percentage, study hours, active and longest streaks.",
)
async def get_my_overall_progress(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> OverallProgressResponse:
    """Return aggregated progress metrics for the student."""
    return await progress_service.get_overall_progress(db, user_id=current_user.id)


@router.get(
    "/me/continue-learning",
    response_model=Optional[ContinueLearningResponse],
    status_code=status.HTTP_200_OK,
    summary="Get Resume Learning Target",
    description="Retrieve the most recently accessed incomplete lesson or first incomplete lesson in enrolled curriculum.",
)
async def get_my_continue_learning(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> Optional[ContinueLearningResponse]:
    """Return the next actionable curriculum resume card."""
    return await progress_service.get_continue_learning(db, user_id=current_user.id)


@router.get(
    "/me/activity",
    response_model=List[DailyActivityItem],
    status_code=status.HTTP_200_OK,
    summary="Get Daily Learning Activity Aggregates",
    description="Aggregate study time and completed lessons by calendar date for the specified period ('week', 'month', 'year').",
)
async def get_my_activity(
    period: str = Query(
        default="week", description="Aggregation period: 'week', 'month', 'year'"
    ),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[DailyActivityItem]:
    """Return calendar activity aggregated metrics for heatmaps and charts."""
    return await progress_service.get_daily_activity(
        db, user_id=current_user.id, period=period
    )


@router.get(
    "/me/activity/recent",
    response_model=List[LearningActivityResponse],
    status_code=status.HTTP_200_OK,
    summary="Get Recent Learning Activities",
    description="Fetch recent chronological timeline events (started/completed lessons, enrolled courses).",
)
async def get_my_recent_activity(
    limit: int = Query(default=10, ge=1, le=50, description="Max activities to return"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[LearningActivityResponse]:
    """Return recent student activity feed."""
    return await progress_service.get_recent_activity(
        db, user_id=current_user.id, limit=limit
    )


@router.get(
    "/me/dashboard",
    response_model=DashboardResponse,
    status_code=status.HTTP_200_OK,
    summary="Unified Student Dashboard API",
    description="Single high-performance endpoint consolidating stats, streak, continue-learning, and recent activity.",
)
async def get_my_dashboard(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> DashboardResponse:
    """Return complete real PostgreSQL-backed student dashboard state."""
    return await progress_service.get_dashboard(db, user=current_user)


# ==========================================
# Phase 5: Technical Skills Endpoints
# ==========================================


@router.get(
    "/me/skills",
    response_model=UserSkillMatrixResponse,
    status_code=status.HTTP_200_OK,
    summary="Get User Technical Skill Matrix",
    description="Calculates student proficiency across all engineering competencies based on lesson & course completions.",
)
async def get_my_skills(
    category: Optional[str] = Query(default=None, description="Optional domain filter"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UserSkillMatrixResponse:
    """Return student skill proficiency matrix."""
    return await skill_service.get_user_skill_matrix(
        db, user_id=current_user.id, category=category
    )


@router.get(
    "/me/skills/{skill_id}",
    response_model=UserSkillResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Single User Skill Progress",
    description="Fetch calculated proficiency, current level, target level, and related courses for a skill.",
)
async def get_my_skill_detail(
    skill_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UserSkillResponse:
    """Return calculated user skill detail."""
    return await skill_service.get_user_skill_detail(
        db, user_id=current_user.id, identifier=skill_id
    )


@router.post(
    "/me/skills/{skill_id}/recalculate",
    response_model=UserSkillResponse,
    status_code=status.HTTP_200_OK,
    summary="Recalculate User Skill",
    description="Force re-evaluation of user skill evidence from learning progress.",
)
async def recalculate_my_skill(
    skill_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UserSkillResponse:
    """Recalculate user skill from verified evidence."""
    return await skill_service.get_user_skill_detail(
        db, user_id=current_user.id, identifier=skill_id
    )


# ==========================================
# Phase 5: Career Roadmaps Endpoints
# ==========================================


@router.get(
    "/me/roadmaps",
    response_model=List[UserRoadmapProgressResponse],
    status_code=status.HTTP_200_OK,
    summary="Get User Started Roadmaps",
    description="Fetch career roadmaps started by the student with calculated step completions and progress.",
)
async def get_my_roadmaps(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> List[UserRoadmapProgressResponse]:
    """Return roadmaps started by student."""
    return await roadmap_service.get_user_roadmaps(db, user_id=current_user.id)


@router.get(
    "/me/roadmaps/{roadmap_id}",
    response_model=UserRoadmapProgressResponse,
    status_code=status.HTTP_200_OK,
    summary="Get User Roadmap Progress",
    description="Fetch single career roadmap progress with evaluated pipeline milestones.",
)
async def get_my_roadmap_progress(
    roadmap_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UserRoadmapProgressResponse:
    """Return user progress for roadmap."""
    return await roadmap_service.get_user_roadmap_progress(
        db,
        user_id=current_user.id,
        roadmap_identifier=roadmap_id,
    )
