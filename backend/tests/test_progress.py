"""
Comprehensive Test Suite for Phase 4: Learning Progress & Dashboard Analytics.
"""
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, get_password_hash
from app.models.course import Course, CourseCategory, CourseDifficulty, CourseEnrollment, CourseModule, EnrollmentStatus, Lesson
from app.models.progress import ActivityType, LearningActivity, LessonProgress, LessonProgressStatus
from app.models.user import User, UserRole


async def create_test_user(db: AsyncSession, email: str = "student@cloudforge.io", role: str = "student") -> User:
    """Helper to create and commit a test user."""
    user = User(
        email=email,
        hashed_password=get_password_hash("Password123!"),
        name="Alex Mercer",
        role=UserRole(role),
        is_active=True,
        is_verified=True,
        learning_goal="DevOps",
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def create_test_course_with_lessons(db: AsyncSession, slug: str = "k8s-fundamentals") -> Tuple[Course, Lesson, Lesson]:
    """Helper to create a course with 1 module and 2 published lessons."""
    course = Course(
        slug=slug,
        title="Kubernetes Fundamentals",
        category="Kubernetes",
        difficulty="Beginner",
        duration_minutes=120,
        thumbnail_url="https://cloudforge.test/thumb.png",
        description="Kubernetes basics",
        published=True,
    )
    db.add(course)
    await db.flush()

    module = CourseModule(
        course_id=course.id,
        module_number="01",
        title="Pods & Services",
        order_index=0,
        published=True,
    )
    db.add(module)
    await db.flush()

    lesson1 = Lesson(
        module_id=module.id,
        title="Understanding Pods",
        slug="understanding-pods",
        lesson_type="theory",
        estimated_minutes=15,
        order_index=0,
        published=True,
    )
    lesson2 = Lesson(
        module_id=module.id,
        title="Understanding Services",
        slug="understanding-services",
        lesson_type="hands-on",
        estimated_minutes=20,
        order_index=1,
        published=True,
    )
    db.add_all([lesson1, lesson2])
    await db.commit()
    await db.refresh(course)
    await db.refresh(lesson1)
    await db.refresh(lesson2)
    return course, lesson1, lesson2



@pytest.mark.asyncio
async def test_lesson_start_flow(client: AsyncClient, db_session: AsyncSession):
    """Test starting a lesson updates status to in_progress and records activity."""
    user = await create_test_user(db_session, email="start_user@cloudforge.io")
    token = create_access_token(subject=user.id, role=user.role.value, email=user.email)
    headers = {"Authorization": f"Bearer {token}"}

    course, lesson1, _ = await create_test_course_with_lessons(db_session, slug="course-start-test")

    # Start lesson
    response = await client.post(f"/api/v1/lessons/{lesson1.id}/start", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["lesson_id"] == lesson1.id
    assert data["user_id"] == user.id
    assert data["status"] == "in_progress"
    assert data["time_spent_seconds"] == 0
    assert data["started_at"] is not None


@pytest.mark.asyncio
async def test_lesson_progress_time_tracking(client: AsyncClient, db_session: AsyncSession):
    """Test recording incremental study duration seconds."""
    user = await create_test_user(db_session, email="time_user@cloudforge.io")
    token = create_access_token(subject=user.id, role=user.role.value, email=user.email)
    headers = {"Authorization": f"Bearer {token}"}

    course, lesson1, _ = await create_test_course_with_lessons(db_session, slug="course-time-test")

    # 1. Send valid progress
    res1 = await client.post(
        f"/api/v1/lessons/{lesson1.id}/progress",
        headers=headers,
        json={"time_spent_seconds": 300, "status": "in_progress"}
    )
    assert res1.status_code == 200
    assert res1.json()["time_spent_seconds"] == 300

    # 2. Send additional study time
    res2 = await client.post(
        f"/api/v1/lessons/{lesson1.id}/progress",
        headers=headers,
        json={"time_spent_seconds": 450}
    )
    assert res2.status_code == 200
    assert res2.json()["time_spent_seconds"] == 750

    # 3. Test invalid time rejected (< 0 or > 86400)
    res_neg = await client.post(
        f"/api/v1/lessons/{lesson1.id}/progress",
        headers=headers,
        json={"time_spent_seconds": -50}
    )
    assert res_neg.status_code == 422


@pytest.mark.asyncio
async def test_lesson_completion_and_course_graduation(client: AsyncClient, db_session: AsyncSession):
    """Test complete flow: complete lesson 1 (50%), then complete lesson 2 (100% and marks course completed)."""
    user = await create_test_user(db_session, email="grad_user@cloudforge.io")
    token = create_access_token(subject=user.id, role=user.role.value, email=user.email)
    headers = {"Authorization": f"Bearer {token}"}

    course, lesson1, lesson2 = await create_test_course_with_lessons(db_session, slug="grad-course")

    # Enroll in course
    enroll_res = await client.post(f"/api/v1/courses/{course.slug}/enroll", headers=headers)
    assert enroll_res.status_code == 201

    # 1. Complete Lesson 1
    c1_res = await client.post(
        f"/api/v1/lessons/{lesson1.id}/complete",
        headers=headers,
        json={"time_spent_seconds": 600}
    )
    assert c1_res.status_code == 200
    assert c1_res.json()["status"] == "completed"

    # Check course progress = 50%
    prog1 = await client.get(f"/api/v1/users/me/courses/{course.id}/progress", headers=headers)
    assert prog1.status_code == 200
    pdata1 = prog1.json()
    assert pdata1["completed_lessons"] == 1
    assert pdata1["total_lessons"] == 2
    assert pdata1["progress_percentage"] == 50.0
    assert pdata1["status"] == "active"

    # 2. Complete Lesson 2 (Final lesson)
    c2_res = await client.post(
        f"/api/v1/lessons/{lesson2.id}/complete",
        headers=headers,
        json={"time_spent_seconds": 900}
    )
    assert c2_res.status_code == 200

    # Check course progress = 100% and enrollment status = completed
    prog2 = await client.get(f"/api/v1/users/me/courses/{course.id}/progress", headers=headers)
    assert prog2.status_code == 200
    pdata2 = prog2.json()
    assert pdata2["completed_lessons"] == 2
    assert pdata2["progress_percentage"] == 100.0
    assert pdata2["status"] == "completed"
    assert pdata2["completed_at"] is not None


@pytest.mark.asyncio
async def test_duplicate_completion_idempotency(client: AsyncClient, db_session: AsyncSession):
    """Test calling complete multiple times is idempotent and does not corrupt records."""
    user = await create_test_user(db_session, email="idemp_user@cloudforge.io")
    token = create_access_token(subject=user.id, role=user.role.value, email=user.email)
    headers = {"Authorization": f"Bearer {token}"}

    course, lesson1, _ = await create_test_course_with_lessons(db_session, slug="idemp-course")

    res1 = await client.post(f"/api/v1/lessons/{lesson1.id}/complete", headers=headers)
    assert res1.status_code == 200
    assert res1.json()["status"] == "completed"

    # Repeat complete
    res2 = await client.post(f"/api/v1/lessons/{lesson1.id}/complete", headers=headers)
    assert res2.status_code == 200
    assert res2.json()["status"] == "completed"
    assert res2.json()["id"] == res1.json()["id"]


@pytest.mark.asyncio
async def test_streak_calculation_and_activity_feed(client: AsyncClient, db_session: AsyncSession):
    """Test streak calculation algorithm and activity stream."""
    user = await create_test_user(db_session, email="streak_user@cloudforge.io")
    token = create_access_token(subject=user.id, role=user.role.value, email=user.email)
    headers = {"Authorization": f"Bearer {token}"}

    now = datetime.now(timezone.utc)
    # Seed 3 consecutive days of activity (today, yesterday, 2 days ago)
    for i in range(3):
        act = LearningActivity(
            user_id=user.id,
            activity_type=ActivityType.LESSON_COMPLETED.value,
            duration_seconds=1800,
            activity_metadata={"day": i},
            created_at=now - timedelta(days=i),
        )
        db_session.add(act)
    await db_session.commit()

    # Query overall progress
    res = await client.get("/api/v1/users/me/progress", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["current_streak"] == 3
    assert data["longest_streak"] >= 3

    # Query recent activity
    act_res = await client.get("/api/v1/users/me/activity/recent", headers=headers)
    assert act_res.status_code == 200
    activities = act_res.json()
    assert len(activities) == 3


@pytest.mark.asyncio
async def test_continue_learning_resolution(client: AsyncClient, db_session: AsyncSession):
    """Test GET /api/v1/users/me/continue-learning picks up active in_progress lesson."""
    user = await create_test_user(db_session, email="continue_user@cloudforge.io")
    token = create_access_token(subject=user.id, role=user.role.value, email=user.email)
    headers = {"Authorization": f"Bearer {token}"}

    course, lesson1, lesson2 = await create_test_course_with_lessons(db_session, slug="continue-course")

    # Enroll
    await client.post(f"/api/v1/courses/{course.slug}/enroll", headers=headers)

    # Start Lesson 1
    await client.post(f"/api/v1/lessons/{lesson1.id}/start", headers=headers)

    # Fetch continue learning
    res = await client.get("/api/v1/users/me/continue-learning", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data is not None
    assert data["lesson_id"] == lesson1.id
    assert data["course_slug"] == course.slug


@pytest.mark.asyncio
async def test_unified_dashboard_aggregation(client: AsyncClient, db_session: AsyncSession):
    """Test unified GET /api/v1/users/me/dashboard single-roundtrip aggregation."""
    user = await create_test_user(db_session, email="dash_user@cloudforge.io")
    token = create_access_token(subject=user.id, role=user.role.value, email=user.email)
    headers = {"Authorization": f"Bearer {token}"}

    course, lesson1, _ = await create_test_course_with_lessons(db_session, slug="dash-course")
    await client.post(f"/api/v1/courses/{course.slug}/enroll", headers=headers)
    await client.post(f"/api/v1/lessons/{lesson1.id}/complete", headers=headers, json={"time_spent_seconds": 3600})

    res = await client.get("/api/v1/users/me/dashboard", headers=headers)
    assert res.status_code == 200
    payload = res.json()

    assert "user" in payload
    assert payload["user"]["email"] == "dash_user@cloudforge.io"
    assert "stats" in payload
    assert payload["stats"]["learning_hours"] >= 1.0
    assert payload["stats"]["courses_enrolled"] == 1
    assert payload["stats"]["lessons_completed"] == 1
    assert "weekly_activity" in payload
    assert "weekly_hours" in payload
    assert "course_progress" in payload
    assert len(payload["course_progress"]) == 1
