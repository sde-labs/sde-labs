"""
Configuration settings loaded from environment variables.
"""
import os

from dotenv import load_dotenv
from pydantic import BaseModel, field_validator


class Settings(BaseModel):
    """
    Application configuration sourced from environment variables.

    TODO (Week 5): Students will test this behavior.
    """
    env: str
    database_url: str
    api_token: str
    log_level: str = "INFO"

    @classmethod
    def from_env(cls):
        """
        Build Settings from environment variables.

        Local development reads from `.env` via python-dotenv.
        CI (GitHub Actions) should provide the same keys as environment variables.

        Required variables:
        - APP_ENV
        - DATABASE_URL
        - API_TOKEN

        Reads required values and validates quickly.
        """
        load_dotenv()

        env = os.getenv("APP_ENV")
        database_url = os.getenv("DATABASE_URL")
        api_token = os.getenv("API_TOKEN")
        log_level = os.getenv("LOG_LEVEL", "INFO")

        missing = []
        if env is None:
            missing.append("env")
        if database_url is None:
            missing.append("database_url")
        if api_token is None:
            missing.append("api_token")

        if missing:
            raise ValueError("Missing required environment variable(s): " + ", ".join(missing))

        assert env is not None
        assert database_url is not None
        assert api_token is not None

        return cls(
            env=env,
            database_url=database_url,
            api_token=api_token,
            log_level=log_level,
        )

    @field_validator("env")
    def validate_env(cls, value):
        if value not in {"dev", "test", "prod"}:
            raise ValueError("env must be one of: dev, test, prod")
        return value

    @field_validator("database_url")
    def validate_database_url(cls, value):
        if value is None or value.strip() == "":
            raise ValueError("database_url must be non-empty")
        if not value.endswith(".db"):
            raise ValueError("database_url must end with .db")
        return value

    @field_validator("api_token")
    def validate_api_token(cls, value):
        if value is None or value.strip() == "":
            raise ValueError("api_token must be non-empty")
        return value

    @field_validator("log_level")
    def validate_log_level(cls, value):
        normalized = value.upper()
        allowed = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if normalized not in allowed:
            allowed_values = ", ".join(sorted(allowed))
            raise ValueError(f"log_level must be one of: {allowed_values}")
        return normalized
