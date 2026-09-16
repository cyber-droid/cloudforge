# CloudForge Database Design & Schema Specification

This document defines the complete PostgreSQL schema, relationships, indexes, constraints, and cascade behavior for the CloudForge platform.

---

## 1. Entity-Relationship Diagram (Phases 1–6)

```
┌───────────┐         ┌─────────────────────┐
│   users   ├────────►│  course_enrollments │
└─────┬─────┘         └──────────┬──────────┘
      │                          │
      │ 1:N                      │ N:1
      ▼                          ▼
┌──────────────────┐  ┌─────────────────────┐
│ lesson_progress  │  │       courses       │
└──────────────────┘  └──────────┬──────────┘
                                 │ 1:N
                                 ▼
                      ┌─────────────────────┐
                      │    course_modules   │
                      └──────────┬──────────┘
                                 │ 1:N
                                 ▼
                      ┌─────────────────────┐
                      │       lessons       │
                      └─────────────────────┘

┌──────────────────┐  ┌───────────────────────────────┐
│     roadmaps     │  │             skills            │
└────────┬─────────┘  └───────────────┬───────────────┘
         │ 1:N                        │ 1:N
         ▼                            ▼
┌──────────────────┐  ┌───────────────────────────────┐
│  roadmap_steps   │  │         course_skills         │
└──────────────────┘  └───────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                       certifications                        │
└──────────────┬───────────────────────────────┬──────────────┘
               │ 1:N                           │ 1:N
               ▼                               ▼
┌───────────────────────────────┐  ┌───────────────────────────┐
│     certification_trainings   │  │     practice_questions    │
└──────────────┬────────────────┘  └───────────┬───────────────┘
               │ 1:N                           │ 1:N
               ▼                               ▼
┌───────────────────────────────┐  ┌───────────────────────────┐
│ user_certification_enrollments│  │     practice_attempts     │
└───────────────────────────────┘  └───────────┬───────────────┘
                                               │ 1:N
                                               ▼
                                   ┌───────────────────────────┐
                                   │ practice_attempt_answers  │
                                   └───────────────────────────┘

┌───────────────────────────────┐
│          certificates         │
│  (CloudForge Verification)    │
└───────────────────────────────┘
```

---

## 2. Phase 6 Schema Tables

### 2.1 `certifications`
Represents an industry certification preparation track or CloudForge foundational track.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | VARCHAR(36) | PK | Unique identifier (UUID) |
| `name` | VARCHAR(255) | NOT NULL | Display title |
| `vendor` | VARCHAR(100) | NOT NULL, INDEX | Vendor or provider (AWS, Azure, Kubernetes, DevOps) |
| `code` | VARCHAR(50) | NULL, INDEX | Official exam code (e.g., `CLF-C02`, `AZ-900`) |
| `slug` | VARCHAR(100) | NOT NULL, UNIQUE, INDEX | URL-safe slug |
| `description` | TEXT | NOT NULL | Detailed description |
| `level` | VARCHAR(50) | NOT NULL | Difficulty level (`Foundational`, `Associate`, `Professional`) |
| `category` | VARCHAR(100) | NOT NULL, INDEX | Domain category (`Cloud`, `DevOps`, `AI`) |
| `official_url` | VARCHAR(500) | NULL | Vendor reference URL |
| `is_official_certification` | BOOLEAN | NOT NULL, DEFAULT False | `True` for vendor prep, `False` for CloudForge foundational |
| `is_published` | BOOLEAN | NOT NULL, DEFAULT True, INDEX | Visibility status |
| `exam_domains` | JSON | NOT NULL, DEFAULT '[]' | Blueprint domain names & weighting percentages |
| `skills_gained` | JSON | NOT NULL, DEFAULT '[]' | Target competencies list |
| `badge_icon` | VARCHAR(50) | NOT NULL, DEFAULT 'Award' | UI icon identifier |
| `duration` | VARCHAR(50) | NOT NULL, DEFAULT '18h' | Estimated completion duration |
| `training_title` | VARCHAR(255) | NOT NULL | Primary training track label |
| `training_certificate_name` | VARCHAR(255) | NOT NULL | Title on CloudForge completion certificate |
| `created_at` | TIMESTAMPTZ | NOT NULL, DEFAULT now() | UTC timestamp |
| `updated_at` | TIMESTAMPTZ | NOT NULL, DEFAULT now() | UTC timestamp |

