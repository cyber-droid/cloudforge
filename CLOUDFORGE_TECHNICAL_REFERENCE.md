# CloudForge Technical Reference Document

## 1. Project Overview
**Project Name:** CloudForge – AI-Assisted Cloud & DevOps Engineering Platform
**Purpose:** A production-oriented learning and engineering platform covering Cloud, DevOps, DevSecOps, Kubernetes, IaC, GitOps, Observability, and AI-assisted operations.
**Current Implemented Functionality:** The source code implements a comprehensive backend API (FastAPI) and frontend (React) for an educational platform. Features include User authentication, Course catalog, Curriculums (Modules & Lessons), Skill tracking, Career Roadmaps, Hands-on Projects, Certifications (Trainings & Practice Exams), and Learning Progress tracking.
**Status:** Under active development. Core models and basic API structures are in place.

## 2. Repository Structure
- `/backend`: Python FastAPI application
  - `/app/api`: FastAPI routers organized by version (v1) and feature (auth, courses, etc.)
  - `/app/core`: Configuration, database setup, security utilities.
  - `/app/models`: SQLAlchemy ORM database models.
  - `/app/schemas`: Pydantic models for API request/response validation.
  - `/app/services`: Business logic layer.
  - `/alembic`: Database migrations.
  - `pyproject.toml`: Backend dependencies and configuration.
- `/src`: React frontend application
  - `/pages`: React route components (Landing, Courses, Profile, etc.)
  - `/components`: Reusable UI components.
  - `/App.tsx`: Main React Router configuration.
  - `package.json`: Frontend dependencies.

## 3. Actual Technology Stack
| Component | Technology | Version | Evidence | Purpose |
| :--- | :--- | :--- | :--- | :--- |
| Backend Framework | FastAPI | >=0.115.0 | `backend/pyproject.toml` | High-performance Python web API |
| Database ORM | SQLAlchemy | >=2.0.32 | `backend/pyproject.toml` | Database interactions |
| Migrations | Alembic | >=1.13.2 | `backend/pyproject.toml` | Database schema management |
| Async Database Driver | asyncpg / aiosqlite | >=0.29.0 | `backend/pyproject.toml` | PostgreSQL / SQLite connectivity |
| Frontend Library | React | ^19.2.8 | `package.json` | UI rendering |
| Frontend Routing | React Router DOM | ^7.18.3 | `package.json` | Client-side routing |
| Styling | Tailwind CSS | ^4.3.3 | `package.json` | Utility-first CSS framework |
| Build Tool | Vite | ^8.3.0 | `package.json` | Frontend bundler |
| Type Checking | TypeScript | ~6.0.2 | `package.json` | Static typing for frontend |

## 4. User Types and Authorization
- **User Model:** Implemented as a single `User` class in `app/models/user.py`.
- **Roles:** Handled via the `UserRole` enum.
  - `STUDENT` (Default)
  - `INSTRUCTOR`
  - `ADMIN`
- **Authentication:** JWT-based access tokens with stateful refresh tokens stored in the `RefreshToken` database model. Passwords hashed using bcrypt.
- **Authorization:** Handled via FastAPI dependencies. Operations like enrollment require a logged-in user.

| User Type / Role | Verified Capabilities | Evidence | Verification Status |
| :--- | :--- | :--- | :--- |
| Any Authenticated | Access own profile, enroll in courses, track progress | `courses.py`, `user.py` | Verified |
| INSTRUCTOR | Not explicitly isolated in API endpoints reviewed; likely relies on role checks | `user.py` | Partially Verified |
| ADMIN | Not explicitly isolated in API endpoints reviewed; likely relies on role checks | `user.py` | Partially Verified |

## 5. Database Models and Class Inventory
**Models (Verified in `backend/app/models/`):**

1. **User Management:**
   - `User`: Core user account and profile (fields: id, email, hashed_password, role, etc.)
   - `RefreshToken`: Secure session tracking.

2. **Course Curriculum:**
   - `Course`: Root curriculum entity (fields: id, title, category, difficulty, etc.)
   - `CourseModule`: Syllabus sections.
   - `Lesson`: Individual learning unit (theory/hands-on/quiz).
   - `LessonResource`: Attached artifacts (GitHub repos, docs).
   - `CourseEnrollment`: Tracks student enrollment status.

3. **Skills & Competencies:**
   - `Skill`: Technical competencies.
   - `CourseSkill`: Association between courses and skills.
   - `UserSkill`: Computed proficiency percentages.
   - `SkillEvidence`: Audit log of learning events.

4. **Career Roadmaps:**
   - `Roadmap`: Structured career pathways.
   - `RoadmapStep`: Sequential milestones.
   - `UserRoadmapProgress`: Tracks roadmap enrollment.

5. **Projects:**
   - `Project`: Hands-on engineering capstones.
   - `ProjectStep`, `ProjectResource`, `ProjectCourse`, `ProjectSkill`, `UserProjectEnrollment`, `ProjectStepProgress`.

