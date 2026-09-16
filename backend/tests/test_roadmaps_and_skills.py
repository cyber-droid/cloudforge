"""
Comprehensive Test Suite for Phase 5: Learning Roadmaps & Technical Skills Development.
"""
from datetime import datetime, timezone
from typing import Optional, Tuple
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, get_password_hash
from app.models.course import Course, CourseEnrollment, CourseModule, EnrollmentStatus, Lesson
from app.models.progress import LessonProgress, LessonProgressStatus
from app.models.roadmap import Roadmap, RoadmapStep, RoadmapStepType, UserRoadmapProgress
from app.models.skill import CourseSkill, Skill, SkillCategory, UserSkill, get_level_from_percentage
from app.models.user import User, UserRole


async def create_test_user(db: AsyncSession, email: str = "engineer@cloudforge.io") -> User:
    """Helper to create and commit a test user."""
    user = User(
        email=email,
        hashed_password=get_password_hash("Password123!"),
        name="Alex Mercer",
        role=UserRole.STUDENT,
        is_active=True,
        is_verified=True,
        learning_goal="DevOps",
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def setup_skills_and_courses(db: AsyncSession) -> Tuple[Skill, Skill, Course, Lesson, Lesson]:
    """Helper to set up 2 skills, 1 course with 2 lessons, and map course to skill."""
    skill_linux = Skill(
        slug="test-linux",
        name="Linux Administration",
        category="DevOps",
        target_level=4,
        trend="+5%",
        description="Linux internals and shell scripting",
    )
    skill_k8s = Skill(
        slug="test-k8s",
        name="Kubernetes Orchestration",
        category="Kubernetes",
        target_level=4,
        trend="+10%",
        description="Kubernetes clusters",
    )
    db.add_all([skill_linux, skill_k8s])
    await db.flush()

    course = Course(
        slug="linux-mastery",
        title="Linux Mastery Course",
        description="Comprehensive Linux mastery course covering shell and daemons",
        category="DevOps",
        difficulty="Beginner",
        duration_minutes=180,
        published=True,
    )
    db.add(course)
    await db.flush()

    # Link course to linux skill
    db.add(CourseSkill(course_id=course.id, skill_id=skill_linux.id, weight=1.0))
    await db.flush()

    module = CourseModule(
        course_id=course.id,
        module_number="01",
        title="Core Shell",
        order_index=0,
        published=True,
    )
    db.add(module)
    await db.flush()

    lesson1 = Lesson(
        module_id=module.id,
        title="Bash Commands",
        slug="bash-commands",
        lesson_type="hands-on",
        estimated_minutes=15,
        order_index=0,
        published=True,
    )
    lesson2 = Lesson(
        module_id=module.id,
        title="Systemd Daemons",
        slug="systemd-daemons",
        lesson_type="hands-on",
        estimated_minutes=20,
        order_index=1,
        published=True,
    )
    db.add_all([lesson1, lesson2])
    await db.commit()
    await db.refresh(skill_linux)
    await db.refresh(skill_k8s)
    await db.refresh(course)
    await db.refresh(lesson1)
    await db.refresh(lesson2)
    return skill_linux, skill_k8s, course, lesson1, lesson2


async def setup_test_roadmap(db: AsyncSession, course: Course, skill: Skill) -> Roadmap:
    """Helper to create a test roadmap with course, skill, and milestone steps."""
    roadmap = Roadmap(
        slug="devops-pathway",
        title="DevOps Pathway",
        category="DevOps",
        difficulty="Intermediate",
        duration_label="6 months",
        skills_count=10,
        projects_count=3,
        description="Complete DevOps career track",
        certifications_targeted=["DevOps Certification"],
        published=True,
    )
    db.add(roadmap)
    await db.flush()

    step1 = RoadmapStep(
        roadmap_id=roadmap.id,
        title="Master Linux",
        step_type=RoadmapStepType.COURSE.value,
        order_index=0,
        required=True,
        estimated_hours="25h",
        skills_covered=["Linux", "Bash"],
        course_id=course.id,
        skill_id=skill.id,
    )
    step2 = RoadmapStep(
        roadmap_id=roadmap.id,
        title="Kubernetes Competency",
        step_type=RoadmapStepType.SKILL.value,
        order_index=1,
        required=True,
        estimated_hours="35h",
        skills_covered=["Kubernetes"],
        skill_id=skill.id,
    )
    step3 = RoadmapStep(
        roadmap_id=roadmap.id,
        title="Final Capstone",
        step_type=RoadmapStepType.MILESTONE.value,
        order_index=2,
        required=True,
        estimated_hours="40h",
        skills_covered=["Production Deployment"],
    )
    db.add_all([step1, step2, step3])
    await db.commit()
    await db.refresh(roadmap)
    return roadmap


@pytest.mark.asyncio
async def test_skills_catalog_and_filtering(client: AsyncClient, db_session: AsyncSession):
    """Test listing skills with domain filtering."""
    skill_linux, skill_k8s, _, _, _ = await setup_skills_and_courses(db_session)

    # 1. List all skills
    res = await client.get("/api/v1/skills")
    assert res.status_code == 200
    skills = res.json()
    assert len(skills) >= 2

    # 2. Filter by category
    res_devops = await client.get("/api/v1/skills?category=DevOps")
    assert res_devops.status_code == 200
    d_skills = res_devops.json()
    assert all(s["category"] == "DevOps" for s in d_skills)


@pytest.mark.asyncio
async def test_user_skill_proficiency_calculation(client: AsyncClient, db_session: AsyncSession):
    """Test that completed lessons and courses deterministically increase student skill score."""
    user = await create_test_user(db_session, email="skill_user@cloudforge.io")
    token = create_access_token(subject=user.id, role=user.role.value, email=user.email)
    headers = {"Authorization": f"Bearer {token}"}

    skill_linux, _, course, lesson1, lesson2 = await setup_skills_and_courses(db_session)

    # Initial skill matrix -> 0%
    matrix_res = await client.get("/api/v1/users/me/skills", headers=headers)
    assert matrix_res.status_code == 200
    matrix = matrix_res.json()
    linux_item = next(s for s in matrix["skills"] if s["slug"] == skill_linux.slug)
    assert linux_item["proficiency_percentage"] == 0.0
    assert linux_item["current_level"] == 1
    assert linux_item["current_level_name"] == "Beginner"

    # Enroll in course and complete Lesson 1 (+5%)
    await client.post(f"/api/v1/courses/{course.slug}/enroll", headers=headers)
    await client.post(f"/api/v1/lessons/{lesson1.id}/complete", headers=headers, json={"time_spent_seconds": 900})

    # Query skill -> 5%
    detail_res1 = await client.get(f"/api/v1/users/me/skills/{skill_linux.slug}", headers=headers)
    assert detail_res1.status_code == 200
    assert detail_res1.json()["proficiency_percentage"] == 5.0

    # Complete Lesson 2 -> Entire Course Completed (+5% lesson + 25% course completion = 35%)
    await client.post(f"/api/v1/lessons/{lesson2.id}/complete", headers=headers, json={"time_spent_seconds": 1200})

    detail_res2 = await client.get(f"/api/v1/users/me/skills/{skill_linux.slug}", headers=headers)
    assert detail_res2.status_code == 200
    p = detail_res2.json()["proficiency_percentage"]
    assert p == 35.0  # (2 lessons * 5%) + (1 course * 25%) = 35%
    assert detail_res2.json()["current_level"] == 2  # 21-40% = Foundational
    assert detail_res2.json()["current_level_name"] == "Foundational"


@pytest.mark.asyncio
async def test_roadmap_catalog_and_details(client: AsyncClient, db_session: AsyncSession):
    """Test listing roadmaps and fetching roadmap detail with ordered steps."""
    skill_linux, _, course, _, _ = await setup_skills_and_courses(db_session)
    roadmap = await setup_test_roadmap(db_session, course, skill_linux)

    # List roadmaps
    list_res = await client.get("/api/v1/roadmaps")
    assert list_res.status_code == 200
    data = list_res.json()
    assert data["total"] >= 1
    assert any(r["slug"] == roadmap.slug for r in data["items"])

    # Detail roadmap
    detail_res = await client.get(f"/api/v1/roadmaps/{roadmap.slug}")
    assert detail_res.status_code == 200
    detail = detail_res.json()
    assert detail["title"] == "DevOps Pathway"
    assert len(detail["nodes"]) == 3
    assert detail["nodes"][0]["title"] == "Master Linux"
    assert detail["nodes"][0]["step_type"] == "course"


@pytest.mark.asyncio
async def test_roadmap_start_and_user_progress_advancement(client: AsyncClient, db_session: AsyncSession):
    """Test full integration: start roadmap, complete mapped course, and verify step completion & roadmap progress %."""
    user = await create_test_user(db_session, email="roadmap_student@cloudforge.io")
    token = create_access_token(subject=user.id, role=user.role.value, email=user.email)
    headers = {"Authorization": f"Bearer {token}"}

    skill_linux, _, course, lesson1, lesson2 = await setup_skills_and_courses(db_session)
    roadmap = await setup_test_roadmap(db_session, course, skill_linux)

    # 1. Start Roadmap
    start_res = await client.post(f"/api/v1/roadmaps/{roadmap.slug}/start", headers=headers)
    assert start_res.status_code == 200
    start_data = start_res.json()
    assert start_data["status"] == "in_progress"
    assert start_data["progress_percentage"] == 0.0
    assert start_data["completed_steps"] == 0

    # Duplicate start idempotency
    start_res_repeat = await client.post(f"/api/v1/roadmaps/{roadmap.slug}/start", headers=headers)
    assert start_res_repeat.status_code == 200
    assert start_res_repeat.json()["id"] == start_data["id"]

    # 2. Complete Course Step (Complete all lessons of course)
    await client.post(f"/api/v1/courses/{course.slug}/enroll", headers=headers)
    await client.post(f"/api/v1/lessons/{lesson1.id}/complete", headers=headers)
    await client.post(f"/api/v1/lessons/{lesson2.id}/complete", headers=headers)

    # 3. Check User Roadmap Progress
    # Step 1 (course step) is now completed! Total required steps = 3, completed = 1 -> 33.3%
    prog_res = await client.get(f"/api/v1/users/me/roadmaps/{roadmap.slug}", headers=headers)
    assert prog_res.status_code == 200
    prog_data = prog_res.json()
    assert prog_data["completed_steps"] == 1
    assert prog_data["progress_percentage"] == 33.3
    assert prog_data["roadmap"]["nodes"][0]["completed"] is True
    assert prog_data["roadmap"]["nodes"][0]["status"] == "completed"


@pytest.mark.asyncio
async def test_roadmap_and_skills_unauthorized_and_missing(client: AsyncClient, db_session: AsyncSession):
    """Test 401 on protected endpoints and 404 on missing entities."""
    # 401 on starting roadmap without auth
    res_unauth = await client.post("/api/v1/roadmaps/invalid-id/start")
    assert res_unauth.status_code == 401

    # 404 on missing roadmap
    res_404_rm = await client.get("/api/v1/roadmaps/nonexistent-roadmap-999")
    assert res_404_rm.status_code == 404

    # 404 on missing skill
    res_404_sk = await client.get("/api/v1/skills/nonexistent-skill-999")
    assert res_404_sk.status_code == 404
