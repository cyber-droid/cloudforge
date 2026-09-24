"""
Project, Steps, Resources, and Enrollment Repository Layer.
"""

from datetime import datetime, timezone
from typing import List, Optional, Tuple

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.project import (
    Project,
    ProjectEnrollmentStatus,
    ProjectStatus,
    ProjectStep,
    ProjectStepProgress,
    StepProgressStatus,
    UserProjectEnrollment,
)


class ProjectRepository:
    """Data access methods for Projects, Engineering Steps, Resources, and Progress."""

    async def get_paginated(
        self,
        db: AsyncSession,
        *,
        page: int = 1,
        page_size: int = 10,
        search: Optional[str] = None,
        difficulty: Optional[str] = None,
        status: Optional[str] = None,
        featured: Optional[bool] = None,
        student_view: bool = True,
    ) -> Tuple[List[Project], int]:
        """Fetch paginated project catalog with SQL filters and eager relations."""
        query = select(Project).options(
            selectinload(Project.steps),
            selectinload(Project.resources),
            selectinload(Project.courses),
            selectinload(Project.skills),
        )

        if student_view:
            query = query.where(Project.status == ProjectStatus.PUBLISHED.value)
        elif status and status != "All":
            query = query.where(Project.status == status)

        if difficulty and difficulty != "All":
            query = query.where(Project.difficulty.ilike(difficulty))

        if featured is not None:
            query = query.where(Project.featured == featured)

        if search:
            query = query.where(
                or_(
                    Project.title.ilike(f"%{search}%"),
                    Project.description.ilike(f"%{search}%"),
                    Project.short_description.ilike(f"%{search}%"),
                )
            )

        # Count total matching rows
        count_query = select(func.count()).select_from(query.order_by(None).subquery())
        count_res = await db.execute(count_query)
        total = count_res.scalar() or 0

        # Deterministic sorting: featured first, then created_at
        offset = (page - 1) * page_size
        query = (
            query.order_by(Project.featured.desc(), Project.created_at.asc())
            .offset(offset)
            .limit(page_size)
        )
        result = await db.execute(query)
        return list(result.scalars().all()), total

    async def get_by_id_or_slug(
        self,
        db: AsyncSession,
        *,
        identifier: str,
    ) -> Optional[Project]:
        """Fetch single project by UUID or slug with steps, resources, courses, and skills."""
        query = (
            select(Project)
            .options(
                selectinload(Project.steps),
                selectinload(Project.resources),
                selectinload(Project.courses),
                selectinload(Project.skills),
            )
            .where(or_(Project.id == identifier, Project.slug == identifier))
        )
        result = await db.execute(query)
        return result.scalars().first()

    async def get_enrollment(
        self,
        db: AsyncSession,
        *,
        user_id: str,
        project_id: str,
    ) -> Optional[UserProjectEnrollment]:
        """Fetch single user enrollment record for a project."""
        query = (
            select(UserProjectEnrollment)
            .options(
                selectinload(UserProjectEnrollment.project).selectinload(Project.steps),
                selectinload(UserProjectEnrollment.project).selectinload(
                    Project.resources
                ),
            )
            .where(
                UserProjectEnrollment.user_id == user_id,
                UserProjectEnrollment.project_id == project_id,
            )
        )
        result = await db.execute(query)
        return result.scalars().first()

    async def get_user_enrollments(
        self,
        db: AsyncSession,
        *,
        user_id: str,
    ) -> List[UserProjectEnrollment]:
        """Fetch all project enrollments for a user."""
        query = (
            select(UserProjectEnrollment)
            .options(
                selectinload(UserProjectEnrollment.project).selectinload(Project.steps),
                selectinload(UserProjectEnrollment.project).selectinload(
                    Project.resources
                ),
                selectinload(UserProjectEnrollment.project).selectinload(
                    Project.courses
                ),
                selectinload(UserProjectEnrollment.project).selectinload(
                    Project.skills
                ),
            )
            .where(UserProjectEnrollment.user_id == user_id)
            .order_by(UserProjectEnrollment.last_activity_at.desc())
        )
        result = await db.execute(query)
        return list(result.scalars().all())

    async def enroll_user(
        self,
        db: AsyncSession,
        *,
        user_id: str,
        project_id: str,
    ) -> Tuple[UserProjectEnrollment, bool]:
        """Enroll user in a project. Returns (enrollment, is_new)."""
        now = datetime.now(timezone.utc)
        record = await self.get_enrollment(db, user_id=user_id, project_id=project_id)

        if record:
            record.last_activity_at = now
            await db.commit()
            await db.refresh(record)
            return record, False

        new_record = UserProjectEnrollment(
            user_id=user_id,
            project_id=project_id,
            status=ProjectEnrollmentStatus.IN_PROGRESS.value,
            started_at=now,
            last_activity_at=now,
        )
        db.add(new_record)
        await db.commit()
        await db.refresh(new_record)
        return new_record, True

    async def get_step_by_id(
        self,
        db: AsyncSession,
        *,
        step_id: str,
        project_id: Optional[str] = None,
    ) -> Optional[ProjectStep]:
        """Fetch a project step by ID."""
        query = select(ProjectStep).where(ProjectStep.id == step_id)
        if project_id:
            query = query.where(ProjectStep.project_id == project_id)
        result = await db.execute(query)
        return result.scalars().first()

    async def get_user_step_progress(
        self,
        db: AsyncSession,
        *,
        user_id: str,
        project_step_id: str,
    ) -> Optional[ProjectStepProgress]:
        """Fetch progress for a single step by a user."""
        query = select(ProjectStepProgress).where(
            ProjectStepProgress.user_id == user_id,
            ProjectStepProgress.project_step_id == project_step_id,
        )
        result = await db.execute(query)
        return result.scalars().first()

    async def get_user_step_progress_list_for_project(
        self,
        db: AsyncSession,
        *,
        user_id: str,
        project_id: str,
    ) -> List[ProjectStepProgress]:
        """Fetch all step progress records for a user within a project."""
        query = (
            select(ProjectStepProgress)
            .join(ProjectStep, ProjectStepProgress.project_step_id == ProjectStep.id)
            .where(
                ProjectStepProgress.user_id == user_id,
                ProjectStep.project_id == project_id,
            )
        )
        result = await db.execute(query)
        return list(result.scalars().all())

    async def start_step(
        self,
        db: AsyncSession,
        *,
        user_id: str,
        step_id: str,
    ) -> ProjectStepProgress:
        """Mark a project step as in_progress."""
        now = datetime.now(timezone.utc)
        record = await self.get_user_step_progress(
            db, user_id=user_id, project_step_id=step_id
        )

        if not record:
            record = ProjectStepProgress(
                user_id=user_id,
                project_step_id=step_id,
                status=StepProgressStatus.IN_PROGRESS.value,
                started_at=now,
            )
            db.add(record)
        elif record.status == StepProgressStatus.NOT_STARTED.value:
            record.status = StepProgressStatus.IN_PROGRESS.value
            if not record.started_at:
                record.started_at = now

        await db.commit()
        await db.refresh(record)
        return record

    async def complete_step(
        self,
        db: AsyncSession,
        *,
        user_id: str,
        step_id: str,
        notes: Optional[str] = None,
    ) -> Tuple[ProjectStepProgress, bool]:
        """Mark a project step as completed idempotently. Returns (progress, is_newly_completed)."""
        now = datetime.now(timezone.utc)
        record = await self.get_user_step_progress(
            db, user_id=user_id, project_step_id=step_id
        )
        is_newly_completed = False

        if not record:
            record = ProjectStepProgress(
                user_id=user_id,
                project_step_id=step_id,
                status=StepProgressStatus.COMPLETED.value,
                started_at=now,
                completed_at=now,
                notes=notes,
            )
            db.add(record)
            is_newly_completed = True
        else:
            if record.status != StepProgressStatus.COMPLETED.value:
                record.status = StepProgressStatus.COMPLETED.value
                record.completed_at = now
                is_newly_completed = True
            if notes is not None:
                record.notes = notes

        await db.commit()
        await db.refresh(record)
        return record, is_newly_completed

    async def update_enrollment(
        self,
        db: AsyncSession,
        enrollment: UserProjectEnrollment,
        *,
        status: Optional[str] = None,
        completed_at: Optional[datetime] = None,
        last_activity_at: Optional[datetime] = None,
    ) -> UserProjectEnrollment:
        """Update enrollment status and timestamps."""
        if status:
            enrollment.status = status
        if completed_at is not None:
            enrollment.completed_at = completed_at
        if last_activity_at:
            enrollment.last_activity_at = last_activity_at
        await db.commit()
        await db.refresh(enrollment)
        return enrollment


project_repo = ProjectRepository()
