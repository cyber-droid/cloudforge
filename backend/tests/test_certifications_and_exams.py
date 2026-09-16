"""
Integration and Unit Tests for Phase 6:
Certifications, Training Programs, Practice Exams & CloudForge Certificates.
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import User, UserRole
from app.models.course import Course, CourseModule, Lesson
from app.models.progress import LessonProgress, LessonProgressStatus
from app.models.certification import (
    Certification,
    CertificationLevel,
    CertificationTraining,
    UserCertificationEnrollment,
    PracticeQuestion,
    PracticeAttempt,
    AttemptType,
)
from app.models.certificate import Certificate, CertificateStatus
from app.core.security import create_access_token, get_password_hash


@pytest.fixture
async def test_users(db_session: AsyncSession):
    """Seed test users (student1, student2, admin)."""
    u1 = User(
        email="cert_student1@cloudforge.io",
        name="Alice Explorer",
        hashed_password=get_password_hash("SecretPassword123!"),
        is_active=True,
        role=UserRole.STUDENT,
    )
    u2 = User(
        email="cert_student2@cloudforge.io",
        name="Bob Builder",
        hashed_password=get_password_hash("SecretPassword123!"),
        is_active=True,
        role=UserRole.STUDENT,
    )
    admin = User(
        email="cert_admin@cloudforge.io",
        name="Admin Director",
        hashed_password=get_password_hash("AdminPass123!"),
        is_active=True,
        role=UserRole.ADMIN,
    )
    db_session.add_all([u1, u2, admin])
    await db_session.commit()
    await db_session.refresh(u1)
    await db_session.refresh(u2)
    await db_session.refresh(admin)

    return {"student1": u1, "student2": u2, "admin": admin}


def auth_headers(user: User) -> dict:
    role_str = user.role.value if hasattr(user.role, "value") else str(user.role)
    token = create_access_token(subject=str(user.id), role=role_str)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def sample_cert_and_course(db_session: AsyncSession):
    """Seed sample course, lessons, certification, training, and questions."""
    # 1. Course with 2 modules and 3 lessons
    course = Course(
        slug="cloud-architecture-mastery",
        title="Cloud Architecture Mastery",
        description="Comprehensive engineering course covering multi-tier cloud architectures.",
        category="Cloud",
        difficulty="Beginner",
        duration_minutes=180,
        published=True,
    )
    db_session.add(course)
    await db_session.flush()

    m1 = CourseModule(course_id=course.id, module_number="01", title="Foundations", order_index=1)
    m2 = CourseModule(course_id=course.id, module_number="02", title="Networking", order_index=2)
    db_session.add_all([m1, m2])
    await db_session.flush()

    l1 = Lesson(module_id=m1.id, slug="intro-cloud", title="Intro to Cloud", lesson_type="theory", order_index=1)
    l2 = Lesson(module_id=m1.id, slug="iam-basics", title="IAM Basics", lesson_type="theory", order_index=2)
    l3 = Lesson(module_id=m2.id, slug="vpc-routing", title="VPC Routing", lesson_type="hands-on", order_index=3)
    db_session.add_all([l1, l2, l3])
    await db_session.flush()

    # 2. Certification (External)
    cert = Certification(
        code="CLF-C02",
        slug="aws-certified-cloud-practitioner",
        name="AWS Certified Cloud Practitioner",
        vendor="AWS",
        description="Foundational AWS Certification preparation track.",
        level=CertificationLevel.FOUNDATIONAL,
        category="Cloud",
        is_official_certification=True,
        official_url="https://aws.amazon.com/certification/certified-cloud-practitioner/",
        exam_duration_minutes=90,
        total_exam_questions=65,
        passing_score_percentage=70,
        domains=[
            {"domain_name": "Cloud Concepts", "weight_percentage": 30, "question_count": 10},
            {"domain_name": "Security & IAM", "weight_percentage": 70, "question_count": 20},
        ],
        is_published=True,
    )
    db_session.add(cert)
    await db_session.flush()

    # 3. Training mapped to course
    training = CertificationTraining(
        certification_id=cert.id,
        title="AWS Cloud Practitioner Training Program",
        slug="aws-cloud-practitioner-training",
        description="Comprehensive preparation covering all CLF-C02 domains.",
        level=CertificationLevel.FOUNDATIONAL,
        estimated_hours=20,
        course_id=course.id,
        is_published=True,
    )
    db_session.add(training)
    await db_session.flush()

    # 4. Questions
    q1 = PracticeQuestion(
        certification_id=cert.id,
        training_id=training.id,
        question_text="What AWS service provides managed distributed DNS routing?",
        question_type="single_choice",
        options=["Amazon Route 53", "Amazon VPC", "AWS Direct Connect", "Amazon CloudFront"],
        correct_option=0,
        explanation="Amazon Route 53 is a highly available and scalable cloud Domain Name System (DNS) web service.",
        topic="Cloud Concepts",
        difficulty="easy",
        points=10,
        is_published=True,
    )
    q2 = PracticeQuestion(
        certification_id=cert.id,
        training_id=training.id,
        question_text="Which AWS principle represents granting only the required permissions?",
        question_type="single_choice",
        options=["Defense in Depth", "Principle of Least Privilege", "Separation of Concerns", "Shared Responsibility"],
        correct_option=1,
        explanation="The Principle of Least Privilege dictates granting only permissions strictly required for the task.",
        topic="Security & IAM",
        difficulty="easy",
        points=10,
        is_published=True,
    )
    db_session.add_all([q1, q2])
    await db_session.commit()

    return {
        "course": course,
        "lessons": [l1, l2, l3],
        "certification": cert,
        "training": training,
        "questions": [q1, q2],
    }


# ============================================================================
# 1. CERTIFICATION CATALOG TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_list_certifications_and_filter(client: AsyncClient, sample_cert_and_course):
    """Test listing certifications with filtering by provider/vendor and level."""
    # List all
    res = await client.get("/api/v1/certifications")
    assert res.status_code == 200
    data = res.json()
    items = data.get("items", [])
    assert len(items) >= 1
    assert any(c["slug"] == "aws-certified-cloud-practitioner" for c in items)

    # Filter by vendor
    res_vendor = await client.get("/api/v1/certifications?provider=AWS")
    assert res_vendor.status_code == 200
    v_items = res_vendor.json().get("items", [])
    assert len(v_items) >= 1
    assert all(c.get("vendor") == "AWS" or c.get("provider") == "AWS" for c in v_items)

    # Filter by non-matching vendor
    res_empty = await client.get("/api/v1/certifications?provider=NonExistentVendor")
    assert res_empty.status_code == 200
    assert len(res_empty.json().get("items", [])) == 0


@pytest.mark.asyncio
async def test_get_certification_detail(client: AsyncClient, sample_cert_and_course):
    """Test fetching single certification by slug or ID."""
    cert = sample_cert_and_course["certification"]

    # By slug
    res = await client.get(f"/api/v1/certifications/{cert.slug}")
    assert res.status_code == 200
    data = res.json()
    assert data["name"] == cert.name
    assert data["code"] == "CLF-C02"
    assert data["is_official_certification"] is True
    assert len(data["domains"]) == 2

    # By ID
    res_id = await client.get(f"/api/v1/certifications/{cert.id}")
    assert res_id.status_code == 200
    assert res_id.json()["slug"] == cert.slug


# ============================================================================
# 2. TRAINING & ENROLLMENT TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_training_enrollment_and_duplicate_prevention(
    client: AsyncClient, test_users, sample_cert_and_course
):
    """Test enrolling in a training program and idempotent duplicate prevention."""
    student1 = test_users["student1"]
    training = sample_cert_and_course["training"]

    # Unauthorized enrollment fails
    res_anon = await client.post(f"/api/v1/trainings/{training.slug}/enroll")
    assert res_anon.status_code == 401

    # Authorized enrollment succeeds
    res_auth = await client.post(f"/api/v1/trainings/{training.slug}/enroll", headers=auth_headers(student1))
    assert res_auth.status_code == 200
    enr_data = res_auth.json()
    assert enr_data["status"] == "in_progress" or enr_data["status"] == "enrolled"

    # Second enrollment is idempotent / prevents duplicates
    res_dup = await client.post(f"/api/v1/trainings/{training.slug}/enroll", headers=auth_headers(student1))
    assert res_dup.status_code == 200
    assert res_dup.json()["id"] == training.id
    assert res_dup.json()["status"] in ["in_progress", "enrolled"]


# ============================================================================
# 3. REAL PROGRESS CALCULATION TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_real_training_progress_calculation(
    client: AsyncClient, db_session: AsyncSession, test_users, sample_cert_and_course
):
    """Test progress is accurately derived from real LessonProgress records."""
    student1 = test_users["student1"]
    training = sample_cert_and_course["training"]
    lessons = sample_cert_and_course["lessons"]

    # 1. Check initial progress (0%)
    res0 = await client.get(f"/api/v1/trainings/{training.id}/progress", headers=auth_headers(student1))
    assert res0.status_code == 200
    p0 = res0.json()
    assert p0["total_lessons"] == 3
    assert p0["completed_lessons"] == 0
    assert p0["progress_percentage"] == 0.0
    assert p0["is_eligible_for_certificate"] is False

    # 2. Complete 1 lesson (33.3%)
    lp1 = LessonProgress(
        user_id=student1.id,
        lesson_id=lessons[0].id,
        status=LessonProgressStatus.COMPLETED.value,
    )
    db_session.add(lp1)
    await db_session.commit()

    res1 = await client.get(f"/api/v1/trainings/{training.id}/progress", headers=auth_headers(student1))
    assert res1.status_code == 200
    p1 = res1.json()
    assert p1["completed_lessons"] == 1
    assert p1["progress_percentage"] == 33.3
    assert p1["is_eligible_for_certificate"] is False

    # 3. Complete remaining 2 lessons (100%)
    lp2 = LessonProgress(
        user_id=student1.id,
        lesson_id=lessons[1].id,
        status=LessonProgressStatus.COMPLETED.value,
    )
    lp3 = LessonProgress(
        user_id=student1.id,
        lesson_id=lessons[2].id,
        status=LessonProgressStatus.COMPLETED.value,
    )
    db_session.add_all([lp2, lp3])
    await db_session.commit()

    res2 = await client.get(f"/api/v1/trainings/{training.id}/progress", headers=auth_headers(student1))
    assert res2.status_code == 200
    p2 = res2.json()
    assert p2["completed_lessons"] == 3
    assert p2["progress_percentage"] == 100.0
    assert p2["is_eligible_for_certificate"] is True


# ============================================================================
# 4. PRACTICE EXAM SIMULATION & SERVER-SIDE SCORING
# ============================================================================

@pytest.mark.asyncio
async def test_practice_exam_flow_and_server_evaluation(
    client: AsyncClient, test_users, sample_cert_and_course
):
    """
    Test full practice exam lifecycle:
    1. Start attempt -> questions returned WITHOUT correct answers or explanations.
    2. Submit answers -> server evaluates score, percentage, and pass/fail.
    3. Cannot resubmit an already completed attempt.
    4. Review results -> correct answers and explanations revealed.
    5. Another user cannot view the attempt.
    """
    student1 = test_users["student1"]
    student2 = test_users["student2"]
    cert = sample_cert_and_course["certification"]
    questions = sample_cert_and_course["questions"]

    # 1. Start attempt
    start_payload = {
        "attempt_type": "practice_quiz",
        "question_count": 2,
    }
    res_start = await client.post(
        f"/api/v1/certifications/{cert.id}/practice-attempts",
        json=start_payload,
        headers=auth_headers(student1),
    )
    assert res_start.status_code == 201
    attempt_data = res_start.json()
    attempt_id = attempt_data["id"]
    assert attempt_data["total_questions"] == 2
    assert len(attempt_data["questions"]) == 2

    # Verify correct answers are NOT exposed
    for q in attempt_data["questions"]:
        assert "correct_option" not in q
        assert "explanation" not in q
        assert "options" in q
        assert len(q["options"]) == 4

    # 2. Submit answers: 1 correct (q1: 0), 1 incorrect (q2: 3 instead of 1)
    submit_payload = {
        "answers": [
            {"question_id": questions[0].id, "selected_option": 0},  # Correct (Route 53)
            {"question_id": questions[1].id, "selected_option": 3},  # Incorrect (Shared Resp instead of Least Priv)
        ]
    }
    res_sub = await client.post(
        f"/api/v1/practice-attempts/{attempt_id}/submit",
        json=submit_payload,
        headers=auth_headers(student1),
    )
    assert res_sub.status_code == 200
    result_data = res_sub.json()
    assert result_data["score"] == 10
    assert result_data["total_questions"] == 2
    assert result_data["correct_answers"] == 1
    assert result_data["percentage"] == 50.0
    assert result_data["passed"] is False  # Required 70%
    assert len(result_data["question_results"]) == 2

    # Correct answers & explanations ARE returned in results
    q1_res = next(r for r in result_data["question_results"] if r["question_id"] == questions[0].id)
    assert q1_res["is_correct"] is True
    assert q1_res["correct_option"] == 0
    assert "explanation" in q1_res and q1_res["explanation"] != ""

    q2_res = next(r for r in result_data["question_results"] if r["question_id"] == questions[1].id)
    assert q2_res["is_correct"] is False
    assert q2_res["selected_option"] == 3
    assert q2_res["correct_option"] == 1

    # 3. Duplicate submission rejected
    res_re_sub = await client.post(
        f"/api/v1/practice-attempts/{attempt_id}/submit",
        json=submit_payload,
        headers=auth_headers(student1),
    )
    assert res_re_sub.status_code == 400

    # 4. User 2 cannot access User 1's attempt results
    res_unauth = await client.get(
        f"/api/v1/practice-attempts/{attempt_id}/results",
        headers=auth_headers(student2),
    )
    assert res_unauth.status_code == 404 or res_unauth.status_code == 403


# ============================================================================
# 5. TRAINING COMPLETION & IDEMPOTENT CERTIFICATE ISSUANCE
# ============================================================================

@pytest.mark.asyncio
async def test_training_completion_and_certificate_issuance(
    client: AsyncClient, db_session: AsyncSession, test_users, sample_cert_and_course
):
    """
    Test certificate issuance lifecycle:
    1. Incomplete training cannot be marked completed.
    2. Completed training issues certificate.
    3. Calling completion endpoint repeatedly is idempotent (same certificate returned).
    4. Public verification verifies validity and returns snapshot without private data.
    """
    student1 = test_users["student1"]
    training = sample_cert_and_course["training"]
    lessons = sample_cert_and_course["lessons"]

    # 1. Attempt completion when lessons are incomplete -> 400 Bad Request
    res_fail = await client.post(f"/api/v1/trainings/{training.id}/complete", headers=auth_headers(student1))
    assert res_fail.status_code == 400

    # 2. Complete all required lessons
    for l in lessons:
        db_session.add(LessonProgress(
            user_id=student1.id,
            lesson_id=l.id,
            status=LessonProgressStatus.COMPLETED.value,
        ))
    await db_session.commit()

    # 3. Mark complete -> certificate generated
    res_comp = await client.post(f"/api/v1/trainings/{training.id}/complete", headers=auth_headers(student1))
    assert res_comp.status_code == 200
    cert_data = res_comp.json()
    assert cert_data["status"] == "issued"
    assert cert_data["certificate_number"].startswith("CF-")
    assert len(cert_data["verification_code"]) >= 12
    assert cert_data["recipient_name"] == student1.name
    assert cert_data["training_title"] in [training.title, "Certificate of Completion - AWS Certified Cloud Practitioner"]
    verification_code = cert_data["verification_code"]
    cert_num = cert_data["certificate_number"]

    # 4. Repeated completion call is idempotent
    res_idempotent = await client.post(f"/api/v1/trainings/{training.id}/complete", headers=auth_headers(student1))
    assert res_idempotent.status_code == 200
    assert res_idempotent.json()["certificate_number"] == cert_num

    # 5. List user certificates
    res_list = await client.get("/api/v1/certificates", headers=auth_headers(student1))
    assert res_list.status_code == 200
    assert len(res_list.json()) >= 1
    assert any(c["certificate_number"] == cert_num for c in res_list.json())

    # 6. Public Certificate Verification (Unauthenticated)
    res_pub = await client.get(f"/api/v1/certificates/verify/{verification_code}")
    assert res_pub.status_code == 200
    pub_data = res_pub.json()
    assert pub_data["is_valid"] is True
    assert pub_data["certificate_number"] == cert_num
    assert pub_data["recipient_name"] == "Alice Explorer"
    assert pub_data["training_title"] in [training.title, "Certificate of Completion - AWS Certified Cloud Practitioner"]
    assert pub_data["status"] == "issued"

    # Confirm private user data is NOT exposed
    assert "email" not in pub_data
    assert "user_id" not in pub_data
    assert "password" not in pub_data
    assert "hashed_password" not in pub_data

    # 7. Verification of invalid code returns is_valid = False (or 404)
    res_invalid = await client.get("/api/v1/certificates/verify/INVALID-CODE-999")
    assert res_invalid.status_code == 200 or res_invalid.status_code == 404
    if res_invalid.status_code == 200:
        assert res_invalid.json()["is_valid"] is False
