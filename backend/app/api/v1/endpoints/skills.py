"""
Technical Skills and Competency Matrix Endpoints.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_optional_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.skill import (
    SkillSummaryResponse,
    UserSkillMatrixResponse,
    UserSkillResponse,
)
from app.services.skill_service import skill_service

router = APIRouter()


@router.get(
    "",
    response_model=List[SkillSummaryResponse],
    status_code=status.HTTP_200_OK,
    summary="List Technical Skills",
    description="Fetch list of all engineering competency skills with optional domain category filter."
)
async def list_skills(
    category: Optional[str] = Query(default=None, description="Filter by domain category (e.g. Cloud, DevOps, Kubernetes)"),
    search: Optional[str] = Query(default=None, description="Search skill name or description"),
    db: AsyncSession = Depends(get_db),
) -> List[SkillSummaryResponse]:
    """Fetch skills catalog."""
    return await skill_service.list_skills(db, category=category, search=search)


@router.get(
    "/{skill_id}",
    response_model=SkillSummaryResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Skill Details",
    description="Fetch single technical skill definition by UUID or slug."
)
async def get_skill(
    skill_id: str,
    db: AsyncSession = Depends(get_db),
) -> SkillSummaryResponse:
    """Fetch single skill details."""
    skill = await skill_service.get_skill(db, identifier=skill_id)
    return SkillSummaryResponse(
        id=skill.id,
        slug=skill.slug,
        name=skill.name,
        description=skill.description,
        category=skill.category,
        target_level=skill.target_level,
        trend=skill.trend or "+5%",
        courses_count=len(skill.courses or []),
        created_at=skill.created_at,
    )
