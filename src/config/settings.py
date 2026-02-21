"""
Configuration settings loaded from environment variables.
"""
import os

from dotenv import load_dotenv
from pydantic import BaseModel, field_validator


class Settings(BaseModel):
    """
    Application configuration sourced from environment variables.

    TODO (Week 4): Implement the following:
    - from_env classmethod to read required env vars
    - validators for env, database_url, api_token, and log_level
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

        Optional variables:
        - LOG_LEVEL (defaults to INFO)

        TODO: Implement reading and missing-variable handling.
        """
        load_dotenv()

        values = {
            "env": os.getenv("APP_ENV"),
            "database_url": os.getenv("DATABASE_URL"),
            "api_token": os.getenv("API_TOKEN"),
        }

        missing = [
            field
            for field in ("env", "database_url", "api_token")
            if values[field] is None
        ]
        if missing:
            raise ValueError(
                "Missing required environment variable(s): " + ", ".join(missing)
            )

        return cls(**values)

    # TODO: Add @field_validator for env
    # Valid values: "dev", "test", "prod"

    @field_validator("env")
    def validate_env(cls, value):
        valid = {"dev", "test", "prod"}
        if value not in valid:
            raise ValueError("env must be one of: dev, test, prod")
        return value

    # TODO: Add @field_validator for database_url
    # Must end with .db and not be empty

    @field_validator("database_url")
    def validate_database_url(cls, value):
        if value is None or value.strip() == "":
            raise ValueError("database_url must be non-empty")
        if not value.endswith(".db"):
            raise ValueError("database_url must end with .db")
        return value

    # TODO: Add @field_validator for api_token
    # Must be non-empty

    @field_validator("api_token")
    def validate_api_token(cls, value):
        if value is None or value.strip() == "":
            raise ValueError("api_token must be non-empty")
        return value

    # TODO: Add @field_validator for log_level
    # Valid values: DEBUG, INFO, WARNING, ERROR, CRITICAL
