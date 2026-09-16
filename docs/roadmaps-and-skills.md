# CloudForge: Learning Roadmaps & Skill Development Architecture (Phase 5)

> **Important Clarification**: CloudForge skill levels and progression metrics are internal engineering learning indicators and formative mastery estimates. They are **not** official industry certifications or accredited standardized assessments.

---

## 1. Architectural Overview

Phase 5 introduces two interconnected systems designed to guide engineers through structured career learning paths:

1. **Learning Roadmaps (`Roadmap`, `RoadmapStep`, `UserRoadmapProgress`)**: Structured, multi-stage career progression paths (e.g., Cloud Engineer, DevOps Engineer, DevSecOps Engineer, AI + DevOps Engineer) composed of sequential, ordered learning nodes.
2. **Technical Skills Development (`Skill`, `CourseSkill`, `UserSkill`, `SkillEvidence`)**: Granular engineering capabilities across 9 technical categories (Cloud, DevOps, DevSecOps, Kubernetes, Security, Observability, AI, Programming, Infrastructure) evaluated through deterministic learning evidence.

```
+-----------------------------------------------------------------------------------+
|                                 CAREER ROADMAP                                    |
| (e.g., DevOps Engineer: Step 1 Linux -> Step 2 Docker -> Step 3 K8s -> Milestone) |
+-----------------------------------------+-----------------------------------------+
                                          |
                    Evaluates live student progress
                                          |
                                          v
+-----------------------------------+   +-------------------------------------------+
|          COURSE COMPLETION        |   |              SKILL PROFICIENCY            |
| (Enrolled, modules & lessons done)|   | (Deterministic score calculated from labs)|
+-----------------------------------+   +-------------------------------------------+
                                          ^
                                          |
                          Derives evidence from completed
                                courses & lessons
                                          |
+-----------------------------------------+-----------------------------------------+
|                    COURSE <----> SKILL (Many-to-Many)                             |
| (e.g., Kubernetes Engineering maps to Kubernetes, Docker, Helm, Networking)       |
+-----------------------------------------------------------------------------------+
```

---

## 2. Roadmap Architecture & Progress Calculation

### 2.1 Database Models

- **`Roadmap`**:
  - `id` (UUID Primary Key)
  - `slug` (Unique string identifier)
  - `title`, `description`, `category`, `difficulty`, `duration_label`
  - `skills_count`, `projects_count`, `certifications_targeted` (JSON array)
  - `published` (Boolean)
  - `created_at`, `updated_at`

- **`RoadmapStep`**:
  - `id` (UUID Primary Key)
  - `roadmap_id` (Foreign Key -> `roadmaps.id`, indexed)
  - `title`, `description`
  - `step_type`: Enum (`course`, `skill`, `milestone`)
  - `order_index`: Integer ordering within the roadmap
  - `required`: Boolean (whether completion is mandatory for path progression)
  - `estimated_hours`: String (e.g., `"25h"`)
  - `skills_covered`: JSON array of skill names
  - `course_id`: Foreign Key -> `courses.id` (nullable)
  - `skill_id`: Foreign Key -> `skills.id` (nullable)
  - `project_id`: Nullable placeholder for future Phase 7 project links
  - `certification_id`: Nullable placeholder for future Phase 6 certification links

- **`UserRoadmapProgress`**:
  - `id` (UUID Primary Key)
  - `user_id` (Foreign Key -> `users.id`)
  - `roadmap_id` (Foreign Key -> `roadmaps.id`)
  - `status`: String (`not_started`, `in_progress`, `completed`)
  - `started_at`, `completed_at`, `last_activity_at`
  - Unique Constraint: `(user_id, roadmap_id)`

### 2.2 Dynamic Roadmap Step Evaluation

Roadmap progress is **derived dynamically** from live platform activity rather than storing duplicate state that can go out of sync:

1. **Course Step (`step_type == "course"`)**:
   - Step is marked completed when the user has an active `CourseEnrollment` with `status == "completed"`.
