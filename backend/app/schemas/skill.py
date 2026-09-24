"""
Skill and User Competency Pydantic v2 Schemas.
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class SkillCourseReference(BaseModel):
    """Brief course preview linked to a technical skill."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    slug: str
    title: str


class SkillSummaryResponse(BaseModel):
    """Catalog preview for a technical skill competency."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    slug: str
    name: str
    description: Optional[str] = None
    category: str
    target_level: int
    target_level_name: str = "Advanced"
    trend: str = "+5%"
    courses_count: int = 0
    related_courses: List[SkillCourseReference] = Field(default_factory=list)
    created_at: Optional[datetime] = None


class UserSkillResponse(BaseModel):
    """Student competency score and derived level for a single skill."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    skill_id: str
    slug: str
    name: str
    category: str
    current_level: int
    current_level_name: str
    target_level: int
    target_level_name: str
    proficiency_percentage: float
    trend: str = "+5%"
    related_courses: List[SkillCourseReference] = Field(default_factory=list)
    last_updated_at: Optional[datetime] = None


class UserSkillMatrixResponse(BaseModel):
    """Aggregated competency matrix for student profile & dashboard widgets."""

    skills: List[UserSkillResponse]
    total_skills: int
    average_proficiency: float
