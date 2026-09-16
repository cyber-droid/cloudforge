"""
Integration Tests for Courses, Curriculum, Modules, Lessons, and Enrollment APIs.
"""
import pytest
from httpx import AsyncClient
from app.db.seed import seed_courses
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.fixture(autouse=True)
async def populate_seed_data(db_session: AsyncSession):
    """Ensure seed curriculum is populated for course tests."""
    await seed_courses(db_session)


@pytest.mark.asyncio
async def test_list_courses_pagination(client: AsyncClient):
    """Test GET /api/v1/courses pagination and metadata."""
    response = await client.get("/api/v1/courses?page=1&page_size=4")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 4
    assert data["total"] >= 9
    assert data["page"] == 1
    assert data["page_size"] == 4
    assert data["total_pages"] >= 3


@pytest.mark.asyncio
async def test_filter_courses_by_category_and_difficulty(client: AsyncClient):
    """Test filtering courses by domain category and difficulty level."""
    # Filter by Kubernetes
    k8s_resp = await client.get("/api/v1/courses?category=Kubernetes")
    assert k8s_resp.status_code == 200
    k8s_data = k8s_resp.json()
    assert len(k8s_data["items"]) >= 1
    for course in k8s_data["items"]:
        assert course["category"] == "Kubernetes"

    # Filter by Beginner
    beg_resp = await client.get("/api/v1/courses?difficulty=Beginner")
    assert beg_resp.status_code == 200
    beg_data = beg_resp.json()
    assert len(beg_data["items"]) >= 1


@pytest.mark.asyncio
async def test_search_courses(client: AsyncClient):
    """Test searching courses across title, description, and technologies."""
    search_resp = await client.get("/api/v1/courses?search=terraform")
    assert search_resp.status_code == 200
    data = search_resp.json()
    assert len(data["items"]) >= 1
    assert any("terraform" in c["title"].lower() or "terraform" in c["slug"] for c in data["items"])


@pytest.mark.asyncio
async def test_get_course_detail_and_curriculum(client: AsyncClient):
    """Test retrieving course detail and curriculum tree."""
    slug = "kubernetes-engineering"
    
    # 1. Course Detail
    detail_resp = await client.get(f"/api/v1/courses/{slug}")
    assert detail_resp.status_code == 200
    detail = detail_resp.json()
    assert detail["slug"] == slug
    assert detail["title"] == "Kubernetes Engineering"
    assert len(detail["modules"]) >= 14
    
    # 2. Course Curriculum
    curr_resp = await client.get(f"/api/v1/courses/{slug}/curriculum")
    assert curr_resp.status_code == 200
    curr = curr_resp.json()
    assert curr["course_slug"] == slug
    assert len(curr["modules"]) >= 14
    assert "lessons" in curr["modules"][0]


@pytest.mark.asyncio
async def test_course_enrollment_lifecycle(client: AsyncClient):
    """
    Test full enrollment lifecycle:
    1. Register user
    2. Enroll in course
    3. Duplicate enrollment prevention
    4. View enrolled courses (GET /users/me/courses)
    5. View single enrollment status
    6. Unenroll
    """
    # 1. Register Student
    reg_resp = await client.post("/api/v1/auth/register", json={
        "email": "enrollment_tester@cloudforge.io",
        "password": "EnrollPassword123!",
        "name": "Enrollment Student",
    })
    assert reg_resp.status_code == 201
    token = reg_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    course_slug = "kubernetes-engineering"

    # 2. Unauthenticated enroll -> should fail with 401
    unauth_resp = await client.post(f"/api/v1/courses/{course_slug}/enroll")
    assert unauth_resp.status_code == 401

    # 3. Authenticated enroll -> should succeed with 201
    enroll_resp = await client.post(f"/api/v1/courses/{course_slug}/enroll", headers=headers)
    assert enroll_resp.status_code == 201
    enroll_data = enroll_resp.json()
    assert enroll_data["status"] == "active"
    assert enroll_data["course"]["slug"] == course_slug

    # 4. Duplicate enroll -> should fail with 400
    dup_resp = await client.post(f"/api/v1/courses/{course_slug}/enroll", headers=headers)
    assert dup_resp.status_code == 400
    assert "already enrolled" in dup_resp.json()["message"]

    # 5. Fetch enrolled courses (GET /users/me/courses)
    my_courses_resp = await client.get("/api/v1/users/me/courses", headers=headers)
    assert my_courses_resp.status_code == 200
    my_courses = my_courses_resp.json()
    assert len(my_courses) == 1
    assert my_courses[0]["course"]["slug"] == course_slug

    # 6. Fetch single course enrollment detail
    single_enroll_resp = await client.get(f"/api/v1/users/me/courses/{course_slug}", headers=headers)
    assert single_enroll_resp.status_code == 200
    assert single_enroll_resp.json()["status"] == "active"

    # 7. Unenroll from course
    unenroll_resp = await client.delete(f"/api/v1/courses/{course_slug}/enroll", headers=headers)
    assert unenroll_resp.status_code == 200
    assert "Successfully unenrolled" in unenroll_resp.json()["message"]

    # 8. Verify enrollment is removed
    my_courses_after = await client.get("/api/v1/users/me/courses", headers=headers)
    assert len(my_courses_after.json()) == 0
