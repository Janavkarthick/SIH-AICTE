"""Configuration module for AICTE-Verify backend.

All threshold values defined here are illustrative: replace with Approval Process Handbook values.
Any mock or synthetic configurations are marked SIMULATED.
"""

from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment or defaults."""

    # Project metadata
    PROJECT_NAME: str = "AICTE-Verify Backend"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = True

    # Database connection string
    # Supports SQLite (sqlite+aiosqlite) and PostgreSQL (postgresql+asyncpg)
    DATABASE_URL: str = "sqlite+aiosqlite:///./aicte_verify.db"

    # Security & JWT Token
    JWT_SECRET_KEY: str = "aicte-verify-development-super-secret-jwt-key-2024"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480  # 8 hours

    # File uploads
    MAX_UPLOAD_SIZE_MB: int = 50
    UPLOAD_DIR: str = "./uploads"

    # AI & External integrations
    GEMINI_API_KEY: Optional[str] = None
    RATE_LIMIT_AUTH: str = "10/minute"
    DATA_RETENTION_DAYS: int = 365

    # Service URLs
    FRONTEND_URL: str = "http://localhost:3000"
    BACKEND_URL: str = "http://localhost:8000"

    # Path to rules configurations (checklists, norms, doc_validity)
    CONFIG_RULES_DIR: str = "./config/rules"

    # SIMULATED Mock Issuer Settings
    # Note: SIMULATED issuer simulation parameters
    MOCK_ISSUER_SIMULATED_FAILURES_ENABLED: bool = True
    MOCK_ISSUER_TIMEOUT_SEC: float = 2.0

    # Risk scoring thresholds (illustrative: replace with Approval Process Handbook values)
    RISK_THRESHOLD_LOW_MAX: float = 30.0  # 0 to 30 = Low
    RISK_THRESHOLD_MEDIUM_MAX: float = 60.0  # 31 to 60 = Medium
    RISK_THRESHOLD_HIGH_MIN: float = 61.0  # 61 to 100 = High

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    def resolve_rules_path(self, filename: str) -> Path:
        """Resolve rule configuration path safely across local or docker runtime."""
        # Try relative to current working directory
        p = Path(self.CONFIG_RULES_DIR) / filename
        if p.exists():
            return p.resolve()
        
        # Try relative to repo root (up 2 levels from backend/app/core)
        repo_root = Path(__file__).resolve().parent.parent.parent.parent
        p2 = repo_root / "config" / "rules" / filename
        if p2.exists():
            return p2.resolve()

        # Try backend/../config
        p3 = Path(__file__).resolve().parent.parent.parent / "config" / "rules" / filename
        if p3.exists():
            return p3.resolve()

        return p


settings = Settings()
