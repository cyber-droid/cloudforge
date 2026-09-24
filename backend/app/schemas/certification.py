"""
Certification, Training, and Practice Exam Pydantic v2 Schemas.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, ConfigDict, Field


class ExamDomainSchema(BaseModel):
    """Domain weighting breakdown for official exam blueprint."""

    name: str
    percentage: int


class CertificationSummaryResponse(BaseModel):
    """Catalog summary of a certification or prep track."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    code: Optional[str] = None
    title: str
    name: str
    slug: str
    provider: str
    vendor: str
    level: str
    category: str
    badge_icon: str
    duration: str
    training_title: str
    description: str
    training_certificate_name: str
    official_url: Optional[str] = None
    is_official_certification: bool
    is_published: bool
    exam_domains: List[Dict[str, Any]] = Field(default_factory=list)
    domains: List[Dict[str, Any]] = Field(default_factory=list)
    skills_gained: List[str] = Field(default_factory=list)
    practice_questions_count: int
    mock_exams_count: int
    progress: float = 0.0  # User readiness percentage (0-100) when authenticated
    created_at: Optional[datetime] = None


class CertificationDetailResponse(CertificationSummaryResponse):
    """Detailed certification view including training curriculum tracks."""

    trainings: List["TrainingSummaryResponse"] = Field(default_factory=list)


class CertificationListResponse(BaseModel):
    """Paginated or filtered certification catalog response."""

    items: List[CertificationSummaryResponse]
    total: int


class TrainingSummaryResponse(BaseModel):
    """Summary of a structured certification training track."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    certification_id: str
    title: str
    slug: str
    description: str
    level: str
    estimated_hours: Union[str, int] = "18h"
    course_id: Optional[str] = None
    modules: List[str] = Field(default_factory=list)
    is_published: bool
    progress_percentage: float = 0.0
    status: str = (
        "not_enrolled"  # 'not_enrolled', 'enrolled', 'in_progress', 'completed'
    )
    created_at: Optional[datetime] = None


class TrainingDetailResponse(TrainingSummaryResponse):
    """Full detail view of training program with linked course preview."""

    course_title: Optional[str] = None
    course_slug: Optional[str] = None
    total_lessons: int = 0
    completed_lessons: int = 0


class TrainingProgressResponse(BaseModel):
    """Live progress breakdown for a certification training program."""

    training_id: str
    certification_id: str
    status: str
    progress_percentage: float
    completed_lessons: int
    total_lessons: int
    completed_modules: int
    total_modules: int
    is_eligible_for_certificate: bool
    certificate_id: Optional[str] = None


class PracticeQuestionPublicResponse(BaseModel):
    """Practice question sent during an exam (OMITS correct option and explanation)."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    question_text: str
    question_type: str = "single_choice"
    options: List[str]
    topic: Optional[str] = None
    domain: Optional[str] = None
    difficulty: str = "medium"
    points: int = 10


class PracticeAttemptStartRequest(BaseModel):
    """Request to initiate a new practice quiz or mock exam."""

    attempt_type: str = "practice_quiz"  # 'practice_quiz', 'practice_exam'
    limit: int = 10
    question_count: Optional[int] = None
    domain: Optional[str] = None


class QuestionAnswerItem(BaseModel):
    """Answer submission for a specific question."""

    question_id: str
    selected_option: int


class PracticeAttemptSubmitRequest(BaseModel):
    """User submission for evaluation by backend."""

    answers: Optional[Any] = (
        None  # Supports either Dict[str, int] or List[QuestionAnswerItem]
    )
    time_spent_seconds: int = 0


class QuestionReviewResponse(BaseModel):
    """Question review item returned AFTER exam submission."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: Optional[str] = None
    question_id: Optional[str] = None
    question_text: str
    options: List[str]
    topic: Optional[str] = None
    domain: Optional[str] = None
    difficulty: str = "medium"
    selected_answer: Optional[int] = None
    selected_option: Optional[int] = None
    correct_answer: Optional[int] = None
    correct_option: Optional[int] = None
    is_correct: bool
    explanation: str
    points_earned: int = 0


class PracticeAttemptDetailResponse(BaseModel):
    """Practice attempt session with questions (omits correct answers/explanations)."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    certification_id: str
    attempt_type: str
    total_questions: int
    score: int = 0
    percentage: float = 0.0
    passed: bool = False
    passing_percentage: float = 70.0
    correct_answers: int = 0
    time_spent_seconds: int = 0
    started_at: datetime
    submitted_at: Optional[datetime] = None
    questions: List[PracticeQuestionPublicResponse] = Field(default_factory=list)


class PracticeAttemptResultResponse(BaseModel):
    """Evaluated score and feedback for a completed practice attempt."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    certification_id: str
    attempt_type: str
    score: int
    percentage: float
    passed: bool
    passing_percentage: float
    total_questions: int
    correct_answers: int
    time_spent_seconds: int
    started_at: datetime
    submitted_at: Optional[datetime] = None
    results: List[QuestionReviewResponse] = Field(default_factory=list)
    question_results: List[QuestionReviewResponse] = Field(default_factory=list)


class PracticeAttemptSummaryResponse(BaseModel):
    """Brief history summary item for previous exam attempts."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    certification_id: str
    certification_title: Optional[str] = None
    certification_code: Optional[str] = None
    attempt_type: str
    score: int
    percentage: float
    passed: bool
    total_questions: int
    correct_answers: int
    time_spent_seconds: int
    started_at: datetime
    submitted_at: Optional[datetime] = None
