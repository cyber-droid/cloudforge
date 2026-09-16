"""
Roadmap and Step Progression Repository Layer.
"""
from datetime import datetime, timezone
from typing import List, Optional, Tuple
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.roadmap import Roadmap, RoadmapStatus, RoadmapStep, UserRoadmapProgress


class RoadmapRepository:
    """Data access methods for Roadmaps, Steps, and UserRoadmapProgress."""

    async def get_paginated(
        self,
        db: AsyncSession,
        *,
        page: int = 1,
        page_size: int = 10,
        search: Optional[str] = None,
        category: Optional[str] = None,
        difficulty: Optional[str] = None,
        published: Optional[bool] = None,
    ) -> Tuple[List[Roadmap], int]:
        """Fetch paginated roadmap catalog with SQL filters."""
        query = select(Roadmap).options(
            selectinload(Roadmap.steps).selectinload(RoadmapStep.course),
            selectinload(Roadmap.steps).selectinload(RoadmapStep.skill),
        )

        if published is not None:
            query = query.where(Roadmap.published == published)
        if category and category != "All":
            query = query.where(Roadmap.category == category)
        if difficulty and difficulty != "All":
            query = query.where(Roadmap.difficulty == difficulty)
        if search:
            query = query.where(
                or_(
                    Roadmap.title.ilike(f"%{search}%"),
                    Roadmap.description.ilike(f"%{search}%"),
                )
            )

        # Count total matches
        count_query = select(func.count()).select_from(query.order_by(None).subquery())
        count_res = await db.execute(count_query)
        total = count_res.scalar() or 0

        # Apply ordering and pagination
        offset = (page - 1) * page_size
        query = query.order_by(Roadmap.created_at.asc()).offset(offset).limit(page_size)
        result = await db.execute(query)
        return list(result.scalars().all()), total

    async def get_by_id_or_slug(
        self,
        db: AsyncSession,
        *,
        identifier: str
    ) -> Optional[Roadmap]:
        """Fetch single roadmap by UUID or slug with steps and connected relations."""
        query = (
            select(Roadmap)
            .options(
                selectinload(Roadmap.steps).selectinload(RoadmapStep.course),
                selectinload(Roadmap.steps).selectinload(RoadmapStep.skill),
            )
            .where(or_(Roadmap.id == identifier, Roadmap.slug == identifier))
        )
        result = await db.execute(query)
        return result.scalars().first()

    async def get_steps_for_roadmap(
        self,
        db: AsyncSession,
        *,
        roadmap_id: str
    ) -> List[RoadmapStep]:
        """Fetch ordered step nodes for a roadmap."""
        query = (
            select(RoadmapStep)
            .options(
                selectinload(RoadmapStep.course),
                selectinload(RoadmapStep.skill),
            )
            .where(RoadmapStep.roadmap_id == roadmap_id)
            .order_by(RoadmapStep.order_index.asc())
        )
        result = await db.execute(query)
        return list(result.scalars().all())

    async def get_user_roadmap(
        self,
        db: AsyncSession,
        *,
        user_id: str,
        roadmap_id: str
    ) -> Optional[UserRoadmapProgress]:
        """Fetch single user roadmap enrollment record."""
        query = (
            select(UserRoadmapProgress)
            .options(
                selectinload(UserRoadmapProgress.roadmap)
                .selectinload(Roadmap.steps)
                .selectinload(RoadmapStep.course),
                selectinload(UserRoadmapProgress.roadmap)
                .selectinload(Roadmap.steps)
                .selectinload(RoadmapStep.skill),
            )
            .where(
                UserRoadmapProgress.user_id == user_id,
                UserRoadmapProgress.roadmap_id == roadmap_id,
            )
        )
        result = await db.execute(query)
        return result.scalars().first()

    async def get_user_roadmaps(
        self,
        db: AsyncSession,
        *,
        user_id: str
    ) -> List[UserRoadmapProgress]:
        """Fetch all roadmaps started by a student."""
        query = (
            select(UserRoadmapProgress)
            .options(
                selectinload(UserRoadmapProgress.roadmap)
                .selectinload(Roadmap.steps)
                .selectinload(RoadmapStep.course),
                selectinload(UserRoadmapProgress.roadmap)
                .selectinload(Roadmap.steps)
                .selectinload(RoadmapStep.skill),
            )
            .where(UserRoadmapProgress.user_id == user_id)
            .order_by(UserRoadmapProgress.last_accessed_at.desc())
        )
        result = await db.execute(query)
        return list(result.scalars().all())

    async def start_roadmap(
        self,
        db: AsyncSession,
        *,
        user_id: str,
        roadmap_id: str
    ) -> UserRoadmapProgress:
        """Enroll user in a career roadmap with duplicate prevention."""
        now = datetime.now(timezone.utc)
        record = await self.get_user_roadmap(db, user_id=user_id, roadmap_id=roadmap_id)

        if not record:
            record = UserRoadmapProgress(
                user_id=user_id,
                roadmap_id=roadmap_id,
                status=RoadmapStatus.IN_PROGRESS.value,
                started_at=now,
                last_accessed_at=now,
            )
            db.add(record)
            await db.commit()
            await db.refresh(record)
        else:
            record.last_accessed_at = now
            await db.commit()

        return record


roadmap_repo = RoadmapRepository()