6. **Certifications & Training:**
   - `Certification`: External exam prep tracks.
   - `CertificationTraining`: Links certifications to courses.
   - `UserCertificationEnrollment`: Tracks preparation enrollments.
   - `PracticeQuestion`, `PracticeAttempt`, `PracticeAttemptAnswer`: Mock exam engine.
   - `Certificate`: Platform-issued completion certificates.

7. **Progress Tracking:**
   - `LessonProgress`: Granular learning state per lesson.
   - `LearningActivity`: Append-only event stream of learning actions.

## 6. Relationship and Cardinality Inventory
| Source Model | Relationship | Target Model | Cardinality | Evidence |
| :--- | :--- | :--- | :--- | :--- |
| User | refresh_tokens | RefreshToken | 1:N | `User.refresh_tokens` |
| Course | modules | CourseModule | 1:N | `Course.modules` |
| CourseModule | lessons | Lesson | 1:N | `CourseModule.lessons` |
| Lesson | resources | LessonResource | 1:N | `Lesson.resources` |
| User | enrollments | CourseEnrollment | 1:N | `CourseEnrollment.user_id` |
| Course | enrollments | CourseEnrollment | 1:N | `CourseEnrollment.course_id` |
| Course | skills | Skill | N:M | `CourseSkill` |
| Roadmap | steps | RoadmapStep | 1:N | `Roadmap.steps` |
| Project | steps | ProjectStep | 1:N | `Project.steps` |
| Certification | trainings | CertificationTraining | 1:N | `Certification.trainings` |
| User | practice_attempts| PracticeAttempt | 1:N | `PracticeAttempt.user_id` |

## 7. UML Class Diagram Specification (Simplified Domain)
**User**
- `id`: String
- `email`: String
- `hashed_password`: String
- `role`: UserRole Enum
- `is_active`: Boolean
- Relations: 1:N CourseEnrollment, 1:N RefreshToken

**Course**
- `id`: String
- `title`: String
- `category`: String
- `difficulty`: String
- Relations: 1:N CourseModule, 1:N CourseEnrollment, N:M Skill

**CourseModule**
- `id`: String
- `title`: String
- `order_index`: Integer
- Relations: N:1 Course, 1:N Lesson

**Lesson**
- `id`: String
- `title`: String
- `content`: Text
- Relations: N:1 CourseModule, 1:N LessonResource

**CourseEnrollment** (Association Class)
- `user_id`: String
- `course_id`: String
- `status`: String

## 8. Entity-Relationship Diagram Specification
- **users**: PK id.
- **courses**: PK id.
- **course_modules**: PK id, FK course_id.
- **lessons**: PK id, FK module_id.
- **course_enrollments**: PK id, FK user_id, FK course_id. Unique(user_id, course_id).
- **skills**: PK id.
- **course_skills**: PK (course_id, skill_id).
- **roadmaps**: PK id.
- **projects**: PK id.

## 9. Functional Modules and Business Logic
- **Authentication**: JWT generation, refresh token management, password hashing (bcrypt).
- **Curriculum Management**: Hierarchical retrieval of courses, modules, and lessons.
- **Enrollment**: Logic to link users to courses (`CourseEnrollment`), enforcing uniqueness constraints.
- **Skill Tracking**: Complex logic updating `UserSkill` proficiency percentages based on `SkillEvidence` logs.
- **Mock Exams**: Storing `PracticeAttempt` and linking selected answers (`PracticeAttemptAnswer`) against `PracticeQuestion` correct options.

## 10. API Endpoint Inventory (Partial verified via `courses.py`)
| HTTP Method | Actual Path | Purpose | Authentication |
| :--- | :--- | :--- | :--- |
| GET | `/api/v1/courses` | List and filter courses | Optional/None |
| GET | `/api/v1/courses/{course_id}` | Get course detail | Optional/None |
| GET | `/api/v1/courses/{course_id}/curriculum` | Get syllabus tree | Optional/None |
| POST | `/api/v1/courses/{course_id}/enroll` | Enroll user | Required |
| DELETE | `/api/v1/courses/{course_id}/enroll` | Unenroll user | Required |

*(Other endpoints exist for auth, users, lessons, skills, roadmaps, certifications, projects, etc.)*

## 11. Data Flow and Process Specifications
**Course Enrollment Flow:**
1. **Actor:** Authenticated User (Student)
2. **Process:** Calls POST `/api/v1/courses/{course_id}/enroll`
3. **Data Access:** Creates `CourseEnrollment` record linking `User.id` and `Course.id`.
4. **Validation:** Checks if course exists, enforces unique constraint so a user cannot enroll twice.

## 12. Frontend Architecture and User Interface
- **Framework:** React 19 via Vite.
- **Styling:** TailwindCSS (`@tailwindcss/vite`).
- **Routing:** React Router v7 configured in `App.tsx`.
- **Main Routes:**
  - `/`: LandingPage
  - `/dashboard`: User Dashboard
  - `/courses`, `/courses/:courseId`: Curriculum browsing
  - `/learn/:courseId/:lessonId`: Lesson Player (Specialized layout without global footer)
  - `/roadmaps`, `/skills`, `/projects`, `/certifications`: Domain-specific pages.
