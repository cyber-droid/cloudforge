# CloudForge: Learning Progress & Dashboard Analytics (Phase 4)

## 1. Overview & System Purpose

The **Learning Progress & Analytics Engine** provides deterministic, tamper-resistant tracking of user progression through CloudForge curriculum. It serves as the single source of truth for:
- Lesson completion state and time tracking.
- Automatic course graduation.
- Calendar-day learning streak calculations.
- Aggregated learning metrics (study hours, completion ratios, weekly distribution).
- High-performance unified dashboard data delivery.

No metrics are randomized or hardcoded; every dashboard value is computed live from PostgreSQL tables.

---

## 2. Database Models & Schema Design

### 2.1 `LessonProgress` (`lesson_progress`)
Represents a student's granular status within a single curriculum lesson.

| Column | Type | Constraints / Modifiers | Description |
| :--- | :--- | :--- | :--- |
| `id` | `VARCHAR(36)` | PK, indexed | UUIDv4 identifier |
| `user_id` | `VARCHAR(36)` | FK(`users.id`), indexed, cascade | User ID |
| `lesson_id` | `VARCHAR(36)` | FK(`lessons.id`), indexed, cascade | Lesson ID |
| `status` | `VARCHAR(20)` | indexed, default `'not_started'` | Status: `not_started`, `in_progress`, `completed` |
| `started_at` | `TIMESTAMPTZ` | not null | When student opened the lesson |
| `completed_at` | `TIMESTAMPTZ` | nullable | Timestamp of successful completion |
| `time_spent_seconds` | `INTEGER` | not null, default 0 | Cumulative elapsed study duration |
| `last_accessed_at` | `TIMESTAMPTZ` | not null, indexed | Last interaction timestamp |
| `created_at` | `TIMESTAMPTZ` | not null | Creation timestamp |
| `updated_at` | `TIMESTAMPTZ` | not null | Modification timestamp |

**Unique Constraint:**
```sql
CONSTRAINT uq_user_lesson_progress UNIQUE (user_id, lesson_id);
```
Guarantees a student can never have duplicate progress records for the same lesson.

---

### 2.2 `LearningActivity` (`learning_activities`)
An append-only audit stream recording every significant learning milestone.

| Column | Type | Constraints / Modifiers | Description |
| :--- | :--- | :--- | :--- |
| `id` | `VARCHAR(36)` | PK, indexed | UUIDv4 identifier |
| `user_id` | `VARCHAR(36)` | FK(`users.id`), indexed, cascade | User ID |
| `activity_type` | `VARCHAR(50)` | indexed, not null | `lesson_started`, `lesson_completed`, `lesson_time_recorded`, `course_enrolled`, `course_completed` |
| `course_id` | `VARCHAR(36)` | FK(`courses.id`), nullable, indexed | Associated course |
| `lesson_id` | `VARCHAR(36)` | FK(`lessons.id`), nullable, indexed | Associated lesson |
| `duration_seconds` | `INTEGER` | nullable, default 0 | Duration spent during this event |
| `activity_metadata` | `JSON` | not null, default `{}` | Context metadata (titles, tags) |
| `created_at` | `TIMESTAMPTZ` | not null, indexed | Event occurrence timestamp (UTC) |

---

## 3. Progress Calculation & Business Logic

### 3.1 Course Progress Percentage
Course progress is derived **strictly from published lessons**:
$$\text{Course Progress (\%)} = \left( \frac{\text{Count of Completed Published Lessons}}{\text{Total Published Lessons in Course}} \right) \times 100$$
- Unenrolled preview lessons do not count toward enrolled completion unless the user is enrolled.
- If a course has 0 published lessons, progress evaluates safely to `0.0%`.
- Rounded to 1 decimal place (e.g., `67.5%`).

### 3.2 Automatic Course Graduation
When a student completes a lesson:
1. The service queries all published lessons in that course.
2. Checks if all published lesson IDs exist in the user's `completed` `LessonProgress` set.
3. If complete:
   - Sets `CourseEnrollment.status = 'completed'`.
   - Sets `CourseEnrollment.completed_at = CURRENT_TIMESTAMP`.
   - Emits a `course_completed` `LearningActivity` event.

### 3.3 True Calendar-Day Streak Algorithm
Streaks are calculated from unique UTC calendar dates in `LearningActivity`:
1. Extract all unique event dates `d` from `LearningActivity.created_at`.
2. Check if the most recent activity is **Today** or **Yesterday** (allowing active streaks to stay intact during the current calendar day).
3. Traverse dates in reverse order: increment streak for each uninterrupted consecutive date.
4. Calculate historical longest streak by finding the maximum contiguous date segment.

---

## 4. API Endpoints

### 4.1 Lesson Study Endpoints
- `POST /api/v1/lessons/{lesson_id}/start`: Initialize or resume lesson study; sets `in_progress`.
- `POST /api/v1/lessons/{lesson_id}/progress`: Increment study time in seconds with bounds validation (`0 <= time <= 86400s`).
- `POST /api/v1/lessons/{lesson_id}/complete`: Mark lesson as complete, calculate course progression, and check graduation.

### 4.2 User Progress & Dashboard Endpoints
- `GET /api/v1/users/me/progress`: Overall student metrics (completion %, active courses, hours, streaks).
- `GET /api/v1/users/me/courses/{course_id}/progress`: Specific course progress metrics.
- `GET /api/v1/users/me/continue-learning`: Dynamic resume target card (most recent in-progress lesson or first incomplete lesson).
- `GET /api/v1/users/me/activity`: Aggregated daily activity for heatmaps (`?period=week|month|year`).
- `GET /api/v1/users/me/activity/recent`: Formatted recent activity feed.
- `GET /api/v1/users/me/dashboard`: Unified single-roundtrip aggregation endpoint for high-speed dashboard loading.

---

## 5. Concurrency & Data Consistency

- **Idempotent Operations**: Repeated `start` or `complete` requests update timestamps without generating duplicate rows.
- **Database Indexing**: B-tree indexes on `user_id`, `lesson_id`, `course_id`, `status`, `last_accessed_at`, and `created_at`.
- **UTC Timezone Canonicalization**: All timestamps are persisted in UTC. Time calculations and date aggregations evaluate day boundaries without timezone drift.
