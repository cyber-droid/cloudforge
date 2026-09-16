"""
Practice Exam and Question Service.

Handles timed mock exam simulation, hiding answers before submission, server-side grading, and explanation reviews.
"""
from typing import Dict, List, Optional
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.certification import AttemptType, PracticeAttempt, PracticeAttemptAnswer
from app.repositories.certification_repo import certification_repo
from app.repositories.practice_repo import practice_repo
from app.schemas.certification import (
    PracticeAttemptDetailResponse,
    PracticeAttemptResultResponse,
    PracticeAttemptStartRequest,
    PracticeAttemptSubmitRequest,
    PracticeAttemptSummaryResponse,
    PracticeQuestionPublicResponse,
    QuestionReviewResponse,
)


class PracticeService:
    """Service handling practice quiz/mock exam lifecycle and evaluation."""

    async def start_attempt(
        self,
        db: AsyncSession,
        *,
        user_id: str,
        certification_id: str,
        data: PracticeAttemptStartRequest,
    ) -> PracticeAttemptDetailResponse:
        """
        Start an exam attempt. Returns questions with choices strictly OMITTING correct answers and explanations.
        """
        cert = await certification_repo.get_by_id_or_slug(db, identifier=certification_id)
        if not cert:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Certification '{certification_id}' not found.",
            )

        questions = await practice_repo.get_questions_for_cert(
            db,
            certification_id=cert.id,
            domain=data.domain,
            limit=data.limit,
            randomize=True,
        )

        if not questions:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No published practice questions available for this certification.",
            )

        attempt = await practice_repo.create_attempt(
            db,
            user_id=user_id,
            certification_id=cert.id,
            attempt_type=data.attempt_type,
            total_questions=len(questions),
            passing_percentage=70.0,
        )

        public_questions = [
            PracticeQuestionPublicResponse(
                id=q.id,
                question_text=q.question_text,
                question_type=q.question_type,
                options=q.options,
                domain=q.domain,
                difficulty=q.difficulty,
                points=q.points,
            )
            for q in questions
        ]

        return PracticeAttemptDetailResponse(
            id=attempt.id,
            certification_id=attempt.certification_id,
            attempt_type=attempt.attempt_type,
            score=attempt.score,
            percentage=attempt.percentage,
            passed=attempt.passed,
            passing_percentage=attempt.passing_percentage,
            total_questions=attempt.total_questions,
            correct_answers=attempt.correct_answers,
            time_spent_seconds=attempt.time_spent_seconds,
            started_at=attempt.started_at,
            submitted_at=attempt.submitted_at,
            questions=public_questions,
        )

    async def submit_attempt(
        self,
        db: AsyncSession,
        *,
        user_id: str,
        attempt_id: str,
        data: PracticeAttemptSubmitRequest,
    ) -> PracticeAttemptResultResponse:
        """
        Submit user answers for server-side evaluation.
        Calculates correctness, persists answers transactionally, and returns full question explanations.
        """
        attempt = await practice_repo.get_attempt_by_id(db, attempt_id=attempt_id, user_id=user_id)
        if not attempt:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Practice attempt '{attempt_id}' not found.",
            )

        if attempt.submitted_at is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This practice attempt has already been submitted and finalized.",
            )

        # Normalize answers to dict: {question_id: selected_option_int}
        answers_dict: Dict[str, int] = {}
        if isinstance(data.answers, dict):
            answers_dict = {str(k): int(v) for k, v in data.answers.items()}
        elif isinstance(data.answers, list):
            for item in data.answers:
                if isinstance(item, dict):
                    q_id = item.get("question_id") or item.get("id")
                    opt = item.get("selected_option") if item.get("selected_option") is not None else item.get("selected_answer", -1)
                    if q_id:
                        answers_dict[str(q_id)] = int(opt)
                elif hasattr(item, "question_id") and hasattr(item, "selected_option"):
                    answers_dict[str(item.question_id)] = int(item.selected_option)

        question_ids = list(answers_dict.keys())
        questions_map = await practice_repo.get_questions_by_ids(db, question_ids=question_ids)

        if not questions_map:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No valid questions matched the submitted answers.",
            )

        attempt_answers: List[PracticeAttemptAnswer] = []
        review_items: List[QuestionReviewResponse] = []
        correct_count = 0
        total_points = 0
        total_possible = 0

        for q_id, q_entity in questions_map.items():
            selected_idx = answers_dict.get(q_id, -1)
            is_correct = (selected_idx == q_entity.correct_option)
            pts = q_entity.points if is_correct else 0

            if is_correct:
                correct_count += 1

            total_points += pts
            total_possible += q_entity.points

            ans_record = PracticeAttemptAnswer(
                attempt_id=attempt.id,
                question_id=q_id,
                selected_answer=selected_idx,
                is_correct=is_correct,
                points_earned=pts,
            )
            attempt_answers.append(ans_record)

            review_items.append(
                QuestionReviewResponse(
                    id=q_entity.id,
                    question_id=q_entity.id,
                    question_text=q_entity.question_text,
                    options=q_entity.options,
                    topic=q_entity.topic,
                    domain=q_entity.topic,
                    difficulty=q_entity.difficulty,
                    selected_answer=selected_idx,
                    selected_option=selected_idx,
                    correct_answer=q_entity.correct_option,
                    correct_option=q_entity.correct_option,
                    is_correct=is_correct,
                    explanation=q_entity.explanation,
                    points_earned=pts,
                )
            )

        total_q = len(questions_map)
        score_pct = round((correct_count / total_q) * 100.0, 1) if total_q > 0 else 0.0
        passed = score_pct >= attempt.passing_percentage

        # Finalize and persist
        finalized_attempt = await practice_repo.save_attempt_answers_and_finalize(
            db,
            attempt=attempt,
            answers=attempt_answers,
            score=total_points if total_points > 0 else correct_count,
            percentage=score_pct,
            passed=passed,
            correct_answers=correct_count,
            time_spent_seconds=data.time_spent_seconds,
        )

        return PracticeAttemptResultResponse(
            id=finalized_attempt.id,
            certification_id=finalized_attempt.certification_id,
            attempt_type=finalized_attempt.attempt_type,
            score=finalized_attempt.score,
            percentage=finalized_attempt.percentage,
            passed=finalized_attempt.passed,
            passing_percentage=finalized_attempt.passing_percentage,
            total_questions=total_q,
            correct_answers=correct_count,
            time_spent_seconds=finalized_attempt.time_spent_seconds,
            started_at=finalized_attempt.started_at,
            submitted_at=finalized_attempt.submitted_at,
            results=review_items,
            question_results=review_items,
        )

    async def get_attempt_results(
        self,
        db: AsyncSession,
        *,
        user_id: str,
        attempt_id: str,
    ) -> PracticeAttemptResultResponse:
        """Retrieve results and review explanations for a completed attempt."""
        attempt = await practice_repo.get_attempt_by_id(db, attempt_id=attempt_id, user_id=user_id)
        if not attempt:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Practice attempt '{attempt_id}' not found.",
            )

        if attempt.submitted_at is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Practice attempt is still in progress and has not been submitted.",
            )

        review_items: List[QuestionReviewResponse] = []
        for ans in (attempt.answers or []):
            q = ans.question
            if q:
                review_items.append(
                    QuestionReviewResponse(
                        id=q.id,
                        question_id=q.id,
                        question_text=q.question_text,
                        options=q.options,
                        topic=q.topic,
                        domain=q.topic,
                        difficulty=q.difficulty,
                        selected_answer=ans.selected_answer,
                        selected_option=ans.selected_answer,
                        correct_answer=q.correct_option,
                        correct_option=q.correct_option,
                        is_correct=ans.is_correct,
                        explanation=q.explanation,
                        points_earned=ans.points_earned,
                    )
                )

        return PracticeAttemptResultResponse(
            id=attempt.id,
            certification_id=attempt.certification_id,
            attempt_type=attempt.attempt_type,
            score=attempt.score,
            percentage=attempt.percentage,
            passed=attempt.passed,
            passing_percentage=attempt.passing_percentage,
            total_questions=attempt.total_questions,
            correct_answers=attempt.correct_answers,
            time_spent_seconds=attempt.time_spent_seconds,
            started_at=attempt.started_at,
            submitted_at=attempt.submitted_at,
            results=review_items,
            question_results=review_items,
        )

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
    ) -> List[PracticeAttemptSummaryResponse]:
        """Fetch list of user's past practice attempts."""
        attempts, _ = await practice_repo.list_user_attempts(
            db,
            user_id=user_id,
            certification_id=certification_id,
            attempt_type=attempt_type,
            passed_only=passed_only,
            skip=skip,
            limit=limit,
        )

        return [
            PracticeAttemptSummaryResponse(
                id=a.id,
                certification_id=a.certification_id,
                certification_title=a.certification.title if a.certification else None,
                certification_code=a.certification.code if a.certification else None,
                attempt_type=a.attempt_type,
                score=a.score,
                percentage=a.percentage,
                passed=a.passed,
                total_questions=a.total_questions,
                correct_answers=a.correct_answers,
                time_spent_seconds=a.time_spent_seconds,
                started_at=a.started_at,
                submitted_at=a.submitted_at,
            )
            for a in attempts
        ]


practice_service = PracticeService()
