from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://dsir:dsir@localhost:5432/dsir"
    REDIS_URL: str = "redis://localhost:6379/0"
    SECRET_KEY: str = "dev-secret-change-me"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]
    AI_DEFAULT_PROVIDER: str = "mock"
    AI_FALLBACK_PROVIDER: str | None = None

    class Config:
        env_file = ".env"


settings = Settings()
