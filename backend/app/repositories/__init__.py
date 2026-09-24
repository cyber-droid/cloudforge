"""
Repositories Package - Encapsulates Database Query and Mutation Operations.
"""
from app.repositories.base import BaseRepository
from app.repositories.course_repo import (
    CourseRepository,
    EnrollmentRepository,
    LessonRepository,
    ModuleRepository,
    course_repo,
    enrollment_repo,
    lesson_repo,
    module_repo,
)
from app.repositories.progress_repo import (
    ActivityRepository,
    ProgressRepository,
    activity_repo,
    progress_repo,
)
from app.repositories.certificate_repo import (
    CertificateRepository,
    certificate_repo,
)
from app.repositories.certification_repo import (
    CertificationRepository,
    certification_repo,
)
from app.repositories.practice_repo import (
    PracticeRepository,
    practice_repo,
)
from app.repositories.project_repo import (
    ProjectRepository,
    project_repo,
)
from app.repositories.roadmap_repo import (
    RoadmapRepository,
    roadmap_repo,
)
from app.repositories.skill_repo import (
    SkillRepository,
    skill_repo,
)
from app.repositories.user_repo import (
    RefreshTokenRepository,
    UserRepository,
    refresh_token_repo,
    user_repo,
)

__all__ = [
    "BaseRepository",
    "UserRepository",
    "RefreshTokenRepository",
    "user_repo",
    "refresh_token_repo",
    "CourseRepository",
    "ModuleRepository",
    "LessonRepository",
    "EnrollmentRepository",
    "course_repo",
    "module_repo",
    "lesson_repo",
    "enrollment_repo",
    "ProgressRepository",
    "ActivityRepository",
    "progress_repo",
    "activity_repo",
    "SkillRepository",
    "skill_repo",
    "RoadmapRepository",
    "roadmap_repo",
    "CertificationRepository",
    "certification_repo",
    "PracticeRepository",
    "practice_repo",
    "ProjectRepository",
    "project_repo",
    "CertificateRepository",
    "certificate_repo",
]

