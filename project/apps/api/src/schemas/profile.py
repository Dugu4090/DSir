from __future__ import annotations

from pydantic import BaseModel


class ProfileUpdate(BaseModel):
    full_name: str | None = None
    timezone: str | None = None
    daily_goal_minutes: int | None = None
    preferred_language: str | None = None
    preferences: dict | None = None


class ProfileRead(BaseModel):
    user_id: str  # Will be serialized from UUID by FastAPI
    timezone: str | None = "UTC"
    daily_goal_minutes: int = 30
    preferred_language: str = "en"
    onboarding_completed: bool = False
    preferences: dict = {}

    class Config:
        from_attributes = True
