"""
Certification, Training, User Enrollment, Practice Questions, and Attempt Models.

Why these entities exist:
1. Certification: Root catalog model defining external exam prep tracks (AWS, Azure) and CloudForge foundational tracks.
2. CertificationTraining: Links certification programs to existing curriculum courses and syllabus modules.
3. UserCertificationEnrollment: Tracks student preparation enrollments with unique constraints.
4. PracticeQuestion: Domain-weighted question bank for quizzes and full timed mock exams. Correct options and explanations remain server-side.
5. PracticeAttempt & PracticeAttemptAnswer: Complete immutable attempt history with server-evaluated scores and review metadata.
"""

import enum
import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any, Dict, List, Optional

if TYPE_CHECKING:
    from app.models.certificate import Certificate
    from app.models.course import Course
    from app.models.user import User

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


class CertificationLevel(str, enum.Enum):
    """Certification complexity level."""

    FOUNDATIONAL = "Foundational"
    ASSOCIATE = "Associate"
    PROFESSIONAL = "Professional"
    SPECIALTY = "Specialty"


class EnrollmentStatus(str, enum.Enum):
    """Certification training enrollment lifecycle status."""

    ENROLLED = "enrolled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class AttemptType(str, enum.Enum):
    """Type of practice assessment."""

    PRACTICE_QUIZ = "practice_quiz"
    PRACTICE_EXAM = "practice_exam"


class Certification(Base, TimestampMixin):
    """Certification and exam preparation program."""

    __tablename__ = "certifications"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        index=True,
    )
    code: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        index=True,
    )
    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )
    slug: Mapped[str] = mapped_column(
        String(150),
        unique=True,
        nullable=False,
        index=True,
    )
    provider: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )
    vendor: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    level: Mapped[str] = mapped_column(
        String(50),
        default=CertificationLevel.FOUNDATIONAL.value,
        nullable=False,
        index=True,
    )
    category: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="Cloud",
    )
    badge_icon: Mapped[str] = mapped_column(
        String(50),
        default="Cloud",
        nullable=False,
    )
    icon_name: Mapped[Optional[str]] = mapped_column(
        String(50),
        default="Cloud",
        nullable=True,
    )
    duration: Mapped[str] = mapped_column(
        String(50),
        default="18 hours",
        nullable=False,
    )
    exam_duration_minutes: Mapped[int] = mapped_column(
        Integer,
        default=90,
        nullable=False,
    )
    total_exam_questions: Mapped[int] = mapped_column(
        Integer,
        default=65,
        nullable=False,
    )
    passing_score_percentage: Mapped[float] = mapped_column(
        Float,
        default=70.0,
        nullable=False,
    )
    training_title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    training_certificate_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    official_url: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
    )
    is_official_certification: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )
    is_published: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        index=True,
    )
    exam_domains: Mapped[List[Dict[str, Any]]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
    )
    domains: Mapped[List[Dict[str, Any]]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
    )
    skills_gained: Mapped[List[str]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
    )
    practice_questions_count: Mapped[int] = mapped_column(
        Integer,
        default=100,
        nullable=False,
    )
    mock_exams_count: Mapped[int] = mapped_column(
        Integer,
        default=3,
        nullable=False,
    )

    def __init__(self, **kwargs):
        if "domains" in kwargs and "exam_domains" not in kwargs:
            kwargs["exam_domains"] = kwargs["domains"]
        elif "exam_domains" in kwargs and "domains" not in kwargs:
            kwargs["domains"] = kwargs["exam_domains"]
        if "name" in kwargs and "title" not in kwargs:
            kwargs["title"] = kwargs["name"]
        elif "title" in kwargs and "name" not in kwargs:
            kwargs["name"] = kwargs["title"]
        if "vendor" in kwargs and "provider" not in kwargs:
            kwargs["provider"] = kwargs["vendor"]
        elif "provider" in kwargs and "vendor" not in kwargs:
            kwargs["vendor"] = kwargs["provider"]
        if "level" in kwargs and hasattr(kwargs["level"], "value"):
            kwargs["level"] = kwargs["level"].value
        if "training_title" not in kwargs:
            name_val = kwargs.get("name") or kwargs.get("title", "Training")
            kwargs["training_title"] = f"{name_val} Training Program"
        if "training_certificate_name" not in kwargs:
            name_val = kwargs.get("name") or kwargs.get("title", "Training")
            kwargs["training_certificate_name"] = (
                f"Certificate of Completion - {name_val}"
            )
        super().__init__(**kwargs)

    # Relationships
    trainings: Mapped[List["CertificationTraining"]] = relationship(
        "CertificationTraining",
        back_populates="certification",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    questions: Mapped[List["PracticeQuestion"]] = relationship(
        "PracticeQuestion",
        back_populates="certification",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    enrollments: Mapped[List["UserCertificationEnrollment"]] = relationship(
        "UserCertificationEnrollment",
        back_populates="certification",
        cascade="all, delete-orphan",
    )
    practice_attempts: Mapped[List["PracticeAttempt"]] = relationship(
        "PracticeAttempt",
        back_populates="certification",
        cascade="all, delete-orphan",
    )


class CertificationTraining(Base, TimestampMixin):
    """Structured training track mapped to curriculum courses."""

    __tablename__ = "certification_trainings"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        index=True,
    )
    certification_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("certifications.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    slug: Mapped[str] = mapped_column(
        String(150),
        unique=True,
        nullable=False,
        index=True,
    )
    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    level: Mapped[str] = mapped_column(
        String(50),
        default=CertificationLevel.FOUNDATIONAL.value,
        nullable=False,
    )
    estimated_hours: Mapped[str] = mapped_column(
        String(50),
        default="18h",
        nullable=False,
    )
    course_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("courses.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    modules: Mapped[List[str]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
    )
    is_published: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        index=True,
    )

    def __init__(self, **kwargs):
        if "level" in kwargs and hasattr(kwargs["level"], "value"):
            kwargs["level"] = kwargs["level"].value
        if "estimated_hours" in kwargs:
            kwargs["estimated_hours"] = str(kwargs["estimated_hours"])
        super().__init__(**kwargs)

    # Relationships
    certification: Mapped["Certification"] = relationship(
        "Certification",
        back_populates="trainings",
    )
    course: Mapped[Optional["Course"]] = relationship(
        "Course",
        lazy="joined",
    )
    enrollments: Mapped[List["UserCertificationEnrollment"]] = relationship(
        "UserCertificationEnrollment",
        back_populates="training",
        cascade="all, delete-orphan",
    )
    certificates: Mapped[List["Certificate"]] = relationship(
        "Certificate",
        back_populates="training",
        cascade="all, delete-orphan",
    )