### 2.2 `certification_trainings`
Curriculum syllabus programs mapped to underlying courses.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | VARCHAR(36) | PK | Unique identifier (UUID) |
| `certification_id` | VARCHAR(36) | FK -> `certifications.id` (CASCADE), NOT NULL, INDEX | Parent certification |
| `title` | VARCHAR(255) | NOT NULL | Program title |
| `slug` | VARCHAR(100) | NOT NULL, INDEX | URL slug |
| `description` | TEXT | NOT NULL | Program description |
| `level` | VARCHAR(50) | NOT NULL | Level |
| `estimated_hours` | VARCHAR(50) | NOT NULL, DEFAULT '18h' | Time commitment |
| `course_id` | VARCHAR(36) | FK -> `courses.id` (SET NULL), NULL, INDEX | Reusable curriculum course |
| `modules` | JSON | NOT NULL, DEFAULT '[]' | Module checklist items |
| `is_published` | BOOLEAN | NOT NULL, DEFAULT True, INDEX | Published flag |
| `created_at` | TIMESTAMPTZ | NOT NULL | UTC timestamp |
| `updated_at` | TIMESTAMPTZ | NOT NULL | UTC timestamp |

### 2.3 `user_certification_enrollments`
Tracks student enrollment in a certification training pathway.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | VARCHAR(36) | PK | Unique identifier (UUID) |
| `user_id` | VARCHAR(36) | FK -> `users.id` (CASCADE), NOT NULL, INDEX | Enrolled student |
| `certification_id` | VARCHAR(36) | FK -> `certifications.id` (CASCADE), NOT NULL, INDEX | Certification track |
| `training_id` | VARCHAR(36) | FK -> `certification_trainings.id` (CASCADE), NOT NULL, INDEX | Training program |
| `status` | VARCHAR(50) | NOT NULL, DEFAULT 'enrolled', INDEX | Status (`enrolled`, `in_progress`, `completed`) |
| `enrolled_at` | TIMESTAMPTZ | NOT NULL | Enrollment date |
| `started_at` | TIMESTAMPTZ | NULL | First study session date |
| `completed_at` | TIMESTAMPTZ | NULL | Graduation timestamp |
| `created_at` | TIMESTAMPTZ | NOT NULL | UTC timestamp |
| `updated_at` | TIMESTAMPTZ | NOT NULL | UTC timestamp |

*Unique Constraint:* `uq_user_training_enrollment` on `(user_id, training_id)`.

### 2.4 `practice_questions`
Question bank for quizzes and timed practice exams.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | VARCHAR(36) | PK | Unique identifier (UUID) |
| `certification_id` | VARCHAR(36) | FK -> `certifications.id` (CASCADE), NOT NULL, INDEX | Parent certification |
| `training_id` | VARCHAR(36) | FK -> `certification_trainings.id` (CASCADE), NULL, INDEX | Optional training link |
| `question_text` | TEXT | NOT NULL | Problem statement |
| `question_type` | VARCHAR(50) | NOT NULL, DEFAULT 'single_choice' | Type (`single_choice`, `multiple_choice`) |
| `options` | JSON | NOT NULL | Array of multiple-choice text options |
| `correct_option` | INTEGER | NOT NULL | 0-indexed correct option (never exposed before submit) |
| `explanation` | TEXT | NOT NULL | Technical justification & domain review |
| `topic` | VARCHAR(100) | NULL, INDEX | Domain subtopic |
| `domain` | VARCHAR(100) | NULL | Exam blueprint domain |
| `difficulty` | VARCHAR(50) | NOT NULL, DEFAULT 'medium' | Difficulty (`beginner`, `medium`, `hard`) |
| `points` | INTEGER | NOT NULL, DEFAULT 10 | Point weighting |
| `is_published` | BOOLEAN | NOT NULL, DEFAULT True, INDEX | Visibility flag |
| `created_at` | TIMESTAMPTZ | NOT NULL | UTC timestamp |
| `updated_at` | TIMESTAMPTZ | NOT NULL | UTC timestamp |

