"""
Career Roadmap and Step Progression Service.

Why this architecture exists:
1. Derived Roadmap Progression:
   Roadmap step completion is dynamically evaluated against live course enrollments and skill proficiencies
   rather than maintaining duplicate, out-of-sync completion flags.

2. Flexible Step Types:
   - Course Steps: Completed when the student finishes all published lessons in the mapped course.
   - Skill Steps: Completed when the student achieves foundational/intermediate proficiency (>=40%) in the skill.
   - Milestone Steps: Capstone integration stages awaiting subsequent practical project modules.
"""

from math import ceil
from typing import List, Optional, Tuple

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.course import EnrollmentStatus
from app.models.progress import LessonProgressStatus
from app.models.roadmap import (
    Roadmap,
    RoadmapStep,
    RoadmapStepType,
)
from app.repositories.course_repo import enrollment_repo
from app.repositories.progress_repo import progress_repo
from app.repositories.roadmap_repo import roadmap_repo
from app.repositories.skill_repo import skill_repo
from app.schemas.roadmap import (
    RoadmapDetailResponse,
    RoadmapListResponse,
    RoadmapStepResponse,
    RoadmapSummaryResponse,
    UserRoadmapProgressResponse,
)
from app.services.skill_service import skill_service


class RoadmapService:
    """Service handling career learning roadmaps, step evaluations, and user enrollments."""

    async def _evaluate_step_status(
        self, db: AsyncSession, *, step: RoadmapStep, user_id: Optional[str] = None
    ) -> Tuple[str, bool]:
        """
        Evaluate live completion status for a roadmap step for an authenticated student.
        Returns (status_label: 'completed' | 'in-progress' | 'upcoming', completed: bool).
        """
        if not user_id:
            return "upcoming", False

        if step.step_type == RoadmapStepType.COURSE.value and step.course_id:
            # Check enrollment and lesson progress
            enrollment = await enrollment_repo.get_by_user_and_course(
                db, user_id=user_id, course_id=step.course_id
            )
            if enrollment and enrollment.status == EnrollmentStatus.COMPLETED.value:
                return "completed", True

            progs = await progress_repo.get_course_lesson_progress(
                db, user_id=user_id, course_id=step.course_id
            )
            completed_count = sum(
                1 for p in progs if p.status == LessonProgressStatus.COMPLETED.value
            )
            in_prog_count = sum(
                1 for p in progs if p.status == LessonProgressStatus.IN_PROGRESS.value
            )

            if enrollment or completed_count > 0 or in_prog_count > 0:
                return "in-progress", False
            return "upcoming", False

        elif step.step_type == RoadmapStepType.SKILL.value and step.skill_id:
            skill = await skill_repo.get_by_id_or_slug(db, identifier=step.skill_id)
            if skill:
                user_skill = await skill_service.calculate_user_skill(
                    db, user_id=user_id, skill=skill
                )
                if user_skill.proficiency_percentage >= 40.0:
                    return "completed", True
                elif user_skill.proficiency_percentage > 0:
                    return "in-progress", False
            return "upcoming", False

        # Milestone step
        return "upcoming", False

    async def _to_roadmap_summary(
        self, db: AsyncSession, roadmap: Roadmap, user_id: Optional[str] = None
    ) -> RoadmapSummaryResponse:
        """Helper to transform Roadmap ORM model into summary schema with computed step nodes and progress."""
        steps = roadmap.steps or []
        step_responses: List[RoadmapStepResponse] = []
        completed_required = 0
        total_required = 0

        for s in steps:
            status_label, is_completed = await self._evaluate_step_status(
                db, step=s, user_id=user_id
            )

            if s.required:
                total_required += 1
                if is_completed:
                    completed_required += 1

            step_responses.append(
                RoadmapStepResponse(
                    id=s.id,
                    roadmap_id=s.roadmap_id,
                    title=s.title,
                    description=s.description,
                    step_type=s.step_type,
                    order_index=s.order_index,
                    required=s.required,
                    estimated_hours=s.estimated_hours,
                    skills=s.skills_covered or [],
                    course_id=s.course_id,
                    course_slug=s.course.slug if s.course else None,
                    course_title=s.course.title if s.course else None,
                    skill_id=s.skill_id,
                    skill_slug=s.skill.slug if s.skill else None,
                    skill_name=s.skill.name if s.skill else None,
                    status=status_label,
                    completed=is_completed,
                )
            )

        progress_pct = (
            round((completed_required / total_required * 100), 1)
            if total_required > 0
            else 0.0
        )

        return RoadmapSummaryResponse(
            id=roadmap.id,
            slug=roadmap.slug,
            title=roadmap.title,
            description=roadmap.description,
            category=roadmap.category,
            difficulty=roadmap.difficulty,
            duration=roadmap.duration_label,
            skills_count=roadmap.skills_count,
            projects_count=roadmap.projects_count,
            progress=progress_pct if user_id else 0.0,
            certifications_targeted=roadmap.certifications_targeted or [],
            nodes=step_responses,
            published=roadmap.published,
            created_at=roadmap.created_at,
        )

    async def list_roadmaps(
        self,
        db: AsyncSession,
        *,
        page: int = 1,
        page_size: int = 10,
        category: Optional[str] = None,
        difficulty: Optional[str] = None,
        search: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> RoadmapListResponse:
        """Fetch paginated roadmap catalog."""
        roadmaps, total = await roadmap_repo.get_paginated(
            db,
            page=page,
            page_size=page_size,
            category=category,
            difficulty=difficulty,
            search=search,
            published=True,
        )

        items = [
            await self._to_roadmap_summary(db, r, user_id=user_id) for r in roadmaps
        ]
        total_pages = ceil(total / page_size) if total > 0 else 1

        return RoadmapListResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    async def get_roadmap(
        self, db: AsyncSession, *, identifier: str, user_id: Optional[str] = None
    ) -> RoadmapDetailResponse:
        """Fetch full roadmap detail by UUID or slug."""
        roadmap = await roadmap_repo.get_by_id_or_slug(db, identifier=identifier)
        if not roadmap:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Roadmap '{identifier}' not found.",
            )

        summary = await self._to_roadmap_summary(db, roadmap, user_id=user_id)
        return RoadmapDetailResponse(**summary.model_dump())

    async def get_roadmap_steps(
        self,
        db: AsyncSession,
        *,
        roadmap_identifier: str,
        user_id: Optional[str] = None,
    ) -> List[RoadmapStepResponse]:
        """Fetch ordered steps for a roadmap."""
        detail = await self.get_roadmap(
            db, identifier=roadmap_identifier, user_id=user_id
        )
        return detail.nodes

    async def start_roadmap(
        self, db: AsyncSession, *, user_id: str, roadmap_identifier: str
    ) -> UserRoadmapProgressResponse:
        """Start a career roadmap for the authenticated user."""
        roadmap = await roadmap_repo.get_by_id_or_slug(
            db, identifier=roadmap_identifier
        )
        if not roadmap:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Roadmap '{roadmap_identifier}' not found.",
            )

        progress_record = await roadmap_repo.start_roadmap(
            db, user_id=user_id, roadmap_id=roadmap.id
        )
        summary = await self._to_roadmap_summary(db, roadmap, user_id=user_id)

        required_nodes = [n for n in summary.nodes if n.required]
        completed_count = sum(1 for n in required_nodes if n.completed)

        return UserRoadmapProgressResponse(
            id=progress_record.id,
            user_id=user_id,
            roadmap_id=roadmap.id,
            status=progress_record.status,
            progress_percentage=summary.progress,
            completed_steps=completed_count,
            total_required_steps=len(required_nodes),
            started_at=progress_record.started_at,
            completed_at=progress_record.completed_at,
            last_accessed_at=progress_record.last_accessed_at,
            roadmap=summary,
        )

    async def get_user_roadmaps(
        self, db: AsyncSession, *, user_id: str
    ) -> List[UserRoadmapProgressResponse]:
        """Fetch all roadmaps started by the student."""
        progress_records = await roadmap_repo.get_user_roadmaps(db, user_id=user_id)
        results: List[UserRoadmapProgressResponse] = []

        for p in progress_records:
            if p.roadmap:
                summary = await self._to_roadmap_summary(db, p.roadmap, user_id=user_id)
                required_nodes = [n for n in summary.nodes if n.required]
                completed_count = sum(1 for n in required_nodes if n.completed)

                results.append(
                    UserRoadmapProgressResponse(
                        id=p.id,
                        user_id=user_id,
                        roadmap_id=p.roadmap.id,
                        status=p.status,
                        progress_percentage=summary.progress,
                        completed_steps=completed_count,
                        total_required_steps=len(required_nodes),
                        started_at=p.started_at,
                        completed_at=p.completed_at,
                        last_accessed_at=p.last_accessed_at,
                        roadmap=summary,
                    )
                )

        return results

    async def get_user_roadmap_progress(
        self, db: AsyncSession, *, user_id: str, roadmap_identifier: str
    ) -> UserRoadmapProgressResponse:
        """Fetch single user roadmap progress."""
        roadmap = await roadmap_repo.get_by_id_or_slug(
            db, identifier=roadmap_identifier
        )
        if not roadmap:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Roadmap '{roadmap_identifier}' not found.",
            )

        progress_record = await roadmap_repo.get_user_roadmap(
            db, user_id=user_id, roadmap_id=roadmap.id
        )
        if not progress_record:
            # Auto-start if querying own progress
            progress_record = await roadmap_repo.start_roadmap(
                db, user_id=user_id, roadmap_id=roadmap.id
            )

        summary = await self._to_roadmap_summary(db, roadmap, user_id=user_id)
        required_nodes = [n for n in summary.nodes if n.required]
        completed_count = sum(1 for n in required_nodes if n.completed)

        return UserRoadmapProgressResponse(
            id=progress_record.id,
            user_id=user_id,
            roadmap_id=roadmap.id,
            status=progress_record.status,
            progress_percentage=summary.progress,
            completed_steps=completed_count,
            total_required_steps=len(required_nodes),
            started_at=progress_record.started_at,
            completed_at=progress_record.completed_at,
            last_accessed_at=progress_record.last_accessed_at,
            roadmap=summary,
        )


roadmap_service = RoadmapService()
