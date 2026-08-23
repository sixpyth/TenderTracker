import os
from pydantic import PostgresDsn, EmailStr, AnyHttpUrl, field_validator, ValidationInfo
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Any
import secrets
from app.enums import ModeEnum


class Settings(BaseSettings):
    MODE: ModeEnum = ModeEnum.development
    API_VERSION: str = "v1"
    API_V1_STR: str = f"/api/{API_VERSION}"
    PROJECT_NAME: str = "Tender Status Tracking Microservice"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 1  # 1 hour
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 100  # 100 days
    DATABASE_USER: str = "postgres"
    DATABASE_PASSWORD: str = "postgres"
    DATABASE_HOST: str = "database"
    DATABASE_PORT: int | str = 5432
    DATABASE_NAME: str = "fastapi_db"
    REDIS_HOST: str = "redis_server"
    REDIS_PORT: str = "6379"
    DB_POOL_SIZE: int = 83
    WEB_CONCURRENCY: int = 9
    POOL_SIZE: int = max(DB_POOL_SIZE // WEB_CONCURRENCY, 5)
    ASYNC_DATABASE_URI: str | None = None

    @field_validator("ASYNC_DATABASE_URI", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: str | None, info: ValidationInfo) -> Any:
        if isinstance(v, str):
            return v
        values = info.data
        return str(PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=values.get("DATABASE_USER"),
            password=values.get("DATABASE_PASSWORD"),
            host=values.get("DATABASE_HOST"),
            port=int(values.get("DATABASE_PORT")),
            path=f"{values.get('DATABASE_NAME') or ''}",
        ))

    FIRST_SUPERUSER_EMAIL: EmailStr = "admin@admin.com"
    FIRST_SUPERUSER_PASSWORD: str = "admin"

    SECRET_KEY: str = "09d25e0sas4faa6c52gf6c818166b7a9563b93f7sdsdef6f0f4caa6cf63b88e8d3e7"
    ENCRYPT_KEY: str = "TshgGacKPYrm35m89UqbRg46JAbUm2yRtxOCQFdqa3w="
    BACKEND_CORS_ORIGINS: list[str] | list[AnyHttpUrl] = ["*"]

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: str | list[str]) -> list[str] | str:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    model_config = SettingsConfigDict(
        case_sensitive=True,
        env_file=".env",
        extra="ignore",
    )


settings = Settings()