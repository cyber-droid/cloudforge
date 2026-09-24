"""
Aggregated API v1 Router.

Combines all sub-routers for CloudForge endpoints.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth,
    certificates,
    certifications,
    courses,
    health,
    lessons,
    practice,
    projects,
    roadmaps,
    skills,
    trainings,
    users,
)

api_router = APIRouter()

# Core System & Diagnostics
api_router.include_router(health.router, tags=["System Diagnostics"])

# Authentication & Sessions
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])

# User Profiles, Preferences, Progress, Skills & Roadmaps
api_router.include_router(users.router, prefix="/users", tags=["Users & Progress"])

# Courses & Curriculum
api_router.include_router(courses.router, prefix="/courses", tags=["Courses"])

# Lessons & Study Progress
api_router.include_router(
    lessons.router, prefix="/lessons", tags=["Lessons & Progress"]
)

# Technical Skills & Competency Matrix
api_router.include_router(
    skills.router, prefix="/skills", tags=["Skills & Competencies"]
)

# Career Learning Roadmaps
api_router.include_router(roadmaps.router, prefix="/roadmaps", tags=["Career Roadmaps"])

# Certifications & Exam Preparation
api_router.include_router(
    certifications.router, prefix="/certifications", tags=["Certifications"]
)

# Certification Training Tracks
api_router.include_router(
    trainings.router, prefix="/trainings", tags=["Certification Training"]
)

# Practice Quizzes & Timed Mock Exams
api_router.include_router(practice.router, tags=["Practice Exams & Quizzes"])

# CloudForge Certificates & Public Verification
api_router.include_router(
    certificates.router, prefix="/certificates", tags=["Certificates"]
)

# Engineering Projects & DevOps Workflows
api_router.include_router(
    projects.router, prefix="/projects", tags=["Engineering Projects"]
)