class UserCertificationEnrollment(Base, TimestampMixin):
    """Tracks a student's enrollment and progress in certification training."""

    __tablename__ = "user_certification_enrollments"
    __table_args__ = (
        UniqueConstraint("user_id", "training_id", name="uq_user_training_enrollment"),
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
    certification_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("certifications.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    training_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("certification_trainings.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    status: Mapped[str] = mapped_column(
        String(30),
        default=EnrollmentStatus.ENROLLED.value,
        nullable=False,
        index=True,
    )
    enrolled_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    started_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Relationships
    user: Mapped["User"] = relationship("User")
    certification: Mapped["Certification"] = relationship(
        "Certification", back_populates="enrollments"
    )
    training: Mapped["CertificationTraining"] = relationship(
        "CertificationTraining", back_populates="enrollments"
    )


class PracticeQuestion(Base, TimestampMixin):
    """Domain-weighted question bank entry for exam simulation."""

    __tablename__ = "practice_questions"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        index=True,
    )
    certification_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("certifications.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    training_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("certification_trainings.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    question_text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    question_type: Mapped[str] = mapped_column(
        String(50),
        default="single-choice",
        nullable=False,
    )
    options: Mapped[List[str]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
    )
    correct_option: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    explanation: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    domain: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
        default="General",
        index=True,
    )
    topic: Mapped[Optional[str]] = mapped_column(
        String(150),
        nullable=True,
        index=True,
    )
    difficulty: Mapped[str] = mapped_column(
        String(50),
        default="Intermediate",
        nullable=False,
    )
    points: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
    )
    is_published: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        index=True,
    )

    def __init__(self, **kwargs):
        if "topic" in kwargs and "domain" not in kwargs:
            kwargs["domain"] = kwargs["topic"]
        elif "domain" in kwargs and "topic" not in kwargs:
            kwargs["topic"] = kwargs["domain"]
        super().__init__(**kwargs)

    # Relationships
    certification: Mapped["Certification"] = relationship(
        "Certification", back_populates="questions"
    )
    answers: Mapped[List["PracticeAttemptAnswer"]] = relationship(
        "PracticeAttemptAnswer",
        back_populates="question",
        cascade="all, delete-orphan",
    )


class PracticeAttempt(Base, TimestampMixin):
    """Practice quiz or timed mock exam attempt instance."""

    __tablename__ = "practice_attempts"

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
    certification_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("certifications.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    training_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("certification_trainings.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    attempt_type: Mapped[str] = mapped_column(
        String(50),
        default=AttemptType.PRACTICE_EXAM.value,
        nullable=False,
        index=True,
    )
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    submitted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    score: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    percentage: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
    )
    passed: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        index=True,
    )
    passing_percentage: Mapped[float] = mapped_column(
        Float,
        default=70.0,
        nullable=False,
    )
    total_questions: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    correct_answers: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    time_spent_seconds: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    # Relationships
    user: Mapped["User"] = relationship("User")
    certification: Mapped["Certification"] = relationship(
        "Certification", back_populates="practice_attempts"
    )
    answers: Mapped[List["PracticeAttemptAnswer"]] = relationship(
        "PracticeAttemptAnswer",
        back_populates="attempt",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class PracticeAttemptAnswer(Base, TimestampMixin):
    """User response to a single practice question during an attempt."""

    __tablename__ = "practice_attempt_answers"
    __table_args__ = (
        UniqueConstraint(
            "attempt_id", "question_id", name="uq_attempt_question_answer"
        ),
    )

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        index=True,
    )
    attempt_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("practice_attempts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    question_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("practice_questions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    selected_answer: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    is_correct: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
    )
    points_earned: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    # Relationships
    attempt: Mapped["PracticeAttempt"] = relationship(
        "PracticeAttempt", back_populates="answers"
    )
    question: Mapped["PracticeQuestion"] = relationship(
        "PracticeQuestion", back_populates="answers", lazy="joined"
    )
