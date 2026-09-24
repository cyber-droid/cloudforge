"""
Pydantic v2 Schemas for Projects, Project Steps, Resources, Enrollments, and Progress.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class ProjectCourseReference(BaseModel):
    """Curriculum course linked to a project."""
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    slug: str
    category: Optional[str] = None
    difficulty: Optional[str] = None


class ProjectSkillReference(BaseModel):
    """Competency skill linked to a project."""
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    slug: str
    category: Optional[str] = None
    target_level: Optional[int] = None


class ProjectStepResponse(BaseModel):
    """Individual engineering milestone inside a project."""
    model_config = ConfigDict(from_attributes=True)

    id: str
    project_id: str
    title: str
    description: Optional[str] = None
    step_order: int
    step_type: str
    instructions: Optional[str] = None
    command: Optional[str] = None
    expected_outcome: Optional[str] = None
    is_required: bool = True
    completed: bool = False
    status: str = "not_started"  # 'not_started', 'in_progress', 'completed'
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class ProjectResourceResponse(BaseModel):
    """Supplementary asset, architecture diagram, or repository."""
    model_config = ConfigDict(from_attributes=True)

    id: str
    project_id: str
    title: str
    resource_type: str
    url: str
    description: Optional[str] = None
    display_order: int = 0


class ProjectStepProgressResponse(BaseModel):
    """Granular user progress record for a single project step."""
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    project_step_id: str
    status: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    notes: Optional[str] = None


class ProjectStepCompleteRequest(BaseModel):
    """Optional payload when completing a project step."""
    notes: Optional[str] = None


class ProjectSummaryResponse(BaseModel):
    """Catalog summary of a DevOps engineering project."""
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    slug: str
    short_description: Optional[str] = None
    description: str
    difficulty: str
    estimated_hours: str
    status: str
    featured: bool
    technologies: List[str] = Field(default_factory=list)
    deliverables: List[str] = Field(default_factory=list)
    repository_url: Optional[str] = None
    documentation_url: Optional[str] = None
    progress: float = 0.0  # Alias for progress_percentage
    progress_percentage: float = 0.0
    user_status: str = "not_started"
    completed_steps: int = 0
    total_steps: int = 0
    skills: List[str] = Field(default_factory=list)
    created_at: Optional[datetime] = None


class ProjectDetailResponse(ProjectSummaryResponse):
    """Full detailed view of an engineering project including syllabus and resources."""
    architecture_overview: Optional[str] = None
    prerequisites: List[str] = Field(default_factory=list)
    learning_objectives: List[str] = Field(default_factory=list)
    steps: List[ProjectStepResponse] = Field(default_factory=list)
    resources: List[ProjectResourceResponse] = Field(default_factory=list)
    related_courses: List[ProjectCourseReference] = Field(default_factory=list)
    related_skills: List[ProjectSkillReference] = Field(default_factory=list)


class ProjectListResponse(BaseModel):
    """Paginated project listing response."""
    items: List[ProjectSummaryResponse]
    total: int
    page: int
    page_size: int


class ProjectEnrollmentResponse(BaseModel):
    """User project enrollment state."""
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    project_id: str
    status: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    last_activity_at: datetime
    progress_percentage: float = 0.0
    completed_steps: int = 0
    total_steps: int = 0
    project: Optional[ProjectSummaryResponse] = None


class ProjectProgressResponse(BaseModel):
    """Live calculated progress breakdown for a project."""
    project_id: str
    user_id: str
    status: str
    progress_percentage: float
    completed_steps: int
    total_steps: int
    is_completed: bool
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    last_activity_at: Optional[datetime] = None
    steps: List[ProjectStepResponse] = Field(default_factory=list)


class ProjectCreate(BaseModel):
    """Payload for creating a new project (Admin/Instructor)."""
    title: str
    slug: str
    short_description: Optional[str] = None
    description: str
    difficulty: str = "Intermediate"
    estimated_hours: str = "14 hours"
    status: str = "published"
    featured: bool = False
    prerequisites: List[str] = Field(default_factory=list)
    learning_objectives: List[str] = Field(default_factory=list)
    deliverables: List[str] = Field(default_factory=list)
    technologies: List[str] = Field(default_factory=list)
    architecture_overview: Optional[str] = None
    repository_url: Optional[str] = None
    documentation_url: Optional[str] = None
    course_ids: List[str] = Field(default_factory=list)
    skill_ids: List[str] = Field(default_factory=list)


class ProjectUpdate(BaseModel):
    """Payload for updating project metadata."""
    title: Optional[str] = None
    slug: Optional[str] = None
    short_description: Optional[str] = None
    description: Optional[str] = None
    difficulty: Optional[str] = None
    estimated_hours: Optional[str] = None
    status: Optional[str] = None
    featured: Optional[bool] = None
    prerequisites: Optional[List[str]] = None
    learning_objectives: Optional[List[str]] = None
    deliverables: Optional[List[str]] = None
    technologies: Optional[List[str]] = None
    architecture_overview: Optional[str] = None
    repository_url: Optional[str] = None
    documentation_url: Optional[str] = None
    course_ids: Optional[List[str]] = None
    skill_ids: Optional[List[str]] = None
