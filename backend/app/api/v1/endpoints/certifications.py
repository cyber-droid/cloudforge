"""
Certifications API Endpoints.
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_optional_current_user
from app.models.user import User
from app.repositories.certification_repo import certification_repo
from app.schemas.certification import (
    CertificationDetailResponse,
    CertificationListResponse,
    TrainingSummaryResponse,
)
from app.services.certification_service import certification_service

router = APIRouter()


@router.get(
    "",
    response_model=CertificationListResponse,
    status_code=status.HTTP_200_OK,
    summary="List Certifications Catalog",
    description="Fetch published certifications and exam prep programs with provider/level filtering.",
)
async def list_certifications(
    provider: Optional[str] = Query(
        default=None,
        description="Filter by cloud provider (AWS, Microsoft Azure, Kubernetes, DevOps)",
    ),
    level: Optional[str] = Query(
        default=None,
        description="Filter by level (Foundational, Associate, Professional)",
    ),
    category: Optional[str] = Query(
        default=None, description="Filter by domain category"
    ),
    search: Optional[str] = Query(
        default=None, description="Search term for code, title, or description"
    ),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db),
) -> CertificationListResponse:
    """List certifications with readiness calculated when authenticated."""
    user_id = current_user.id if current_user else None
    return await certification_service.list_certifications(
        db,
        user_id=user_id,
        provider=provider,
        level=level,
        category=category,
        search=search,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/{slug_or_id}",
    response_model=CertificationDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Certification Details",
    description="Retrieve comprehensive certification blueprint, domain weightings, trainings, and user readiness.",
)
async def get_certification(
    slug_or_id: str,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db),
) -> CertificationDetailResponse:
    """Fetch single certification detail."""
    user_id = current_user.id if current_user else None
    return await certification_service.get_certification_detail(
        db,
        identifier=slug_or_id,
        user_id=user_id,
    )


@router.get(
    "/{certification_id}/trainings",
    response_model=List[TrainingSummaryResponse],
    status_code=status.HTTP_200_OK,
    summary="Get Training Tracks for Certification",
    description="Retrieve structured training curriculum tracks associated with a certification program.",
)
async def get_certification_trainings(
    certification_id: str,
    db: AsyncSession = Depends(get_db),
) -> List[TrainingSummaryResponse]:
    """List training tracks linked to a certification."""
    cert = await certification_repo.get_by_id_or_slug(db, identifier=certification_id)
    if not cert:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Certification '{certification_id}' not found.",
        )

    trainings = await certification_repo.get_trainings_for_cert(
        db, certification_id=cert.id
    )
    return [
        TrainingSummaryResponse(
            id=t.id,
            certification_id=t.certification_id,
            title=t.title,
            slug=t.slug,
            description=t.description,
            level=t.level,
            estimated_hours=t.estimated_hours,
            course_id=t.course_id,
            modules=t.modules or [],
            is_published=t.is_published,
            created_at=t.created_at,
        )
        for t in trainings
    ]
