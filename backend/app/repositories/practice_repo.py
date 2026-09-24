"""
Practice Question and Exam Attempt Repository.

Handles querying question banks, starting new exam sessions, persisting student answers, and retrieving attempt history.
"""

import random
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.certification import (
    AttemptType,
    PracticeAttempt,
    PracticeAttemptAnswer,
    PracticeQuestion,
)


class PracticeRepository:
    """Repository handling Practice Questions and Exam Attempt evaluation."""

    async def get_questions_for_cert(
        self,
        db: AsyncSession,
        *,
        certification_id: str,
        domain: Optional[str] = None,
        difficulty: Optional[str] = None,
        limit: int = 10,
        randomize: bool = True,
    ) -> List[PracticeQuestion]:
        """Fetch question bank entries for practice exam or quiz."""
        query = select(PracticeQuestion).where(
            PracticeQuestion.certification_id == certification_id,
            PracticeQuestion.is_published.is_(True),
        )

        if domain and domain != "All":
            query = query.where(func.lower(PracticeQuestion.domain) == domain.lower())

        if difficulty and difficulty != "All":
            query = query.where(
                func.lower(PracticeQuestion.difficulty) == difficulty.lower()
            )

        result = await db.execute(query)
        all_matching = list(result.scalars().all())

        if randomize and len(all_matching) > limit:
            return random.sample(all_matching, limit)
        return all_matching[:limit]

    async def get_questions_by_ids(
        self,
        db: AsyncSession,
        *,
        question_ids: List[str],
    ) -> Dict[str, PracticeQuestion]:
        """Fetch dictionary of questions by IDs for fast server-side grading."""
        if not question_ids:
            return {}

        query = select(PracticeQuestion).where(PracticeQuestion.id.in_(question_ids))
        result = await db.execute(query)
        questions = result.scalars().all()
        return {q.id: q for q in questions}

    async def create_attempt(
        self,
        db: AsyncSession,
        *,
        user_id: str,
        certification_id: str,
        training_id: Optional[str] = None,
        attempt_type: str = AttemptType.PRACTICE_EXAM.value,
        total_questions: int = 0,
        passing_percentage: float = 70.0,
    ) -> PracticeAttempt:
        """Create a new exam attempt instance."""
        attempt = PracticeAttempt(
            user_id=user_id,
            certification_id=certification_id,
            training_id=training_id,
            attempt_type=attempt_type,
            started_at=datetime.now(timezone.utc),
            total_questions=total_questions,
            passing_percentage=passing_percentage,
            score=0,
            percentage=0.0,
            passed=False,
        )
        db.add(attempt)
        await db.flush()
        await db.refresh(attempt)
        return attempt

    async def get_attempt_by_id(
        self,
        db: AsyncSession,
        *,
        attempt_id: str,
        user_id: Optional[str] = None,
    ) -> Optional[PracticeAttempt]:
        """Fetch single exam attempt with eager loaded answers and questions."""
        query = (
            select(PracticeAttempt)
            .options(
                selectinload(PracticeAttempt.answers).selectinload(
                    PracticeAttemptAnswer.question
                ),
                selectinload(PracticeAttempt.certification),
            )
            .where(PracticeAttempt.id == attempt_id)
        )

        if user_id:
            query = query.where(PracticeAttempt.user_id == user_id)

        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def list_user_attempts(
        self,
        db: AsyncSession,
        *,
        user_id: str,
        certification_id: Optional[str] = None,
        attempt_type: Optional[str] = None,
        passed_only: Optional[bool] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> Tuple[List[PracticeAttempt], int]:
        """Fetch student's exam attempt history with filters."""
        query = (
            select(PracticeAttempt)
            .options(
                selectinload(PracticeAttempt.certification),
            )
            .where(PracticeAttempt.user_id == user_id)
        )

        if certification_id:
            query = query.where(PracticeAttempt.certification_id == certification_id)

        if attempt_type:
            query = query.where(PracticeAttempt.attempt_type == attempt_type)

        if passed_only is not None:
            query = query.where(PracticeAttempt.passed.is_(passed_only))

        count_query = select(func.count()).select_from(query.subquery())
        total_res = await db.execute(count_query)
        total = total_res.scalar() or 0

        query = (
            query.order_by(PracticeAttempt.started_at.desc()).offset(skip).limit(limit)
        )
        result = await db.execute(query)
        items = list(result.scalars().all())

        return items, total

    async def save_attempt_answers_and_finalize(
        self,
        db: AsyncSession,
        *,
        attempt: PracticeAttempt,
        answers: List[PracticeAttemptAnswer],
        score: int,
        percentage: float,
        passed: bool,
        correct_answers: int,
        time_spent_seconds: int,
    ) -> PracticeAttempt:
        """Persist answers and score evaluation transactionally."""
        db.add_all(answers)

        attempt.score = score
        attempt.percentage = percentage
        attempt.passed = passed
        attempt.correct_answers = correct_answers
        attempt.time_spent_seconds = time_spent_seconds
        attempt.submitted_at = datetime.now(timezone.utc)

        await db.flush()
        await db.refresh(attempt)
        return attempt


practice_repo = PracticeRepository()
