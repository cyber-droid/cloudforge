"""
Skill and Competency Repository Layer.
"""
from datetime import datetime, timezone
from typing import List, Optional, Tuple
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.course import Course, CourseEnrollment, CourseModule, EnrollmentStatus, Lesson
from app.models.progress import LessonProgress, LessonProgressStatus
from app.models.skill import CourseSkill, Skill, SkillEvidence, UserSkill, get_level_from_percentage


class SkillRepository:
    """Data access methods for Skills and UserSkill competencies."""

    async def get_all(
        self,
        db: AsyncSession,
        *,
        category: Optional[str] = None,
        search: Optional[str] = None
    ) -> List[Skill]:
        """Fetch all skills with optional domain category or search filters."""
        query = select(Skill).options(selectinload(Skill.courses))

        if category and category != "All":
            query = query.where(Skill.category == category)
        if search:
            query = query.where(
                or_(
                    Skill.name.ilike(f"%{search}%"),
                    Skill.description.ilike(f"%{search}%"),
                )
            )

        query = query.order_by(Skill.name.asc())
        result = await db.execute(query)
        return list(result.scalars().all())

    async def get_by_id_or_slug(
        self,
        db: AsyncSession,
        *,
        identifier: str
    ) -> Optional[Skill]:
        """Fetch a single skill by UUID or slug."""
        query = (
            select(Skill)
            .options(selectinload(Skill.courses))
            .where(or_(Skill.id == identifier, Skill.slug == identifier))
        )
        result = await db.execute(query)
        return result.scalars().first()

    async def get_user_skills(
        self,
        db: AsyncSession,
        *,
        user_id: str
    ) -> List[UserSkill]:
        """Fetch all user skill records for a student."""
        query = (
            select(UserSkill)
            .options(
                selectinload(UserSkill.skill).selectinload(Skill.courses)
            )
            .where(UserSkill.user_id == user_id)
        )
        result = await db.execute(query)
        return list(result.scalars().all())

    async def get_user_skill(
        self,
        db: AsyncSession,
        *,
        user_id: str,
        skill_id: str
    ) -> Optional[UserSkill]:
        """Fetch single user skill record."""
        query = (
            select(UserSkill)
            .options(
                selectinload(UserSkill.skill).selectinload(Skill.courses)
            )
            .where(
                UserSkill.user_id == user_id,
                UserSkill.skill_id == skill_id
            )
        )
        result = await db.execute(query)
        return result.scalars().first()

    async def upsert_user_skill(
        self,
        db: AsyncSession,
        *,
        user_id: str,
        skill_id: str,
        proficiency: float,
        target_level: int = 4
    ) -> UserSkill:
        """Create or update a user skill proficiency record."""
        now = datetime.now(timezone.utc)
        record = await self.get_user_skill(db, user_id=user_id, skill_id=skill_id)
        current_level = get_level_from_percentage(proficiency)

        if not record:
            record = UserSkill(
                user_id=user_id,
                skill_id=skill_id,
                proficiency_percentage=min(100.0, max(0.0, proficiency)),
                current_level=current_level,
                target_level=target_level,
                last_updated_at=now,
            )
            db.add(record)
        else:
            record.proficiency_percentage = min(100.0, max(0.0, proficiency))
            record.current_level = current_level
            record.target_level = target_level
            record.last_updated_at = now

        await db.commit()
        await db.refresh(record)
        return record


skill_repo = SkillRepository()