2. **Skill Step (`step_type == "skill"`)**:
   - Step is marked completed when the user's calculated skill proficiency reaches foundational competency ($\ge 40\%$, corresponding to Level 2+).
3. **Milestone Step (`step_type == "milestone"`)**:
   - Evaluated as upcoming/in-progress until a future capstone project or manual verification is recorded.

### 2.3 Path Progression Formula

$$\text{Roadmap Progress \%} = \min\left(100.0, \frac{\text{Count of Completed Required Steps}}{\text{Total Required Steps}} \times 100\right)$$

- Optional steps (`required == False`) are excluded from the denominator.
- Empty roadmaps safely evaluate to $0.0\%$.

---

## 3. Skill System & Evidence Scoring

### 3.1 Skill Levels

| Level | Name | Score Range | Learning Interpretation |
| :---: | :--- | :---: | :--- |
| **1** | **Beginner** | $0\% - 20\%$ | Initial exposure to core commands and basic syntax |
| **2** | **Foundational** | $21\% - 40\%$ | Understanding of architecture, basic workflows, and runtime config |
| **3** | **Intermediate** | $41\% - 70\%$ | Autonomous execution of deployment pipelines and troubleshooting |
| **4** | **Advanced** | $71\% - 90\%$ | Production-grade cluster maintenance, security policies, and automation |
| **5** | **Expert** | $91\% - 100\%$ | High-scale multi-cloud architecture, governance, and site reliability |

### 3.2 Deterministic Evidence Scoring Algorithm

Skill proficiency is calculated deterministically from verified student progress:

$$\text{Skill Proficiency \%} = \min\left(100.0, \sum_{\text{mapped lessons}} w_l \times 5.0\% + \sum_{\text{mapped courses}} w_c \times 25.0\%\right)$$

- **Lesson Completion**: Each completed lesson associated with a skill's mapped course awards $+5.0\% \times \text{weight}$.
- **Course Completion**: Completing an entire course syllabus awards a major milestone bonus of $+25.0\% \times \text{weight}$.
- **Weight**: Configurable between $0.5$ and $1.0$ per Course-Skill association.

This model is deterministic, explainable, and prevents arbitrary or randomly generated percentages.

---

## 4. Course-to-Skill Mappings

Skills map to courses via the `course_skills` association table:

| Course Slug | Mapped Skills | Association Weights |
| :--- | :--- | :---: |
| `cloud-computing-foundations` | Cloud Security, AWS, Networking | 1.0, 1.0, 0.8 |
| `devops-engineering-foundations` | Linux, Git, Docker, CI/CD | 1.0, 1.0, 1.0, 1.0 |
| `kubernetes-engineering` | Kubernetes, Docker, Helm, Networking | 1.0, 0.8, 1.0, 0.7 |
| `devsecops-engineering` | DevSecOps, Cloud Security, CI/CD | 1.0, 1.0, 0.8 |
| `infrastructure-as-code-terraform` | Terraform, Infrastructure, AWS | 1.0, 1.0, 0.7 |
| `gitops-continuous-delivery` | GitOps, Kubernetes, CI/CD | 1.0, 0.9, 0.8 |
| `production-observability-sre` | Observability, Linux | 1.0, 0.6 |
| `ai-assisted-devops` | AI for DevOps, Python, CI/CD | 1.0, 1.0, 0.6 |

---

## 5. Seeded Career Roadmaps

### 1. Cloud Engineer
1. **Linux Fundamentals** (`course`: `devops-engineering-foundations`)
2. **Networking Fundamentals** (`skill`: `networking`)
3. **Cloud Computing Foundations** (`course`: `cloud-computing-foundations`)
4. **AWS Fundamentals** (`skill`: `aws`)
5. **Identity & Access Management (IAM)** (`skill`: `cloud-security`)
6. **Infrastructure as Code** (`course`: `infrastructure-as-code-terraform`)
7. **Cloud Security & Governance** (`skill`: `cloud-security`)
8. **Cloud Architecture Project** (`milestone`)

