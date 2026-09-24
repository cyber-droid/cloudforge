"""
Project and DevOps Engineering Workflow Service Layer.

Why this architecture exists:
1. Derived Project Progress:
   Project progress is calculated directly from granular ProjectStepProgress records over total project steps.
   This guarantees that completion percentages and completion status are mathematically deterministic and
   cannot be forged or corrupted by frontend state tampering.

2. Deterministic & Idempotent Completion:
   A project is marked completed if and only if all required project steps are verified completed.
   Calling step completion repeatedly is idempotent and does not emit duplicate learning activity logs
   or alter historical completion timestamps.

3. Activity Integration:
   Seamlessly integrates with the existing LearningActivity audit trail for project milestones
   (PROJECT_STARTED, PROJECT_STEP_COMPLETED, PROJECT_COMPLETED).
"""

from datetime import datetime, timezone
from typing import Dict, List, Optional

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import logger
from app.models.progress import ActivityType
from app.models.project import (
    Project,
    ProjectEnrollmentStatus,
    ProjectStatus,
    ProjectStep,
    ProjectStepProgress,
    StepProgressStatus,
)
from app.models.user import User
from app.repositories.progress_repo import activity_repo
from app.repositories.project_repo import project_repo
from app.schemas.project import (
    ProjectCourseReference,
    ProjectDetailResponse,
    ProjectEnrollmentResponse,
    ProjectListResponse,
    ProjectProgressResponse,
    ProjectResourceResponse,
    ProjectSkillReference,
    ProjectStepResponse,
    ProjectSummaryResponse,
)


