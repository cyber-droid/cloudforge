"""
Course, Module, Lesson, Resource, and Enrollment Pydantic Schemas.
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class InstructorSchema(BaseModel):
    """Course instructor details."""

    model_config = ConfigDict(from_attributes=True)

    name: Optional[str] = None
    role: Optional[str] = None
    avatar: Optional[str] = None
    verified: bool = True


class LessonResourceResponse(BaseModel):
    """Resource attached to a lesson."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    lesson_id: str
    title: str
    resource_type: str
    url: str
    description: Optional[str] = None
    order_index: int


class LessonSummaryResponse(BaseModel):
    """Lightweight lesson representation for curriculum tree."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    slug: str
    lesson_type: str = "theory"
    estimated_minutes: int
    order_index: int
    published: bool


class LessonDetailResponse(BaseModel):
    """Complete lesson payload with markdown content and resources."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    module_id: str
    title: str
    slug: str
    description: Optional[str] = None
    content: str
    lesson_type: str
    estimated_minutes: int
    order_index: int
    video_url: Optional[str] = None
    published: bool
    resources: List[LessonResourceResponse] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime


class ModuleSummaryResponse(BaseModel):
    """Module summary with embedded ordered lessons."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    course_id: str
    module_number: str
    title: str
    description: Optional[str] = None
    order_index: int
    published: bool
    lessons_count: int = 0
    lessons: List[LessonSummaryResponse] = Field(default_factory=list)


class ModuleDetailResponse(BaseModel):
    """Module detail with full lesson list."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    course_id: str
    module_number: str
    title: str
    description: Optional[str] = None
    order_index: int
    published: bool
    lessons: List[LessonDetailResponse] = Field(default_factory=list)


class CourseSummaryResponse(BaseModel):
    """Course catalog card and list schema."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    slug: str
    title: str
    description: str
    category: str
    difficulty: str
    duration_minutes: int
    thumbnail_url: Optional[str] = None
    rating: float
    students_count: int
    certificate_available: bool
    published: bool
    technologies: List[str] = Field(default_factory=list)
    learning_outcomes: List[str] = Field(default_factory=list)
    instructor_name: Optional[str] = None
    instructor_role: Optional[str] = None
    instructor_avatar: Optional[str] = None
    instructor_verified: bool = True
    modules_count: int = 0
    lessons_count: int = 0
    created_at: datetime


class CourseDetailResponse(CourseSummaryResponse):
    """Complete course detail including curriculum syllabus."""

    long_description: Optional[str] = None
    modules: List[ModuleSummaryResponse] = Field(default_factory=list)


class CourseListResponse(BaseModel):
    """Paginated course list payload."""

    items: List[CourseSummaryResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class CourseCurriculumResponse(BaseModel):
    """Course Curriculum tree."""

    model_config = ConfigDict(from_attributes=True)

    course_id: str
    course_title: str
    course_slug: str
    modules: List[ModuleSummaryResponse] = Field(default_factory=list)


class CourseEnrollmentResponse(BaseModel):
    """Student course enrollment record."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    course_id: str
    status: str
    enrolled_at: datetime
    completed_at: Optional[datetime] = None
    course: Optional[CourseSummaryResponse] = None
