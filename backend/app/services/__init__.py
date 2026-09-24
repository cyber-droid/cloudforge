"""
Services Package - Houses domain business logic.
"""

from app.services.auth_service import AuthService, auth_service
from app.services.course_service import CourseService, course_service
from app.services.project_service import ProjectService, project_service
from app.services.user_service import UserService, user_service

__all__ = [
    "AuthService",
    "auth_service",
    "UserService",
    "user_service",
    "CourseService",
    "course_service",
    "ProjectService",
    "project_service",
]
