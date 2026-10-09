# cloudforge

# ☁️ CloudForge — AI-Assisted Cloud & DevOps Engineering Platform

**A structured learning and engineering platform for Cloud Computing, DevOps, DevSecOps, Kubernetes, Infrastructure as Code, GitOps, Observability, and AI-assisted operations.**

CloudForge is a web-based platform designed to bring modern cloud and DevOps learning resources into one organized environment. It combines a structured course curriculum with a modular backend, secure user authentication, relational data management, and a React-based user interface.

The project is being developed with a focus on maintainable architecture, secure API design, and practical engineering workflows.

---

## 🚀 Project Overview

Learning modern cloud and DevOps technologies often requires navigating multiple documentation sites, tutorials, repositories, and training platforms. CloudForge aims to provide a centralized environment where learners can discover courses, follow structured curricula, access lessons, and manage their course enrollments.

The platform's broader vision covers:

- ☁️ **Cloud Computing** — Cloud concepts and infrastructure fundamentals.
- ⚙️ **DevOps** — Development and operations practices.
- 🛡️ **DevSecOps** — Security integrated into engineering workflows.
- ☸️ **Kubernetes** — Container orchestration concepts.
- 🏗️ **Infrastructure as Code** — Infrastructure provisioning and configuration.
- 🔄 **GitOps & CI/CD** — Version-controlled delivery and automation.
- 📊 **Observability** — Monitoring, logs, metrics, and troubleshooting.
- 🤖 **AI-Assisted Operations** — A foundation for intelligent engineering assistance.

CloudForge is under active development. Its core learning platform is implemented, while the broader engineering capabilities are being developed and expanded.

## ✨ Key Features

### 📚 Course Learning Platform
- Structured courses organized into modules and lessons.
- Course catalog with search and filtering.
- Pagination for course listings.
- Detailed course information and curriculum access.
- Lesson content and supporting learning resources.
- Course enrollment and cancellation.
- Access to a user's enrolled courses.

### 🔐 Authentication and Security
- JWT-based access-token authentication.
- Refresh-token management.
- Password hashing using bcrypt.
- Role-based access control using a centralized user model.
- Protected operations for authenticated users.

### 🧩 Modular Backend Architecture
- FastAPI REST API.
- SQLAlchemy ORM models.
- Pydantic request and response schemas.
- Repository and service layers.
- Versioned API routes.
- Database migrations with Alembic.

### 🎯 Learning and Engineering Domains
The project includes domain models and application structures for areas such as skills, career roadmaps, hands-on projects, certifications, practice questions, and learning progress. The completeness of individual workflows may vary as development continues.

---

## 🛠️ Technology Stack

| Component | Technology |
|---|---|
| Frontend | React |
| Programming Language | TypeScript |
| Frontend Build Tool | Vite |
| Styling | Tailwind CSS |
| Frontend Routing | React Router |
| Backend | Python, FastAPI |
| API Validation | Pydantic |
| ORM | SQLAlchemy |
| Database | PostgreSQL 16 |
| Database Migrations | Alembic |
| Authentication | JWT access tokens and refresh tokens |
| Password Security | bcrypt |
| Automated Testing | pytest |

---

## 🏗️ System Architecture

CloudForge follows a modular client–server architecture.

```text
┌──────────────────────────────────────┐
│            React Frontend             │
│          TypeScript + Vite            │
│                                      │
│  Course Catalog │ Course Details      │
│  Curriculum     │ Lesson Interface    │
└───────────────────┬──────────────────┘
                    │
              RESTful HTTP API
                    │
┌───────────────────▼──────────────────┐
│             FastAPI Backend           │
│                                      │
│  API Routes → Schemas → Services     │
│                     → Repositories   │
│                                      │
│  Authentication │ Authorization      │
└───────────────────┬──────────────────┘
                    │
               SQLAlchemy ORM
                    │
┌───────────────────▼──────────────────┐
│           PostgreSQL Database         │
│                                      │
│  Users │ Courses │ Modules │ Lessons │
│  Resources │ Enrollments │ Other Data│
└──────────────────────────────────────┘
```

The frontend communicates with the backend through RESTful APIs. The backend validates requests, applies application logic, enforces access requirements, and interacts with persistent data through SQLAlchemy.

Alembic manages database schema migrations.

---

## 🗂️ Project Structure

The main application directories are organized as follows:

```text
CloudForge/
├── backend/
│   ├── app/
│   │   ├── api/          # API routers and endpoints
│   │   ├── core/         # Configuration, database and security
│   │   ├── models/       # SQLAlchemy database models
│   │   ├── schemas/      # Pydantic validation schemas
│   │   ├── repositories/ # Data access layer
│   │   └── services/     # Business logic
│   ├── alembic/          # Database migrations
│   ├── tests/            # Backend tests
│   └── pyproject.toml    # Backend dependencies and settings
│
├── src/
│   ├── components/       # Reusable UI components
│   ├── pages/            # Frontend pages
│   ├── services/         # API client and service functions
│   └── App.tsx           # Application routing
│
├── package.json          # Frontend dependencies and scripts
└── README.md
```

*Directory names are illustrative of the documented architecture; consult the current repository for the complete file structure.*

---

## 🗄️ Core Data Models

The application uses SQLAlchemy models to represent its main domain entities.

| Model | Responsibility |
|---|---|
| `User` | User accounts, profile data, and roles |
| `RefreshToken` | Refresh-token session records |
| `Course` | Course information and metadata |
| `CourseModule` | Modules belonging to a course |
| `Lesson` | Lessons belonging to a module |
| `LessonResource` | Resources associated with lessons |
| `CourseEnrollment` | Links users to courses they enroll in |
| `Skill` | Technical skills and competencies |
| `CourseSkill` | Association between courses and skills |
| `Roadmap` | Structured learning or career roadmaps |
| `Project` | Hands-on engineering project definitions |
| `Certification` | Certification-related learning structures |
| `LessonProgress` | Lesson-level learning progress |

