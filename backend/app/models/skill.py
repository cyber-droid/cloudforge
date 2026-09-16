"""
Skill, CourseSkill, UserSkill, and SkillEvidence Database Models.

Why these entities exist:
1. Skill: Represents technical competencies (e.g. Linux, Docker, Kubernetes, Terraform, AWS, CI/CD)
   independent of individual courses.
2. CourseSkill: Many-to-Many association linking curriculum courses to the engineering competencies they build.
3. UserSkill: Stores computed proficiency percentages (0-100%) and derived levels (1=Beginner to 5=Expert)
   derived deterministically from lesson and course completions.
4. SkillEvidence: Audit log capturing learning evidence points contributing to skill progression.
"""
import enum
import uuid
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import (
    DateTime,
    Enum as SQLEnum,
    Float,
    ForeignKey,
    Integer,
    JSON,
    String,
    Table,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class SkillCategory(str, enum.Enum):
    """Supported technical skill domain classifications."""
    CLOUD = "Cloud"
    DEVOPS = "DevOps"
    DEVSECOPS = "DevSecOps"
    KUBERNETES = "Kubernetes"
    SECURITY = "Security"
    OBSERVABILITY = "Observability"
    AI = "AI"
    PROGRAMMING = "Programming"
    INFRASTRUCTURE = "Infrastructure"


class SkillLevel(int, enum.Enum):
    """Standardized CloudForge learning indicator levels."""
    BEGINNER = 1      # 0 - 20%
    FOUNDATIONAL = 2  # 21 - 40%
    INTERMEDIATE = 3  # 41 - 70%
    ADVANCED = 4      # 71 - 90%
    EXPERT = 5        # 91 - 100%


LEVEL_NAMES = {
    SkillLevel.BEGINNER: "Beginner",
    SkillLevel.FOUNDATIONAL: "Foundational",
    SkillLevel.INTERMEDIATE: "Intermediate",
    SkillLevel.ADVANCED: "Advanced",
    SkillLevel.EXPERT: "Expert",
}


def get_level_from_percentage(percentage: float) -> int:
    """Deterministic conversion from percentage (0-100) to level (1-5)."""
    if percentage >= 91:
        return SkillLevel.EXPERT.value
    elif percentage >= 71:
        return SkillLevel.ADVANCED.value
    elif percentage >= 41:
        return SkillLevel.INTERMEDIATE.value
    elif percentage >= 21:
        return SkillLevel.FOUNDATIONAL.value
    else:
        return SkillLevel.BEGINNER.value


class CourseSkill(Base):
    """Many-to-Many association between Courses and Skills."""
    __tablename__ = "course_skills"

    course_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("courses.id", ondelete="CASCADE"),
        primary_key=True,
    )
    skill_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("skills.id", ondelete="CASCADE"),
        primary_key=True,
    )
    weight: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)


class Skill(Base, TimestampMixin):
    """Core Engineering Skill entity."""
    __tablename__ = "skills"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        index=True,
    )
    slug: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        index=True,
        nullable=False,
    )
    name: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    category: Mapped[str] = mapped_column(
        String(50),
        default=SkillCategory.DEVOPS.value,
        index=True,
        nullable=False,
    )
    target_level: Mapped[int] = mapped_column(
        Integer,
        default=4,  # Advanced
        nullable=False,
    )
    trend: Mapped[str] = mapped_column(
        String(20),
        default="+5%",
        nullable=False,
    )

    # Relationships
    courses: Mapped[List["Course"]] = relationship(
        "Course",
        secondary="course_skills",
        back_populates="skills",
        lazy="selectin",
    )
    user_skills: Mapped[List["UserSkill"]] = relationship(
        "UserSkill",
        back_populates="skill",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class UserSkill(Base, TimestampMixin):
    """Computed student skill proficiency record."""
    __tablename__ = "user_skills"
    __table_args__ = (
        UniqueConstraint("user_id", "skill_id", name="uq_user_skill"),
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
    skill_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("skills.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    current_level: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
    )
    target_level: Mapped[int] = mapped_column(
        Integer,
        default=4,
        nullable=False,
    )
    proficiency_percentage: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
    )
    last_updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    user: Mapped["User"] = relationship("User", lazy="selectin")
    skill: Mapped["Skill"] = relationship("Skill", back_populates="user_skills", lazy="selectin")


class SkillEvidence(Base):
    """Audit log of individual learning events contributing to skill score."""
    __tablename__ = "skill_evidence"

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
    skill_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("skills.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    source_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,  # 'lesson', 'course', 'quiz'
    )
    source_id: Mapped[str] = mapped_column(
        String(36),
        nullable=False,
    )
    points: Mapped[float] = mapped_column(
        Float,
        default=5.0,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
