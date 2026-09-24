"""
Course, Module, Lesson, Resource, and Enrollment Database Models.

Why these entities exist:
1. Course: The root curriculum entity supporting multi-domain engineering pathways.
2. CourseModule & Lesson: Two-tier curriculum hierarchy preserving ordered pedagogical progression.
3. LessonResource: Attached artifacts (GitHub repos, RFCs, manifests) for deep hands-on learning.
4. CourseEnrollment: Tracks student enrollment status (active, completed, cancelled) with uniqueness enforcement.
"""

import enum
import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, List, Optional

if TYPE_CHECKING:
    from app.models.skill import Skill

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin


class CourseCategory(str, enum.Enum):
    """CloudForge Curriculum Domain Categories."""

    CLOUD = "Cloud"
    DEVOPS = "DevOps"
    DEVSECOPS = "DevSecOps"
    KUBERNETES = "Kubernetes"
    SECURITY = "Security"
    OBSERVABILITY = "Observability"
    AI = "AI"
    IAC = "Infrastructure as Code"


class CourseDifficulty(str, enum.Enum):
    """Curriculum Experience Levels."""

    BEGINNER = "Beginner"
    INTERMEDIATE = "Intermediate"
    ADVANCED = "Advanced"
    BEGINNER_TO_INTERMEDIATE = "Beginner to Intermediate"


class EnrollmentStatus(str, enum.Enum):
    """Student Enrollment Status."""

    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Course(Base, TimestampMixin):
    """Root Course entity."""

    __tablename__ = "courses"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        index=True,
    )
    slug: Mapped[str] = mapped_column(
        String(120),
        unique=True,
        index=True,
        nullable=False,
    )
    title: Mapped[str] = mapped_column(
        String(200),
        index=True,
        nullable=False,
    )
    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    long_description: Mapped[Optional[str]] = mapped_column(
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
        index=True,
        nullable=False,
    )
    duration_minutes: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    thumbnail_url: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
    )
    rating: Mapped[float] = mapped_column(
        Float,
        default=4.9,
        nullable=False,
    )
    students_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    certificate_available: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )
    published: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        index=True,
        nullable=False,
    )

    # Structured Lists using PostgreSQL JSON
    learning_outcomes: Mapped[List[str]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
    )
    technologies: Mapped[List[str]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
    )

    # Instructor Profile Metadata
    instructor_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    instructor_role: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    instructor_avatar: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    instructor_verified: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )

    # Relationships
    modules: Mapped[List["CourseModule"]] = relationship(
        "CourseModule",
        back_populates="course",
        order_by="CourseModule.order_index",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    enrollments: Mapped[List["CourseEnrollment"]] = relationship(
        "CourseEnrollment",
        back_populates="course",
        cascade="all, delete-orphan",
    )
    skills: Mapped[List["Skill"]] = relationship(
        "Skill",
        secondary="course_skills",
        back_populates="courses",
        lazy="selectin",
    )


class CourseModule(Base, TimestampMixin):
    """Course syllabus module grouping lessons."""

    __tablename__ = "course_modules"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        index=True,
    )
    course_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("courses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    module_number: Mapped[str] = mapped_column(
        String(10),
        default="01",
        nullable=False,
    )
    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    order_index: Mapped[int] = mapped_column(
        Integer,
        default=0,
        index=True,
        nullable=False,
    )
    published: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    # Relationships
    course: Mapped["Course"] = relationship(
        "Course",
        back_populates="modules",
    )
    lessons: Mapped[List["Lesson"]] = relationship(
        "Lesson",
        back_populates="module",
        order_by="Lesson.order_index",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class Lesson(Base, TimestampMixin):
    """Individual learning unit (theory, hands-on, quiz)."""

    __tablename__ = "lessons"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        index=True,
    )
    module_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("course_modules.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )
    slug: Mapped[str] = mapped_column(
        String(150),
        index=True,
        nullable=False,
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    content: Mapped[str] = mapped_column(
        Text,
        default="",
        nullable=False,
    )
    lesson_type: Mapped[str] = mapped_column(
        String(30),
        default="theory",
        nullable=False,
    )
    estimated_minutes: Mapped[int] = mapped_column(
        Integer,
        default=15,
        nullable=False,
    )
    order_index: Mapped[int] = mapped_column(
        Integer,
        default=0,
        index=True,
        nullable=False,
    )
    video_url: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
    )
    published: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    # Relationships
    module: Mapped["CourseModule"] = relationship(
        "CourseModule",
        back_populates="lessons",
    )
    resources: Mapped[List["LessonResource"]] = relationship(
        "LessonResource",
        back_populates="lesson",
        order_by="LessonResource.order_index",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class LessonResource(Base, TimestampMixin):
    """External links, GitHub repos, manifests, and reference material."""

    __tablename__ = "lesson_resources"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        index=True,
    )
    lesson_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("lessons.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )
    resource_type: Mapped[str] = mapped_column(
        String(50),
        default="documentation",
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
    order_index: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    # Relationships
    lesson: Mapped["Lesson"] = relationship(
        "Lesson",
        back_populates="resources",
    )


class CourseEnrollment(Base, TimestampMixin):
    """Student course enrollment record."""

    __tablename__ = "course_enrollments"
    __table_args__ = (
        UniqueConstraint("user_id", "course_id", name="uq_user_course_enrollment"),
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
    course_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("courses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    status: Mapped[str] = mapped_column(
        String(20),
        default=EnrollmentStatus.ACTIVE.value,
        nullable=False,
        index=True,
    )
    enrolled_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Relationships
    course: Mapped["Course"] = relationship(
        "Course",
        back_populates="enrollments",
        lazy="joined",
    )