Additional models support roadmap steps, project resources, skill evidence, practice questions, certification training, and other learning-related functionality.

### Core Relationships

- A course contains multiple modules.
- A module contains multiple lessons.
- A lesson can have associated learning resources.
- A user can enroll in multiple courses.
- A course can have multiple enrolled users.
- Courses and skills can be associated through `CourseSkill`.
- A user has a role represented by the `UserRole` enum.

---

## 🔌 API Overview

The backend exposes versioned REST endpoints under `/api/v1`.

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/api/v1/courses` | List, search, and filter courses |
| `GET` | `/api/v1/courses/{course_id}` | Retrieve course details |
| `GET` | `/api/v1/courses/{course_id}/curriculum` | Retrieve a course curriculum |
| `GET` | `/api/v1/courses/{course_id}/modules/{module_id}` | Retrieve module information |
| `GET` | `/api/v1/courses/{course_id}/lessons/{lesson_id}` | Retrieve lesson information |
| `POST` | `/api/v1/courses/{course_id}/enroll` | Enroll the authenticated user |
| `DELETE` | `/api/v1/courses/{course_id}/enroll` | Cancel course enrollment |
| `GET` | `/api/v1/users/me/courses` | List the current user's enrolled courses |
| `GET` | `/api/v1/users/me/courses/{course_id}` | Retrieve the user's course enrollment details |

Authentication requirements depend on the endpoint. Enrollment operations require an authenticated user.

---

## 📊 Implementation Highlights

The documented core learning-platform implementation includes:

- **9 production-oriented courses**
- **103 course modules**
- Structured course, module, lesson, resource, and enrollment models
- Search, filtering, and pagination
- REST API integration with the React frontend
- Database migrations and structured seed data
- JWT-based authentication and role-based access control
- Automated backend testing

The course content covers cloud and DevOps-related domains and includes structured lessons, Markdown content, YAML examples, and relevant technical references.

## 🧪 Testing

The documented implementation has a pytest test suite covering areas such as:

- Authentication
- Course operations
- Enrollment behavior
- User functionality
- Security
- Health checks
- Role-based access control

The recorded test result for the documented test run was **22 passing tests**. This is a recorded result, not a guarantee that the latest version of the repository has the same result; rerun the tests after making changes.

---

## 💻 Getting Started

### Prerequisites

Install the following tools before setting up the application:

- Python compatible with the backend dependencies
- Node.js and npm
- PostgreSQL 16
- Git

### 1. Clone the Repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd CloudForge
```

Replace the placeholder with your actual repository URL.

### 2. Configure the Backend

Navigate to the backend directory:

```bash
cd backend
```

Create and activate a Python virtual environment:

```bash
python -m venv .venv
```

Windows:

```powershell
.venv\Scripts\Activate.ps1
```

Linux/macOS:

```bash
source .venv/bin/activate
```

Install the backend dependencies using the repository's documented dependency manager and `pyproject.toml`.

Configure the required database connection and authentication settings using the project's environment configuration. **Do not commit passwords, secret keys, or tokens to GitHub.**

Apply the database migrations using the project's configured Alembic setup before starting the backend.

### 3. Start the Backend

Run the FastAPI application using the entry point and development command configured in the repository.

Once the server is running, use the configured API base URL to access the backend and its API documentation, if enabled.

### 4. Configure the Frontend

From the repository root, install the frontend dependencies:

```bash
npm install
```

Start the Vite development server using the script configured in `package.json`:

```bash
npm run dev
```

Configure the frontend API base URL to point to the running backend.

**Note:** Exact environment variable names, migration commands, seed commands, and server ports depend on the current project configuration. Refer to the repository's configuration files before running deployment or setup commands.

---

## 🔒 Security Considerations

CloudForge incorporates security practices including:

- Password hashing rather than storing plaintext passwords.
- JWT-based authentication.
- Refresh-token records.
- Role-based access control.
- Request validation through Pydantic schemas.
- Protected endpoints for user-specific operations.

For local development, use separate credentials and secret values. Never upload `.env` files, database credentials, private keys, or access tokens to a public repository.

---

## 🗺️ Development Roadmap

Potential areas for continued development include:

- [ ] Expand hands-on cloud and DevOps learning exercises.
- [ ] Add interactive infrastructure and Kubernetes laboratories.
- [ ] Improve personalized learning paths and progress visualization.
- [ ] Expand practical assessment and certification-preparation workflows.
- [ ] Develop AI-assisted troubleshooting capabilities.
- [ ] Improve deployment automation and operational observability.
- [ ] Expand automated testing and security validation.

These items represent development goals and should not be interpreted as already completed features.

---

## 🎓 Project Information

**Project:** CloudForge – AI-Assisted Cloud & DevOps Engineering Platform  
**Project Type:** Web Application / Cloud & DevOps Learning Platform  
**Academic Context:** BCA Project  
**Development Status:** Active Development

This project explores modern web application architecture, API development, database design, authentication, and structured technical learning within the Cloud and DevOps domain.

---

## 🤝 Contributing

Contributions, suggestions, and constructive feedback are welcome.

1. Fork the repository.
2. Create a feature branch.
3. Make your changes.
4. Test the affected functionality.
5. Submit a pull request with a clear description.

Please avoid including secrets, credentials, generated files, or unrelated changes in pull requests.

---

## 📄 License

A license has not been specified yet. Until a license is added to the repository, do not assume that the project is open for unrestricted reuse or redistribution.

---

**CloudForge — Learn the cloud. Engineer the future.**
