"""
Practice Exam and Quiz Endpoints.
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.certification import (
    PracticeAttemptDetailResponse,
    PracticeAttemptResultResponse,
    PracticeAttemptStartRequest,
    PracticeAttemptSubmitRequest,
    PracticeAttemptSummaryResponse,
)
from app.services.practice_service import practice_service

router = APIRouter()


@router.post(
    "/certifications/{certification_id}/practice-attempts",
    response_model=PracticeAttemptDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Start Practice Quiz or Timed Mock Exam",
    description="Initiates an exam session and returns question bank items strictly OMITTING correct answers.",
)
async def start_practice_attempt(
    certification_id: str,
    data: PracticeAttemptStartRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> PracticeAttemptDetailResponse:
    """Start practice attempt session."""
    return await practice_service.start_attempt(
        db,
        user_id=current_user.id,
        certification_id=certification_id,
        data=data,
    )


@router.get(
    "/practice-attempts",
    response_model=List[PracticeAttemptSummaryResponse],
    status_code=status.HTTP_200_OK,
    summary="List Practice Exam Attempts",
    description="Retrieve student's exam history, scores, and pass/fail statuses.",
)
async def list_practice_attempts(
    certification_id: Optional[str] = Query(default=None),
    attempt_type: Optional[str] = Query(default=None),
    passed_only: Optional[bool] = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[PracticeAttemptSummaryResponse]:
    """List exam attempt history."""
    return await practice_service.list_user_attempts(
        db,
        user_id=current_user.id,
        certification_id=certification_id,
        attempt_type=attempt_type,
        passed_only=passed_only,
        skip=skip,
        limit=limit,
    )


@router.post(
    "/practice-attempts/{attempt_id}/submit",
    response_model=PracticeAttemptResultResponse,
    status_code=status.HTTP_200_OK,
    summary="Submit Practice Exam Answers",
    description="Evaluates answers server-side, calculates percentage and pass/fail, and unlocks question explanations.",
)
async def submit_practice_attempt(
    attempt_id: str,
    data: PracticeAttemptSubmitRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> PracticeAttemptResultResponse:
    """Submit attempt and calculate score."""
    return await practice_service.submit_attempt(
        db,
        user_id=current_user.id,
        attempt_id=attempt_id,
        data=data,
    )


@router.get(
    "/practice-attempts/{attempt_id}/results",
    response_model=PracticeAttemptResultResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Practice Exam Results & Review",
    description="Retrieve score breakdown and detailed question-by-question explanations for a submitted exam attempt.",
)
async def get_practice_attempt_results(
    attempt_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> PracticeAttemptResultResponse:
    """Get exam results and explanation reviews."""
    return await practice_service.get_attempt_results(
        db,
        user_id=current_user.id,
        attempt_id=attempt_id,
    )