### 2.5 `practice_attempts`
Attempt sessions for quizzes and full-length timed mock exams.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | VARCHAR(36) | PK | Unique identifier (UUID) |
| `user_id` | VARCHAR(36) | FK -> `users.id` (CASCADE), NOT NULL, INDEX | Authenticated student |
| `certification_id` | VARCHAR(36) | FK -> `certifications.id` (CASCADE), NOT NULL, INDEX | Target certification |
| `training_id` | VARCHAR(36) | FK -> `certification_trainings.id` (CASCADE), NULL | Optional training link |
| `attempt_type` | VARCHAR(50) | NOT NULL, DEFAULT 'practice_quiz', INDEX | Type (`practice_quiz`, `practice_exam`) |
| `total_questions` | INTEGER | NOT NULL, DEFAULT 0 | Number of questions |
| `score` | INTEGER | NOT NULL, DEFAULT 0 | Earned points |
| `percentage` | FLOAT | NOT NULL, DEFAULT 0.0 | Calculated percentage (0-100) |
| `passed` | BOOLEAN | NOT NULL, DEFAULT False, INDEX | Pass status ($\ge 70\%$) |
| `passing_percentage` | FLOAT | NOT NULL, DEFAULT 70.0 | Passing threshold |
| `correct_answers` | INTEGER | NOT NULL, DEFAULT 0 | Count of correct answers |
| `time_spent_seconds` | INTEGER | NOT NULL, DEFAULT 0 | Elapsed time |
| `question_ids` | JSON | NOT NULL, DEFAULT '[]' | Selected question UUIDs in attempt |
| `started_at` | TIMESTAMPTZ | NOT NULL | Start time |
| `submitted_at` | TIMESTAMPTZ | NULL | Finalization timestamp |
| `created_at` | TIMESTAMPTZ | NOT NULL | UTC timestamp |

### 2.6 `practice_attempt_answers`
Stores student answers evaluated server-side.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | VARCHAR(36) | PK | Unique identifier (UUID) |
| `attempt_id` | VARCHAR(36) | FK -> `practice_attempts.id` (CASCADE), NOT NULL, INDEX | Parent attempt |
| `question_id` | VARCHAR(36) | FK -> `practice_questions.id` (CASCADE), NOT NULL, INDEX | Answered question |
| `selected_answer` | VARCHAR(255) | NULL | Legacy string answer |
| `selected_option` | INTEGER | NULL | Chosen option index (0, 1, 2, 3) |
| `is_correct` | BOOLEAN | NOT NULL, DEFAULT False | Server-evaluated correctness |
| `points_earned` | INTEGER | NOT NULL, DEFAULT 0 | Points awarded |
| `created_at` | TIMESTAMPTZ | NOT NULL | UTC timestamp |

*Unique Constraint:* `uq_attempt_question` on `(attempt_id, question_id)`.

### 2.7 `certificates`
CloudForge-issued completion credentials with public verification codes.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | VARCHAR(36) | PK | Unique identifier (UUID) |
| `user_id` | VARCHAR(36) | FK -> `users.id` (CASCADE), NOT NULL, INDEX | Certificate recipient |
| `training_id` | VARCHAR(36) | FK -> `certification_trainings.id` (CASCADE), NOT NULL, INDEX | Completed training track |
| `certification_id` | VARCHAR(36) | FK -> `certifications.id` (SET NULL), NULL, INDEX | Associated certification |
| `certificate_number` | VARCHAR(100) | NOT NULL, UNIQUE, INDEX | Unique human-readable code (`CF-CLF-C02-...`) |
| `verification_code` | VARCHAR(64) | NOT NULL, UNIQUE, INDEX | Cryptographically secure random token |
| `issued_at` | TIMESTAMPTZ | NOT NULL | Issuance date |
| `status` | VARCHAR(50) | NOT NULL, DEFAULT 'issued', INDEX | Status (`issued`, `revoked`) |
| `completion_percentage` | FLOAT | NOT NULL, DEFAULT 100.0 | Completion percentage |
| `recipient_name_snapshot` | VARCHAR(255) | NOT NULL | Recipient name at time of issuance |
| `training_title_snapshot` | VARCHAR(255) | NOT NULL | Training title at time of issuance |
| `created_at` | TIMESTAMPTZ | NOT NULL | UTC timestamp |
| `updated_at` | TIMESTAMPTZ | NOT NULL | UTC timestamp |

*Unique Constraint:* `uq_user_training_certificate` on `(user_id, training_id)`.
