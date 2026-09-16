# CloudForge — Certifications, Training Programs, Practice Exams & Certificates

## Overview

CloudForge provides structured training pathways and exam simulation environments for Cloud & DevOps engineers. 

> [!IMPORTANT]
> **Vendor Distinction & Disclaimer**:
> CloudForge certificates are formative training completion certificates issued by CloudForge upon verified curriculum mastery. CloudForge is an educational platform and does **not** claim to issue official vendor credentials for AWS, Microsoft, Kubernetes, or other cloud providers. External exam preparation tracks prepare students for official third-party vendor exams administered separately.

---

## 1. Domain Entities & Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                       Certification                         │
│  (e.g., AWS CLF-C02, Azure AZ-900, DevOps Foundations)      │
└──────────────┬───────────────────────────────┬──────────────┘
               │ 1:N                           │ 1:N
               ▼                               ▼
┌───────────────────────────────┐  ┌───────────────────────────┐
│     CertificationTraining     │  │      PracticeQuestion     │
│   (Curriculum syllabus track) │  │ (Questions & explanations)│
└──────────────┬────────────────┘  └───────────┬───────────────┘
               │ maps to course                │ evaluated in
               ▼                               ▼
┌───────────────────────────────┐  ┌───────────────────────────┐
│       Course / Modules        │  │      PracticeAttempt      │
│   (Reusable lesson content)   │  │   (Quiz & Exam sessions)  │
└──────────────┬────────────────┘  └───────────┬───────────────┘
               │ progress                      │ contains
               ▼                               ▼
┌───────────────────────────────┐  ┌───────────────────────────┐
│     User Training Progress    │  │   PracticeAttemptAnswer   │
│   (Derived from LessonProg)   │  │  (Server-graded answers)  │
└──────────────┬────────────────┘  └───────────────────────────┘
               │ 100% completion
               ▼
┌───────────────────────────────┐
│          Certificate          │
│   (Idempotent CloudForge Cert)│
│  - verification_code (public) │
│  - certificate_number (CF-*)  │
└───────────────────────────────┘
```

---

## 2. Reusing Existing Course Curriculum

To avoid duplicating lesson content:
1. `CertificationTraining` contains a `course_id` foreign key referencing an existing `Course` entity.
2. Training progress is **dynamically calculated** from the student's authentic `LessonProgress` records on that linked course.
3. Enrollment in a certification training program automatically creates active enrollment in the underlying course.

### Progress Formula
$$\text{Progress \%} = \text{round}\left(\frac{\text{Completed Published Lessons}}{\text{Total Published Lessons}} \times 100, 1\right)$$

---

## 3. Practice Exam Simulation Lifecycle

1. **Start Attempt (`POST /api/v1/certifications/{id}/practice-attempts`)**:
   - Randomly selects questions for the target certification.
   - Strictly **omits** correct options and explanations from the initial response payload.
2. **Submit Answers (`POST /api/v1/practice-attempts/{attempt_id}/submit`)**:
   - Rejects duplicate submissions if the attempt was already finalized.
   - Evaluates each answer server-side against the internal correct answer index.
   - Calculates total score, percentage, and pass/fail (default: $\ge 70\%$).
   - Returns full question-by-question review, revealing correct answers and explanations.

---

## 4. Certificate Issuance & Public Verification

### Issuance Rule
A CloudForge Certificate is issued **only** when all required curriculum lessons in the training track have been verified as completed (`status == 'completed'`).

### Idempotency & Race Protection
- Calling completion repeatedly (`POST /api/v1/trainings/{training_id}/complete`) checks for existing certificates and returns the single canonical certificate.
- Unique constraints on `(user_id, training_id)` prevent duplicate records.

### Public Verification Endpoint (`GET /api/v1/certificates/verify/{verification_code}`)
Anyone with a verification code can confirm authenticity without exposing private student information:
- **Publicly Returned**: `is_valid`, `certificate_number`, `recipient_name`, `training_title`, `issued_at`, `status`, `completion_percentage`.
- **Protected/Omitted**: Email, passwords/hashes, internal user IDs, and private activity streams.

---

## 5. Seed Catalog

1. **AWS Certified Cloud Practitioner — CLF-C02** (Official Prep Track)
2. **Microsoft Azure Fundamentals — AZ-900** (Official Prep Track)
3. **Microsoft Azure AI Fundamentals — AI-900** (Official Prep Track)
4. **AWS Cloud Computing Foundations** (CloudForge Training Program)
5. **Kubernetes Fundamentals** (CloudForge Training Program)
6. **DevOps Foundations** (CloudForge Training Program)
