"""
Career Learning Roadmaps and Pipeline Progression Endpoints.
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_optional_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.roadmap import (
    RoadmapDetailResponse,
    RoadmapListResponse,
    RoadmapStepResponse,
    UserRoadmapProgressResponse,
)
from app.services.roadmap_service import roadmap_service

router = APIRouter()


@router.get(
    "",
    response_model=RoadmapListResponse,
    status_code=status.HTTP_200_OK,
    summary="List Career Roadmaps",
    description="Fetch paginated career roadmaps catalog. Includes real user progress if authenticated.",
)
async def list_roadmaps(
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=10, ge=1, le=50, description="Items per page"),
    category: Optional[str] = Query(default=None, description="Filter by category"),
    difficulty: Optional[str] = Query(default=None, description="Filter by difficulty"),
    search: Optional[str] = Query(
        default=None, description="Search roadmaps by title or description"
    ),
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db),
) -> RoadmapListResponse:
    """List career roadmaps."""
    return await roadmap_service.list_roadmaps(
        db,
        page=page,
        page_size=page_size,
        category=category,
        difficulty=difficulty,
        search=search,
        user_id=current_user.id if current_user else None,
    )


@router.get(
    "/{roadmap_id}",
    response_model=RoadmapDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Career Roadmap Details",
    description="Fetch full roadmap specification with ordered milestones and live step statuses.",
)
async def get_roadmap(
    roadmap_id: str,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db),
) -> RoadmapDetailResponse:
    """Fetch roadmap details."""
    return await roadmap_service.get_roadmap(
        db,
        identifier=roadmap_id,
        user_id=current_user.id if current_user else None,
    )


@router.get(
    "/{roadmap_id}/steps",
    response_model=List[RoadmapStepResponse],
    status_code=status.HTTP_200_OK,
    summary="Get Roadmap Steps",
    description="Fetch ordered pipeline steps for a specific career roadmap.",
)
async def get_roadmap_steps(
    roadmap_id: str,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[RoadmapStepResponse]:
    """Fetch steps for roadmap."""
    return await roadmap_service.get_roadmap_steps(
        db,
        roadmap_identifier=roadmap_id,
        user_id=current_user.id if current_user else None,
    )


@router.post(
    "/{roadmap_id}/start",
    response_model=UserRoadmapProgressResponse,
    status_code=status.HTTP_200_OK,
    summary="Start Career Roadmap",
    description="Enroll current student in a career roadmap with duplicate prevention.",
)
async def start_roadmap(
    roadmap_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UserRoadmapProgressResponse:
    """Enroll student in career roadmap."""
    return await roadmap_service.start_roadmap(
        db,
        user_id=current_user.id,
        roadmap_identifier=roadmap_id,
    )
