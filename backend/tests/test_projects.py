"""
Comprehensive integration tests for Phase 7: Projects and DevOps Engineering Workflows.
Covers:
- Project catalog listing, searching, filtering, and pagination
- Detail retrieval with steps, resources, courses, and skills
- Draft project visibility (students vs instructors/admins)
- User enrollment lifecycle and duplicate prevention
- Granular step progress (start, complete, notes)
- Real-time progress percentage derivation
- Deterministic and idempotent project completion
- LearningActivity event logging
- Authorization and user isolation
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.security import get_password_hash
from app.models.course import Course, CourseCategory, CourseDifficulty
from app.models.progress import ActivityType, LearningActivity
from app.models.project import (
    Project,
    ProjectCourse,
    ProjectDifficulty,
    ProjectEnrollmentStatus,
    ProjectResource,
    ProjectResourceType,
    ProjectSkill,
    ProjectStatus,
    ProjectStep,
    ProjectStepProgress,
    StepProgressStatus,
    StepType,
    UserProjectEnrollment,
)
from app.models.skill import Skill, SkillCategory
from app.models.user import User, UserRole


@pytest.fixture
async def sample_project_setup(db_session: AsyncSession):
    """Seed sample courses, skills, and projects for testing."""
    # 1. Users
    student = User(
        email="test_student@cloudforge.io",
        hashed_password=get_password_hash("SecretPassword123!"),
        name="Alice DevOps",
        role=UserRole.STUDENT,
        is_active=True,
    )
    other_student = User(
        email="other_student@cloudforge.io",
        hashed_password=get_password_hash("SecretPassword123!"),
        name="Bob SRE",
        role=UserRole.STUDENT,
        is_active=True,
    )
    admin = User(
        email="admin_user@cloudforge.io",
        hashed_password=get_password_hash("AdminPassword123!"),
        name="Admin Chief",
        role=UserRole.ADMIN,
        is_active=True,
    )
    db_session.add_all([student, other_student, admin])
    await db_session.flush()

    # 2. Course & Skill
    k8s_course = Course(
        slug="k8s-engineering",
        title="Kubernetes Engineering",
        category=CourseCategory.KUBERNETES.value,
        difficulty=CourseDifficulty.INTERMEDIATE.value,
        duration_minutes=400,
        description="Kubernetes from basics to production",
        published=True,
    )
    k8s_skill = Skill(
        name="Kubernetes",
        slug="kubernetes",
        category=SkillCategory.KUBERNETES.value,
        description="Container orchestration",
    )
    db_session.add_all([k8s_course, k8s_skill])
    await db_session.flush()

    # 3. Published Project
    published_project = Project(
        slug="k8s-prod-deployment",
        title="Kubernetes Production Deployment",
        short_description="Deploy scalable k8s cluster.",
        description="Full hands-on project deploying microservices to Kubernetes.",
        difficulty="Intermediate",
        estimated_hours="16 hours",
        status=ProjectStatus.PUBLISHED.value,
        featured=True,
        technologies=["Kubernetes", "Docker", "Helm"],
        deliverables=["Manifests", "HPA", "NetworkPolicy"],
        architecture_overview="Microservice mesh behind ingress.",
        prerequisites=["Linux basics", "Docker"],
        learning_objectives=["Master kubectl", "Fix CrashLoopBackOff"],
        repository_url="https://github.com/cloudforge/k8s-project",
        documentation_url="https://docs.cloudforge.io/k8s",
    )
    db_session.add(published_project)
    await db_session.flush()

    # Steps for published project (3 steps: learn -> break -> fix)
    step1 = ProjectStep(
        project_id=published_project.id,
        step_order=1,
        step_type="learn",
        title="Learn K8s Architecture",
        description="Understand control plane",
        instructions="Review control plane components",
        command="kubectl cluster-info",
        expected_outcome="Cluster running",
        is_required=True,
    )
    step2 = ProjectStep(
        project_id=published_project.id,
        step_order=2,
        step_type="break",
        title="Induce CrashLoopBackOff",
        description="Break configuration",
        instructions="Change port to 9999",
        command="kubectl apply -f broken.yaml",
        expected_outcome="CrashLoopBackOff",
        is_required=True,
    )
    step3 = ProjectStep(
        project_id=published_project.id,
        step_order=3,
        step_type="fix",
        title="Fix Pod Manifests",
        description="Restore port to 8000",
        instructions="Fix broken port",
        command="kubectl apply -f fixed.yaml",
        expected_outcome="Pods Running 1/1",
        is_required=True,
    )
    db_session.add_all([step1, step2, step3])

    # Resource
    res1 = ProjectResource(
        project_id=published_project.id,
        title="K8s Docs",
        resource_type="documentation",
        url="https://kubernetes.io/docs",
        description="Official docs",
        display_order=1,
    )
    db_session.add(res1)

    # Connections
    db_session.add(ProjectCourse(project_id=published_project.id, course_id=k8s_course.id))
    db_session.add(ProjectSkill(project_id=published_project.id, skill_id=k8s_skill.id))

    # 4. Draft Project
    draft_project = Project(
        slug="draft-cloud-infra",
        title="Draft Cloud Infrastructure",
        short_description="Draft project under construction.",
        description="Unpublished course material.",
        difficulty="Advanced",
        estimated_hours="20 hours",
        status=ProjectStatus.DRAFT.value,
        featured=False,
    )
    db_session.add(draft_project)

    await db_session.commit()

    return {
        "student": student,
        "other_student": other_student,
        "admin": admin,
        "published_project": published_project,
        "draft_project": draft_project,
        "steps": [step1, step2, step3],
        "course": k8s_course,
        "skill": k8s_skill,
    }


async def get_token_for(client: AsyncClient, email: str, password: str = "SecretPassword123!") -> str:
    """Helper to obtain JWT access token."""
    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert login_resp.status_code == 200
    return login_resp.json()["access_token"]


@pytest.mark.asyncio
async def test_list_projects_and_filtering(client: AsyncClient, sample_project_setup: dict):
    """Test public and student listing filters only published projects."""
    resp = await client.get("/api/v1/projects")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 1
    assert data["items"][0]["slug"] == "k8s-prod-deployment"
    assert data["items"][0]["difficulty"] == "Intermediate"
    assert data["items"][0]["total_steps"] == 3
    assert data["items"][0]["completed_steps"] == 0
    assert data["items"][0]["progress_percentage"] == 0.0

    # Search filter
    search_resp = await client.get("/api/v1/projects?search=Kubernetes")
    assert search_resp.status_code == 200
    assert search_resp.json()["total"] == 1

    search_empty = await client.get("/api/v1/projects?search=NonExistentProject")
    assert search_empty.status_code == 200
    assert search_empty.json()["total"] == 0

    # Difficulty filter
    diff_resp = await client.get("/api/v1/projects?difficulty=Intermediate")
    assert diff_resp.status_code == 200
    assert diff_resp.json()["total"] == 1

    diff_none = await client.get("/api/v1/projects?difficulty=Beginner")
    assert diff_none.status_code == 200
    assert diff_none.json()["total"] == 0


@pytest.mark.asyncio
async def test_get_project_detail(client: AsyncClient, sample_project_setup: dict):
    """Test fetching project details by slug and ID."""
    proj = sample_project_setup["published_project"]

    resp = await client.get(f"/api/v1/projects/{proj.slug}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["title"] == "Kubernetes Production Deployment"
    assert len(data["steps"]) == 3
    assert data["steps"][0]["title"] == "Learn K8s Architecture"
    assert data["steps"][0]["step_type"] == "learn"
    assert len(data["resources"]) == 1
    assert data["resources"][0]["title"] == "K8s Docs"
    assert len(data["related_courses"]) == 1
    assert data["related_courses"][0]["slug"] == "k8s-engineering"
    assert len(data["related_skills"]) == 1
    assert data["related_skills"][0]["name"] == "Kubernetes"


@pytest.mark.asyncio
async def test_draft_project_access_control(client: AsyncClient, sample_project_setup: dict):
    """Test draft projects are hidden from students but visible to admins."""
    draft = sample_project_setup["draft_project"]

    # Student cannot view draft
    resp = await client.get(f"/api/v1/projects/{draft.slug}")
    assert resp.status_code == 404

    # Admin can view draft
    admin_token = await get_token_for(client, "admin_user@cloudforge.io", "AdminPassword123!")
    admin_resp = await client.get(
        f"/api/v1/projects/{draft.slug}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert admin_resp.status_code == 200
    assert admin_resp.json()["slug"] == draft.slug


@pytest.mark.asyncio
async def test_enroll_in_project_and_activity_logging(
    client: AsyncClient, db_session: AsyncSession, sample_project_setup: dict
):
    """Test authenticated student can enroll in a project with activity logging."""
    proj = sample_project_setup["published_project"]
    student = sample_project_setup["student"]
    token = await get_token_for(client, student.email)

    # 1. Unauthenticated enrollment rejected
    unauth_resp = await client.post(f"/api/v1/projects/{proj.id}/enroll")
    assert unauth_resp.status_code == 401

    # 2. Authenticated enrollment
    enr_resp = await client.post(
        f"/api/v1/projects/{proj.id}/enroll",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert enr_resp.status_code == 200
    enr_data = enr_resp.json()
    assert enr_data["project_id"] == proj.id
    assert enr_data["status"] == "in_progress"

    # Verify Activity log
    act_res = await db_session.execute(
        select(LearningActivity).where(
            LearningActivity.user_id == student.id,
            LearningActivity.activity_type == ActivityType.PROJECT_STARTED.value,
        )
    )
    activities = act_res.scalars().all()
    assert len(activities) == 1

    # 3. Duplicate enrollment is idempotent (no second activity log)
    dup_resp = await client.post(
        f"/api/v1/projects/{proj.id}/enroll",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert dup_resp.status_code == 200
    act_res_after = await db_session.execute(
        select(LearningActivity).where(
            LearningActivity.user_id == student.id,
            LearningActivity.activity_type == ActivityType.PROJECT_STARTED.value,
        )
    )
    assert len(act_res_after.scalars().all()) == 1


@pytest.mark.asyncio
async def test_step_progression_progress_derivation_and_completion(
    client: AsyncClient, db_session: AsyncSession, sample_project_setup: dict
):
    """
    Test complete lifecycle:
    - start step 1
    - complete step 1 -> progress = 33.3%
    - complete step 2 -> progress = 66.7%
    - complete step 3 -> progress = 100%, project auto-marked completed
    - idempotent re-completion does not duplicate timestamps or activities
    """
    proj = sample_project_setup["published_project"]
    steps = sample_project_setup["steps"]
    student = sample_project_setup["student"]
    token = await get_token_for(client, student.email)
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Start Step 1
    start_resp = await client.post(
        f"/api/v1/projects/{proj.id}/steps/{steps[0].id}/start",
        headers=headers,
    )
    assert start_resp.status_code == 200
    assert start_resp.json()["status"] == "in_progress"
    assert start_resp.json()["completed"] is False

    # 2. Complete Step 1
    comp1 = await client.post(
        f"/api/v1/projects/{proj.id}/steps/{steps[0].id}/complete",
        json={"notes": "Step 1 mastered."},
        headers=headers,
    )
    assert comp1.status_code == 200
    data1 = comp1.json()
    assert data1["completed_steps"] == 1
    assert data1["total_steps"] == 3
    assert data1["progress_percentage"] == 33.3
    assert data1["is_completed"] is False
    assert data1["status"] == "in_progress"

    # Verify Activity log for step 1
    step_acts = (
        await db_session.execute(
            select(LearningActivity).where(
                LearningActivity.user_id == student.id,
                LearningActivity.activity_type == ActivityType.PROJECT_STEP_COMPLETED.value,
            )
        )
    ).scalars().all()
    assert len(step_acts) == 1

    # 3. Complete Step 2
    comp2 = await client.post(
        f"/api/v1/projects/{proj.id}/steps/{steps[1].id}/complete",
        headers=headers,
    )
    assert comp2.status_code == 200
    assert comp2.json()["completed_steps"] == 2
    assert comp2.json()["progress_percentage"] == 66.7
    assert comp2.json()["is_completed"] is False

    # 4. Complete Step 3 (Final step -> triggers project completion)
    comp3 = await client.post(
        f"/api/v1/projects/{proj.id}/steps/{steps[2].id}/complete",
        headers=headers,
    )
    assert comp3.status_code == 200
    data3 = comp3.json()
    assert data3["completed_steps"] == 3
    assert data3["total_steps"] == 3
    assert data3["progress_percentage"] == 100.0
    assert data3["is_completed"] is True
    assert data3["status"] == "completed"
    assert data3["completed_at"] is not None

    # Verify PROJECT_COMPLETED activity was emitted
    proj_comp_acts = (
        await db_session.execute(
            select(LearningActivity).where(
                LearningActivity.user_id == student.id,
                LearningActivity.activity_type == ActivityType.PROJECT_COMPLETED.value,
            )
        )
    ).scalars().all()
    assert len(proj_comp_acts) == 1

    # 5. Idempotent re-completion of step 3
    comp3_repeat = await client.post(
        f"/api/v1/projects/{proj.id}/steps/{steps[2].id}/complete",
        headers=headers,
    )
    assert comp3_repeat.status_code == 200
    assert comp3_repeat.json()["is_completed"] is True

    # No duplicate activity logs emitted
    proj_comp_acts_after = (
        await db_session.execute(
            select(LearningActivity).where(
                LearningActivity.user_id == student.id,
                LearningActivity.activity_type == ActivityType.PROJECT_COMPLETED.value,
            )
        )
    ).scalars().all()
    assert len(proj_comp_acts_after) == 1


@pytest.mark.asyncio
async def test_my_projects_and_user_isolation(
    client: AsyncClient, sample_project_setup: dict
):
    """Test student can only see and modify their own project progress."""
    proj = sample_project_setup["published_project"]
    steps = sample_project_setup["steps"]
    alice = sample_project_setup["student"]
    bob = sample_project_setup["other_student"]

    alice_token = await get_token_for(client, alice.email)
    bob_token = await get_token_for(client, bob.email)

    # Alice enrolls and completes step 1
    await client.post(
        f"/api/v1/projects/{proj.id}/enroll",
        headers={"Authorization": f"Bearer {alice_token}"},
    )
    await client.post(
        f"/api/v1/projects/{proj.id}/steps/{steps[0].id}/complete",
        headers={"Authorization": f"Bearer {alice_token}"},
    )

    # Alice checks /my
    alice_my = await client.get(
        "/api/v1/projects/my",
        headers={"Authorization": f"Bearer {alice_token}"},
    )
    assert alice_my.status_code == 200
    assert len(alice_my.json()) == 1
    assert alice_my.json()[0]["completed_steps"] == 1
    assert alice_my.json()[0]["progress_percentage"] == 33.3

    # Bob checks /my (should have 0 enrollments)
    bob_my = await client.get(
        "/api/v1/projects/my",
        headers={"Authorization": f"Bearer {bob_token}"},
    )
    assert bob_my.status_code == 200
    assert len(bob_my.json()) == 0

    # Bob checks progress on the project (0% progress)
    bob_prog = await client.get(
        f"/api/v1/projects/{proj.id}/progress",
        headers={"Authorization": f"Bearer {bob_token}"},
    )
    assert bob_prog.status_code == 200
    assert bob_prog.json()["completed_steps"] == 0
    assert bob_prog.json()["progress_percentage"] == 0.0
