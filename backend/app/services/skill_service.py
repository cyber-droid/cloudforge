"""
Skill and Technical Competency Calculation Service.

Why this architecture exists:
1. Deterministic Evidence-Based Scoring:
   Skill proficiency (0-100%) is derived directly from verified lesson and course completions
   in associated curriculum areas rather than arbitrary or random numbers.

2. Normalized Skill Levels (1-5):
   Maps percentage scores into standardized CloudForge learning indicators:
   - Level 1 (0-20%): Beginner
   - Level 2 (21-40%): Foundational
   - Level 3 (41-70%): Intermediate
   - Level 4 (71-90%): Advanced
   - Level 5 (91-100%): Expert
"""

from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.course import (
    EnrollmentStatus,
)
from app.models.progress import LessonProgressStatus
from app.models.skill import (
    LEVEL_NAMES,
    Skill,
    SkillLevel,
)
from app.repositories.course_repo import enrollment_repo
from app.repositories.progress_repo import progress_repo
from app.repositories.skill_repo import skill_repo
from app.schemas.skill import (
    SkillCourseReference,
    SkillSummaryResponse,
    UserSkillMatrixResponse,
    UserSkillResponse,
)


class SkillService:
    """Service managing technical skills, course-skill associations, and competency scoring."""

    async def list_skills(
        self,
        db: AsyncSession,
        *,
        category: Optional[str] = None,
        search: Optional[str] = None,
    ) -> List[SkillSummaryResponse]:
        """Fetch all skills in the catalog."""
        skills = await skill_repo.get_all(db, category=category, search=search)
        return [
            SkillSummaryResponse(
                id=s.id,
                slug=s.slug,
                name=s.name,
                description=s.description,
                category=s.category,
                target_level=s.target_level,
                target_level_name=LEVEL_NAMES.get(SkillLevel(s.target_level), "Advanced"),
                trend=s.trend or "+5%",
                courses_count=len(s.courses or []),
                related_courses=[
                    SkillCourseReference(id=c.id, slug=c.slug, title=c.title)
                    for c in (s.courses or [])
                ],
                created_at=s.created_at,
            )
            for s in skills
        ]

    async def get_skill(self, db: AsyncSession, *, identifier: str) -> Skill:
        """Fetch skill entity by UUID or slug."""
        skill = await skill_repo.get_by_id_or_slug(db, identifier=identifier)
        if not skill:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Skill '{identifier}' not found.",
            )
        return skill

    async def calculate_user_skill(
        self, db: AsyncSession, *, user_id: str, skill: Skill
    ) -> UserSkillResponse:
        """
        Calculate deterministic skill proficiency for a student from course and lesson progress.

        Algorithm:
        1. Find all courses associated with this skill (via course_skills mapping or tag matching).
        2. Count completed lessons across those courses (+5.0% per lesson).
        3. Check completed course enrollments (+25.0% per finished course).
        4. Cap result at 100.0%.
        5. Map to level (1 to 5).
        """
        related_courses = skill.courses or []
        related_course_ids = [c.id for c in related_courses]

        completed_lessons_count = 0
        completed_courses_count = 0

        if related_course_ids:
            for c_id in related_course_ids:
                # Lessons completed in this course
                progs = await progress_repo.get_course_lesson_progress(
                    db, user_id=user_id, course_id=c_id
                )
                completed_lessons_count += sum(
                    1 for p in progs if p.status == LessonProgressStatus.COMPLETED.value
                )

                # Enrollment status
                enr = await enrollment_repo.get_by_user_and_course(
                    db, user_id=user_id, course_id=c_id
                )
                if enr and enr.status == EnrollmentStatus.COMPLETED.value:
                    completed_courses_count += 1

        # Calculate score: 5% per lesson completed + 25% per full course finished
        computed_score = (completed_lessons_count * 5.0) + (
            completed_courses_count * 25.0
        )
        proficiency = min(100.0, max(0.0, round(computed_score, 1)))

        # Update or create user skill record
        user_skill = await skill_repo.upsert_user_skill(
            db,
            user_id=user_id,
            skill_id=skill.id,
            proficiency=proficiency,
            target_level=skill.target_level,
        )

        current_level_enum = SkillLevel(user_skill.current_level)
        target_level_enum = SkillLevel(min(5, max(1, user_skill.target_level)))

        return UserSkillResponse(
            id=user_skill.id,
            skill_id=skill.id,
            slug=skill.slug,
            name=skill.name,
            category=skill.category,
            current_level=user_skill.current_level,
            current_level_name=LEVEL_NAMES.get(current_level_enum, "Beginner"),
            target_level=user_skill.target_level,
            target_level_name=LEVEL_NAMES.get(target_level_enum, "Advanced"),
            proficiency_percentage=user_skill.proficiency_percentage,
            trend=skill.trend or "+5%",
            related_courses=[
                SkillCourseReference(id=c.id, slug=c.slug, title=c.title)
                for c in related_courses
            ],
            last_updated_at=user_skill.last_updated_at,
        )

    async def get_user_skill_matrix(
        self, db: AsyncSession, *, user_id: str, category: Optional[str] = None
    ) -> UserSkillMatrixResponse:
        """Calculate and return full competency matrix for student."""
        all_skills = await skill_repo.get_all(db, category=category)
        user_skill_responses: List[UserSkillResponse] = []

        for skill in all_skills:
            resp = await self.calculate_user_skill(db, user_id=user_id, skill=skill)
            user_skill_responses.append(resp)

        avg_prof = (
            round(
                sum(s.proficiency_percentage for s in user_skill_responses)
                / len(user_skill_responses),
                1,
            )
            if user_skill_responses
            else 0.0
        )

        return UserSkillMatrixResponse(
            skills=user_skill_responses,
            total_skills=len(user_skill_responses),
            average_proficiency=avg_prof,
        )

    async def get_user_skill_detail(
        self, db: AsyncSession, *, user_id: str, identifier: str
    ) -> UserSkillResponse:
        """Fetch computed user skill for single competency."""
        skill = await self.get_skill(db, identifier=identifier)
        return await self.calculate_user_skill(db, user_id=user_id, skill=skill)


skill_service = SkillService()