class ProjectService:
    """Service handling DevOps engineering projects, steps, enrollments, and progress."""

    def _build_step_responses(
        self,
        steps: List[ProjectStep],
        progress_map: Dict[str, ProjectStepProgress],
    ) -> List[ProjectStepResponse]:
        """Convert ProjectStep models into response schemas with user-specific progress state."""
        sorted_steps = sorted(steps, key=lambda s: s.step_order)
        responses = []
        for step in sorted_steps:
            prog = progress_map.get(step.id)
            is_completed = (
                prog is not None and prog.status == StepProgressStatus.COMPLETED.value
            )
            step_status = prog.status if prog else StepProgressStatus.NOT_STARTED.value

            responses.append(
                ProjectStepResponse(
                    id=step.id,
                    project_id=step.project_id,
                    title=step.title,
                    description=step.description,
                    step_order=step.step_order,
                    step_type=step.step_type,
                    instructions=step.instructions,
                    command=step.command,
                    expected_outcome=step.expected_outcome,
                    is_required=step.is_required,
                    completed=is_completed,
                    status=step_status,
                    started_at=prog.started_at if prog else None,
                    completed_at=prog.completed_at if prog else None,
                )
            )
        return responses

    def _extract_skill_names(self, project: Project) -> List[str]:
        """Extract flat string list of skill names for summary views."""
        skills = []
        if project.skills:
            for s in project.skills:
                skills.append(s.name)
        return skills

    async def list_projects(
        self,
        db: AsyncSession,
        *,
        page: int = 1,
        page_size: int = 10,
        search: Optional[str] = None,
        difficulty: Optional[str] = None,
        status_filter: Optional[str] = None,
        featured: Optional[bool] = None,
        current_user: Optional[User] = None,
    ) -> ProjectListResponse:
        """Fetch paginated project catalog with real-time user progress."""
        # Students/public only see published projects; instructors/admins can filter by any status
        is_staff = current_user and current_user.role in ["instructor", "admin"]
        student_view = not is_staff

        projects, total = await project_repo.get_paginated(
            db,
            page=page,
            page_size=page_size,
            search=search,
            difficulty=difficulty,
            status=status_filter,
            featured=featured,
            student_view=student_view,
        )

        items: List[ProjectSummaryResponse] = []

        for p in projects:
            progress_pct = 0.0
            user_status = "not_started"
            completed_steps = 0
            total_steps = len(p.steps) if p.steps else 0

            if current_user:
                enrollment = await project_repo.get_enrollment(
                    db, user_id=current_user.id, project_id=p.id
                )
                if enrollment:
                    user_status = enrollment.status
                    user_progs = (
                        await project_repo.get_user_step_progress_list_for_project(
                            db, user_id=current_user.id, project_id=p.id
                        )
                    )
                    completed_steps = sum(
                        1
                        for prog in user_progs
                        if prog.status == StepProgressStatus.COMPLETED.value
                    )
                    if total_steps > 0:
                        progress_pct = round((completed_steps / total_steps) * 100.0, 1)

            skills_list = self._extract_skill_names(p)

            items.append(
                ProjectSummaryResponse(
                    id=p.id,
                    title=p.title,
                    slug=p.slug,
                    short_description=p.short_description,
                    description=p.description,
                    difficulty=p.difficulty,
                    estimated_hours=p.estimated_hours,
                    status=p.status,
                    featured=p.featured,
                    technologies=p.technologies or [],
                    deliverables=p.deliverables or [],
                    repository_url=p.repository_url,
                    documentation_url=p.documentation_url,
                    progress=progress_pct,
                    progress_percentage=progress_pct,
                    user_status=user_status,
                    completed_steps=completed_steps,
                    total_steps=total_steps,
                    skills=skills_list,
                    created_at=p.created_at,
                )
            )

        return ProjectListResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
        )

    async def get_project_detail(
        self,
        db: AsyncSession,
        *,
        identifier: str,
        current_user: Optional[User] = None,
    ) -> ProjectDetailResponse:
        """Fetch comprehensive project detail by UUID or slug."""
        project = await project_repo.get_by_id_or_slug(db, identifier=identifier)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project '{identifier}' not found.",
            )

        # Check access permission for drafts
        is_staff = current_user and current_user.role in ["instructor", "admin"]
        if project.status != ProjectStatus.PUBLISHED.value and not is_staff:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project '{identifier}' not found.",
            )

        progress_map: Dict[str, ProjectStepProgress] = {}
        user_status = "not_started"
        progress_pct = 0.0
        completed_steps = 0
        total_steps = len(project.steps) if project.steps else 0

        if current_user:
            enrollment = await project_repo.get_enrollment(
                db, user_id=current_user.id, project_id=project.id
            )
            if enrollment:
                user_status = enrollment.status

            user_progs = await project_repo.get_user_step_progress_list_for_project(
                db, user_id=current_user.id, project_id=project.id
            )
            for up in user_progs:
                progress_map[up.project_step_id] = up
                if up.status == StepProgressStatus.COMPLETED.value:
                    completed_steps += 1

            if total_steps > 0:
                progress_pct = round((completed_steps / total_steps) * 100.0, 1)

        step_responses = self._build_step_responses(project.steps or [], progress_map)

        resource_responses = [
            ProjectResourceResponse(
                id=r.id,
                project_id=r.project_id,
                title=r.title,
                resource_type=r.resource_type,
                url=r.url,
                description=r.description,
                display_order=r.display_order,
            )
            for r in sorted(project.resources or [], key=lambda r: r.display_order)
        ]

        course_references = [
            ProjectCourseReference(
                id=c.id,
                title=c.title,
                slug=c.slug,
                category=c.category,
                difficulty=c.difficulty,
            )
            for c in (project.courses or [])
        ]

        skill_references = [
            ProjectSkillReference(
                id=s.id,
                name=s.name,
                slug=s.slug,
                category=s.category,
                target_level=s.target_level,
            )
            for s in (project.skills or [])
        ]

        skills_list = self._extract_skill_names(project)

        return ProjectDetailResponse(
            id=project.id,
            title=project.title,
            slug=project.slug,
            short_description=project.short_description,
            description=project.description,
            difficulty=project.difficulty,
            estimated_hours=project.estimated_hours,
            status=project.status,
            featured=project.featured,
            technologies=project.technologies or [],
            deliverables=project.deliverables or [],
            repository_url=project.repository_url,
            documentation_url=project.documentation_url,
            progress=progress_pct,
            progress_percentage=progress_pct,
            user_status=user_status,
            completed_steps=completed_steps,
            total_steps=total_steps,
            skills=skills_list,
            created_at=project.created_at,
            architecture_overview=project.architecture_overview,
            prerequisites=project.prerequisites or [],
            learning_objectives=project.learning_objectives or [],
            steps=step_responses,
            resources=resource_responses,
            related_courses=course_references,
            related_skills=skill_references,
        )

    async def enroll_project(
        self,
        db: AsyncSession,
        *,
        user_id: str,
        project_identifier: str,
    ) -> ProjectEnrollmentResponse:
        """Enroll user in a project and log learning activity."""
        project = await project_repo.get_by_id_or_slug(
            db, identifier=project_identifier
        )
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project '{project_identifier}' not found.",
            )

        enrollment, is_new = await project_repo.enroll_user(
            db, user_id=user_id, project_id=project.id
        )

        if is_new:
            await activity_repo.log_activity(
                db,
                user_id=user_id,
                activity_type=ActivityType.PROJECT_STARTED.value,
                metadata={
                    "project_id": project.id,
                    "project_title": project.title,
                    "project_slug": project.slug,
                },
            )
            logger.info(
                "User %s enrolled in project %s (%s)",
                user_id,
                project.title,
                project.id,
            )

        user_progs = await project_repo.get_user_step_progress_list_for_project(
            db, user_id=user_id, project_id=project.id
        )
        completed_steps = sum(
            1
            for prog in user_progs
            if prog.status == StepProgressStatus.COMPLETED.value
        )
        total_steps = len(project.steps) if project.steps else 0
        progress_pct = (
            round((completed_steps / total_steps) * 100.0, 1)
            if total_steps > 0
            else 0.0
        )

        return ProjectEnrollmentResponse(
            id=enrollment.id,
            user_id=enrollment.user_id,
            project_id=enrollment.project_id,
            status=enrollment.status,
            started_at=enrollment.started_at,
            completed_at=enrollment.completed_at,
            last_activity_at=enrollment.last_activity_at,
            progress_percentage=progress_pct,
            completed_steps=completed_steps,
            total_steps=total_steps,
        )

    async def get_my_projects(
        self,
        db: AsyncSession,
        *,
        user_id: str,
    ) -> List[ProjectEnrollmentResponse]:
        """Fetch all projects enrolled by the current user with live progress calculation."""
        enrollments = await project_repo.get_user_enrollments(db, user_id=user_id)
        results: List[ProjectEnrollmentResponse] = []

        for e in enrollments:
            if not e.project:
                continue

            user_progs = await project_repo.get_user_step_progress_list_for_project(
                db, user_id=user_id, project_id=e.project_id
            )
            completed_steps = sum(
                1
                for prog in user_progs
                if prog.status == StepProgressStatus.COMPLETED.value
            )
            total_steps = len(e.project.steps) if e.project.steps else 0
            progress_pct = (
                round((completed_steps / total_steps) * 100.0, 1)
                if total_steps > 0
                else 0.0
            )

            skills_list = self._extract_skill_names(e.project)

            summary = ProjectSummaryResponse(
                id=e.project.id,
                title=e.project.title,
                slug=e.project.slug,
                short_description=e.project.short_description,
                description=e.project.description,
                difficulty=e.project.difficulty,
                estimated_hours=e.project.estimated_hours,
                status=e.project.status,
                featured=e.project.featured,
                technologies=e.project.technologies or [],
                deliverables=e.project.deliverables or [],
                repository_url=e.project.repository_url,
                documentation_url=e.project.documentation_url,
                progress=progress_pct,
                progress_percentage=progress_pct,
                user_status=e.status,
                completed_steps=completed_steps,
                total_steps=total_steps,
                skills=skills_list,
                created_at=e.project.created_at,
            )

            results.append(
                ProjectEnrollmentResponse(
                    id=e.id,
                    user_id=e.user_id,
                    project_id=e.project_id,
                    status=e.status,
                    started_at=e.started_at,
                    completed_at=e.completed_at,
                    last_activity_at=e.last_activity_at,
                    progress_percentage=progress_pct,
                    completed_steps=completed_steps,
                    total_steps=total_steps,
                    project=summary,
                )
            )

        return results

    async def get_project_progress(
        self,
        db: AsyncSession,
        *,
        user_id: str,
        project_identifier: str,
    ) -> ProjectProgressResponse:
        """Fetch granular step breakdown and calculated progress for a project."""
        project = await project_repo.get_by_id_or_slug(
            db, identifier=project_identifier
        )
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project '{project_identifier}' not found.",
            )

        enrollment = await project_repo.get_enrollment(
            db, user_id=user_id, project_id=project.id
        )

        user_progs = await project_repo.get_user_step_progress_list_for_project(
            db, user_id=user_id, project_id=project.id
        )
        progress_map = {p.project_step_id: p for p in user_progs}

        completed_steps = sum(
            1
            for prog in user_progs
            if prog.status == StepProgressStatus.COMPLETED.value
        )
        total_steps = len(project.steps) if project.steps else 0
        progress_pct = (
            round((completed_steps / total_steps) * 100.0, 1)
            if total_steps > 0
            else 0.0
        )
        is_completed = (
            enrollment is not None
            and enrollment.status == ProjectEnrollmentStatus.COMPLETED.value
        ) or (total_steps > 0 and completed_steps >= total_steps)

        step_responses = self._build_step_responses(project.steps or [], progress_map)

        return ProjectProgressResponse(
            project_id=project.id,
            user_id=user_id,
            status=enrollment.status if enrollment else "not_started",
            progress_percentage=progress_pct,
            completed_steps=completed_steps,
            total_steps=total_steps,
            is_completed=is_completed,
            started_at=enrollment.started_at if enrollment else None,
            completed_at=enrollment.completed_at if enrollment else None,
            last_activity_at=enrollment.last_activity_at if enrollment else None,
            steps=step_responses,
        )

    async def start_step(
        self,
        db: AsyncSession,
        *,
        user_id: str,
        project_identifier: str,
        step_id: str,
    ) -> ProjectStepResponse:
        """Start working on a specific project engineering step."""
        project = await project_repo.get_by_id_or_slug(
            db, identifier=project_identifier
        )
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project '{project_identifier}' not found.",
            )

        step = await project_repo.get_step_by_id(
            db, step_id=step_id, project_id=project.id
        )
        if not step:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Step '{step_id}' not found in project '{project.title}'.",
            )

        # Ensure enrollment exists
        enrollment, _ = await project_repo.enroll_user(
            db, user_id=user_id, project_id=project.id
        )

        prog = await project_repo.start_step(db, user_id=user_id, step_id=step.id)

        # Update enrollment activity timestamp
        now = datetime.now(timezone.utc)
        await project_repo.update_enrollment(db, enrollment, last_activity_at=now)

        return ProjectStepResponse(
            id=step.id,
            project_id=step.project_id,
            title=step.title,
            description=step.description,
            step_order=step.step_order,
            step_type=step.step_type,
            instructions=step.instructions,
            command=step.command,
            expected_outcome=step.expected_outcome,
            is_required=step.is_required,
            completed=prog.status == StepProgressStatus.COMPLETED.value,
            status=prog.status,
            started_at=prog.started_at,
            completed_at=prog.completed_at,
        )

    async def complete_step(
        self,
        db: AsyncSession,
        *,
        user_id: str,
        project_identifier: str,
        step_id: str,
        notes: Optional[str] = None,
    ) -> ProjectProgressResponse:
        """
        Complete a project step idempotently, recalculate completion percentage,
        and update project completion status if all required steps are completed.
        """
        project = await project_repo.get_by_id_or_slug(
            db, identifier=project_identifier
        )
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project '{project_identifier}' not found.",
            )

        step = await project_repo.get_step_by_id(
            db, step_id=step_id, project_id=project.id
        )
        if not step:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Step '{step_id}' not found in project '{project.title}'.",
            )

        # Ensure user is enrolled
        enrollment, _ = await project_repo.enroll_user(
            db, user_id=user_id, project_id=project.id
        )

        # Mark step complete idempotently
        prog, is_newly_completed = await project_repo.complete_step(
            db, user_id=user_id, step_id=step.id, notes=notes
        )

        now = datetime.now(timezone.utc)

        if is_newly_completed:
            # Log step completion activity
            await activity_repo.log_activity(
                db,
                user_id=user_id,
                activity_type=ActivityType.PROJECT_STEP_COMPLETED.value,
                metadata={
                    "project_id": project.id,
                    "project_title": project.title,
                    "step_id": step.id,
                    "step_title": step.title,
                    "step_order": step.step_order,
                },
            )
            logger.info(
                "User %s completed step %s (%s) for project %s",
                user_id,
                step.title,
                step.id,
                project.title,
            )

        # Re-evaluate all steps to check if project is completed
        user_progs = await project_repo.get_user_step_progress_list_for_project(
            db, user_id=user_id, project_id=project.id
        )
        progress_map = {p.project_step_id: p for p in user_progs}

        total_steps = len(project.steps) if project.steps else 0
        required_steps = [s for s in (project.steps or []) if s.is_required]
        total_required = len(required_steps)

        completed_count = sum(
            1 for p in user_progs if p.status == StepProgressStatus.COMPLETED.value
        )
        completed_required_count = sum(
            1
            for s in required_steps
            if progress_map.get(s.id)
            and progress_map[s.id].status == StepProgressStatus.COMPLETED.value
        )

        progress_pct = (
            round((completed_count / total_steps) * 100.0, 1)
            if total_steps > 0
            else 0.0
        )

        # Check project completion condition
        all_required_done = (
            total_required > 0 and completed_required_count >= total_required
        )

        if (
            all_required_done
            and enrollment.status != ProjectEnrollmentStatus.COMPLETED.value
        ):
            # Mark enrollment as completed
            await project_repo.update_enrollment(
                db,
                enrollment,
                status=ProjectEnrollmentStatus.COMPLETED.value,
                completed_at=now,
                last_activity_at=now,
            )
            # Log project completed event
            await activity_repo.log_activity(
                db,
                user_id=user_id,
                activity_type=ActivityType.PROJECT_COMPLETED.value,
                metadata={
                    "project_id": project.id,
                    "project_title": project.title,
                    "project_slug": project.slug,
                    "completed_steps": completed_count,
                    "total_steps": total_steps,
                },
            )
            logger.info(
                "User %s completed project %s (%s)", user_id, project.title, project.id
            )
        else:
            await project_repo.update_enrollment(
                db,
                enrollment,
                last_activity_at=now,
            )

        step_responses = self._build_step_responses(project.steps or [], progress_map)
        is_completed = enrollment.status == ProjectEnrollmentStatus.COMPLETED.value

        return ProjectProgressResponse(
            project_id=project.id,
            user_id=user_id,
            status=enrollment.status,
            progress_percentage=progress_pct,
            completed_steps=completed_count,
            total_steps=total_steps,
            is_completed=is_completed,
            started_at=enrollment.started_at,
            completed_at=enrollment.completed_at,
            last_activity_at=enrollment.last_activity_at,
            steps=step_responses,
        )


project_service = ProjectService()
