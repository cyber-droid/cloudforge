"""
Roadmap, RoadmapStep, and UserRoadmapProgress Database Models.

Why these entities exist:
1. Roadmap: Represents structured career pathways (Cloud Engineer, DevOps Engineer, DevSecOps Engineer, AI + DevOps Engineer).
2. RoadmapStep: Sequential milestones in the career progression referencing courses, skills, or capstone milestones.
3. UserRoadmapProgress: Tracks student enrollment and active milestones in roadmaps.
"""
import enum
import uuid
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import (
    Boolean,
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class RoadmapStepType(str, enum.Enum):
    """Types of steps in a career learning roadmap."""
    COURSE = "course"
    SKILL = "skill"
    MILESTONE = "milestone"


class RoadmapStatus(str, enum.Enum):
    """User roadmap progression state."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class Roadmap(Base, TimestampMixin):
    """Career Learning Roadmap entity."""
    __tablename__ = "roadmaps"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        index=True,
    )
    slug: Mapped[str] = mapped_column(
        String(150),
        unique=True,
        index=True,
        nullable=False,
    )
    title: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    category: Mapped[str] = mapped_column(
        String(50),
        index=True,
        nullable=False,
    )
    difficulty: Mapped[str] = mapped_column(
        String(50),
        default="Beginner to Intermediate",
        nullable=False,
    )
    duration_label: Mapped[str] = mapped_column(
        String(50),
        default="4-6 months",
        nullable=False,
    )
    skills_count: Mapped[int] = mapped_column(
        Integer,
        default=18,
        nullable=False,
    )
    projects_count: Mapped[int] = mapped_column(
        Integer,
        default=4,
        nullable=False,
    )
    published: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )
    certifications_targeted: Mapped[List[str]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
    )

    # Relationships
    steps: Mapped[List["RoadmapStep"]] = relationship(
        "RoadmapStep",
        back_populates="roadmap",
        cascade="all, delete-orphan",
        order_by="RoadmapStep.order_index",
        lazy="selectin",
    )
    user_progresses: Mapped[List["UserRoadmapProgress"]] = relationship(
        "UserRoadmapProgress",
        back_populates="roadmap",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class RoadmapStep(Base, TimestampMixin):
    """Sequential stage in a career learning roadmap."""
    __tablename__ = "roadmap_steps"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        index=True,
    )
    roadmap_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("roadmaps.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    title: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    step_type: Mapped[str] = mapped_column(
        String(50),
        default=RoadmapStepType.COURSE.value,
        nullable=False,
    )
    order_index: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    required: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )
    estimated_hours: Mapped[str] = mapped_column(
        String(50),
        default="25h",
        nullable=False,
    )
    skills_covered: Mapped[List[str]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
    )

    # Optional references to curriculum entities
    course_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("courses.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    skill_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("skills.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    project_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        nullable=True,
    )
    certification_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        nullable=True,
    )

    # Relationships
    roadmap: Mapped["Roadmap"] = relationship("Roadmap", back_populates="steps", lazy="selectin")
    course: Mapped[Optional["Course"]] = relationship("Course", lazy="selectin")
    skill: Mapped[Optional["Skill"]] = relationship("Skill", lazy="selectin")


class UserRoadmapProgress(Base, TimestampMixin):
    """User started career roadmap tracking."""
    __tablename__ = "user_roadmap_progress"
    __table_args__ = (
        UniqueConstraint("user_id", "roadmap_id", name="uq_user_roadmap"),
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
        index=True,
        nullable=False,
    )
    roadmap_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("roadmaps.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(20),
        default=RoadmapStatus.IN_PROGRESS.value,
        nullable=False,
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
    last_accessed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    user: Mapped["User"] = relationship("User", lazy="selectin")
    roadmap: Mapped["Roadmap"] = relationship("Roadmap", back_populates="user_progresses", lazy="selectin")
