"""
Certification Training Endpoints.
"""
from typing import Optional
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db, get_optional_current_user
from app.models.user import User
from app.schemas.certificate import CertificateResponse
from app.schemas.certification import (
    TrainingDetailResponse,
    TrainingProgressResponse,
    TrainingSummaryResponse,
)
from app.services.training_service import training_service

router = APIRouter()


@router.get(
    "/{training_id_or_slug}",
    response_model=TrainingDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Training Track Details",
    description="Retrieve syllabus details and linked curriculum course preview for a certification training track.",
)
async def get_training_detail(
    training_id_or_slug: str,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db),
) -> TrainingDetailResponse:
    """Fetch training track details."""
    user_id = current_user.id if current_user else None
    return await training_service.get_training_detail(
        db,
        identifier=training_id_or_slug,
        user_id=user_id,
    )


@router.post(
    "/{training_id_or_slug}/enroll",
    response_model=TrainingSummaryResponse,
    status_code=status.HTTP_200_OK,
    summary="Enroll in Certification Training",
    description="Enroll authenticated student into a structured certification training program and auto-enroll in mapped courses.",
)
async def enroll_training(
    training_id_or_slug: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> TrainingSummaryResponse:
    """Enroll student in training track."""
    return await training_service.enroll_training(
        db,
        user_id=current_user.id,
        identifier=training_id_or_slug,
    )


@router.get(
    "/{training_id_or_slug}/progress",
    response_model=TrainingProgressResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Training Progress",
    description="Fetch live lesson/module progress breakdown and certificate eligibility for a training track.",
)
async def get_training_progress(
    training_id_or_slug: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> TrainingProgressResponse:
    """Fetch student training progress."""
    return await training_service.get_training_progress(
        db,
        user_id=current_user.id,
        identifier=training_id_or_slug,
    )


@router.post(
    "/{training_id_or_slug}/complete",
    response_model=CertificateResponse,
    status_code=status.HTTP_200_OK,
    summary="Complete Certification Training & Issue Certificate",
    description="Verifies all required curriculum lessons are completed, finalizes training status, and issues CloudForge certificate idempotently.",
)
async def complete_training(
    training_id_or_slug: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> CertificateResponse:
    """Verify completion and issue certificate."""
    return await training_service.complete_training(
        db,
        user_id=current_user.id,
        identifier=training_id_or_slug,
    )