### 2. DevOps Engineer
1. **Linux Fundamentals** (`course`: `devops-engineering-foundations`)
2. **Git & Version Control** (`skill`: `git`)
3. **Docker & Containerization** (`skill`: `docker`)
4. **CI/CD Automation** (`skill`: `cicd`)
5. **Kubernetes Engineering** (`course`: `kubernetes-engineering`)
6. **Helm Package Management** (`skill`: `helm`)
7. **Infrastructure as Code** (`course`: `infrastructure-as-code-terraform`)
8. **GitOps Continuous Delivery** (`course`: `gitops-continuous-delivery`)
9. **Production Observability & SRE** (`course`: `production-observability-sre`)
10. **Production DevOps Capstone** (`milestone`)

### 3. DevSecOps Engineer
1. **Linux & Git Foundations** (`skill`: `linux`)
2. **CI/CD Security Foundations** (`skill`: `cicd`)
3. **DevSecOps Engineering** (`course`: `devsecops-engineering`)
4. **Static Application Security Testing (SAST)** (`skill`: `devsecops`)
5. **Dependency & Supply Chain Security** (`skill`: `devsecops`)
6. **Container & Image Security** (`skill`: `cloud-security`)
7. **Secrets Management** (`skill`: `devsecops`)
8. **Kubernetes Security Hardening** (`skill`: `kubernetes`)
9. **Cloud Security Posture** (`skill`: `cloud-security`)
10. **DevSecOps Pipeline Capstone** (`milestone`)

### 4. AI + DevOps Engineer
1. **Python Automation** (`skill`: `python`)
2. **Cloud Computing Foundations** (`course`: `cloud-computing-foundations`)
3. **DevOps Engineering Foundations** (`course`: `devops-engineering-foundations`)
4. **AI for Cloud & DevOps** (`course`: `ai-assisted-devops`)
5. **Prompt Engineering for Infrastructure** (`skill`: `ai-devops`)
6. **RAG for Ops Documentation** (`skill`: `ai-devops`)
7. **AI-Assisted CI/CD** (`skill`: `ai-devops`)
8. **AI Log Analysis & RCA** (`skill`: `observability`)
9. **AI Incident Auto-Remediation** (`skill`: `ai-devops`)
10. **AI Engineering Capstone Project** (`milestone`)

---

## 6. API Reference

### Roadmaps API

- `GET /api/v1/roadmaps` — List published career roadmaps with pagination, search, category, and difficulty filtering.
- `GET /api/v1/roadmaps/{id_or_slug}` — Retrieve complete roadmap details with ordered steps and linked course/skill entities.
- `GET /api/v1/roadmaps/{id_or_slug}/steps` — Retrieve ordered steps for a specific roadmap.
- `POST /api/v1/roadmaps/{id_or_slug}/start` — Start tracking a roadmap for the authenticated user (idempotent).
- `GET /api/v1/users/me/roadmaps` — List all roadmaps started by the authenticated user with real progress metrics.
- `GET /api/v1/users/me/roadmaps/{id_or_slug}` — Retrieve single user roadmap progress and step completion breakdown.

### Skills API

- `GET /api/v1/skills` — List technical skills catalog with category filtering.
- `GET /api/v1/skills/{id_or_slug}` — Retrieve individual skill details and associated courses.
- `GET /api/v1/users/me/skills` — Retrieve comprehensive student competency matrix with calculated levels, top skills, and average proficiency.
- `GET /api/v1/users/me/skills/{id_or_slug}` — Retrieve single user skill proficiency breakdown.
- `POST /api/v1/users/me/skills/{id_or_slug}/recalculate` — Trigger explicit evidence recalculation for a skill.

---

## 7. Future Extension Points

1. **Phase 6: Certifications & Practice Exams**: Roadmap steps can link to `certification_id` with exam readiness score conditions.
2. **Phase 7: Applied Engineering Projects**: Milestone steps can bind to `project_id` and evaluate GitHub repo PR status.
3. **Phase 8: AI Workbench & Incident Troubleshooting**: Skill evidence can ingest troubleshooting incident lab completions.
