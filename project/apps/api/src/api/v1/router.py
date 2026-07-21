from fastapi import APIRouter

from src.api.v1 import (
    ai,
    auth,
    courses,
    enrollments,
    execution,
    lessons,
    mastery,
    profiles,
    projects,
    revision,
    roadmaps,
    submissions,
    users,
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(profiles.router, prefix="/profiles", tags=["profiles"])
api_router.include_router(courses.router, prefix="/courses", tags=["courses"])
api_router.include_router(roadmaps.router, prefix="/roadmaps", tags=["roadmaps"])
api_router.include_router(enrollments.router, prefix="/enrollments", tags=["enrollments"])
api_router.include_router(lessons.router, prefix="/lessons", tags=["lessons"])
api_router.include_router(submissions.router, prefix="/submissions", tags=["submissions"])
api_router.include_router(mastery.router, prefix="/mastery", tags=["mastery"])
api_router.include_router(revision.router, prefix="/revision", tags=["revision"])
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(ai.router, prefix="/ai", tags=["ai"])
api_router.include_router(execution.router, prefix="/execution", tags=["execution"])
