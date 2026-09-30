"""
Centralized application configuration.

All environment-driven values are declared here and nowhere else.
Never hardcode secrets, hosts, or keys anywhere else in the codebase —
import `settings` from this module instead.
"""
from functools import lru_cache
from typing import List, Literal

from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # ---- App ----
    ENVIRONMENT: Literal["development", "staging", "production"] = "development"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api"
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:5173"]

    # ---- Database ----
    DATABASE_URL: str

    # ---- Auth ----
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ---- AI Provider ----
    AI_PROVIDER: Literal["claude", "openai", "local"] = "claude"
    ANTHROPIC_API_KEY: str | None = None
    ANTHROPIC_MODEL: str = "claude-sonnet-4-6"
    OPENAI_API_KEY: str | None = None
    OPENAI_MODEL: str = "gpt-4o-mini"
    LOCAL_EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"

    # ---- Redis ----
    REDIS_URL: str | None = None

    # ---- Rate limiting ----
    RATE_LIMIT_PER_MINUTE: int = 60

    # ---- Code execution sandbox ----
    CODE_EXEC_SANDBOX_URL: str | None = None
    CODE_EXEC_TIMEOUT_SECONDS: int = 10

    # ---- Logging ----
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: Literal["json", "text"] = "json"

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v):
        if isinstance(v, str) and not v.startswith("["):
            return [origin.strip() for origin in v.split(",")]
        return v


@lru_cache
def get_settings() -> Settings:
    """Settings are cached so the .env file is parsed only once per process."""
    return Settings()


settings = get_settings()
