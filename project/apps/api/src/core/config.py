from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database / Cache
    DATABASE_URL: str = "postgresql+asyncpg://dsir:dsir@localhost:5432/dsir"
    REDIS_URL: str = "redis://localhost:6379/0"

    # Security
    SECRET_KEY: str = "dev-secret-change-me"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALGORITHM: str = "HS256"

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]

    # AI
    AI_DEFAULT_PROVIDER: str = "mock"
    AI_FALLBACK_PROVIDER: str | None = None
    OPENAI_API_KEY: str | None = None
    ANTHROPIC_API_KEY: str | None = None
    GEMINI_API_KEY: str | None = None
    OLLAMA_BASE_URL: str | None = None

    # Rate limiting (requests per minute)
    RATE_LIMIT_DEFAULT: str = "100/minute"
    RATE_LIMIT_AUTH: str = "10/minute"

    # Code execution
    PISTON_BASE_URL: str | None = None
    EXECUTION_TIMEOUT_MS: int = 3000
    EXECUTION_MEMORY_MB: int = 128

    # Workers
    CELERY_BROKER_URL: str | None = None
    CELERY_RESULT_BACKEND: str | None = None

    class Config:
        env_file = ".env"


settings = Settings()
