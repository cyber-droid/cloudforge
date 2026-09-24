"""
SQLAlchemy ORM Models Package.

Re-exports all database models to ensure Alembic and SQLAlchemy registry capture them.
"""

from app.core.database import Base
from app.models.base import TimestampMixin
from app.models.certificate import (
    Certificate,
    CertificateStatus,
    generate_certificate_number,
    generate_verification_code,
)
from app.models.certification import (
    AttemptType,
    Certification,
    CertificationLevel,
    CertificationTraining,
    PracticeAttempt,
    PracticeAttemptAnswer,
    PracticeQuestion,
    UserCertificationEnrollment,
)
from app.models.course import (
    Course,
    CourseCategory,
    CourseDifficulty,
    CourseEnrollment,
    CourseModule,
    EnrollmentStatus,
    Lesson,
    LessonResource,
)
from app.models.progress import (
    ActivityType,
    LearningActivity,
    LessonProgress,
    LessonProgressStatus,
)
from app.models.project import (
    Project,
    ProjectCourse,
    ProjectDifficulty,
    ProjectEnrollmentStatus,
    ProjectResource,
    ProjectResourceType,
    ProjectSkill,
    ProjectStatus,
    ProjectStep,
    ProjectStepProgress,
    StepProgressStatus,
    StepType,
    UserProjectEnrollment,
)
from app.models.roadmap import (
    Roadmap,
    RoadmapStatus,
    RoadmapStep,
    RoadmapStepType,
    UserRoadmapProgress,
)
from app.models.skill import (
    LEVEL_NAMES,
    CourseSkill,
    Skill,
    SkillCategory,
    SkillEvidence,
    SkillLevel,
    UserSkill,
    get_level_from_percentage,
)
from app.models.user import RefreshToken, User, UserRole

__all__ = [
    "Base",
    "TimestampMixin",
    "User",
    "UserRole",
    "RefreshToken",
    "Course",
    "CourseModule",
    "Lesson",
    "LessonResource",
    "CourseEnrollment",
    "CourseCategory",
    "CourseDifficulty",
    "EnrollmentStatus",
    "LessonProgress",
    "LessonProgressStatus",
    "LearningActivity",
    "ActivityType",
    "Skill",
    "CourseSkill",
    "UserSkill",
    "SkillEvidence",
    "SkillCategory",
    "SkillLevel",
    "LEVEL_NAMES",
    "get_level_from_percentage",
    "Roadmap",
    "RoadmapStep",
    "RoadmapStepType",
    "RoadmapStatus",
    "UserRoadmapProgress",
    "Certification",
    "CertificationLevel",
    "CertificationTraining",
    "UserCertificationEnrollment",
    "PracticeQuestion",
    "PracticeAttempt",
    "PracticeAttemptAnswer",
    "AttemptType",
    "Certificate",
    "CertificateStatus",
    "generate_verification_code",
    "generate_certificate_number",
    "Project",
    "ProjectStep",
    "ProjectResource",
    "UserProjectEnrollment",
    "ProjectStepProgress",
    "ProjectCourse",
    "ProjectSkill",
    "ProjectDifficulty",
    "ProjectStatus",
    "StepType",
    "ProjectEnrollmentStatus",
    "StepProgressStatus",
    "ProjectResourceType",
]
