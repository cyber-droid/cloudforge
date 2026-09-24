"""
Career Roadmap and Step Progression Pydantic v2 Schemas.
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class RoadmapStepResponse(BaseModel):
    """Step node within a career learning path."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    roadmap_id: str
    title: str
    description: Optional[str] = None
    step_type: str
    order_index: int
    required: bool
    estimated_hours: str
    skills: List[str] = Field(default_factory=list)
    course_id: Optional[str] = None
    course_slug: Optional[str] = None
    course_title: Optional[str] = None
    skill_id: Optional[str] = None
    skill_slug: Optional[str] = None
    skill_name: Optional[str] = None
    status: str = "upcoming"  # 'completed', 'in-progress', 'upcoming'
    completed: bool = False


class RoadmapSummaryResponse(BaseModel):
    """Catalog summary of a career roadmap."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    slug: str
    title: str
    description: Optional[str] = None
    category: str
    difficulty: str
    duration: str  # duration_label in ORM
    skills_count: int
    projects_count: int
    progress: float = 0.0
    certifications_targeted: List[str] = Field(default_factory=list)
    nodes: List[RoadmapStepResponse] = Field(default_factory=list)
    published: bool = True
    created_at: Optional[datetime] = None


class RoadmapDetailResponse(RoadmapSummaryResponse):
    """Full detail view of roadmap with ordered pipeline steps."""

    pass


class RoadmapListResponse(BaseModel):
    """Paginated roadmaps catalog."""

    items: List[RoadmapSummaryResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class UserRoadmapProgressResponse(BaseModel):
    """Active user roadmap enrollment and step advancement tracking."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    roadmap_id: str
    status: str
    progress_percentage: float
    completed_steps: int
    total_required_steps: int
    started_at: datetime
    completed_at: Optional[datetime] = None
    last_accessed_at: datetime
    roadmap: RoadmapSummaryResponse
