"""
DevOps Engineering Projects and Workflow Endpoints.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_optional_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.project import (
    ProjectDetailResponse,
    ProjectEnrollmentResponse,
    ProjectListResponse,
    ProjectProgressResponse,
    ProjectStepCompleteRequest,
    ProjectStepResponse,
)
from app.services.project_service import project_service

router = APIRouter()


@router.get(
    "",
    response_model=ProjectListResponse,
    status_code=status.HTTP_200_OK,
    summary="List Engineering Projects",
    description="Fetch paginated practical DevOps projects with search and filtering.",
)
async def list_projects(
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=10, ge=1, le=50, description="Items per page"),
    difficulty: Optional[str] = Query(default=None, description="Filter by difficulty"),
    status: Optional[str] = Query(default=None, description="Filter by status (Instructors/Admins only)"),
    featured: Optional[bool] = Query(default=None, description="Filter featured projects"),
    search: Optional[str] = Query(default=None, description="Search by title or description"),
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db),
) -> ProjectListResponse:
    """List projects catalog."""
    return await project_service.list_projects(
        db,
        page=page,
        page_size=page_size,
        search=search,
        difficulty=difficulty,
        status_filter=status,
        featured=featured,
        current_user=current_user,
    )


@router.get(
    "/my",
    response_model=List[ProjectEnrollmentResponse],
    status_code=status.HTTP_200_OK,
    summary="Get My Project Enrollments",
    description="Fetch all DevOps projects the authenticated user has enrolled in.",
)
async def get_my_projects(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[ProjectEnrollmentResponse]:
    """Fetch student project enrollments."""
    return await project_service.get_my_projects(
        db,
        user_id=current_user.id,
    )


@router.get(
    "/{project_id}",
    response_model=ProjectDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Project Details",
    description="Fetch detailed specification, sequential steps, resources, and linked courses/skills.",
)
async def get_project(
    project_id: str,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db),
) -> ProjectDetailResponse:
    """Fetch project detail by slug or UUID."""
    return await project_service.get_project_detail(
        db,
        identifier=project_id,
        current_user=current_user,
    )


@router.post(
    "/{project_id}/enroll",
    response_model=ProjectEnrollmentResponse,
    status_code=status.HTTP_200_OK,
    summary="Enroll in Project",
    description="Enroll current user in an engineering project and log activity.",
)
async def enroll_project(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ProjectEnrollmentResponse:
    """Enroll student in project."""
    return await project_service.enroll_project(
        db,
        user_id=current_user.id,
        project_identifier=project_id,
    )


@router.get(
    "/{project_id}/progress",
    response_model=ProjectProgressResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Project Progress",
    description="Fetch derived step completion progress and overall percentage for a project.",
)
async def get_project_progress(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ProjectProgressResponse:
    """Fetch project progress."""
    return await project_service.get_project_progress(
        db,
        user_id=current_user.id,
        project_identifier=project_id,
    )


@router.post(
    "/{project_id}/steps/{step_id}/start",
    response_model=ProjectStepResponse,
    status_code=status.HTTP_200_OK,
    summary="Start Project Step",
    description="Mark a specific engineering step as in-progress.",
)
async def start_step(
    project_id: str,
    step_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ProjectStepResponse:
    """Start working on a project step."""
    return await project_service.start_step(
        db,
        user_id=current_user.id,
        project_identifier=project_id,
        step_id=step_id,
    )


@router.post(
    "/{project_id}/steps/{step_id}/complete",
    response_model=ProjectProgressResponse,
    status_code=status.HTTP_200_OK,
    summary="Complete Project Step",
    description="Complete a step idempotently, recalculate completion percentage, and mark project completed if finished.",
)
async def complete_step(
    project_id: str,
    step_id: str,
    payload: Optional[ProjectStepCompleteRequest] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ProjectProgressResponse:
    """Complete a project step."""
    notes = payload.notes if payload else None
    return await project_service.complete_step(
        db,
        user_id=current_user.id,
        project_identifier=project_id,
        step_id=step_id,
        notes=notes,
    )
