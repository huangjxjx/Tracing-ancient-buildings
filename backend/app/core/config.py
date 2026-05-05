import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from pydantic import Field
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


BACKEND_DIR = Path(__file__).resolve().parents[2]


def _default_database_url() -> str:
    database_path = (BACKEND_DIR / "local.db").resolve()
    return f"sqlite+pysqlite:///{database_path.as_posix()}"


def _default_local_storage_root() -> str:
    return str((BACKEND_DIR / "storage").resolve())


class Settings(BaseSettings):
    app_name: str = "Gujian Platform Backend"
    app_description: str = "Phase 1 FastAPI backend shell for overview, twin, and detection APIs."
    app_version: str = "0.1.0"
    environment: str = "development"
    debug: bool = True
    log_level: str = "INFO"
    api_v1_prefix: str = "/api/v1"
    cors_origins: list[str] = Field(
        default_factory=lambda: [
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "http://localhost:5174",
            "http://127.0.0.1:5174",
        ]
    )
    cors_origin_regex: str | None = r"^http://(localhost|127\.0\.0\.1|192\.168\.\d+\.\d+|10\.\d+\.\d+\.\d+):\d+$"
    database_url: str = Field(default_factory=_default_database_url)
    local_storage_root: str = Field(default_factory=_default_local_storage_root)
    upload_public_base_url: str = "http://localhost:8000/api/v1/uploads/files"

    model_config = SettingsConfigDict(
        env_file=BACKEND_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: Any) -> Any:
        if isinstance(value, str):
            normalized = value.strip()
            if not normalized:
                return []
            if normalized.startswith("["):
                return json.loads(normalized)
            return [item.strip() for item in normalized.split(",") if item.strip()]
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()
