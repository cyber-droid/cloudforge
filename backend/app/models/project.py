"""
Project, ProjectStep, ProjectResource, UserProjectEnrollment, and ProjectStepProgress Database Models.

Why these entities exist:
1. Project: Represents realistic DevOps and Cloud engineering capstones where students build,
   break, troubleshoot, observe, and document cloud architectures.
2. ProjectStep: Deterministic sequential engineering milestones (Learn -> Build -> Break -> Troubleshoot -> Fix -> Document -> Automate).
3. ProjectResource: Architecture diagrams, repositories, and documentation guides.
4. UserProjectEnrollment: Tracks user project enrollment state with uniqueness constraints on (user_id, project_id).
5. ProjectStepProgress: Tracks granular step progress per user with derived project completion.
6. ProjectCourse & ProjectSkill: Many-to-Many associations connecting projects to curriculum courses and skill competencies.
"""

import enum
import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, List, Optional

if TYPE_CHECKING:
    from app.models.course import Course
    from app.models.skill import Skill
    from app.models.user import User

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin


class ProjectDifficulty(str, enum.Enum):
    """Standardized project difficulty levels."""

    BEGINNER = "Beginner"
    INTERMEDIATE = "Intermediate"
    ADVANCED = "Advanced"


class ProjectStatus(str, enum.Enum):
    """Lifecycle status for project discovery."""

    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class StepType(str, enum.Enum):
    """DevOps engineering workflow phase types."""

    LEARN = "learn"
    BUILD = "build"
    CONFIGURE = "configure"
    TEST = "test"
    BREAK = "break"
    TROUBLESHOOT = "troubleshoot"
    DEPLOY = "deploy"
    OBSERVE = "observe"
    DOCUMENT = "document"


class ProjectEnrollmentStatus(str, enum.Enum):
    """User project progress status."""

    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class StepProgressStatus(str, enum.Enum):
    """Status of an individual project step for a user."""

    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class ProjectResourceType(str, enum.Enum):
    """Types of supplementary engineering resources."""

    DOCUMENTATION = "documentation"
    REPOSITORY = "repository"
    DIAGRAM = "diagram"
    TUTORIAL = "tutorial"
    REFERENCE = "reference"
    GUIDE = "guide"


class ProjectCourse(Base):
    """Many-to-Many association between Projects and Courses."""

    __tablename__ = "project_courses"

    project_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("projects.id", ondelete="CASCADE"),
        primary_key=True,
    )
    course_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("courses.id", ondelete="CASCADE"),
        primary_key=True,
    )


class ProjectSkill(Base):
    """Many-to-Many association between Projects and Skills."""

    __tablename__ = "project_skills"

    project_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("projects.id", ondelete="CASCADE"),
        primary_key=True,
    )
    skill_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("skills.id", ondelete="CASCADE"),
        primary_key=True,
    )


class Project(Base, TimestampMixin):
    """Hands-on CloudForge DevOps & Cloud engineering project."""

    __tablename__ = "projects"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        index=True,
    )
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    slug: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        index=True,
        nullable=False,
    )
    short_description: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
    )
    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    difficulty: Mapped[str] = mapped_column(
        String(50),
        default=ProjectDifficulty.INTERMEDIATE.value,
        index=True,
        nullable=False,
    )
    estimated_hours: Mapped[str] = mapped_column(
        String(50),
        default="14 hours",
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(50),
        default=ProjectStatus.PUBLISHED.value,
        index=True,
        nullable=False,
    )
    featured: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        index=True,
        nullable=False,
    )
    prerequisites: Mapped[List[str]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
    )
    learning_objectives: Mapped[List[str]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
    )
    deliverables: Mapped[List[str]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
    )
    technologies: Mapped[List[str]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
    )
    architecture_overview: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    repository_url: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
    )
    documentation_url: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
    )

    # Relationships
    steps: Mapped[List["ProjectStep"]] = relationship(
        "ProjectStep",
        back_populates="project",
        cascade="all, delete-orphan",
        order_by="ProjectStep.step_order",
        lazy="selectin",
    )
    resources: Mapped[List["ProjectResource"]] = relationship(
        "ProjectResource",
        back_populates="project",
        cascade="all, delete-orphan",
        order_by="ProjectResource.display_order",
        lazy="selectin",
    )
    courses: Mapped[List["Course"]] = relationship(
        "Course",
        secondary="project_courses",
        lazy="selectin",
    )
    skills: Mapped[List["Skill"]] = relationship(
        "Skill",
        secondary="project_skills",
        lazy="selectin",
    )
    enrollments: Mapped[List["UserProjectEnrollment"]] = relationship(
        "UserProjectEnrollment",
        back_populates="project",
        cascade="all, delete-orphan",
    )


class ProjectStep(Base, TimestampMixin):
    """Sequential engineering milestone within a project."""

    __tablename__ = "project_steps"
    __table_args__ = (
        UniqueConstraint("project_id", "step_order", name="uq_project_step_order"),
    )

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        index=True,
    )
    project_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    step_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    step_type: Mapped[str] = mapped_column(
        String(50),
        default=StepType.BUILD.value,
        nullable=False,
    )
    instructions: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    command: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
    )
    expected_outcome: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    is_required: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    # Relationships
    project: Mapped["Project"] = relationship(
        "Project",
        back_populates="steps",
    )


class ProjectResource(Base, TimestampMixin):
    """Supplementary engineering assets, repositories, and diagrams."""

    __tablename__ = "project_resources"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        index=True,
    )
    project_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    resource_type: Mapped[str] = mapped_column(
        String(50),
        default=ProjectResourceType.DOCUMENTATION.value,
        nullable=False,
    )
    url: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    display_order: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    # Relationships
    project: Mapped["Project"] = relationship(
        "Project",
        back_populates="resources",
    )


class UserProjectEnrollment(Base, TimestampMixin):
    """Tracks a user's enrollment and progress state in a project."""

    __tablename__ = "user_project_enrollments"
    __table_args__ = (
        UniqueConstraint("user_id", "project_id", name="uq_user_project_enrollment"),
    )

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        index=True,
    )
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    project_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    status: Mapped[str] = mapped_column(
        String(50),
        default=ProjectEnrollmentStatus.IN_PROGRESS.value,
        nullable=False,
        index=True,
    )
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    last_activity_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    project: Mapped["Project"] = relationship(
        "Project",
        back_populates="enrollments",
        lazy="joined",
    )
    user: Mapped["User"] = relationship(
        "User",
        lazy="joined",
    )


class ProjectStepProgress(Base, TimestampMixin):
    """User completion records for individual project steps."""

    __tablename__ = "project_step_progress"
    __table_args__ = (
        UniqueConstraint(
            "user_id", "project_step_id", name="uq_user_project_step_progress"
        ),
    )

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        index=True,
    )
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    project_step_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("project_steps.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    status: Mapped[str] = mapped_column(
        String(50),
        default=StepProgressStatus.COMPLETED.value,
        nullable=False,
        index=True,
    )
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    notes: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    # Relationships
    project_step: Mapped["ProjectStep"] = relationship(
        "ProjectStep",
        lazy="joined",
    )
