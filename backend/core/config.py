"""
Application Configuration Settings
"""
from pydantic_settings import BaseSettings
from typing import List, Optional
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application Settings
    APP_NAME: str = "AI Teaching Assistant API"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "Backend API for AI-powered teaching assistant with automated grading and Q&A support"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"

    # Server Settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 1
    RELOAD: bool = True

    # CORS Settings
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: List[str] = ["*"]
    CORS_ALLOW_HEADERS: List[str] = ["*"]

    # API Settings
    API_V1_PREFIX: str = "/api/v1"

    # AI/LLM Settings
    OPENAI_API_KEY: str = ""
    OPENAI_API_BASE: str = "https://api.openai.com/v1"
    OPENAI_ORG_ID: Optional[str] = None
    AI_MODEL: str = "gpt-4"
    AI_TEMPERATURE: float = 0.7
    AI_MAX_TOKENS: int = 2000
    AI_TIMEOUT: int = 30
    USE_LOCAL_LLM: bool = False
    LOCAL_LLM_MODEL_PATH: str = ""

    # FastChat Local Deployment Settings
    USE_FASTCHAT: bool = False
    FASTCHAT_API_BASE: str = "http://localhost:8000/v1"
    FASTCHAT_MODEL_NAME: str = "qwen2.5-7b"
    FASTCHAT_TEMPERATURE: float = 0.7
    FASTCHAT_MAX_TOKENS: int = 2000
    FASTCHAT_TIMEOUT: int = 60

    # Database Settings
    DATABASE_URL: str = "sqlite:///./teaching_assistant.db"
    DATABASE_ECHO: bool = False

    # Redis/Cache Settings (optional)
    REDIS_URL: Optional[str] = None
    CACHE_TTL: int = 3600

    # File Upload Settings
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    UPLOAD_DIR: str = "./uploads"
    ALLOWED_EXTENSIONS: List[str] = [
        ".py", ".java", ".cpp", ".c", ".cc", ".cxx",
        ".js", ".jsx", ".ts", ".tsx",
        ".h", ".hpp",
        ".pdf", ".docx", ".txt"
    ]

    # Code Analysis Settings
    MAX_LINE_LENGTH: int = 120
    COMPLEXITY_THRESHOLD: int = 10
    MIN_MAINTAINABILITY_INDEX: float = 20.0

    # Plagiarism Detection Settings
    PLAGIARISM_THRESHOLD: float = 0.7
    STORE_SUBMISSIONS: bool = True

    # Security Settings
    SECRET_KEY: str = "change-this-in-production-use-a-secure-random-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    TOKEN_URL: str = "/api/v1/auth/login"

    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_PERIOD: int = 60

    class Config:
        import os
        # Support both backend/.env and .env paths
        env_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
        case_sensitive = True
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()

